#/bin/python

import argparse
import os
import xml.etree.ElementTree
import subprocess
import sys
import shutil
import time 


home="/home/mau/Research/"
d4jHome = os.environ['D4J_HOME']
defects4jCommand = d4jHome + "/framework/bin/defects4j"
buggyPath=""
fixedPath=""
#suitePath=home+"/QualityEvaluationDefects4jGenProg/Evosuite30MinGenProgFixesEvosuite103Comparison/testSuites/"
outputFile=""
project=""
bug=""
pathToSource=""

#navigate each line of the coverageNeg.xml and coveragePos.xml to record data from each line, things such as: line number, file name, method name, etc
#difference of buggy and fixed to get the class value


def createPosAndNegFiles():
	posClasses = getEditedFiles()
	for p in posClasses:
		cmd = "echo " + str(p) + " >> " + str(buggyPath) + "tests.pos "
		print cmd
		p = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	

	negTestCases = getFailingTests()
	for p in negTestCases:
		cmd = "echo " + str(p) + " >> " + str(buggyPath) + "tests.neg "
		print cmd
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
	
		
def getEditedFiles():
	cmd = defects4jCommand + " export -p classes.modified"
	p = subprocess.Popen(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return [ line.split("2>&1")[-1].strip().replace(".", "/") + ".java" for line in p.stdout ]

#FIX THIS
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

def updateGlobalVars(args):
	global buggyPath
	buggyPath=d4jHome+"/ExamplesCheckedOut/"+str(args.project).lower()+str(args.bug)+"Buggy/"
	global fixedPath
	fixedPath=d4jHome+"/ExamplesCheckedOut/"+str(args.project).lower()+str(args.bug)+"Fixed/"
	#global suitePath=home+"/QualityEvaluationDefects4jGenProg/Evosuite30MinGenProgFixesEvosuite103Comparison/testSuites/"
	global outputFile
	outputFile=args.output
	global bug
	bug=args.bug
	global project
	project=args.project

def writeNumberOfHits(coverageTot,coverageNeg):
	#calculate coverageTot.xml - coverageNeg.xml to get coveragePos.xml
	eTot = xml.etree.ElementTree.parse(coverageTot).getroot()
	eNeg = xml.etree.ElementTree.parse(coverageNeg).getroot()
	
	
	linesT = eTot.findall(".//line")
	for lineT in linesT:
		lineNumberT = lineT.attrib['number']
		#look for this line in the neg file
		linesN = eNeg.findall(".//line")
		for lineN in linesN:
			lineNumberN = lineN.attrib['number']
			if(lineNumberN == lineNumberT):
				hitsN = lineN.attrib['hits']
				hitsT = lineT.attrib['hits']
				hitsP = int(hitsT) - int(hitsN)
				#print lineNumberT+","+hitsT+","+hitsN+","+str(hitsP)
				cmd = "echo \""+ project+","+bug+","+ lineNumberT+","+hitsT+","+hitsN+","+str(hitsP) +"\" >> "+ outputFile
				p = subprocess.call(cmd, shell=True)#, cwd=bug.getBugPath(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				break
	
def getFailingTests():
	cmd = defects4jCommand + " export -p tests.trigger"
	p = subprocess.Popen(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return [ line for line in p.stdout ]
	
def generateCoverageNeg(listOfNegTC):
	fileNum=0
	for negTest in listOfNegTC:
		print negTest
		cmd = defects4jCommand + " coverage -t " + negTest + " -w " + str(buggyPath) 
		p = subprocess.call(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
		#rename it to buggy (if there is more than one buggy test then create several coverageNeg.xml and then merge them)
		p = subprocess.call("mv coverage.xml coverageNeg" + str(fileNum) + ".xml", shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
		fileNum+=1
#TODO: MERGE ALL THE COVERAGE NEG INTO A SINGLE COVERAGE NEG, MEANWHILE I'M JUST RENAMING
		p = subprocess.call("mv coverageNeg0.xml coverageNeg.xml", shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
	
def generateCovTot():
	#run coverage with the whole test suite and create coverageTot.xml
	cmd = defects4jCommand + " coverage" # -w " + bug.getFixPath() + " -s " + str(suitePath)
	p = subprocess.call(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
	p = subprocess.call("mv coverage.xml coverageTot.xml", shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#def getEditedFiles():
#	cmd = defects4jCommand + " export -p classes.modified"
#	p = subprocess.Popen(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#	return [ line.split("2>&1")[-1].strip().replace(".", "/") + ".java" for line in p.stdout ]
	
def getOptions():
#ask as param project and bug number
	parser = argparse.ArgumentParser(description="This script assumes a buggy version has already been checked out and manually changed to include only positive test cases or only negative. Example of usage: python createFLCsvRows.py Closure 38 /home/mau/Research/MLFaultLocProject/output.csv")
	parser.add_argument("project", help="the project in upper case (ex: Lang, Chart, Closure, Math, Time)")
	parser.add_argument("bug", help="the bug number (ex: 1,2,3,4,...)")
	parser.add_argument("output", help="full path of the output file")
	return parser.parse_args()
	
def main():
	args=getOptions()
	#errorHandling(args)
	updateGlobalVars(args)
	
	#checkout buggy and fixed versions
	checkout(buggyPath, project, bug, "b")
	checkout(fixedPath, project, bug, "f")
	setScrPath()
	
	if(os.path.isfile(outputFile)):
		os.remove(outputFile)
	cmd = "echo \"Project,Bug,Line Number,hitsTotal,hitsNeg,hitsPos\" >> "+ outputFile
	p = subprocess.call(cmd, shell=True)#, cwd=bug.getBugPath(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				
	#creating xml file
	pathToXmlFile=buggyPath+"/coverage.xml"
	if os.path.exists(pathToXmlFile):
		os.remove(pathToXmlFile)
		
	#obtain test that fails in buggy version by running defects4j info (maybe there is an easier way)
	failingTestList=getFailingTests()
	
	#run only that one using coverage -t and create coverageNeg.xml
	generateCoverageNeg(failingTestList)
	#run coverage to get the coverage of all the test suite
	generateCovTot()

	writeNumberOfHits(buggyPath+"/coverageTot.xml",buggyPath+"/coverageNeg.xml")

	createPosAndNegFiles()
	
	#writeClassValue()
	
	
	###################################################

	print "Results in "+outputFile
main()
