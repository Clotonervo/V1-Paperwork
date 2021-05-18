#!/usr/bin/python

import sys
import requests
import re
from os import environ as env
from dotenv import load_dotenv

'''
This current paperwork parser takes a single story/defect number and checks version 1 for
whether or not the paperwork fields are empty. This could be altered to check every asset
in a sprint to see if any need to have more completed paperwork, or some other use, this
is intended to be just base code
'''
# Environment Variables
load_dotenv()
# Headers contain my authToken for V1 api
headers = {'Authorization': 'Bearer ' + env.get("API_KEY"), 'Accept': 'application/json'}
# Simple list that helps us know if there are any empty fields
empty_fields = []
task_problems = []
acceptance_problems = []
finalOutput = ""

def getPaperwork(asset, type):

    global empty_fields
    global task_problems
    global acceptance_problems
    task_problems = []
    acceptance_problems = []
    empty_fields = []
    taskList = findAllTasks(asset)
    acceptanceCriteriaList = findAllAcceptanceCriteria(asset)
    evaluateTasks(taskList)
    evaluateAcceptanceCriteria(acceptanceCriteriaList)
    global finalOutput
    finalOutput = ''
    print("HERE")

    if type == "Defect":
        assetID = evaluateDefectFields(asset)
        evaluateAllDefectVXTFields(assetID)
    else:
        assetID = evaluateStoryFields(asset)
        evaluateAllStoryVXTFields(assetID)

    # Final output
    if len(empty_fields) == 0:
        finalOutput = finalOutput + "<font color='green'><b>All fields complete for " + asset + "!</b></font> <br/>"
    else:
        finalOutput = finalOutput + "<font color='red'><b>Missing fields for " + asset + ": </b></font> <br/><i>"
        for problem in empty_fields:
            finalOutput = finalOutput + problem + ", "
        finalOutput = finalOutput[:-1][:-1] + "</i></font><br/>"

    if len(task_problems) == 0:
        finalOutput = finalOutput + "<font color='green'><b>All tasks complete for " + asset + "!</b></font> <br/>"
    else:
        # finalOutput = finalOutput + "<br/>"
        finalOutput = finalOutput + "<font color='red'><b>Tasks Incomplete for " + asset + ":</font><ul>"
        for task in task_problems:
            finalOutput = finalOutput + "<li>" + task["Name"] + "<font color='red'>"
            for value in task["Values"]:
                finalOutput = finalOutput + "<i> " + value + ","
            finalOutput = finalOutput[:-1] + "</i></li>"
        finalOutput += "</ul></font>"

    if len(acceptance_problems) == 0:
        finalOutput = finalOutput + "<font color='green'><b>All acceptance criteria complete for " + asset + "!</b></font><br/>"
    else:
        # finalOutput = finalOutput + "<br/>"
        finalOutput = finalOutput + "<font color='red'><b>Acceptance criteria Incomplete for " + asset + ":</font><ul>"
        for ac in acceptance_problems:
            finalOutput = finalOutput + "<li>" + ac["Name"] + "<font color='red'>"
            for value in ac["Values"]:
                finalOutput = finalOutput + "<i> " + value + ","
            finalOutput = finalOutput[:-1] + "</i></li>"
        finalOutput += "</ul></font>"

    returnString = finalOutput
    finalOutput = ""
    return returnString



'''
****************************** Helper functions! ***************************
'''
##
## Here we evaluate all the tasks for the given Asset
##
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

