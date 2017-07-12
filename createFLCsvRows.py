#/bin/python

import argparse
import os
import xml.etree.ElementTree
import subprocess
import sys
import shutil
import time 
import csv
import pickle


home="/home/mau/Research/"
d4jHome = os.environ['D4J_HOME']
defects4jCommand = d4jHome + "/framework/bin/defects4j"
buggyPath=""
fixedPath=""
#suitePath=home+"/QualityEvaluationDefects4jGenProg/Evosuite30MinGenProgFixesEvosuite103Comparison/testSuites/"
outputFile="output.csv"
outputFileDotSer="output.ser"
project=""
bug=""
pathToSource=""
outputMatrix = []
columnHitsPos=5
columnNumOfLineNumber=2
columnNumOfCovPassTest=6
columnNumOfNonCovPassTest=7
columnNumOfCovFailTest=8
columnNumOfNonCovFailTest=9

#navigate each line of the coverageNeg.xml and coveragePos.xml to record data from each line, things such as: line number, file name, method name, etc
#difference of buggy and fixed to get the class value


def createPosAndNegClasses():
	posClasses = getRelevantTests()
	for p in posClasses:
		cmd = "echo " + str(p).strip() + " >> " + str(buggyPath) + "tests.pos "
		print cmd
		p = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	negTestCases = getFailingTests()
	for p in negTestCases:
		cmd = "echo " + str(p).strip() + " >> " + str(buggyPath) + "tests.neg "
		print cmd
		p = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def createPosAndNegMethods():
	p = subprocess.Popen("defects4j export -p cp.test", shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	for i in p.stdout:
		#print i
		cmd="java -cp .:junit-4.12.jar MethodExtractor "+str(buggyPath) + "tests.pos "+str(buggyPath) + "tests.neg "+i
		print "CMD: "+cmd
		p = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def writeClassValue():
	for f in getEditedFiles():
		listOfAddedLines = getADiff(f, True)
		listOfDeletedLines = getADiff(f, False)
		if len(listOfAddedLines) > 0:
			print ""
		else:
			print ""
		if len(listOfAddedLines) > 0:
			print ""
		else:
			print ""

def checkout(folderToCheckout, project, bugNum, vers):
	cmd = defects4jCommand + " checkout -p " + str(project) + " -v " + str(bugNum) + str(vers) + " -w " + str(folderToCheckout)
	print cmd
	p = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def setScrPath():
	global pathToSource
	cmd = defects4jCommand + " export -p dir.src.classes"
	p = subprocess.Popen(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	for i in p.stdout:
		pathToSource = str(i).split("2>&1")[-1].strip()
		#print pathToSource
	
#def getEditedFiles():
#	cmd = defects4jCommand + " export -p classes.modified"
#	p = subprocess.Popen(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#	return [ line.split("2>&1")[-1].strip().replace(".", "/") + ".java" for line in p.stdout ]
	

#FIX THIS
###############################################
def getADiff(pathToFile, new):
	cmd = "diff -w --unchanged-line-format=\"\"  "
	if new:
		cmd+="--old-line-format=\"\" --new-line-format=\"%dn \" " 
	else:
		cmd+="--old-line-format=\"%dn \" --new-line-format=\"\" " 
	cmd+=buggyPath+"/"+pathToSource+"/"#+pathToFile +" " + bug.getFixPath()+"/"+pathToSource+"/"+pathToFile
	#cmd+=bug.getBugPath()+"/"+pathToSource+"/"+pathToFile +" " + bug.getFixPath()+"/"+pathToSource+"/"+pathToFile
	#print cmd
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	diffLines=""
	for line in p.stdout:
		diffLines = line
	diffLines=diffLines.strip().split(" ")
	#remove empty strings
	diffLines=list(filter(None, diffLines))
	
	#ignore lines where there is a single bracket because it won't be covered by cobertura
	ret=[]
	for changedLine in diffLines:
		cmd="sed \'"+ str(changedLine)+"q;d\' "
		if new:
			cmd+= fixedPath
		else:
			cmd+= buggyPath()
		cmd+="/"+pathToSource+"/"+pathToFile 
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		for line in p.stdout:
			if line.strip() != "}" and line.strip() != "{" and not line.strip() is None:
				#print "Appending to ret: \'" + str(changedLine) + "\'"
				ret.append(changedLine)
	return ret
####################################################

def updateGlobalVars(args):
	global buggyPath
	buggyPath=d4jHome+"/ExamplesCheckedOut/"+str(args.project).lower()+str(args.bug)+"Buggy/"
	global fixedPath
	fixedPath=d4jHome+"/ExamplesCheckedOut/"+str(args.project).lower()+str(args.bug)+"Fixed/"
	#global suitePath=home+"/QualityEvaluationDefects4jGenProg/Evosuite30MinGenProgFixesEvosuite103Comparison/testSuites/"
	global outputFile
	outputFile="attributeFiles/"+str(args.project)+str(args.bug)+".csv"
	if not args.output is None:
		outputFile=args.output
	global bug
	bug=args.bug
	global project
	project=args.project
	global outputFileDotSer
	outputFileDotSer="attributeFiles/"+str(args.project)+str(args.bug)+".ser"
	if not args.output is None:
		outputFile=args.output[:-4]+".ser"
	
	
	
def writeNumberOfHits(coverageTot,coverageNeg):
	#calculate coverageTot.xml - coverageNeg.xml to get coveragePos.xml
	eTot = xml.etree.ElementTree.parse(coverageTot).getroot()
	eNeg = xml.etree.ElementTree.parse(coverageNeg).getroot()
	
	
	linesT = eTot.findall(".//class/lines/line")
	for lineT in linesT:
		lineNumberT = lineT.attrib['number']
		#look for this line in the neg file
		linesN = eNeg.findall(".//class/lines/line")
		for lineN in linesN:
			lineNumberN = lineN.attrib['number']
			if(lineNumberN == lineNumberT):
				hitsN = lineN.attrib['hits']
				hitsT = lineT.attrib['hits']
				hitsP = int(hitsT) - int(hitsN)
				hitsP = str(hitsP)
				#print lineNumberT+","+hitsT+","+hitsN+","+str(hitsP)
				listOfAttributes = []
				listOfAttributes.append(project)
				listOfAttributes.append(bug)
				listOfAttributes.append(lineNumberT)
				listOfAttributes.append(hitsT)
				listOfAttributes.append(hitsN)
				listOfAttributes.append(hitsP)
				outputMatrix.append(listOfAttributes)
				break
	
def getFailingTests():
	cmd = defects4jCommand + " export -p tests.trigger"
	p = subprocess.Popen(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return [ line for line in p.stdout ]

def getRelevantTests():
	#Relevant tests are the ones that touch the modified class
	cmd = defects4jCommand + " export -p tests.relevant"
	p = subprocess.Popen(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return [ line for line in p.stdout ]

def calculateCoverageAndRenameXMLFile(testName,newXmlName):
	cmd = defects4jCommand + " coverage"
	if len(testName) > 0:
		cmd+=" -t " + testName + " -w " + str(buggyPath) 
	p = subprocess.call(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
	p = subprocess.call("mv coverage.xml "+newXmlName, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

def generateCovNeg(listOfNegTC):
	fileNum=0
	for negTest in listOfNegTC:
		#TODO: rename it to buggy (if there is more than one buggy test then create several coverageNeg.xml and then merge them)
		newName="coverageNeg" + str(fileNum) + ".xml"
		calculateCoverageAndRenameXMLFile(negTest,newName)
		fileNum+=1
		#TODO: MERGE ALL THE COVERAGE NEG INTO A SINGLE COVERAGE NEG, MEANWHILE I'M JUST RENAMING
		p = subprocess.call("mv coverageNeg0.xml coverageNeg.xml", shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
	
def generateCovTot():
	#run coverage with the whole test suite and create coverageTot.xml
	calculateCoverageAndRenameXMLFile("","coverageTot.xml")

def addMethodHits(negOrPos):
	negOrPos=negOrPos.lower()
	filePath=buggyPath+"/methods."+negOrPos
	fileNum=0
	negOrPos=negOrPos.capitalize()
	with open(filePath) as f:
	    for test in f:
			print test
			nameCovFile="coverage"+str(negOrPos)+"Test"+str(fileNum)+".xml"
			calculateCoverageAndRenameXMLFile(test,nameCovFile)
			addStatsPosAndNegTests(nameCovFile,negOrPos)
			fileNum+=1
		
def addStatsPosAndNegTests(nameCovFile,negOrPos):
	ePosTest = xml.etree.ElementTree.parse(buggyPath+nameCovFile).getroot()
	
	linesP = ePosTest.findall(".//class/lines/line")
	for lineP in linesP:
		lineNumberT = lineP.attrib['number']
		#look for this line in the outputMatrix
		for attributeRow in outputMatrix:
			if str(attributeRow[0])!="Project":
				#print "Comparing "+ str(lineP.attrib['hits']) + " to "+ str(0) + ". Are they equal? "+str(lineP.attrib['hits']) == str(0)
				if attributeRow[columnNumOfLineNumber] == lineNumberT:
					if str(lineP.attrib['hits']) != str(0) and negOrPos.lower()=="pos":
						attributeRow[columnNumOfCovPassTest]+=1
					elif str(lineP.attrib['hits']) == str(0) and negOrPos.lower()=="pos":
						attributeRow[columnNumOfNonCovPassTest]+=1
					elif str(lineP.attrib['hits']) != str(0) and negOrPos.lower()=="neg":
						attributeRow[columnNumOfCovFailTest]+=1
					elif str(lineP.attrib['hits']) == str(0) and negOrPos.lower()=="neg":
						attributeRow[columnNumOfNonCovFailTest]+=1
					else:
						p = subprocess.call("echo ERROR, PLEASE CHECK", shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
					
def addZerosToSBFLAttributeColumns():
	for attributeRow in outputMatrix:
		if str(attributeRow[0])!="Project":
			attributeRow.append(0)
			attributeRow.append(0)
			attributeRow.append(0)
			attributeRow.append(0)

	
		
def addFirstLineOfOutput():
	listOfAttributes = []
	listOfAttributes.append("Project")
	listOfAttributes.append("Bug")
	listOfAttributes.append("LineNum")
	listOfAttributes.append("HitsTotal")
	listOfAttributes.append("HitsNeg")
	listOfAttributes.append("HitsPos")
	listOfAttributes.append("CoveringPassingTests")
	listOfAttributes.append("NonCoveringPassingTests")
	listOfAttributes.append("CoveringFailingTests")
	listOfAttributes.append("NonCoveringFailingTests")
	listOfAttributes.append("ClassValue")
	outputMatrix.append(listOfAttributes)

def writeMatrixToCSVFile():
	global outputMatrix
	with open(outputFile, "wb") as f:
	    writer = csv.writer(f)
	    writer.writerows(outputMatrix)
	    
def loadSerializable(serializableMatrix):
	global outputMatrix
	f=open(serializableMatrix,'r')
	outputMatrix = pickle.load(f)
	f.close()
	
def createSerializable():
	print outputFileDotSer
	f=open(outputFileDotSer,'wb')
	pickle.dump(outputMatrix, f)
	f.close()
	
def getOptions():
	#ask as param project and bug number
	parser = argparse.ArgumentParser(description="Example of usage: python createFLCsvRows.py Closure 38")
	parser.add_argument("project", help="the project in upper case (ex: Lang, Chart, Closure, Math, Time)")
	parser.add_argument("bug", help="the bug number (ex: 1,2,3,4,...)")
	parser.add_argument("--serializable", help="full path of the serializable file containing previous results for one project")
	parser.add_argument("--output", help="full path of the output file")
	return parser.parse_args()
	
def main():
	args=getOptions()
	updateGlobalVars(args)
	if not args.serializable is None:
		loadSerializable(args.serializable)
		#checkout buggy and fixed versions
		checkout(buggyPath, project, bug, "b")
		#checkout(fixedPath, project, bug, "f")
		setScrPath()


	print str(outputMatrix[0])
	if int(len(outputMatrix[0])-1) < columnHitsPos:
		addFirstLineOfOutput()
				
		#creating xml file
		pathToXmlFile=buggyPath+"/coverage.xml"
		if os.path.exists(pathToXmlFile):
			os.remove(pathToXmlFile)
		
		#obtain test that fails in buggy version by running defects4j info (maybe there is an easier way)
		failingTestList=getFailingTests()
	
		#run only that one using coverage -t and create coverageNeg.xml
		generateCovNeg(failingTestList)
		#run coverage to get the coverage of all the test suite
		generateCovTot()
		writeNumberOfHits(buggyPath+"/coverageTot.xml",buggyPath+"/coverageNeg.xml")


	if int(len(outputMatrix[0])-1) < columnNumOfNonCovFailTest:
		createPosAndNegClasses()
		createPosAndNegMethods()
		addZerosToSBFLAttributeColumns()
		addMethodHits("neg")
		addMethodHits("pos")
	
	#writeClassValue()
	
	if(os.path.isfile(outputFileDotSer)):
		os.remove(outputFileDotSer)
	createSerializable()
	if(os.path.isfile(outputFile)):
		os.remove(outputFile)
	writeMatrixToCSVFile()

	print "Results in "+outputFile
	
main()
