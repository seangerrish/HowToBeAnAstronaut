#!/usr/bin/python
#
# Here we create several types of models:
# 1. An N-gram model.
# 2. A model in which careers are partitioned into the following
#  types:
# HS -> Work
# HS -> Work 
# HS -> 4-year college (within 3 years)
# HS -> Work (3 - 8 years) -> college
#

import csv
import copy
import datetime
import math
import os
import pickle
import sys
import random

random.seed(1)

from resume_parser.career import NormalizedCareer, CareersFromFile, DEGREE_EVENT, DEGREE_ORDER, JOB_EVENT

from models.v1_1.model_constants import (
    DEGREE_COUNTS_FILE,
    DEPTHS,
    START_DEPTH,
    OVERALL_STATS_FILE,
    JOB_CLUSTERS)

TOPICS_FILE = "data/v1.1/final.beta"
VOCAB_FILE = "data/v1.1/vocab.csv"
DOCS_FILE = "data/v1.1/docs.csv"
WORD_LIKELIHOODS = "data/v1.1/word-assignments.dat"
WORD_LIKELIHOODS_CATEGORIES = "data/v1.1.1/word-assignments.dat"
ROLE_THEMES_FILE = "data/v1.1/role_themes.csv"
ROLETHEME_CATEGORIES = "data/v1.1/roletheme_categories.csv"

def NewSummary():
    return {
        "summary event": None,
        "number of jobs sum": 0,
        "years of college sum": 0,
        "duration": 0,
        "count": 0,
        "events": {},
        "degrees": {},
        "jobs": {},
    }

def ReadMetadata():
    vocab = {}
    f = open(VOCAB_FILE, "r")
    for i, terms in enumerate(f):
        vocab[i] = terms.split(",")[0]
    f.close()

    f = open(ROLE_THEMES_FILE, "r")
    reader = csv.reader(f)
    role_themes = {}
    for role, topic, _ in reader:
        role_themes[(role, topic)] = True

    f.close()

    docs = {}
    docs_f = open(WORD_LIKELIHOODS, "r")
    doc_ids_f = open(DOCS_FILE, "r")
    for i, (doc_id, row) in enumerate(zip(doc_ids_f, docs_f)):
        doc_id = doc_id.strip().split(",")[1]
        role_rolethemes = {}
        roles = row.strip().split(" ")[1:]
        roles_themes = {}
        for role_theme in roles:
            role, theme = role_theme.split(":")
            role = vocab[int(role)]
            if "role_" not in role:
                continue
            roles_themes[role] = CanonicalRoleTheme(role, theme, role_themes)

        docs[doc_id] = role_themes

    docs_f.close()
    doc_ids_f.close()

    return (vocab, role_themes, docs)

