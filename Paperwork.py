#!/usr/bin/python

import sys
import requests
import re


print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

if len(sys.argv) != 2:
    print("usage: <Story/Defect>")
    exit()

asset = sys.argv[1]
headers = {'Authorization': 'Bearer 1.u3re+B2QHhxi052xeqPhxs39moY=', 'Accept': 'application/json'}

if asset[0] == 'D':
    print("Defect stated")
    # defectRegex = re.compile('/D-\d\d\d\d\d/g')
    if re.match("/D-\d\d\d\d\d/g",asset):
        print("Invalid Defect Number")
        exit()

    defectURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Defect?where=Number="

    resp = requests.get(defectURL + "'" + asset + "'", headers=headers)
    print(headers)
    if resp.status_code != 200:
        print(resp.status_code)
        print(resp.json())
        # This means something went wrong.
        raise ApiError('GET /tasks/ {}'.format(resp.status_code))
    data = resp.json()["Assets"][0]["Attributes"]
    print(data)

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


elif asset[0] == 'S':
    print("Story stated")

    if re.match("/S-\d\d\d\d\d/g",asset):
        print("Invalid Defect Number")
        exit()

    storyURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Story?where=Number="

    resp = requests.get(storyURL + "'" + asset + "'", headers=headers)
    print(headers)
    if resp.status_code != 200:
        print(resp.status_code)
        print(resp.json())
        # This means something went wrong.
        raise ApiError('GET /tasks/ {}'.format(resp.status_code))
    data = resp.json()["Assets"][0]["Attributes"]
    print(data)

    planning_level = data["Scope.Name"]["value"]
    sprint = data["Timebox.Name"]["value"]
    tags = data["TaggedWith"]["value"]
    status =  data["Status.Name"]["value"]
    estimate_sp =  data["Estimate"]["value"]
    solution =  data["Parent.Name"]["value"]
    owners = data["Owners.Name"]["value"]
    # commit_version = data["FixedInBuild"]["value"]
    # type = data["Type.Name"]["value"]
    # resolution = data["ResolutionReason.Name"]["value"]
    # lean_budget =  data["Priority.Name"]["value"]

else:
    print("Invalid story/defect number")
