#!/usr/bin/python

import pickle

from server.server import (
    MAJORS_BY_ID,
    ROLES_BY_ID,
    RoleToPretty)

from models.v1_1.model_constants import (
    OVERALL_STATS_FILE,
    SUGGESTION_JAVASCRIPT)

def GenerateSuggestionList():
    print "Loading stats file"
    f = open(OVERALL_STATS_FILE, "r")
    roles = pickle.load(f).keys()
    f.close()

    items_map = {}
    for role_id in roles:
        pretty = RoleToPretty(role_id)
        
        if "job:" in role_id:
            if len(role_id.split(":")) != 2:
                continue
            key = "Jobs"
            if key not in items_map:
                items_map[key] = []
            items_map[key].append((pretty, role_id, key))
            continue
        
        assert "degree:" in role_id, "role id does not contain degree or job: " + role_id
        parts = role_id.split(":")
        if len(parts) != 3:
            continue
    
        key = None
        if parts[1] in [ "phd", "jd", "md", "ms", "ma", "mba" ]:
            key = "Graduate Degrees"
        elif parts[1] in [ "bs", "ba", "aa", "as", "bfa", "a" ]:
            key = "Undergraduate Degrees"
        else: #  parts[1] in [ "courses", "certificate", "diploma" ]: ???
            key = "Courses, Trade School, and Certifications"
        if key not in items_map:
            items_map[key] = []
        items_map[key].append((pretty, role_id, key))

    items = []
    for key in [ "Jobs",
                 "Undergraduate Degrees",
                 "Graduate Degrees",
                 "Courses, Trade School, and Certifications",
                ]:
        for v in items_map[key]:
            items.append(v)
        
    return items

def Save(l):
    out = open(SUGGESTION_JAVASCRIPT, "w")
    print >>out, """$(function() {
var data = ["""
    for i, (label, key, category) in enumerate(l):
        if i:
            print >>out, ","

        print >>out, '  { label: "%s", key: "%s", category: "%s" }' % (label, key, category),

    print >>out, """  ];

  $( "#request-box" ).catcomplete({
    delay: 0,
    source: data
    minLength: 2,
    autoFocus: true,
  });
});"""
    

    out.close()

    
if __name__ == '__main__':
    l = GenerateSuggestionList()
    Save(l)