def Cluster(generator):
    vocab, role_themes, docs = ReadMetadata()

    # docs are indexed by career ID and year.
    doc_terms_by_year = {}

    # Clusters are indexed as { role_id: { cluster : { year : { term: count} } } }
    # where year is an index of years forward or years back.
    YEAR_RANGE = [ -30, 30 ]
    y0, y1 = YEAR_RANGE[0], YEAR_RANGE[1]

    files = {}
    for i, career in enumerate(generator):
        if i % 1000 == 0:
            print "handling %d" % i

        if i > 20000000:
            break

        if career is None:
            print "skipping None career."
            continue
        normalized_career = NormalizedCareer(career)
        role_tuple = []
        events_by_year = normalized_career.events_by_year

        # Only collect counts for a career if an individual gained a degree in
        # a particular year.
        # print normalized_career.normalized_events
        for i, event in enumerate(normalized_career.normalized_events):
            # print i, event.Id()
            if "-1" in event.Id():
                continue
            
            id = event.Id()
            if id not in files:
                files[id] = open("/tmp/%s" % id, "w")

            event_date = event.start_date
            if event_date is None:
                continue

            terms = []
            for depth in range(y0, y1):
                added_event = False
                date = event_date + datetime.timedelta(days=365 * depth)

                for e in normalized_career.normalized_events:
                    if e.start_date is None or e.end_date is None:
                        continue

                    if "-1" in e.Id():
                        continue
                    if e.start_date < date and e.end_date > date:
                        # print "adding: " + e.Id()
                        terms.append(e.Id())
                        added_event = True
                        break

                if not added_event:
                    terms.append("None")

            # print len(terms)
        
            row = "%s,%s" % (career.id.replace(",", ";"), ",".join([ x for x in terms ]))
            print >>files[id], row

    for id, f in files.items():
        f.close()

    all_clusters = {}
    job_clusters = {}

    NUMBER_CLUSTERS = 5
    for id, f in files.items():
        clusters = {}
        items = {}
        f = open(f.name, "r")
        for i, _ in enumerate(f):
            pass
        
        f.close()
        if i < 600:
            print "skipping file, length %d" % i
            continue

        print "Reading and clustering file, length %d" % i
        
        f = open(f.name, "r")        
        for i, row in enumerate(f):
            parts = row.strip().split(",")
            id = parts[0]
            roles = parts[1:]
            assert len(roles) == len(range(y0, y1)), "Error: line %d, file %s: roles has length %d vs %d" % (i, f.name, len(roles), len(range(y0, y1)))
            #print id, counts
            items[id] = {}
            for year, role in zip(range(YEAR_RANGE[0], YEAR_RANGE[1]), roles):
                if role != "None":
                    items[id][year] = role
        f.close()

        clusters[id] = {}
        y0, y1 = YEAR_RANGE
        for i in range(NUMBER_CLUSTERS):
            clusters[i] = {}
            for year in range(y0, y1):
                clusters[i][year] = {}
                for term in vocab:
                    clusters[i][year][term] = random.random() + 1.0

        def LogSum(log_a, log_b):
            if log_a <= log_b:
                return math.log(math.exp(log_a - log_b) + 1) + log_b
            else:
                return LogSum(log_b, log_a)

        def MStep(clusters):
            for c in range(NUMBER_CLUSTERS):
                if c not in clusters:
                    clusters[c] = {}
                    
                for year in range(y0, y1):
                    if year not in clusters[c]:
                        clusters[c][year] = {}
                    
                    total = None
                    for term in clusters[c][year]:
                        if term not in clusters[c][year]:
                            clusters[c][year][term] = -10.0

                        log_weight = clusters[c][year][term]
                        if total is None:
                            total = log_weight
                        else:
                            total = LogSum(log_weight, total)
                    
                    t = 0.0
                    # print c, year
                    #print "length:", len(clusters[c][year])
                    #print clusters[c][year]
                    for term in clusters[c][year]:
                        clusters[c][year][term] = clusters[c][year][term] - total
                        t += math.exp(clusters[c][year][term])

                    if len(clusters[c][year]):
                           assert abs(t - 1.0) < 0.001, "Error: total is not 1: %.2f" % t

        def EStep(item, clusters, new_clusters, destination=None):
            e_cluster = {}
            total_weight = None
            for c in range(NUMBER_CLUSTERS):
                log_weight = 0.0
                for year in range(y0, y1):
                    term = item.get(year, None)
                    if term is None:
                        continue

                    if term not in clusters[c][year]:
                        # print "filling in: " + str(len(clusters[c][year]))
                        clusters[c][year][term] = random.random() - 10.0

                    # If this is the first iteration, initialize with random numbers.
                    # No log weight should go below -10.
                    log_weight += max(clusters[c][year][term], -10)

                if log_weight == None:
                    log_weight = -1000

                #print total_weight

                # Take this likelihood to the power of 1/3 to soften it some.
                log_weight = log_weight / 5.0

                if log_weight < -1000:
                    # print "  ", log_weight
                    log_weight = -1000

                # print log_weight

                # Take e_cluster log likelihood to the power of 1/100 since
                # these observations are so highly correlated.
                e_cluster[c] = log_weight
                if total_weight == None:
                    total_weight = log_weight
                else:
                    total_weight = LogSum(total_weight, log_weight)
                    #print "total weight: " + str(total_weight) 

            ll = 0.0
            #print total_weight
            for c in range(NUMBER_CLUSTERS):
                #print c, e_cluster[c], total_weight
                #print e_cluster[c]

                e_cluster[c] = e_cluster[c] - total_weight
                if destination is not None:
                    destination[c] = e_cluster[c]
                
                # print [ (c, x) for (c, x) in e_cluster.items() ]
                #print e_cluster[c]
                p_cluster = math.exp(e_cluster[c])
                # print c, p_cluster

                if c not in new_clusters:
                    new_clusters[c] = {}

                for year in range(y0, y1):
                    if year not in new_clusters[c]:
                        new_clusters[c][year] = {}

                    term = item.get(year, None)
                    if term is None:
                        continue

                    ll_tmp = (clusters[c][year][term]) * p_cluster

                    assert clusters[c][year][term] <= 0.0, "Positive term %d %d %s %s"  % (c, year, term, str(clusters[c][year][term]))
                        
                    #if ll_tmp > 0.0:
                    #    print c, ll_tmp, p_cluster, clusters[c][year][term]
                        
                    ll += ll_tmp

                    if term not in new_clusters[c][year]:
                        new_clusters[c][year][term] = math.log(p_cluster + 1e-9)
                    else:
                        new_clusters[c][year][term] = LogSum(math.log(p_cluster + 1e-9),
                                                             new_clusters[c][year][term])

            return ll

        last_ll = -1e10
        delta = 100.0
        ll = 0.0
        while delta > 10: # 0.5:
            new_clusters = {}
            ll = 0.0
            for doc, value in items.items():
                #print doc, value
                ll += EStep(value, clusters, new_clusters)
            print "log likelihood a:" + str(ll)

            delta = (ll - last_ll)
            last_ll = ll

            MStep(new_clusters)
            clusters = copy.deepcopy(new_clusters)

        print "Last ll:" + str(ll)

        for c in clusters:
            for time in clusters[c]:
                weights = [ (term, weight) for (term, weight) in clusters[c][time].items() ]
                weights.sort(key=lambda x: x[1], reverse=True)
                if len(weights) < 1:
                    break

                terms = []
                term, weight = weights[0]
                i = 0
                while weight > math.log(0.03) and i + 1 < len(weights):
                    i += 1
                    terms.append("%s:%.5f" % (term, weight))
                    term, weight = weights[i]

                if len(terms) == 0:
                    term, weight = weights[0]
                    terms.append("%s:%.5f" % (term, weight))

        row = []
        base = os.path.basename(f.name)
        job_clusters[base] = True
        if base not in all_clusters:
            all_clusters[base] = {}
        for doc, value in items.items():
            new_clusters = {}                        
            if doc not in all_clusters[base]:
                all_clusters[base][doc] = {}
                EStep(value, clusters, new_clusters, all_clusters[base][doc])
                # row_items = [ x for x in all_clusters[base][doc].items() ]
                # row_items = [ "%d:%.4f" % (x, y) for (x, y) in row_items ]
                # row = "%s,%s,%s" % (base, doc, ",".join(row_items))
                # print >>out, row

    out = open(JOB_CLUSTERS, "w")
    pickle.dump(job_clusters, out)
    out.close()

    return all_clusters

