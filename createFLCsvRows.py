#/bin/python

import argparse
import os
import xml.etree.ElementTree
import subprocess
import sys
import shutil
import time 

d4jHome = "/home/mausoto/FaultLocProject/defects4j/" # os.environ['D4J_HOME']
defects4jCommand = d4jHome + "/framework/bin/defects4j"
buggyPath=""
fixedPath=""
#suitePath="/home/mausoto/QualityEvaluationDefects4jGenProg/Evosuite30MinGenProgFixesEvosuite103Comparison/testSuites/"
output=""
project=""
bug=""
pathToSource=""

#navigate each line of the coverageNeg.xml and coveragePos.xml to record data from each line, things such as: line number, file name, method name, etc
#difference of buggy and fixed to get the class value

def writeClassValue():
	for f in getEditedFiles():
		listOfAddedLines = getADiff(f, True)
		listOfDeletedLines = getADiff(f, False)
		if len(listOfAddedLines) > 0:
		
		else:
		
		if len(listOfAddedLines) > 0:
		
		else:
		

def setScrPath():
	cmd = defects4jCommand + " export -p dir.src.classes"
	p = subprocess.Popen(cmd, shell=True, cwd=buggyPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	for i in p.stdout:
		pathToSource = str(i).split("2>&1")[-1].strip()
		
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
	cmd+=buggyPath+"/"+pathToSource+"/"+#pathToFile +" " + bug.getFixPath()+"/"+pathToSource+"/"+pathToFile
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

def checkout(folderToCheckout, project, bugNum, vers):
	cmd = defects4jCommand + " checkout -p " + str(project) + " -v " + str(bugNum) + str(vers) + " -w " + str(folderToCheckout)
	p = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def updateGlobalVars(args):
	#CHECK IF THIS PATH IS CORRECT
	buggyPath="/home/mausoto/FaultLocProject/defects4j/ExamplesCheckedOut/"+str(args.project).toLower+str(args.bug)+"Buggy/"
	fixedPath="/home/mausoto/FaultLocProject/defects4j/ExamplesCheckedOut/"+str(args.project).toLower+str(args.bug)+"Fixed/"
	#suitePath="/home/mausoto/QualityEvaluationDefects4jGenProg/Evosuite30MinGenProgFixesEvosuite103Comparison/testSuites/"
	output=args.output
	bug=args.bug
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
				hitsP = lineT.attrib['hits'] - hitsN
				cmd = "echo \""+ project+","+bug+","+ lineNumberT+","+hitsN+","+hitsP +"\" >> "+ outputFile
				p = subprocess.call(cmd, shell=True)#, cwd=bug.getBugPath(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
def getFailingTests():
#I'LL LEAVE THIS FOR LATER BECAUSE I CAN'T ACCESS THE OTHER SCRIPTS RIGHT NOW AND I THINK THE GENPROG SCRIPTS DO THIS EASILY	

	
def generateCoverageNeg(listOfNegTC):
	for negTest in listOfNegTC:
		print negTest
		cmd = defects4jCommand + " coverage -t " + negTest + " -w " + str(bugPath) + " -o " + #SOME OUTPUT FOLDER TO LATER BUILD THEM UP
		p = subprocess.call(cmd, shell=True, cwd=bugPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
		#rename it to buggy (if there is more than one buggy test then create several coverageNeg.xml and then merge them)
		#NOT SURE IF I CAN USE THE -O TO OUTPUT IT WITH A DIFFERENT NAME, IF NOT, I CAN RENAME IT HERE
	
def generateCovTot(args):
	#run coverage with the whole test suite and create coverageTot.xml
	cmd = defects4jCommand + " coverage" # -w " + bug.getFixPath() + " -s " + str(suitePath)
	p = subprocess.call(cmd, shell=True, cwd=bugPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
		
#def getEditedFiles():
#	cmd = defects4jCommand + " export -p classes.modified"
#	p = subprocess.Popen(cmd, shell=True, cwd=bugPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#	return [ line.split("2>&1")[-1].strip().replace(".", "/") + ".java" for line in p.stdout ]
	
def getOptions():
#ask as param project and bug number
	parser = argparse.ArgumentParser(description="This script assumes a buggy version has already been checked out and manually changed to include only positive test cases or only negative. Example of usage: python createFLCsvRows.py Closure 38")
	parser.add_argument("project", help="the project in upper case (ex: Lang, Chart, Closure, Math, Time)")
	parser.add_argument("bug", help="the bug number (ex: 1,2,3,4,...)")
	parser.add_argument("output", help="full path of the output file")
	return parser.parse_args()
	
def main():
	args=getOptions()
	#errorHandling(args)
	updateGlobalVars(args)
	setScrPath()
	#checkout buggy and fixed versions
	checkout(buggyPath+, project, bug, "b")
	checkout(fixedPath+, project, bug, "f")
	
	#CHECK IF THIS PATH IS CORRECT
	if(os.path.isfile(outputFile)):
		os.remove(outputFile)
	cmd = "echo \"Project,Bug,hitsNeg,hitsPos\" >> "+ outputFile
	p = subprocess.call(cmd, shell=True)#, cwd=bug.getBugPath(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				
	#creating xml file
	pathToXmlFile=bugPath+"/coverage.xml"
	if os.path.exists(pathToXmlFile):
		os.remove(pathToXmlFile)
		
	#obtain test that fails in buggy version by running defects4j info (maybe there is an easier way)
	failingTestList=getFailingTests()
	
	#run only that one using coverage -t and create coverageNeg.xml
	generateCoverageNeg(failingTestList)
	
	writeNumberOfHits()
	
	writeClassValue()
	
	
	###################################################
		allCoverageMetrics=""
		for f in getEditedFiles(bug):
			print "Working on file "+f
			listOfAddedLines = getADiff(f, bug, True)
			#print "Added lines: "+ str(listOfAddedLines)
			listOfDeletedLines = getADiff(f, bug, False)
			#print "Deleted lines: "+ str(listOfDeletedLines) + " Length: " + str(len(listOfDeletedLines))
			allCoverageMetrics=getInitialCoverageMetrics(bug.getFixPath()+"/coverage.xml")
			
			
			if len(listOfDeletedLines) > 0:
				[covInfoBuggy,listOfMethodsDel] = computeCoverage(listOfDeletedLines, bug.getBugPath()+"/coverage.xml")
				#print listOfMethodsDel
				allCoverageMetrics+=covInfoBuggy #index 0 has lines deleted, coverage of lines deleted and methods changed by lines deleted. Index 1 has a list methods changed
			else:
				#print "Nothing deleted"
				allCoverageMetrics+=",0,-,0"
				listOfMethodsDel=[]
			
			if len(listOfAddedLines) > 0:
				[covInfoPatched,listOfMethodsAdd] = computeCoverage(listOfAddedLines, bug.getFixPath()+"/coverage.xml")
				#print listOfMethodsAdd
				allCoverageMetrics+=covInfoPatched
			else:
				#print "Nothing added"
				allCoverageMetrics+=",0,-,0"
				listOfMethodsAdd=[]
				
			methodsChanged = list(set(listOfMethodsAdd))
			#print "Methods changed"
			#print [m for m in methodsChanged]
			for b in listOfMethodsDel:	
				#print "Checking if this is in the list above: "+ b 
				if not (b in methodsChanged):
					#print "It wasnt!"
					methodsChanged.append(b)
			
			#print "Methods changed after adding the others"
			#print [m for m in methodsChanged]
			#Get coverages of changed methods in coverage.xml from the patched version
			allCoverageMetrics+=getCoveragesOfMethodsChanged(methodsChanged, bug.getFixPath()+"/coverage.xml")
				
			#pipes the result to a csv file
			#Generated patch
			if not args.patches is None:
				#patchName=str(bug.getPatch().split('/')[-1].strip())
				diffName=str(bug.getPatch().split('/')[-1].strip())
				defect=diffName.split('_')[0]
				bug=int(filter(str.isdigit, defect))
				project=str(filter(str.isalpha, defect)).title()
				seed=int(filter(str.isdigit, diffName.split('_')[1]))
				edits=diffName.split('_')[2:-1]
				edits=str(edits).replace("['","").replace("']",")").replace("r', '","r(").replace("d', '","d(").replace("a', '","a(").replace("e', '","e(").replace("', '","_").replace("zer)","zer")
				#print "diffName: "+diffName
				#variant=int(filter(str.isdigit, diffName.split('_')[-1]))
				#variant=""
				allCoverageMetrics=str(project)+","+str(bug)+","+str(seed)+","+str(edits)+","+str(allCoverageMetrics)
				#allCoverageMetrics=str(project)+","+str(bug)+","+str(seed)+","+str(edits)+","+str(variant)+","+str(allCoverageMetrics)
			#Human made patch
			if not args.many is None or not args.project is None:
				patchName=str(bug.getProject() +","+ bug.getBugNum())
				allCoverageMetrics=patchName+","+allCoverageMetrics
			print allCoverageMetrics
			cmd = "echo \""+str(allCoverageMetrics)+ "\" >> "+ outputFile
			p = subprocess.call(cmd, shell=True)#, cwd=bug.getBugPath(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			print ""
	print "Results in "+outputFile
main()
