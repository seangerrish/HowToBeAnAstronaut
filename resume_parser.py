#!/usr/bin/python

# Parse resumes.

import re
import sys

class Prerequisite:
    def __init__(self, name, description, level, type):
        self._description = description 
        # Can be any of
        self._name = name
        self._level = level
        self._type = type

    def __str__(self):
        if self._description:
            return "%s: %s" % (self._name,
                               self._description)
        return self._name

class Job(Prerequisite):
    def __init__(self, industry, title):
        Prerequisite.__init__(self, title, description, "", "job")
        self._industry = industry

ROLE_PATTERNS = [
    ("years",
     re.compile("((19|20)\d\d).*?-.*?((19|20)\d\d)", re.IGNORECASE),
     (0, 2),
     100),
    ("years2",
     re.compile("((19|20)\d\d).+?to.+?((19|20)\d\d)", re.IGNORECASE),
     (0, 2),
     100),
    ("years3",
     re.compile("((19|20)\d\d) to ((19|20)\d\d)", re.IGNORECASE),
     (0, 2),
     100),
    ("years4",
     re.compile("((19|20)\d\d)-((19|20)\d\d)", re.IGNORECASE),
     (0, 2),
     100),
    ("year",
     re.compile("(.*[^\d])?((19|20)\d\d)([^\d].*)?", re.IGNORECASE),
     (1,0),
     100),
    ("year only",
     re.compile("((19|20)\d\d)", re.IGNORECASE),
     (0,),
     10),
    ]

