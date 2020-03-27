#!/usr/bin/python

import sys
import requests
import re

'''
This current paperwork parser takes a single story/defect number and checks version 1 for
whether or not the paperwork fields are empty. This could be altered to check every asset
in a sprint to see if any need to have more completed paperwork, or some other use, this
is intended to be just base code
'''

# Check parameters
if len(sys.argv) != 2:
    print("usage: <Story/Defect>")
    exit()

asset = sys.argv[1]
# Headers contain my authToken for V1 api
headers = {'Authorization': 'Bearer 1.u3re+B2QHhxi052xeqPhxs39moY=', 'Accept': 'application/json'}
# Simple list that helps us know if there are any empty fields
empty_fields = []

if asset[0] == 'D':
    # Check correct defect format
    if re.match("/D-\d\d\d\d\d/g",asset):
        print("Invalid Defect Number")
        exit()

    defectURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Defect?where=Number="

    resp = requests.get(defectURL + "'" + asset + "'", headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        print("API_ERROR: Something went wrong")
        print(resp.status_code)
        print(resp.json())
        exit()
    data = resp.json()["Assets"][0]["Attributes"]

    '''
    There are more possible fields, just his is my attempt to map the
    JSON data name to what the field name is, I also didn't know what is
    actually needed for paperwork
    '''
    # Map asset values
    planning_level = data["Scope.Name"]["value"]
    sprint = data["Timebox.Name"]["value"]
    tags = data["TaggedWith"]["value"]
    status =  data["Status.Name"]["value"]
    estimate_sp =  data["Estimate"]["value"]
    solution =  data["Parent.Name"]["value"]
    owners = data["Owners.Name"]["value"]
    commit_version = data["FixedInBuild"]["value"]
    type = data["Type.Name"]["value"]
    resolution = data["ResolutionReason.Name"]["value"]
    lean_budget =  data["Priority.Name"]["value"]

    # Check for empty fields in asset
    if planning_level == None:
        empty_fields.append("Planning Level")
    if sprint == None:
        empty_fields.append("Sprint")
    if len(tags) == 0:
        empty_fields.append("Tags")
    if estimate_sp == None:
        empty_fields.append("Estimate Story Points")
    if solution == None:
        empty_fields.append("Solution")
    if len(owners) == 0:
        empty_fields.append("Owners")
    if commit_version == None:
        empty_fields.append("Commit Version")
    if type == None:
        empty_fields.append("Type")
    if resolution == None:
        empty_fields.append("Resolution")
    if lean_budget == None:
        empty_fields.append("Lean Budget")


elif asset[0] == 'S':
    # Check Story format
    if re.match("/S-\d\d\d\d\d/g",asset):
        print("Invalid Story Number")
        exit()

    storyURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Story?where=Number="

    resp = requests.get(storyURL + "'" + asset + "'", headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        print("API_ERROR: Something went wrong")
        print(resp.status_code)
        print(resp.json())
        exit()
    data = resp.json()["Assets"][0]["Attributes"]

    '''
    There are more possible fields, just his is my attempt to map the
    JSON data name to what the field name is, I also didn't know what is
    actually needed for paperwork
    '''
    # Map asset values
    planning_level = data["Scope.Name"]["value"]
    sprint = data["Timebox.Name"]["value"]
    tags = data["TaggedWith"]["value"]
    status =  data["Status.Name"]["value"]
    estimate_sp =  data["Estimate"]["value"]
    solution =  data["Parent.Name"]["value"]
    owners = data["Owners.Name"]["value"]

    # Check for empty fields in asset
    if planning_level == None:
        empty_fields.append("Planning Level")
    if sprint == None:
        empty_fields.append("Sprint")
    if len(tags) == 0:
        empty_fields.append("Tags")     #This might be optional, but just in case
    if estimate_sp == None:
        empty_fields.append("Estimate Story Points")
    if solution == None:
        empty_fields.append("Solution")
    if len(owners) == 0:
        empty_fields.append("Owners")

else:
    print("Invalid story/defect number")

# Final output
if len(empty_fields) == 0:
    print("All paperwork complete for " + asset + "!")
    exit()
else:
    print("Missing fields for "+ asset + ": ")
    for asset in empty_fields:
        print(asset)
    exit()
