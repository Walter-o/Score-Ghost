import json

def loadSettings():
    with open("README.txt", "r") as settingsFile:
        return json.load(settingsFile)["Settings"]

def saveFile(data, filename):
    with open("Scores/%s"%filename, "wb") as scoreData:
        scoreData.write(data)