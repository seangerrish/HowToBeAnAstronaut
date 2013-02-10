#!/usr/bin/python

import re

a2z_re = re.compile('<a href="[^>]+">([^<]+)</a>')
lmc = re.compile('<a href="http://mymajors.com/[^"]+">([^<]+)</a></li>')
mj = re.compile('<a href=\'http://www.washington.edu/students/gencat/academic/[^\']+\'>([^<]+)</a>')
ch = re.compile('<a href="mh/[^\"]+\" class="featlinku">([^<]+)</a>')

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

if __name__ == '__main__':
    majors = {}
    ParseMJ(majors)
    ParseA2Z(majors)
    ParseLMC(majors)
    ParseCH(majors)

    for major, count in majors.items():
        if count > 1:
            print major