def GenerateDegreeNGrams(years_out_tuple, counts, generator, clusters):
    """Generate ngram dictionary counts for bachelors' degrees."""

    vocab, role_themes, docs = ReadMetadata()
    
    for i, career in enumerate(generator):
        if i % 100 == 0:
            print "handling %d" % i
            c = {}
            for j in counts:
                if len(j) == 1:
                    c[j] = True

        if i > 1000000:
            break
    
        if career is None:
            # print "skipping None career."
            continue
        normalized_career = NormalizedCareer(career)
        role_tuple = []
        events_by_year = normalized_career.events_by_year

        def Index(doc_id, study_event, normalized_career, counts):
            start_date = study_event.start_date
            if start_date == None:  
                return
            
            last_depth = START_DEPTH

            id = study_event.Id()
            
            if id not in counts:
                counts[id] = {}

            id_clusters = None
            if id in clusters:
                id_clusters = clusters[id]
                    
            def AddCounts(counts, summary, last_summary, last_depth, max_event, weight):
                if last_summary is None:
                    return

                last_max_event = last_summary["summary event"]
                if last_depth not in counts:
                    counts[last_depth] = {}

                if (last_max_event,) not in counts[last_depth]:
                    counts[last_depth][(last_max_event,)] = NewSummary()
                    
                for key, value in summary.items():
                    if type(value) == type(0) or type(value) == type(0.0):
                        counts[last_depth][(last_max_event,)][key] += value * weight

                if (last_max_event, max_event) not in counts[last_depth]:
                   counts[last_depth][(last_max_event, max_event)] = NewSummary()
                    
                for key, value in summary.items():
                    if type(value) == type(0):
                        counts[last_depth][(last_max_event, max_event)][key] += value * weight

            last_summary = None
            for depth in DEPTHS:
                pair = (last_depth, depth)
                summary = NewSummary()
                for years_forward in range(last_depth, depth):
                    date = start_date + datetime.timedelta(365*years_forward)
                    for event in normalized_career.normalized_events:
                        if event.start_date is None or event.end_date is None:
                            continue

                        if date < event.start_date or date >= event.end_date:
                            continue

                        summary["count"] += 1
                        summary["events"][event.Id()] = summary["events"].get(event.Id(), 0) + 1
                        if event.type == DEGREE_EVENT:
                            summary["degrees"][event.Id()] = summary["degrees"].get(event.Id(), 0) + 1
                            summary["years of college sum"] += 1
                        elif event.type == JOB_EVENT:
                            summary["jobs"][event.Id()] = summary["jobs"].get(event.Id(), 0) + 1

                if summary["count"] == 0:
                    last_summary = None
                    continue

                last_depth = depth

                max_event = None
                max_count = 0
                for event, count in summary["events"].items():
                    if count > max_event:
                        max_event = event
                        max_count = count

                summary["summary event"] = max_event
                summary["number of jobs sum"] = min(pair[1] - pair[0], len(summary["jobs"]))
                summary["years of college sum"] = min(pair[1] - pair[0],
                                                      sum(summary["degrees"].values()))

                if id == "job:-1":
                    continue
                
                AddCounts(counts[id], summary, last_summary, last_depth, max_event, 1.0)

                if id_clusters is not None:
                    # print "found cluster"
                    if career.id in id_clusters:
                        for cluster, log_weight in id_clusters[career.id].items():
                            cluster_id = "%s:%d" % (id, cluster)
                            if cluster_id not in counts:
                                counts[cluster_id] = {}
                            # print cluster_id, math.exp(log_weight)
                            AddCounts(counts[cluster_id], summary, last_summary, last_depth, max_event, math.exp(log_weight))

                last_summary = summary

        # Only collect counts for a career if an individual gained a degree in
        # a particular year.
        # print normalized_career.normalized_events
        for i, event in enumerate(normalized_career.normalized_events):
            # print i, event.Id()
            Index(career.id, event, normalized_career, counts)


