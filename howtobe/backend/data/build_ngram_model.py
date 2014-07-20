#!/usr/bin/python

#!/usr/bin/python
#
# This script provides a service for bls jobs.
# The main functions exported are:
# next_steps
# previous_steps
import copy
import pickle

CONDITIONALS = {}
GLOBAL_CONDITIONALS = {}
GLOBAL_MARGINALS = {}
MARGINALS = {}
SMOOTHED_CONDITIONALS = {}

DEPTHS = [ -20, -15, -10, -5, 0, 5, 10, 15, 20 ]

from resume_parser.career import (NormalizedCareer,
        CareersFromFile,
        DEGREE_EVENT,
        DEGREE_ORDER)

import pickle

TIMES = [ -20, -15, -10, -5, 0 ]

SMOOTHED_DATA_FILENAME = "howtobe/backend/data/smoothed.pickle"

def NewSummary():
    return {
        "number of jobs": 0,
        "years of college": 0,
        "duration": 0,
        "count": 0,
        "degree": None,
        "classes": None,
        "job": None,
    }


def BuildNGrams():
    pass

def Career():
    pass

class Career:
    def __init__(self, id):
        self.id = id
        self.roles = []
        self.degrees = []

def ResumeGenerator(f):
    c = None
    mode = None
    for i, row in range(f):
        row = row.strip()
        if row == "### ID":
            if c != None:
                yield c

            mode = row
        elif row == "### JOBS":
            mode = row
        elif row == "EDUCATION":
            mode = row
        elif mode == "### JOBS":
            parts = row.split(",")
            start = datetime.strftime("%Y-%m-%d")
            # job = (start, end, 
            # c.jobs.append(job)
        elif mode == "### ID":
            c = Career()

        yield c
"""

def Smooth(raw, smoothed):
    for key, value in raw:
        smoothed[key] = value

def StatsFromCareer():


def AddStats(ngrams_raw, career):
    pass

def CollectNGramStats(ngrams_raw):
    ngram_model = {}
    SHARDS = 100
    for i in range(1):
        continue

        f = open("data/v1.1/parsed_resumes.dat-%05d-of-%05d" % (i, SHARDS), "r")
        for j, career in enumerate(ResumeGenerator(f)):
            AddStats(ngrams_raw)

        f.close()

if __name__ == '__main__':
    ngrams_raw = {}
    CollectNGramStats(ngrams_raw)

    ngrams_smoothed = {}
    Smooth(ngrams_raw, ngrams_smoothed)
    f = open(SMOOTHED_DATA_FILENAME, "w")
    pickle.dump(ngrams_smoothed, f)
    f.close()

