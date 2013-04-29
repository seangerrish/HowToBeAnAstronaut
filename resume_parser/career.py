#!/usr/bin/python

import re

class Degree:
    def __init__(self):
        self.degree = None
        self.concentration = None # Handle multiple concentrations?
        self.institution = None
        self.year = None

    def SetSchool(self, institution):
        self.institution = institution

    def SetConcentration(self, degree, concentration):
        self.degree = degree
        self.concentration = concentration

    def Sufficient(self):
        return self.concentration is not None and self.institution is not None

    def __str__(self):
        as_string = "%s,%s,%s,%s" % (
            self.year,
            self.degree,
            self.concentration,
            self.institution)
        return as_string

class Work:
    def __init__(self):
        self.work_title = None
        self.work_company = None

        self.work_date = None
        self.start_date = None
        self.end_date = None
        self.location = None

        self.WORK_RE = re.compile(r"(.+),(.+),(.+),(.+),(.+)")

    def __str__(self):
        end_date_str = "None"
        start_date_str = "None"
        if self.start_date is not None:
            start_date_str = self.start_date.strftime("%Y-%m-%d")

        if self.end_date is not None:
            end_date_str = self.end_date.strftime("%Y-%m-%d")
        result = "%s,%s,%s,%s,%s" % (
            start_date_str,
            end_date_str,
            self.work_title,
            self.work_company,
            self.location)
        return result

    def Parse(self, s):
        m = self.WORK_RE.match(s)
        if not m:
            return False

        print m.groups()
        self.start_date = datetime.strptime(m.group(0), "%Y-%m-%d")
        self.end_date = len(m.group(1)) and m.group(1) or None
        self.work_title = m.group(2)
        self.work_company = m.group(3)

class Career:
    def __init__(self):
        # A list of Degrees.
        self.education = []
        self.jobs = []

    def __str__(self):
        return ""
