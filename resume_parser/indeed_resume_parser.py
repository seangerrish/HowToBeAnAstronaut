#!/usr/bin/python

import career
import re
import datetime

import indeed_resume_parser_v1
import indeed_resume_parser_v2

from HTMLParser import HTMLParser

def ReadDegrees():
    f = open("education/degrees.txt", "r")
    degrees = {}
    for row in f:
        row = row.strip().lower()
        parts = row.split(",")
        for nym in parts:
            degrees[nym] = parts[0]

    return degrees

DEGREES = ReadDegrees()

DATE_RE = re.compile("([^ ]+ )?((19|20)\d\d)")
MONTHS = {
    "January": 0,
    "February": 1,
    "March": 2,
    "April": 3,
    "May": 4,
    "June": 5,
    "July": 6,
    "August": 7,
    "September": 8,
    "October": 9,
    "November": 10,
    "December": 11
    }

class IndeedCareer(career.Career):
    def __init__(self, text, source):
        self.META_RE = re.compile("(<(/?span)[^>]*>)")
        self.source = source
        self.education = None
        self.jobs = None

        text = re.sub(self.META_RE, "", text)
        self.elts = {}

        self.Parse(text)

    def Parse(self, text):
        p1 = indeed_resume_parser_v1.IndeedHTMLParser()

        p1.feed(text)
        self.education = p1.education
        self.jobs = p1.jobs

        if len(self.jobs) == 0 or len(self.education) == 0:
            return

        print [ str(education) for education in self.education ]
        print [ str(job) for job in self.jobs ]

if __name__ == '__main__':
    resumes = open("data/v1.1/indeed_resume_filenames.txt", "r")

    for row in resumes:
        filename = row.strip()
        print "processing %s." % filename

        try:
            f = open(filename, "r")
            indeed_career = IndeedCareer(f.read(), filename)
            f.close()
        except:
            continue
        
    resumes.close()
