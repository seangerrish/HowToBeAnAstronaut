#!/usr/bin/python

import re

a2z_re = re.compile('<a href="[^>]+">([^<]+)</a>')
lmc = re.compile('<a href="http://mymajors.com/[^"]+">([^<]+)</a></li>')
mj = re.compile('<a href=\'http://www.washington.edu/students/gencat/academic/[^\']+\'>([^<]+)</a>')
ch = re.compile('<a href="mh/[^\"]+\" class="featlinku">([^<]+)</a>')
ugs_re = re.compile('<P><A HREF="[^>]+">([^<]+)</A>')
princeton_re = re.compile('<td><a href="[^>]+">([^<]+)</a>')
umich_re = re.compile('<td class="major"><a href="[^>]+">([^<]+)</a>')
duke_re = re.compile('<li><a href="[^>]+">([^<]+)</a>')
gv_re = re.compile('<td> <a href="acad-view.htm[^>]+">([^-<\(]+)[^<]*</a>')
ucla_re = re.compile('<p> ?(<strong>|<a href="[^>]+">)([^-<\(]+)[^<]*(</a>|</strong>)')

def ParseCH(majors):
    f = open("CareerHandouts.shtml", "r")
    doc_text = f.read()

    m = ch.search(doc_text)
    while m:
        major = m.group(1).lower()
        major = major.replace("&amp;", "and")
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = ch.search(doc_text)
    
    f.close()

def ParseMJ(majors):
    f = open("majoff.php", "r")
    doc_text = f.read()

    m = mj.search(doc_text)
    while m:
        major = m.group(1).lower()
        major = major.replace("&amp;", "and")
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = mj.search(doc_text)
    
    f.close()

def ParseLMC(majors):
    f = open("list-of-majors-in-college.cfml", "r")
    doc_text = f.read()

    m = lmc.search(doc_text)
    while m:
        major = m.group(1).lower()
        major = major.replace("&amp;", "and")
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = lmc.search(doc_text)
    
    f.close()

def ParseA2Z(majors):
    f = open("a2z.html", "r")
    doc_text = f.read()

    m = a2z_re.search(doc_text)
    while m:
        major = m.group(1).lower()
        major = major.replace("&amp;", "and")
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = a2z_re.search(doc_text)
    
    f.close()

def Canonicalize(m):
    m = m.lower()
    m = m.strip()
    m = m.replace("&amp;", "and")
    return m

def ParseUGS(majors):
    f = open("degcprl.htm", "r")
    doc_text = f.read()

    m = ugs_re.search(doc_text)
    while m:
        major = Canonicalize(m.group(1))
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = ugs_re.search(doc_text)
    f.close()

def ParsePrinceton(majors):
    f = open("princeton.html", "r")
    doc_text = f.read()

    m = princeton_re.search(doc_text)
    while m:
        major = Canonicalize(m.group(1))
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = princeton_re.search(doc_text)
    f.close()

def ParseUmich(majors):
    f = open("umich.html", "r")
    doc_text = f.read()

    m = umich_re.search(doc_text)
    while m:
        major = Canonicalize(m.group(1))
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = umich_re.search(doc_text)
    f.close()

def ParseDuke(majors):
    f = open("duke.html", "r")
    doc_text = f.read()

    m = duke_re.search(doc_text)
    while m:
        major = Canonicalize(m.group(1))
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = duke_re.search(doc_text)
    f.close()

def ParseGV(majors):
    f = open("grand_valley.html", "r")
    doc_text = f.read()

    m = gv_re.search(doc_text)
    while m:
        major = Canonicalize(m.group(1))
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]

        m = gv_re.search(doc_text)
    f.close()

def ParseUCLA(majors):
    f = open("ucla.html", "r")
    doc_text = f.read()

    m = ucla_re.search(doc_text)
    while m:
        major = Canonicalize(m.group(2))
        major_len = len(major)
        major = major.replace("  ", " ")
        while len(major) < major_len:
            major_len = len(major)
            major = major.replace("  ", " ")
            major = major.replace("\t", " ")
        if major == "individual field of concentration":
            doc_text = doc_text[m.end():]
            m = ucla_re.search(doc_text)
            continue
        if major not in majors:
            majors[major] = 0
        majors[major] += 1
        doc_text = doc_text[m.end():]
        m = ucla_re.search(doc_text)

    f.close()

def AddMajors(majors, all_majors):
    for major in majors:
        if major not in all_majors:
            all_majors[major] = 0

        all_majors[major] += 1

    majors.clear()


if __name__ == '__main__':
    majors = {}
    all_majors = {}
    
    ParseMJ(majors)
    AddMajors(majors, all_majors)
    ParseA2Z(majors)
    AddMajors(majors, all_majors)
    ParseLMC(majors)
    AddMajors(majors, all_majors)
    ParseCH(majors)
    AddMajors(majors, all_majors)
    ParseUGS(majors)
    AddMajors(majors, all_majors)
    ParsePrinceton(majors)
    AddMajors(majors, all_majors)
    ParseUmich(majors)
    AddMajors(majors, all_majors)
    ParseDuke(majors)
    AddMajors(majors, all_majors)
    ParseGV(majors)
    AddMajors(majors, all_majors)
    ParseUCLA(majors)
    AddMajors(majors, all_majors)

    c = 0
    for i, (major, count) in enumerate(all_majors.items()):
        if count > 1:
            c += 1
            print "%s,%d,%d/9," % (major, c, count)
