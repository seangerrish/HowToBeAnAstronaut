#!/usr/bin/python

# Defines classes for parsing educational level from OOH descriptions.

from xml.parsers import expat
import re
import sys
import urllib

OCOS_LIST_FILENAME = "download/files.txt"

education_res = [
(    "bachelers", "bachelor.?s degrees? in ([^\.,]+) or ([^\.,]+)[,;\.]"),
(    "bachelers", "bachelor.?s degrees? in ([^\.,]+)[\.,;]"),
(    "bachelers", "college degree"),
(    "bachelers", "bachelor.?s degree is required"),
(    "degree", "degrees? in ([^\.,]+) or ([^\.,]+)[,;\.]"),
(    "degree", "degrees? in ([^\.,]+), ([^\.,]+), or ([^\.,]+)[,;\.]"),
(    "degree", "degrees?.* in ([^\.,]+)[\.,;]"),
(    "degree", "degrees?.* in ([^\.,]+) or ([^\.,]+)[,;\.]"),
(    "degree", "degrees?.* in ([^\.,]+), ([^\.,]+), or ([^\.,]+)[,;\.]"),
(    "course", "course in ([^\.,])\.,"),
(    "course", "courses in (both)? ([^\.,]) or ([^\.,])\.,"),
(    "course", "courses in ([^\.,]), ([^\.,]), or ([^\.,])\.,"),
(    "course", "courses in ([^\.,]), ([^\.,]), ([^\.,]), or ([^\.,])\.,"),
(    "masters", "(master'?s|bs|b.s.) degree in ([^\.,]+) or ([^\.,]+)[,;\.]"),
(    "masters", "master'?s degree in ([^\.,]+)[\.,;]"),
(    "masters", "master'?s degree from ([^\.,]+)[\.,;]"),
(    "phd", "require.* a ph\.?d"),
(    "phd", "(a )ph\.?d in ([^\.,]+)(is required)?[\.,;]"),
(    "phd", "ph\.?d degree in ([^\.,]+)[\.,;]"),
(    "phd", "ph\.?d degree in ([^\.,]+)[\.,;]"),
(    "phd", "ph\.?d degree from ([^\.,]+)[\.,;]"),
(    "degree", "a(n) ([^\.,]+) degree[\.,;]"),
(    "degree", "a(n) ([^\.,]+) degree[\.,;]"),
(    "recommendation", "(need|require) [^\.]recommendation"),
(    "academy", "academy"),
(    "program of study", "(attend|pass|requires)(.+) program.of.study"),
(    "highschool", "high ?school diploma"),
(    "highschool", "GED|G\.E\.D\."),
(    "portfolio", "(good|create a) portfolio"),
(    "work_related_experience", "work[- ]related experience"),
(    "work_related_experience", "work (experience )? in a related field"),
(    "on the job training", "on.?the.?job training"),
(    "on the job training", "learn(ed)[^.,]* .*on.?the.?job"),
(    "on the job training", "acquire .*on.?the.?job"),
(    "on the job training", "training [a-z ,]* on.?the.?job"),
(    "associate", "associate degree"),
(    "technical_school", "(through|^) (vocational.*technical|technical) school"),
(    "technical_school", "2-year (vocational.*technical|technical) school"),
(    "reading_skills", "reading skills"),
(    "informal_training", "informal training"),
    # Some employers offer formal apprenticeships.
(    "apprenticeship", "apprenticeship"),
    # Other States may require licenses in the future.
(    "license", "may require licenses"),
(    "license", "(must|require) license"),
(    "license", "(must|require) licensure")
]

OCCUPATION_RE = re.compile("<h1><!-- OOH Title -->(.+)<!-- /OOH Title --></h1>")

education_res_tmp = []
for i, (label, re_string) in enumerate(education_res):
    education_res_tmp.append((i, label, re.compile(re_string)))
education_res = education_res_tmp

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

class Occupation:
    def __init__(self):
        self._name = ""
        self._description = ""
        self._prerequisites = []
        #parser = expat.Parser()
        #self._parser = parser

    def __str__(self):
        s = self._name + "\n"
        for p in self._prerequisites:
            s += "  %s\n" % p
        return s

    def Parse(self, text):
        m = OCCUPATION_RE.search(text)
        if not m:
            print "no occupation match.  skipping."
            return

        self._name = m.group(1)

        for i, prerequisite, p_re in education_res:
            #print i
            #print prerequisite
            m = p_re.search(text, re.IGNORECASE)
            if m:
                label = ""
                if len(m.groups()):
                    label = m.group(1)
                self._prerequisites.append(Prerequisite(prerequisite, label, None, None))

def DownloadOccupations():
    for code in range(1, 359):
        filename = "download/%03d.html" % code
        url = "http://www.bls.gov/oco/ocos%03d.htm" % code
        filename, header = urllib.urlretrieve(url, filename)
        print filename

def ParseOccupations(occupations):
    filenames = open(OCOS_LIST_FILENAME, "r")
    for filename in filenames:
        filename = filename.strip()
        f = open(filename, "r")
        occupation = Occupation()
        text = f.read()
        occupation.Parse(text)
        basename = filename.split("/")[-1]
        basename = basename.split(".")[0]
        occupation._ooh_code = basename
        occupations.append(occupation)
        print occupation
        f.close()
    filenames.close()

def WriteOccupations(occupations):
    pass

ROLE_DESCRIPTIONS_FILENAME = "role_descriptions.txt"
def WriteOccupationNames(occupations):
    f = open(ROLE_DESCRIPTIONS_FILENAME, "w")
#    print occupations
    for occupation in occupations:
#        print occupation

        name = occupation._name
        name_parts = [ name ]
        #name_parts = name.split(" and ")
        if "&mdash;" in name:
            parts = name.split("&mdash;")
            name_parts = [ "%s %s" % (y, parts[0]) for y in parts[1:] ]

        for name in name_parts:
            name = name.lower()
            name = name.rstrip("s")
            print >>f, "%s,%s" % (name, occupation._ooh_code)

    f.close()

if __name__ == "__main__":
    #    DownloadOccupations()

    occupations = []
    ParseOccupations(occupations)

    WriteOccupations(occupations)

    WriteOccupationNames(occupations)
