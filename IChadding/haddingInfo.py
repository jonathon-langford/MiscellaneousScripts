## define constants used across both hadding scripts

cmsswDir = '/vols/build/cms/es811/FreshStart/HggAnalysis/UnifiedStageOne/CMSSW_10_6_8/src/flashgg/'
cmsenv = 'eval `scram runtime -sh`'

from collections import OrderedDict as od
sigs = od()
sigs['ggH'] = 'GluGlu'
sigs['VBF'] = 'VBF'
sigs['ttH'] = 'ttH'
sigs['tH'] = 'TH'
sigs['WH'] = 'WH'
sigs['ZH'] = 'ZH'

from os import system

def run(cmd):
  print cmd
  system(cmd)