##
## Here we evaluate all the acceptance criteria for the given Asset
##
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
    global finalOutput
    taskURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Task?where=Parent.Number="
    resp = requests.get(taskURL + "'" + asset + "'", headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        finalOutput = finalOutput + "API_ERROR: Something went wrong"
        finalOutput = finalOutput + resp.status_code
        finalOutput = finalOutput + resp.json()
        exit()
    data = resp.json()["Assets"]
    return data

##
## Here we find all the Acceptance Criteria for the given Asset
##
def findAllAcceptanceCriteria(asset):
    global finalOutput
    taskURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Test?where=Parent.Number="
    resp = requests.get(taskURL + "'" + asset + "'", headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        finalOutput = finalOutput + "API_ERROR: Something went wrong"
        finalOutput = finalOutput + resp.status_code
        finalOutput = finalOutput + resp.json()
        exit()
    data = resp.json()["Assets"]
    return data

##
## Here we find all the values for the given Story and search for incomplete fields
##
def evaluateStoryFields(asset):
    global finalOutput
    storyURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Story?where=Number="
    resp = requests.get(storyURL + "'" + asset + "'", headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        finalOutput = finalOutput + "API_ERROR: Something went wrong"
        finalOutput = finalOutput + resp.status_code
        finalOutput = finalOutput + resp.json()
        exit()
    storyID = resp.json()["Assets"][0]["id"].split(":", 1)[1]
    data = resp.json()["Assets"][0]["Attributes"]

    # Map asset values
    planning_level = data["Scope.Name"]["value"]
    sprint = data["Timebox.Name"]["value"]
    # status =  data["Status.Name"]["value"]
    estimate_sp =  data["Estimate"]["value"]
    solution =  data["Parent.Name"]["value"]
    owners = data["Owners.Name"]["value"]
    team = data["Team"]["value"]
    theme_investment =  data["Source.Name"]["value"]

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
    # if status != "Done":
    #     empty_fields.append("Status")


    return storyID


##
## Here we find all the values for the given Defect and search for incomplete fields
##
def evaluateDefectFields(asset):
    global finalOutput
    defectURL = "https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/Defect?where=Number="
    resp = requests.get(defectURL + "'" + asset + "'", headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        finalOutput = finalOutput + "API_ERROR: Something went wrong"
        finalOutput = finalOutput + resp.status_code
        finalOutput = finalOutput + resp.json()
        exit()
    print(resp.json())
    defectID = resp.json()["Assets"][0]["id"].split(":", 1)[1]
    data = resp.json()["Assets"][0]["Attributes"]

    # Map asset values
    planning_level = data["Scope.Name"]["value"]
    sprint = data["Timebox.Name"]["value"]
    tags = data["TaggedWith"]["value"]
    # status =  data["Status.Name"]["value"]
    estimate_sp =  data["Estimate"]["value"]
    solution =  data["Parent.Name"]["value"]
    owners = data["Owners.Name"]["value"]
    commit_version = data["FixedInBuild"]["value"]
    type = data["Type.Name"]["value"]
    resolution = data["ResolutionReason.Name"]["value"]
    theme_investment =  data["Source.Name"]["value"]

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
        empty_fields.append("Resolved in Build")
    if type == None:
        empty_fields.append("Type")
    if resolution == None:
        empty_fields.append("Resolution")
    if theme_investment == None:
        empty_fields.append("Theme Investment")

    return defectID

##
## Here we evaluate all the Vxt fields for the given Story
##
def evaluateAllStoryVXTFields(storyID):
        global finalOutput

    #--------------- Code Impact (Vxt)
        resp = getVtxValue(storyID, "/Custom_CodeImpactVxT2", True)
        if(resp["value"] == None):
            empty_fields.append("Code Impact (VxT)")

    #--------------- Complexity (Vxt)
        resp = getVtxValue(storyID, "/Custom_ComplexityVxT2", True)
        if(resp["value"] == None):
            empty_fields.append("Complexity (VxT)")

    #--------------- Size of Change (Vxt)
        resp = getVtxValue(storyID, "/Custom_SizeofChangeVxT2", True)
        if(resp["value"] == None):
            empty_fields.append("Size of Change (VxT)")

    #--------------- Commit Version
        resp = getVtxValue(storyID, "/Custom_CommitVersion", True)
        if(resp["value"] == None):
            empty_fields.append("Commit Version")

    #--------------- Release Notes Required
        resp = getVtxValue(storyID, "/Custom_ReleaseNotesRequired2", True)
        if(resp["value"] == None):
            empty_fields.append("Release Notes Required")

    #--------------- Business Enabler
        resp = getVtxValue(storyID, "/Custom_BusinessEnabler", True)
        if(resp["value"] == None):
            empty_fields.append("Business Enabler")

    #--------------- Installation Change
        resp = getVtxValue(storyID, "/Custom_InstallationChange4", True)
        if(resp["value"] == None):
            empty_fields.append("Installation Change")


##
## Here we evaluate all the vxt fields for the given Defect
##
def evaluateAllDefectVXTFields(defectID):
        #TODO: Can't find Summary, and didn't implement description
        global finalOutput
    #--------------- Component
        resp = getVtxValue(defectID, "/Custom_Component", False)
        if(resp["value"] == None):
            empty_fields.append("Component")

    #--------------- Found in Version
        resp = getVtxValue(defectID, "/Custom_FoundinVersion", False)
        if(resp["value"] == None):
            empty_fields.append("Found in Version")

    #--------------- Priority Group
        resp = getVtxValue(defectID, "/Custom_PriorityGroup2", False)
        if(resp["value"] == None):
            empty_fields.append("Priority Group")

    #--------------- Commit Version
        resp = getVtxValue(defectID, "/Custom_CommitVersion", False)
        if(resp["value"] == None):
            empty_fields.append("Commit Version")

    #--------------- Root Cause
        resp = getVtxValue(defectID, "/Custom_RootCause", False)
        if(resp["value"] == None):
            empty_fields.append("Root Cause")

    #--------------- Release Notes Required
        resp = getVtxValue(storyID, "/Custom_ReleaseNotesRequired2", True)
        if(resp["value"] == None):
            empty_fields.append("Release Notes Required")

    #--------------- Installation Change
        resp = getVtxValue(defectID, "/Custom_InstallationChange5", False)
        if(resp["value"] == None):
            empty_fields.append("Installation Change")

    #--------------- Business Enabler
        resp = getVtxValue(defectID, "/Custom_BusinessEnabler", False)
        if(resp["value"] == None):
            empty_fields.append("Business Enabler")

    #--------------- Code Impact (Vxt)
        resp = getVtxValue(defectID, "/Custom_CodeImpactVxT2", False)
        if(resp["value"] == None):
            empty_fields.append("Code Impact (VxT)")

    #--------------- Complexity (Vxt)
        resp = getVtxValue(defectID, "/Custom_ComplexityVxT2", False)
        if(resp["value"] == None):
            empty_fields.append("Complexity (VxT)")

    #--------------- Size of Change (Vxt)
        resp = getVtxValue(defectID, "/Custom_SizeofChangeVxT2", False)
        if(resp["value"] == None):
            empty_fields.append("Size of Change (VxT)")


##
## Here we get a vtx value of a specific asset
##
def getVtxValue(assetID, urlPath, isStory):
    global finalOutput
    assetType = "Story/" if isStory else "Defect/"
    resp = requests.get("https://www9.v1host.com/MasterControlInc/rest-1.v1/Data/" + assetType + assetID + urlPath, headers=headers)
    if resp.status_code != 200:
        # This means something went wrong.
        finalOutput = finalOutput + "API_ERROR: Something went wrong"
        finalOutput = finalOutput + resp.status_code
        finalOutput = finalOutput + resp.json()
        exit()
    return resp.json()
