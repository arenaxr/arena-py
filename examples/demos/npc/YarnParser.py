from ColorPrinter import *

import copy
import json
import re

# ------------------------------------------ #
# ----------YARN DIALOGUE CLASSES----------- #
# ------------------------------------------ #

#Define Yarn Dialogue Classes and Subcomponents of data structure.
class Dialogue:
    def __init__(self, filename):
        self.jsonString = ""
        self.filename = filename
        self.nodes = self.getNodesFromFile(filename)
        self.currentNode = self.nodes[0] 
    def getNodesFromFile(self, filename):
        # Open file
        f = open(filename)
        jsonString = f.read()
        self.jsonString = jsonString
        jsonString = "{\"nodes\":" + jsonString + "}"
        yarnJson = json.loads(jsonString) #yarnJson is a list of nodeJsons.
        
        # Iterating through the json list
        nodes = []
        for nodeJson in yarnJson['nodes']:
            nodes.append(Node(nodeJson["title"], nodeJson["body"]))
        # Closing file
        f.close()
        return nodes

    def getNodeIndexFromString(self, nodeName):
        for i in range(len(self.nodes)):
            if self.nodes[i].title == nodeName:
                return i
        printError("Node with name \"" + nodeName + "\" not found!")
        return -1

    def printJson(self):
        printYellowB("\n(---JSON File \"" + self.filename + "\":---)")
        printYellow(self.jsonString)

    def printInfo(self):
        printBlueB("\n(---Dialogue parsed with " + str(len(self.nodes)) + " nodes:---)")
        for node in self.nodes:
            printCyan("NodeTitle: " + node.title)        
            
            for l in range(len(node.lines)):
                line = node.lines[l]
                #show full unprocessed lines
                printCyan("  "+str(l)+". Text: " + line.text)        
                # extract commands (format <<commandType (commandTextArg0,commandTextArg1,...)>>)
                for c in range(len(line.commands)):            
                    printGreen("    <<"+str(c)+">> commandType: " + line.commands[c].type)
                    printGreen(         "          commandText: " + line.commands[c].text)
                    if(len(line.commands[c].args) > 0):
                        for a in range(len(line.commands[c].args)):
                            printGreen(     "          --commandArgs["+str(a)+"]: " + line.commands[c].args[a])
                #extract choices (format [[choiceText|choiceNode]])
                for c in range(len(line.choices)):
                    printMagenta("    [["+str(c)+"]] choiceText: " + line.choices[c].text)
                    printMagenta(         "          choiceNode: " + line.choices[c].node)

class Node:
    def __init__(self, titleString, bodyString):
        self.title = titleString
        self.lines = self.getLinesFromBodyString(bodyString)
        self.currentLineIndex = 0
    def getLinesFromBodyString(self, bodyString):
        lineStrings = bodyString.split("\n")
        lines = []
        for c in range(len(lineStrings)):
            lines.append(Line(lineStrings[c]))
        return lines

class Line:
    def __init__(self, lineString):
        self.text = self.getTextFromLine(lineString)
        self.choices = self.getChoicesFromLine(lineString)
        self.commands = self.getCommandsFromLine(lineString)
        self.currentChoiceIndex = 0 # is this needed?
    def getTextFromLine(self, lineString): #[Input: line is a single dialogue line] -> [Output: Dialogue Text only] 
        text = re.sub(r'\<\<.*?\>\>', "", lineString)
        text = re.sub(r'\[\[.*?\]\]', "", text)
        return text
    def getCommandsFromLine(self, lineString): #[Input: line is a single dialogue line] -> [Output: List of string commands in <<>>s, brackets removed.]
        commandStrings = re.findall(r'\<\<.*?\>\>', lineString)
        commands = []
        for c in range(len(commandStrings)):            
            commandStrings[c] = commandStrings[c].replace("<","").replace(">","")
            commands.append(Command(commandStrings[c]))
        return commands
    def getChoicesFromLine(self, lineString): #[Input: line is a single dialogue line] -> [Output: List of string choices in [[]]s, brackets removed.]
        choiceStrings = re.findall(r'\[\[.*?\]\]', lineString)
        choices = []
        for c in range(len(choiceStrings)):
            choiceStrings[c] = choiceStrings[c].replace("[","").replace("]","")
            choices.append(Choice(choiceStrings[c]))
        return choices

class Command:
    def __init__(self, commandString):
        self.type = self.getTypeFromCommand(commandString)
        self.text = self.getTextFromCommand(commandString)
        self.args = self.getArgsFromText(self.text)
    def getTypeFromCommand(self, commandString): #[Input: String command in <<>>] -> [Output: Command TYPE, split by ' '.]
        if(commandString.count(' ') < 1): return ""
        commandType = commandString.split(' ')[0]
        return commandType         
    def getTextFromCommand(self, commandString): #[Input: String command in <<>>] -> [Output: Command TEXT, split by ' '.]
        if(commandString.count(' ') < 1): return ""
        commandText = commandString.split(' ')[1]
        return commandText
    def getArgsFromText(self, textString): #[Input: String TextFromCommand result] -> [Ouptut: Command ARGS list, split by ',' in ().]
        args = []
        textString = textString.replace(" ","")        
        if(len(textString) >= 2 and textString[0] == '(' and textString[-1] == ')'):
            textString = textString[1:-1] #remove first and last '()' chars
            args = textString.split(',')
        else:
            args = [textString]
        return args

class Choice:
    def __init__(self, choiceString):
        self.text = self.getTextFromChoice(choiceString)
        self.node = self.getNodeFromChoice(choiceString)
    def getTextFromChoice(self, choiceString): #[Input: String choice in [[]] ] -> [Output: Choice TEXT, split by '|'.]
        if(choiceString.count('|') != 1): return choiceString
        choiceText = choiceString.split('|')[0]
        return choiceText         
    def getNodeFromChoice(self, choiceString): #[Input: String choice in [[]] ] -> [Output: Choice NODE, split by '|'.]
        if(choiceString.count('|') != 1): return choiceString
        choiceNode = choiceString.split('|')[1]
        return choiceNode 