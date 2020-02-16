#!/usr/bin/env python

from os import system, listdir, getcwd, chdir

from optparse import OptionParser
parser = OptionParser()
parser.add_option('--doSetting', default=False, action='store_true', help='Set up the sub-directories')
parser.add_option('--doHadding', default=False, action='store_true', help='Run the hadding jobs')
parser.add_option('--doSplitting', default=False, action='store_true', help='Run the splitting jobs')
parser.add_option('--doMoving', default=False, action='store_true', help='Move the output files to the non-raw location')
(opts,args) = parser.parse_args()

from haddingInfo import cmsswDir, cmsenv, sigs, run

def writeHaddFile(currentDir):
  haddCmd = 'python $CMSSW_BASE/src/flashgg/Systematics/scripts/hadd_all.py'
  with open('hadd_all.sh','w') as outFile:
    outFile.write('#!/bin/bash \n')
    outFile.write('cd %s \n'%cmsswDir)
    outFile.write('%s \n'%cmsenv)
    outFile.write('cd %s \n'%currentDir)
    outFile.write('%s \n'%haddCmd)
  run('chmod +x hadd_all.sh')

def writeSplitFile(currentDir):
  splitCmd = 'python $CMSSW_BASE/src/flashgg/Systematics/scripts/split_all.py --doStage1p2'
  with open('split_all.sh','w') as outFile:
    outFile.write('#!/bin/bash \n')
    outFile.write('cd %s \n'%cmsswDir)
    outFile.write('%s \n'%cmsenv)
    outFile.write('cd %s \n'%currentDir)
    outFile.write('%s \n'%splitCmd)
  run('chmod +x split_all.sh')

cwd = getcwd()

if opts.doSetting:
  for sig,key in sigs.iteritems():
    system('mkdir %s'%sig)
    system('mv output_%s* %s'%(key,sig))

for sig in sigs.keys():
  currDir = '%s/%s'%(cwd,sig)
  chdir(currDir)
  if opts.doHadding:
    writeHaddFile(currDir)
    run('qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G -o /dev/null -e %s/hadd_all.err %s/hadd_all.sh'%(currDir,currDir))
  elif opts.doSplitting:
    writeSplitFile(currDir)
    run('qsub -q hep.q -l h_rt=3:0:0 -l h_vmem=24G -o /dev/null -e %s/split_all.err %s/split_all.sh'%(currDir,currDir))
  elif opts.doMoving:
    run('python $CMSSW_BASE/src/flashgg/Systematics/scripts/HTXS_mv_irrelevant.py')
    run('python $CMSSW_BASE/src/flashgg/Systematics/scripts/fileRenamer.py')
    run('cp output_*.root ../../')
  chdir(cwd)
