#!/usr/bin/python
#
# Handles parsing for resumes around April 29, 2013.

import career
import re
import datetime
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

class IndeedHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        # For parsing:
        self.in_education = False
        self.in_degree = False
        self.in_school = False
        self.in_work_date = False
        self.in_work_section = False
        self.in_work_title = False
        self.in_work_company = False
        self.in_work_location = False

        self.elements = []

        self.pending_degree = None

        self.education = []
        self.jobs = []

    # 3 handler functions
    def handle_starttag(self, name, attrs_list):
        attrs = dict(attrs_list)

        if name != "div" and name != "p" and name != "span":
            return
        if attrs.get("class", "")[:18] == "education-section ":
            self.in_education = True
            self.pending_degree = career.Degree()
        if name == "p" and attrs.get("class", "") == "edu_title":
            self.in_degree = True
        if attrs.get("class", "") == "education":
            print "found education."
            self.in_school = True
        if attrs.get("class", "") == "experience":
            print "experience found."
            self.in_work_section = True
            self.pending_job = career.Work()
        if attrs.get("class", "") == "work_dates":
            self.in_work_date = True
        if attrs.get("class", "") == "work_title title":
            self.in_work_title = True
        if attrs.get("class", "") == "company":
            print "in company."
            self.in_work_company = True
        #if attrs.get("class", "") == "adr":
        #    self.in_work_location = True

        self.elements.append((name, attrs))

    def handle_endtag(self, name):
        if name != "div" and name != "p" and name != "span":
            return
        name, attrs = self.elements.pop()
        if self.in_education and attrs.get("class", "")[:18] == "education-section ":
            self.education.append(self.pending_degree)
            self.pending_degree = None

            self.in_education = False
        if name == "p" and attrs.get("class", "") == "edu_title":
            self.in_degree = False
            if self.pending_degree and self.pending_degree.Sufficient():
                self.education.append(self.pending_degree)
                self.pending_degree = None

        if attrs.get("class", "") == "edu_school":
            self.in_school = False

        if attrs.get("class", "")[:24] == "work-experience-section ":
            self.in_work_section = False
            self.jobs.append(self.pending_job)
        if attrs.get("class", "") == "work_dates":
            self.in_work_date = False
        if attrs.get("class", "") == "work_title title":
            self.in_work_title = False
        if attrs.get("class", "") == "work_company" or attrs.get("class", "") == "company":
            print "in c"
            self.in_work_company = False

        #if attrs.get("class", "") == "adr":
        #    self.in_work_location = False

        if name != "div" and name != "p":
            return

        self.last = name

    def ParseConcentration(self, indeed_concentration):
        indeed_concentration = indeed_concentration.lower()
        parts = indeed_concentration.split(" in ")
        if len(parts) == 3:
            if " in ".join((parts[0], parts[1])) in DEGREES:
                parts = (parts[0] + " in " + parts[1], " in ".join(parts[2:]))
            else:
                parts = (parts[0], " in ".join(parts[1:]))

        if len(parts) == 1:
            parts = indeed_concentration.split(" of ")
            if len(parts) == 3:
                parts = (parts[0], " of ".join(parts[1:]))

        if len(parts) == 1:
            return "degree", indeed_concentration
            
        degree, concentration = None, None
        if len(parts) == 2:
            nym, concentration = parts
            degree = DEGREES.get(nym, "None")
            if degree == "None":
                for word in nym.split(" "):
                    if word in DEGREES:
                        degree = DEGREES[word]
                        break

                degree = "courses"
                    
            else:
                pass
        else:
            print "Could not find degree for nym: " + indeed_concentration
            concentration = indeed_concentration

        return degree, concentration

    def ParseDates(self, date_string):
        def ParseDate(date_str):
            m = DATE_RE.search(date_str)
            if m:
                month_str = m.group(1) or "January"
                year = int(m.group(2))
                month = MONTHS.get(month_str.strip())
                day = 1
                return datetime.datetime(year, month + 1, day)
            else:
                return None

        dates = date_string.split(" to ")
        first_str = dates[0]
        first = ParseDate(first_str)
        second = None
        if len(dates) == 2:
            second_str = dates[1]
            second = ParseDate(second_str)

        return first, second
    
    def handle_data(self, data):
        if not len(self.elements):
            return
        
        tag, c = self.elements[-1]
        if self.in_education and self.in_degree:
            if self.pending_degree is None:
                self.pending_degree = career.Degree()

            degree, concentration = self.ParseConcentration(data)

            self.pending_degree.SetConcentration(degree, concentration)
            
        if self.in_education and self.in_school:
            # tag == "div" and c == "edu_school":
            if self.pending_degree is None:
                self.pending_degree = career.Degree()
            if self.pending_degree.institution is None:
                data = data.strip()
                data = data.strip("-")
                data = data.strip(" ")
                self.pending_degree.SetSchool(data)
            else:
                self.pending_degree.institution += " (%s)" % data

        if self.in_work_date:
            self.pending_job.work_date = data
            dates = self.ParseDates(data)
            self.pending_job.start_date = dates[0]
            self.pending_job.end_date = dates[1]
            
        if self.in_work_title:
            self.pending_job.work_title = data

        if self.in_work_location:
            self.pending_job.location = data

        if self.in_work_company:
            self.pending_job.work_company = data

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
