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
assetID = ""
releaseNotesRequired = False

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
        assetID = evaluateDefectFields(asset)
        evaluateAllDefectVXTFields(assetID)

    elif asset[0] == 'S':
        # Check Story format
        if re.match("/S-\d\d\d\d\d/g",asset):
            print("Invalid Story Number")
            exit()
        assetID = evaluateStoryFields(asset)
        evaluateAllStoryVXTFields(assetID)

    else:
        print("Invalid story/defect number")



    evaluateTasks(taskList)
    evaluateAcceptanceCriteria(acceptanceCriteriaList)

    # Final output
    if len(empty_fields) == 0:
        print("All fields complete for " + asset + "!")
    else:
        print("Missing fields for "+ asset + ": ")
        for problem in empty_fields:
            print(problem)

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

    if not releaseNotesRequired:
        print()
        print("Reminder: Release Notes Required field should be updated and confirmed by PO")

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

        if len(owner) == 0:
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

        if len(owner) == 0:
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
    storyID = resp.json()["Assets"][0]["id"].split(":", 1)[1]
    data = resp.json()["Assets"][0]["Attributes"]

    '''
    There are more possible fields, just his is my attempt to map the
    JSON data name to what the field name is, I also didn't know what is
    actually needed for paperwork
    '''
    # Map asset values
    planning_level = data["Scope.Name"]["value"]
    sprint = data["Timebox.Name"]["value"]
    status =  data["Status.Name"]["value"]
    estimate_sp =  data["Estimate"]["value"]
    solution =  data["Parent.Name"]["value"]
    owners = data["Owners.Name"]["value"]
    team = data["Team"]["value"]
    theme_investment =  data["Source.Name"]["value"]         #TODO: Check this

    # Check for empty fields in asset
    if planning_level == None:
        empty_fields.append("Planning Level")
    if sprint == None:
        empty_fields.append("Sprint")
    if estimate_sp == None:
        empty_fields.append("Estimate Story Points")
    if solution == None:
        empty_fields.append("Solution")
    if len(owners) == 0:
        empty_fields.append("Owners")
    if team == None:
        empty_fields.append("Team")
    if theme_investment == None:
        empty_fields.append("Theme Investment")
    if status != "Done":
        empty_fields.append("Status")


    return storyID


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
    defectID = resp.json()["Assets"][0]["id"].split(":", 1)[1]
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
    # lean_budget =  data["Priority.Name"]["value"]

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
    # if lean_budget == None:
    #     empty_fields.append("Lean Budget")

    return defectID

def evaluateAllStoryVXTFields(storyID):
        vxtURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Story/"

    #--------------- Code Impact (Vxt)
        resp = requests.get(vxtURL + storyID + "/Custom_CodeImpactVxT2", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Code Impact (VxT)")

    #--------------- Complexity (Vxt)
        resp = requests.get(vxtURL + storyID + "/Custom_ComplexityVxT2", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Complexity (VxT)")

    #--------------- Size of Change (Vxt)
        resp = requests.get(vxtURL + storyID + "/Custom_SizeofChangeVxT2", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Size of Change (VxT)")

    #--------------- Commit Version
        resp = requests.get(vxtURL + storyID + "/Custom_CommitVersion", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Commit Version")

    #--------------- Release Notes Required    TODO: Check that this does what it needs, could be both true or false
        resp = requests.get(vxtURL + storyID + "/Custom_ReleaseNoteRequired", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        global releaseNotesRequired
        releaseNotesRequired = resp.json()["value"]

    #--------------- Business Enabler
        resp = requests.get(vxtURL + storyID + "/Custom_BusinessEnabler", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Business Enabler")

    #--------------- Installation Change
        resp = requests.get(vxtURL + storyID + "/Custom_InstallationChange4", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Installation Change")

def evaluateAllDefectVXTFields(defectID):
        vxtURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Defect/"
        #TODO: Can't find Summary, and didn't implement description
        # Also couldn't find Validation tags (vtest, vexe, ...)
        # Also Planning Item
        # Also figure out how to handle release notes

    #--------------- Component
        resp = requests.get(vxtURL + defectID + "/Custom_Component", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Component")

    #--------------- Found in Version
        resp = requests.get(vxtURL + defectID + "/Custom_FoundinVersion", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Found in Version")

    #--------------- Priority Group
        resp = requests.get(vxtURL + defectID + "/Custom_PriorityGroup2", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Priority Group")

    #--------------- Commit Version
        resp = requests.get(vxtURL + defectID + "/Custom_CommitVersion", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Commit Version")

    #--------------- Root Cause
        resp = requests.get(vxtURL + defectID + "/Custom_RootCause", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Root Cause")

    #--------------- Release Notes Required
        resp = requests.get(vxtURL + defectID + "/Custom_ReleaseNoteRequired", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        global releaseNotesRequired
        releaseNotesRequired = resp.json()["value"]


    #--------------- Installation Change
        resp = requests.get(vxtURL + defectID + "/Custom_InstallationChange5", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Installation Change")

    #--------------- Business Enabler
        resp = requests.get(vxtURL + defectID + "/Custom_BusinessEnabler", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Business Enabler")

    #--------------- Code Impact (Vxt)
        resp = requests.get(vxtURL + defectID + "/Custom_CodeImpactVxT2", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Code Impact (VxT)")

    #--------------- Complexity (Vxt)
        resp = requests.get(vxtURL + defectID + "/Custom_ComplexityVxT2", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Complexity (VxT)")

    #--------------- Size of Change (Vxt)
        resp = requests.get(vxtURL + defectID + "/Custom_SizeofChangeVxT2", headers=headers)
        if resp.status_code != 200:
            # This means something went wrong.
            print("API_ERROR: Something went wrong")
            print(resp.status_code)
            print(resp.json())
            exit()

        if(resp.json()["value"] == None):
            empty_fields.append("Size of Change (VxT)")


if __name__ == "__main__":
    main(sys.argv)
