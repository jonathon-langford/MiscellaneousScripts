import ROOT
import glob
import re
import os
import sys
import math
from optparse import OptionParser
from collections import OrderedDict as od

from lheTools.lheTools import *

def get_options():
  parser = OptionParser()
  parser.add_option('--input-lhe', dest='input_lhe', default='input.lhe', help="Input lhe file")
  parser.add_option('--input-lhe-dir', dest='input_lhe_dir', default='', help="Input lhe directory (for multiple files)")
  parser.add_option('--allWeights', dest='allWeights', default=False, action="store_true", help="Look at all weights defined in weightInfo dict")
  return parser.parse_args()
(opt,args) = get_options()

ROOT.gROOT.ProcessLine('#include "LHEF.h"')

if opt.input_lhe_dir != '':
  if not os.path.isdir(opt.input_lhe_dir):
    print " --> [ERROR] Input lhe directory (%s) does not exist. Leaving"%opt.input_lhe_dir
    sys.exit(1)
  else:
    input_lhes = glob.glob("%s/*.lhe"%opt.input_lhe_dir)
else:
  if not os.path.exists(opt.input_lhe):
    print " --> [ERROR] Input lhe file (%s) does not exist. Leaving"%opt.input_lhe
    sys.exit(1)
  else:
    input_lhes = [opt.input_lhe]

# Define histograms
ROOT.gStyle.SetOptStat(0)
weightInfo = od()
if opt.allWeights:
  weightInfo['sm'] = 'rw0000'
  weightInfo['cHBox_1'] = 'rw0002'
  weightInfo['cHD_1'] = 'rw0004'
  weightInfo['cHW_1'] = 'rw0008'
  weightInfo['cHB_1'] = 'rw0010'
  weightInfo['cHWB_1'] = 'rw0012'
else:
  weightInfo['sm'] = 'nominal'

# Define histograms
histVars = od()
histVars["pTH"] = [100,0,300] #nBins, xlow, xhigh

hists = od()
for hv,binning in histVars.iteritems():
  for w in weightInfo:
    hists['%s_%s'%(hv,w)] = ROOT.TH1F("%s_%s"%(hv,w),"",binning[0],binning[1],binning[2])

# Define counters

for ilhe in input_lhes:
  print " --> Processing: %s"%ilhe
  # Initialise reader
  reader = ROOT.LHEF.Reader(ilhe)
  # Loop over events
  nEvent = 0
  while( reader.readEvent() ):
    nEvent += 1
    ev = Event(reader.hepeup)
    weights = ev.extractWeights(doAllWeights=opt.allWeights)

    leptons = []
    higgs = []
    for ip in range(ev.N): 
      p = Particle(reader.hepeup,ip)
      if abs(p.pdgId) in [11,13]: 
        leptons.append(p)
      elif p.pdgId == 25: higgs.append(p)

    # Calculate event properties
    ev.pTH = higgs[0].P4.Pt()

    # Fill histograms
    for hv in histVars:
      for w, wn in weightInfo.iteritems(): 
        # Fill event
        hists['%s_%s'%(hv,w)].Fill(getattr(ev,hv),weights[wn])