class Resume():
    def __init__(self, text, role_descriptions):
        format = "chronological"
        self._roles = {}
        self.ParseChronologicalResume(text, role_descriptions)

    def ParseEducation(self, text):
        pass

    def ParseExperience(self, text, role_descriptions):
        start = 0
        end = len(text)
        m = 0
        role_description_offsets = []
        pending_role = None
        years = []
        def MatchDate(start, end, text, pending_role,
                      role_description_offsets,
                      years,
                      failed_res):
            best_score = -1
            best_match_end = 1e10
            best_year_begin = None
            best_year_end = None
            for name, pattern, groups, score in ROLE_PATTERNS:
                if name in failed_res:
                    continue
                #print name
                #print pattern
                # Don't bother with resumes longer than 30k chars.
                #print start
                #print end
                m = pattern.search(text[start:end], re.IGNORECASE)
                if m and (score >= best_score and (start + m.end() < best_match_end or start + m.end() + 20 < best_match_end)):
                    #print "begin ."
                    #print name
                    #print m.start()
                    #print m.end()
                    #print text[start + m.start():start + m.end()]
                    best_score = score
                    #print m.groups()
                    #print "replacing %s %s %s" % (str(best_match_end), str(best_year_begin), str(best_year_end))
                    if name in ("years", "years2", "years3", "years4"):
                        #print m.groups()

                        best_year_begin = m.groups()[groups[0]]
                        best_year_end = m.groups()[groups[1]]
                        #print name
                        #print m.groups()
                        #print "years: %s-%s" % (year_begin, year_end)
                        best_match_end = m.end() + start
                    elif name == "year only":
                        #print m.groups()
                        best_year_begin = m.groups()[groups[0]]
                        best_year_end = ""
                        #print name
                        #print m.groups()
                        #print "years: %s-%s" % (year_begin, year_end)
                        best_match_end = m.end() + start
                    else:
                        #print name
                        #print m.groups()
                        best_year_begin = m.groups()[groups[0]]
                        best_year_end = ""
                        #print name
                        #print m.groups()
                        #print "years: %s-%s" % (year_begin, year_end)
                        best_match_end = m.end() + start
                    #print "match. %s %s %s" % (str(best_year_end), str(best_year_begin), str(best_match_end))

                    #print "replaced %s %s %s" % (str(best_match_end), str(best_year_begin), str(best_year_end))
                    #print "begin text %d %d" % (start, best_match_end)
                    #print text[start:best_match_end]
                    #print "end %d %d" % (start, best_match_end)
                elif m:
                    #print "match: %s" % name
                    #print best_score
                    pass
                else:
                    #print "no match %s" % name
                    #print "no match"
                    pass
                if not m:
                    failed_res[name] = True

            if best_year_begin is not None:
                #if pending_role is not None:
                #    role_end = m.start() + start
                #    role_description_offsets.append((pending_role, role_end))
                years.append((best_year_begin, best_year_end))
                #print "adding role %d-%d:" % (pending_role, role_end)
                #print text[pending_role:role_end]

                if pending_role is not None:
                    role_end = m.start() + start
                    role_description_offsets.append((pending_role, role_end))

                pending_role = best_match_end            

            new_start = start
            if m:
                new_start = best_match_end

            return (m, new_start, pending_role)

        pending_role = None
        role_years = []
        role_description_offsets = []
        failed_res = {}
        m, start, pending_role = MatchDate(start, end,
                                           text, pending_role,
                                           role_description_offsets,
                                           role_years,
                                           failed_res)
        while m:
            m, start, pending_role = MatchDate(start, end,
                                               text, pending_role,
                                               role_description_offsets,
                                               role_years,
                                               failed_res)

        self._roles = []
        for time_period, ((y_begin, y_end), (t_begin, t_end)) in enumerate(
            zip(role_years, role_description_offsets)):
            #print "%s-%s:" % (y_begin, y_end)
            #print "------------BEGIN DESCRIPTION"
            #print text[t_begin:t_end]
            self._roles.append([])
            role_text = text[t_begin:t_end]
            role_text = role_text.lower()
            #print "%s-%s text:" % (y_begin, y_end)
            #print role_text
            role_text = role_text.replace("\n", " ")
            role_text = role_text.replace("\t", " ")
            role_text = role_text.replace("\r", " ")
            role_text = role_text.replace(",", " ")
            terms = role_text.split(" ")
            history = []
            role_description = ""
            for term in terms:
                term = term.strip()
                #print history
                if len(history) > 3:
                    history = history[1:4]
                #                print len(history)
                term = term.strip()
                if len(term) == 0:
                    continue
                history.append(term)
                #print history
                history_length = min(len(history), 4)

                for i in range(history_length):
                    terms_ = " ".join(history[i:history_length])
                    #print "'%s'" % terms_

                    #print "terms: " + terms_
                    if "software developer" not in role_descriptions:
                        print "not found."
                        #print role_descriptions
                        sys.exit(1)
                    if terms_ in role_descriptions:
                        self._roles[-1].append((terms_, role_descriptions[terms_]))
                        print "adding role: %s" % str(role_descriptions[terms_])
                        #print terms_
                        #print "Found: %s" % str(terms_)
                        #print "--"
                    else:
                        #print "%s not found." % terms_
                        pass

            #            print role_descriptions
            #            print role_description
            #print self._roles
            #print "---"
                #            print text[t_begin:t_end]
            #print "------------END DESCRIPTION"
            
        print "---"
        print 
        for (y1, y2), roles in zip(role_years, self._roles):
            #print roles
            if len(roles) == 0:
                continue
            print "%s-%s: %s" % (y1, y2, ",".join([canonical for text, (id_, canonical) in roles] ))

    def ParseChronologicalResume(self, text, role_descriptions):
        #print text
        self.ParseEducation(text)
        self.ParseExperience(text, role_descriptions)

class ResumeFactory():
    def ResumeFromText():
        pass

ROLE_DESCRIPTIONS_FILENAME = "role_descriptions.txt"

def ReadRoleDescriptions(role_descriptions):
    f = open(ROLE_DESCRIPTIONS_FILENAME, "r")
    canonical = None
    # This is indexed by role indices.
    canonical_roles = {}
    for l in f:
        l = l.strip()
        if len(l) and l[0] == "#":
            continue
        l = l.lower()
        parts = l.split(",")
        if len(parts) >= 2:
            try:
                index = int(parts[-1])
                role = ",".join(parts[0:len(parts) - 1])
                #print role
                if index not in canonical_roles:
                    canonical_roles[index] = role                
            except:
                continue
            canonical = canonical_roles[index]
        role_descriptions[role] = (index, canonical)

    f.close()
    
if __name__ == '__main__':
    resumes_file = open("resumes.txt", "r")

    role_descriptions = {}

    # Options for parsing role
    # (role in parens)

    # Other things to parse:
    # bar?
    ReadRoleDescriptions(role_descriptions)
    
    for resume_filename in resumes_file:
        resume_filename = resume_filename.strip()
        resume_file = open(resume_filename, "r")
        print resume_filename
        resume = Resume(resume_file.read(), role_descriptions)
        resume_file.close()
    resumes_file.close()

