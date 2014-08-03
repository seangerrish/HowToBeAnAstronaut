#!/usr/bin/python

from models.v1_1.model_constants import (
    SERVING_END_ROLES,
    SERVING_START_ROLES,
    SERVING_METADATA)

def LoadIndex():
    return {}

MAJORS_BY_KEYWORD = {}
MAJORS_BY_ID = {}
f = open("education/majors.txt", "r")
for row in f:
    parts = row.split(",")
    if len(parts) < 2:
        continue

    keyword = parts[0].lower()
    id = str(int(parts[1]))
    MAJORS_BY_KEYWORD[keyword] = id
    MAJORS_BY_ID[id] = keyword

    if len(parts) >= 4:
        other_keywords = parts[3].split(";")
    for keyword in other_keywords:
        MAJORS_BY_KEYWORD[keyword.lower()] = id

f.close()

DEGREES = {}
f = open("education/degrees.txt", "r")
for row in f:
    parts = row.split(",")

    keyword = parts[0].lower()
    DEGREES[keyword] = True

f.close()

ROLES_BY_ID = {}
ROLES_BY_KEYWORD = {}
f = open("data/v1.1/role_descriptions.txt", "r")
for row in f:
    if (row.strip() + " ")[0] == "#":
        continue
    parts = row.strip().split(",")
    if len(parts) != 2:
        continue

    keyword, id = parts
    id = str(int(id))
    ROLES_BY_KEYWORD[keyword.lower().strip()] = id

    if id not in ROLES_BY_ID:
        ROLES_BY_ID[id] = keyword

f.close()

def PrettifyJob(s):
    result = []
    for term in s.split(" "):
        if term in [ "the", "a", "and", "for", "with", "of", "or" ]:
            result.append(term)
        else:
            print "capitalizing: " + term
            result.append(term.capitalize())

    print " ".join(result)
    return " ".join(result)

def JobToRoleId(s):
    if s in ROLES_BY_KEYWORD:
        return "job:%d" % ROLES_BY_KEYWORD[s]

    return None

def RoleToPretty(role_id):
    if role_id[:4] == "job:":
        parts = role_id.split(":")
        id = parts[1]
        id = str(int(id))

        return PrettifyJob(ROLES_BY_ID.get(id, ""))
        
    if role_id[:7] == "degree:":
        degree_pretty = ""
        major_pretty = ""
        parts = role_id.split(":")
        _, degree, major = parts[:3]
        degree = degree.lower()
        if len(degree) == 0:
            return ""

        if degree == "phd":
            degree = "PhD"
        elif degree == "jd":
            degree = "JD"
            major = ""
        elif degree == "bs":
            degree = "BS"
        elif degree == "a":
            degree = "Associates"
        elif degree == "ba":
            degree = "BA"
        elif degree == "mse":
            degree = "MSE"
        elif degree == "ms":
            degree = "MS"
        elif degree == "ma":
            degree = "MA"
        elif degree == "mfa":
            degree = "MFA"
        elif degree == "hs":
            degree = "High School"
            major = ""
        elif degree == "md":
            degree = "MD"
            major = ""
        elif degree == "aa":
            degree = "Associates of Arts"
        elif degree == "as":
            degree = "Associates of Science"
        else:
            degree = degree.capitalize()

        major_str = MAJORS_BY_ID.get(major, "")
        major = PrettifyJob(major_str)

        if len(major) == 0:
            return degree

        return "%s in %s" % (degree, major)

