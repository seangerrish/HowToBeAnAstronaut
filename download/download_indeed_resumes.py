#!/usr/bin/python

import math
import os
import re
import sys
import threading
import traceback
import urllib2

RESUME_RE = re.compile(r'<ol id="results" class="resultsList"><li id="[^"]+" class="sre" itemscope itemtype="http://schema\.org/Person"><div class="sre-entry"><div class="app_name"><a target="_blank" href="([^"]+)"')

t = open("/tmp/i.html").read()

#sys.exit(1)
"""
def DownloadThread(threading.Thread):
    def __init__(self, id):
        self.id = id
        threading.Thread(id)

    def run(self)
"""

def ReadConcentrations():
    concentrations = {}
    f = open("data/v1.1/role_descriptions.txt", "r")
    for row in f:
        row = row.strip()
        if row[0] == "#":
            continue

        parts = row.split(",")
        role = parts[0].strip()
        if len(role) == 0:
            continue

        concentrations[role] = parts[1]

    f.close()
    return concentrations

locations = [ "New York City, NY",
              "Detroit, MI",
              "Saginaw, MI",
              "San Francisco, CA",
              "Austin, TX",
              "Portland, OR",
              "Watertown, SD",
              "Juneau, AK",
              "Hartford, CT",
              "Boston, MA",
              "Albany, NY",
              "Augusta, ME",
              "Honolulu, HI",
              "Kansas City, MO",
              "Orlando, FL",
              "West Palm Beach, FL",
              "Baton Rouge, LA",
              "New Orleans, LA",
              "Jackson, MS",
              "Seattle, WA",
              "San Diego, CA",
              "Hollywood, CA",
              "Chicago, IL",
              "Charleston, NC",
              "Hilton Head, SC",
              "Columbia, SC",
              "Princeton, NJ",
              "Lexington, KY",
              "Nashville, TN",
              "Denver, CO",
              "Houston, TX",
              "Indianapolis, IN",
              "New Ulm, MN",
              "Las Vegas, NV",
              "Tucson, AZ",
              "Boise, ID",
              "Baltimore, MD",
              "Toledo, OH",
              "Philadelphia, PA",
              "Trenton, NJ",
              "Gary, IN",
              "Milwaukee, WI",
              "Dallas, TX",
              ]

def Escaped(s):
    s = s.replace(" ", "+")
    s = s.replace(",", "%2C")
    return s

def DownloadExampleConcentrations(roles):
    seen = {}
    i = 0
    for role, role_id in roles.items():
        for location in locations:
          try:
            i += 1
            seen_id = int(math.log(i + 1) / math.log(1.1))
            if seen_id not in seen:
                print "processing %d." % i

            seen[seen_id] = True

            escaped_role = Escaped(role)
            query = "http://www.indeed.com/resumes?q=%s&l=%s" % (
                escaped_role, Escaped(location))

            q_f = ""
            try:
                q_f = urllib2.urlopen(query).read()
            except:
                q_f = ""

            m = RESUME_RE.search(q_f)
            resume_url = None
            if m:
                resume_url = "http://www.indeed.com%s" % m.group(1)
            else:
                print "no match for query: " + query
                continue
            
            print "downloading " + resume_url
            resume_text = urllib2.urlopen(resume_url).read()
            query = query

            escaped_role = escaped_role.replace("+", "_")
            out_directory = os.path.join("download/indeed", role_id)
            if not os.path.exists(out_directory):
                os.makedirs(out_directory)

            out_filename = os.path.join(out_directory,
                                        resume_url.split("/")[-1])
            out_file = open(out_filename, "w")
            print >>out_file, resume_text
            out_file.close()

          except:
              traceback.print_exc()
              continue
    #result = urllib2.geturl(query)


if __name__ == '__main__':
    concentrations = ReadConcentrations()
    DownloadExampleConcentrations(concentrations)
