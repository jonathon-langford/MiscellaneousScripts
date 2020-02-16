#!/usr/bin/env python

from os import system, listdir, getcwd, chdir

from optparse import OptionParser
parser = OptionParser()
parser.add_option('--doSplitting', default=False, action='store_true', help='Run the splitting jobs')
parser.add_option('--doMoving', default=False, action='store_true', help='Move the splitted jobs to temporary directories based on their STXS bin')
parser.add_option('--doHadding', default=False, action='store_true', help='Run the hadding jobs')
parser.add_option('--doFinalMove', default=False, action='store_true', help='Move the files to the non-raw location')
(opts,args) = parser.parse_args()

from haddingInfo import cmsswDir, cmsenv, run

def writeHaddFile(currentDir):
  outFile = ''
  for fName in listdir('.'):
    if fName.count('intermediate') and fName.count('.root'):
      outFile = fName.split('intermediate')[0] + fName.split('intermediate')[-1][1:]
      break
  haddCmd = 'hadd_workspaces %s/%s %s/output_*.root'%(currentDir, outFile, currentDir)
  with open('hadd_all.sh','w') as outFile:
    outFile.write('#!/bin/bash \n')
    outFile.write('cd %s \n'%cmsswDir)
    outFile.write('%s \n'%cmsenv)
    outFile.write('cd %s \n'%currentDir)
    outFile.write('%s \n'%haddCmd)
  run('chmod +x hadd_all.sh')

def writeSplitFile(currentDir):
  splitCmd = 'python $CMSSW_BASE/src/flashgg/Systematics/scripts/split_all.py --doStage1p2 --doIntermediate'
  with open('split_all.sh','w') as outFile:
    outFile.write('#!/bin/bash \n')
    outFile.write('cd %s \n'%cmsswDir)
    outFile.write('%s \n'%cmsenv)
    outFile.write('cd %s \n'%currentDir)
    outFile.write('%s \n'%splitCmd)
  run('chmod +x split_all.sh')

cwd = getcwd()

procs = []

for fName in listdir('.'):
  if fName.count('intermediate') and fName.count('.root'):
    if opts.doSplitting:
      currDir = '%s/tempDir_%s'%(cwd,fName.replace('.root',''))
      run('mkdir %s'%currDir)
      run('cp %s %s'%(fName,currDir))
      chdir(currDir)
      writeSplitFile(currDir)
      run('qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G -o /dev/null -e %s/split_all.err %s/split_all.sh'%(currDir,currDir))
    elif opts.doMoving:
      currDir = '%s/tempDir_%s'%(cwd,fName.replace('.root',''))
      chdir(currDir)
      run('python $CMSSW_BASE/src/flashgg/Systematics/scripts/HTXS_mv_irrelevant.py')
      if len(procs)==0:
        for procFile in listdir('.'):
          if not (procFile.count('output_') and procFile.count('.root')): continue
          procName = procFile.split(fName.replace('.root',''))[-1][1:].replace('.root','')
          procs.append(procName)
          print 'adding proc %s'%procName
  chdir(cwd)

if opts.doMoving:
  for proc in procs: 
    procDir = '%s/tempDir_%s'%(cwd,proc)
    run('mkdir %s'%procDir)
    for fName in listdir('.'):
      if fName.count('intermediate') and fName.count('.root'):
        currDir = '%s/tempDir_%s'%(cwd,fName.replace('.root',''))
        run('cp %s/output_*%s*.root %s'%(currDir, proc, procDir))

if opts.doHadding:
  for fName in listdir('.'):
    if fName.count('tempDir') and not fName.count('intermediate'):
      currDir = '%s/%s'%(cwd,fName)
      chdir(currDir)
      writeHaddFile(currDir)
      run('qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G -o /dev/null -e %s/hadd_all.err %s/hadd_all.sh'%(currDir,currDir))

if opts.doFinalMove:
  for fName in listdir('.'):
    if fName.count('tempDir') and not fName.count('intermediate'):
      currDir = '%s/%s'%(cwd,fName)
      outFile = ''
      for ffName in listdir(currDir):
        if ffName.count('intermediate') and ffName.count('.root'):
          outFile = ffName.split('intermediate')[0] + ffName.split('intermediate')[-1][1:]
          break
      run('cp %s/%s %s/../../../'%(currDir, outFile, currDir))