def CanonicalRoleTheme(role, theme, role_themes):
    if (role, theme) in role_themes:
        return (role, theme)

    assert (role, "None") in role_themes, "Role / theme %s did not appear in role_themes." % str((role, None))
    return (role, "None")


def GenerateRolethemeCategories():
    # First, read the list of role themes.
    f = open(ROLE_THEMES_FILE, "r")
    reader = csv.reader(f)
    role_themes = {}
    for role, topic, _ in reader:
        role_themes[(role, topic)] = True

    f.close()

    vocab = {}
    vocab_file = open(VOCAB_FILE, "r")
    for i, row in enumerate(vocab_file):
        row = row.split(",")[0]
        vocab[str(i)] = row
    vocab_file.close()
    
    # Next, read through word-assignments and careers to find the main
    # category for each role-theme pair.
    f1 = open(WORD_LIKELIHOODS, "r")
    f2 = open(WORD_LIKELIHOODS_CATEGORIES, "r")
    roletheme_categories = {}
    for l1, l2 in zip(f1, f2):
        parts1 = l1.split(" ")[1:]
        parts2 = l2.split(" ")[1:]
        
        parts1 = [ x.split(":") for x in parts1 ]
        parts2 = [ x.split(":") for x in parts2 ]

        terms = {}
        for term, theme in parts1:
            term = str(int(term))
            role = vocab[term]
            if "role_" not in role:
                continue
            terms[term] = CanonicalRoleTheme(role, theme, role_themes)

        for term, category in parts2:
            term = str(int(term))
            role = vocab[term]
            if "role_" not in role:
                continue
            roletheme = terms[term]
            if roletheme not in roletheme_categories:
                roletheme_categories[roletheme] = {}

            roletheme_categories[roletheme][category] = roletheme_categories[roletheme].get(category, 0) + 1

    f1.close()
    f2.close()

    roletheme_top_categories = {}
    for roletheme in roletheme_categories:
        categories = roletheme_categories[roletheme].items()
        categories.sort(key=lambda x: x[1], reverse=True)
        if len(categories):
            roletheme_top_categories[roletheme] = categories[0][0]

    top_categories_file = open(ROLETHEME_CATEGORIES, "w")
    for roletheme, category in roletheme_top_categories.items():
        print >>top_categories_file, "%s,%s,%d" % (roletheme[0], roletheme[1], int(category))
    top_categories_file.close()

def SaveCounts(counts):
    f = open(DEGREE_COUNTS_FILE, "w")
    pickle.dump(counts, f)
    f.close()

if __name__ == '__main__':
    # First, generate role theme pairs.
    print "Generating role theme pairs."

    # Next, read through word assignments and careers to find the main category of each role theme.
    print "Generating roletheme categories."
    # GenerateRolethemeCategories()

    print "Building an n-gram model."
    counts = {}

    # Generate N-grams starting from bachelors' degrees.
    clusters = Cluster(CareersFromFile("/tmp/foo.txt"))
    GenerateDegreeNGrams(DEPTHS, counts, CareersFromFile("/tmp/foo.txt"), clusters)

    SaveCounts(counts)
