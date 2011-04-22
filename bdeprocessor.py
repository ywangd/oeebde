#!/usr/bin/env python

from bdeerrorlog import BdeErrorLog
from bdefile import BdeFile
from bdeconfig import BdeConfig
from bdedb import BdeDB
from bdesumup import BdeSumup, BdeSumupList
import activitycode
import bdeutil
import bdesumuprules

'''
Created on 15/04/2011

@author: yang
'''

# Read the file into file object
file = BdeFile('good.bde')
file.read()
    
# Process the config file
config = BdeConfig()
config.read()

# Create the sqlite DB for data validations
# Load the file into the Database
# This creates a memory concern that we now have two copies of the file.
# One in the file object and this one in sqlite database.
db = BdeDB()
db.loaddata('good.bde')

# The error logger
errorlog = BdeErrorLog()

# Perform required data validations based on the config file
# Add any error into the error logger
for option in config.validationOptions:
    code, lineIndex = option.routine(db.cursor)
    for index in lineIndex:
            if index is not None:
                errorlog.add(code, file.lines[index])
            else:
                errorlog.add(code, None)

# Be nice and delete the database
del(db)

# Print any errors found
for error in errorlog.errorList:
    print error[0], ': ', error[1].getLineNumber()

# The overall sumup list
sumupList = BdeSumupList()

# Set every sumup to be None at the beginning, meaning
# no sumup is current happening.
categoryNames = activitycode.codeOf.keys()
sumupCurrent = {}
for categoryName in categoryNames:
    sumupCurrent[categoryName] = None
    
# Build the Sumup Rules object
sumupRules = {}
for categoryName in categoryNames:
    tree = bdeutil.readXMLTree()
    node = tree.find('Sumups/Categories')
    for element in node.getiterator('Category'):
        if element.attrib['Name'] == categoryName:
            # Create the rule object
            thisRule = bdesumuprules.SumupRule(categoryName)
            
            # Process the start rule
            ruleElement = element.find('StartRule')
            # The rule name
            thisRule.startSumupRule = ruleElement.attrib['Name']
            for extraElement in ruleElement.getiterator():
                thisRule.setattr(extraElement.tag, extraElement.text)
            # Set the routine 
            rulesNode = tree.find('Sumups/Rules/StartRules/'+thisRule.startSumupRule)
            moduleName = rulesNode.attrib['Module']
            functionName = rulesNode.attrib['Function']
            moduleName = __import__(moduleName)
            thisRule.startSumupRoutine = getattr(moduleName, functionName)
            
            # Process the terminate rule
            ruleElement = element.find('TerminateRule')
            # The rule name
            thisRule.terminateSumupRule = ruleElement.attrib['Name']
            for extraElement in ruleElement.getiterator():
                thisRule.setattr(extraElement.tag, extraElement.text)
            # Set the routine 
            rulesNode = tree.find('Sumups/Rules/TerminateRules/'+thisRule.terminateSumupRule)
            moduleName = rulesNode.attrib['Module']
            functionName = rulesNode.attrib['Function']
            moduleName = __import__(moduleName)
            thisRule.terminateSumupRoutine = getattr(moduleName, functionName)
            
            # Process the end rule
            ruleElement = element.find('EndRule')
            # The rule name
            thisRule.endSumupRule = ruleElement.attrib['Name']
            for extraElement in ruleElement.getiterator():
                thisRule.setattr(extraElement.tag, extraElement.text)
            # Set the routine 
            rulesNode = tree.find('Sumups/Rules/EndRules/'+thisRule.endSumupRule)
            moduleName = rulesNode.attrib['Module']
            functionName = rulesNode.attrib['Function']
            moduleName = __import__(moduleName)
            thisRule.endSumupRoutine = getattr(moduleName, functionName)
            
            # The rule are now complete
            sumupRules[categoryName] = thisRule
            
            # Get out of node loop once match is found
            break;


# Lines that are not used for any sumups
unSumLines = []

# Data sum-ups
for line in file.getCountableLines():
    # Which category the code belongs to
    categoryName = activitycode.findCategory(line.getActivityCode())
    
    # Process the code from this line belongs to a required category
    if categoryName is not None:
        sumupRules[categoryName].action(line, sumupCurrent, sumupList)
    else:
        unSumLines.append(line)
        
# End any unfinished sumup at the end of the file
for categoryName in sumupCurrent.keys():
    if sumupCurrent[categoryName] is not None:
        sumupList.add(sumupCurrent[categoryName])
        sumupCurrent[categoryName] = None
        
    
for sumup in sumupList.list:
    print '%10s %8.2f  %5d  %5d  %s   %s  %12d' % (sumup.name, sumup.calculateDuration(),
                                              sumup.lines[0].getLineNumber(), sumup.lines[len(sumup.lines)-1].getLineNumber(),
                                              sumup.getStartTime(), sumup.getEndTime(), sumup.calculateImpressionTotal())


