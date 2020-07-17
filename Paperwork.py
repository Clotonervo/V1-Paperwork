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

# Headers contain my authToken for V1 api
headers = {'Authorization': 'Bearer 1.u3re+B2QHhxi052xeqPhxs39moY=', 'Accept': 'application/json'}
# Simple list that helps us know if there are any empty fields
empty_fields = []
task_problems = []
acceptance_problems = []

def main(argv):
    if len(argv) != 2:
        print("usage: <Story/Defect>")
        exit()

    # Check parameters
    asset = sys.argv[1]

    taskList = findAllTasks(asset)
    acceptanceCriteriaList = findAllAcceptanceCriteria(asset)

    if asset[0] == 'D':
        # Check correct defect format
        if re.match("/D-\d\d\d\d\d/g",asset):
            print("Invalid Defect Number")
            exit()
        evaluateDefectFields(asset)

    elif asset[0] == 'S':
        # Check Story format
        if re.match("/S-\d\d\d\d\d/g",asset):
            print("Invalid Story Number")
            exit()
        evaluateStoryFields(asset)

    else:
        print("Invalid story/defect number")

    evaluateTasks(taskList)
    evaluateAcceptanceCriteria(acceptanceCriteriaList)

    # Final output
    if len(empty_fields) == 0:
        print("All paperwork complete for " + asset + "!")
    else:
        print("Missing fields for "+ asset + ": ")
        for asset in empty_fields:
            print(asset)

    if len(task_problems) == 0:
        print("All tasks complete for " + asset + "!")
    else:
        print()
        print("Tasks Incomplete for " + asset + "!")
        for task in task_problems:
            print(task)

    if len(acceptance_problems) == 0:
        print("All acceptance criteria complete for " + asset + "!")
    else:
        print()
        print("Acceptance criteria Incomplete for " + asset + "!")
        for ac in acceptance_problems:
            print(ac)

    exit()


'''
****************************** Helper functions! ***************************
'''

def evaluateTasks(taskList):
    for task in taskList:
        taskName = task["Attributes"]["Name"]["value"]
        number = task["Attributes"]["Number"]["value"]
        owner = task["Attributes"]["Owners.Name"]["value"]
        status = task["Attributes"]["Status.Name"]["value"]
        sprint = task["Attributes"]["Timebox.Name"]["value"]
        planning_level = task["Attributes"]["Scope.Name"]["value"]
        team_name = task["Attributes"]["Team.Name"]["value"]

        error_values = [];

        if owner == None:
            error_values.append("Owner")
        if status == None or status == "In Progress":
            error_values.append("Status")
        if sprint == None:
            error_values.append("Sprint")
        if planning_level == None:
            error_values.appened("Planning level")
        if team_name == None:
            error_values.append("Team Name")

        if len(error_values) > 0:
            task_problems.append({"Name": taskName + ": " + number, "Values" :error_values})

def evaluateAcceptanceCriteria(acceptanceCriteriaList):
    for acceptance in acceptanceCriteriaList:
        acceptanceName = acceptance["Attributes"]["Name"]["value"]
        number = acceptance["Attributes"]["Number"]["value"]
        owner = acceptance["Attributes"]["Owners.Name"]["value"]
        status = acceptance["Attributes"]["Status.Name"]["value"]
        sprint = acceptance["Attributes"]["Timebox.Name"]["value"]
        planning_level = acceptance["Attributes"]["Scope.Name"]["value"]
        team_name = acceptance["Attributes"]["Team.Name"]["value"]

        error_values = [];

        if owner == None:
            error_values.append("Owner")
        if status == None or status == "Failed":
            error_values.append("Status")
        if sprint == None:
            error_values.append("Sprint")
        if planning_level == None:
            error_values.append("Planning level")
        if team_name == None:
            error_values.append("Team Name")

        if len(error_values) > 0:
            acceptance_problems.append({"Name": acceptanceName + ": " + number, "Values" :error_values})



# For future reference, both Tasks and Acceptance Criteria inherit from 'WorkItem' asset

##
## Here we find all the Tasks for the given Asset
##
def findAllTasks(asset):
    taskURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Task?where=Parent.Number="
    resp = requests.get(taskURL + "'" + asset + "'", headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        print("API_ERROR: Something went wrong")
        print(resp.status_code)
        print(resp.json())
        exit()
    data = resp.json()["Assets"]
    return data

##
## Here we find all the Acceptance Criteria for the given Asset
##
def findAllAcceptanceCriteria(asset):
    taskURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Test?where=Parent.Number="
    resp = requests.get(taskURL + "'" + asset + "'", headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        print("API_ERROR: Something went wrong")
        print(resp.status_code)
        print(resp.json())
        exit()
    data = resp.json()["Assets"]
    return data

##
## Here we find all the values for the given Story and search for incomplete fields
##
def evaluateStoryFields(asset):
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


##
## Here we find all the values for the given Defect and search for incomplete fields
##
def evaluateDefectFields(asset):
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




if __name__ == "__main__":
    main(sys.argv)
