import uproot as upr
import ROOT
import numpy as np
import pandas as pd
from numpy import sqrt
from collections import OrderedDict as od
import json
from Utilities.General.cmssw_das_client import get_data as das_query
import os, sys
import re
from optparse import OptionParser
from STXS import STXS_bins, xs

# Import tools
from tools.eventPrivate import *

# Sample list: if extracting files from .txt file then specify file path
samples = od()
samples['ggH_2018_minlo'] = "minlo_private_files.txt"

def get_options():
  parser = OptionParser()
  parser.add_option('--sample', dest='sample', default='ggH_2018_minlo', help="Signal sample key")
  parser.add_option('--nEvents', dest='nEvents', default=100, type='int', help="Number of events to process")
  parser.add_option('--doFilesFromList', dest='doFilesFromList', default=False, action="store_true", help="Extract files from .txt file, specified above")
  return parser.parse_args()
(opt,args) = get_options()

# Create list of files
files = []
if opt.doFilesFromList:
  listOfFiles = open( samples[opt.sample], "r" )
  for line in listOfFiles: files.append(line[:-1])
else:
  das_sample = samples[opt.sample]
  for fdata in das_query("file dataset=%s"%das_sample, cmd="dasgoclient --dasmaps=./")['data']: files.append("root://cms-xrd-global.cern.ch/%s"%fdata['file'][0]['name'])

scaleWeights = ['NNLO_1_1_NLO_1_1', 'NNLO_1_1_NLO_1_2', 'NNLO_1_1_NLO_1_0p5', 'NNLO_1_1_NLO_2_1', 'NNLO_1_1_NLO_2_2', 'NNLO_1_1_NLO_0p5_1', 'NNLO_1_1_NLO_0p5_0p5', 'NNLO_2_2_NLO_1_1', 'NNLO_2_2_NLO_1_2', 'NNLO_2_2_NLO_1_0p5', 'NNLO_2_2_NLO_2_1', 'NNLO_2_2_NLO_2_2', 'NNLO_2_2_NLO_0p5_1', 'NNLO_2_2_NLO_0p5_0p5', 'NNLO_0p5_0p5_NLO_1_1', 'NNLO_0p5_0p5_NLO_1_2', 'NNLO_0p5_0p5_NLO_1_0p5', 'NNLO_0p5_0p5_NLO_2_1', 'NNLO_0p5_0p5_NLO_2_2', 'NNLO_0p5_0p5_NLO_0p5_1', 'NNLO_0p5_0p5_NLO_0p5_0p5']

# Define histograms
hists = od()
hists['genWeight'] = ROOT.TH1F("genWeight","",100,-100,100)
for stxs_bin in STXS_bins:
  if stxs_bin.split("_")[0] == "GG2H":
    for sw in scaleWeights:
      k = "%s_%s"%(stxs_bin,sw)
      hists[k] = ROOT.TH1F(k,"",150,-0.5,4.5)

# Define counters
counters = od()
for stxs_bin in STXS_bins:
  if stxs_bin.split("_")[0] == "GG2H":
    counters[stxs_bin] = od()
    counters[stxs_bin]['nominal'] = 0
    for sw in scaleWeights:
      counters[stxs_bin][sw] = 0

    

# Loop over events
nanoAODVars = ['genWeight','HTXS_stage_0','HTXS_stage1_1_cat_pTjet30GeV','HTXS_Higgs_pt','HTXS_njets30']
for sw in scaleWeights: nanoAODVars.append( "LHEWeight_%s"%sw )

evtCounter = 0

for fidx, fname in enumerate(files):

  if evtCounter == opt.nEvents: continue

  print " --> Processing file %g: %s"%(fidx,fname)
  f_upr = upr.open(fname)
  t_upr = f_upr['Events']

  evars = {}
  for v in nanoAODVars: evars[v] = t_upr.array(v)
  print "   * File has %g events"%len(evars[nanoAODVars[0]])
  # Loop over events
  for iev in range(0,len(evars[nanoAODVars[0]])):
    if evtCounter == opt.nEvents: continue   
    ev = Event(evars,iev)

    # Fill histograms and add to counters
    hists['genWeight'].Fill(ev.genWeight)
    counters[ev.STXS_stage1p2]['nominal'] += ev.genWeight
    for sw,v in ev.scaleWeights.iteritems(): 
      hists['%s_%s'%(ev.STXS_stage1p2,sw)].Fill(v,ev.genWeight)
      counters[ev.STXS_stage1p2][sw] += v*ev.genWeight

    evtCounter += 1

print " --> Finished processing events."

# Calculate total sum of NNLOPS weights
y_tot = 0
for stxs_bin, svars in counters.iteritems(): y_tot += svars['NNLO_1_1_NLO_1_1']
cross_sections = od()
for stxs_bin, svars in counters.iteritems(): 
  cross_sections[stxs_bin] = od()
  cross_sections[stxs_bin]['nominal'] = (svars['NNLO_1_1_NLO_1_1']/y_tot)*xs['ggH']
  cross_sections[stxs_bin]['muF_0p5_muR_0p5'] = (svars['NNLO_1_1_NLO_0p5_0p5']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['muF_0p5_muR_1p0'] = (svars['NNLO_1_1_NLO_1_0p5']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['muF_1p0_muR_0p5'] = (svars['NNLO_1_1_NLO_0p5_1']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['muF_1p0_muR_2p0'] = (svars['NNLO_1_1_NLO_2_1']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['muF_2p0_muR_1p0'] = (svars['NNLO_1_1_NLO_1_2']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['muF_2p0_muR_2p0'] = (svars['NNLO_1_1_NLO_2_2']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_2p0_muR_2p0'] = (svars['NNLO_2_2_NLO_1_1']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_2p0_muR_2p0_NLO_muF_0p5_muR_0p5'] = (svars['NNLO_2_2_NLO_0p5_0p5']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_2p0_muR_2p0_NLO_muF_0p5_muR_1p0'] = (svars['NNLO_2_2_NLO_1_0p5']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_2p0_muR_2p0_NLO_muF_1p0_muR_0p5'] = (svars['NNLO_2_2_NLO_0p5_1']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_2p0_muR_2p0_NLO_muF_1p0_muR_2p0'] = (svars['NNLO_2_2_NLO_2_1']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_2p0_muR_2p0_NLO_muF_2p0_muR_1p0'] = (svars['NNLO_2_2_NLO_1_2']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_2p0_muR_2p0_NLO_muF_2p0_muR_2p0'] = (svars['NNLO_2_2_NLO_2_2']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_0p5_muR_0p5'] = (svars['NNLO_0p5_0p5_NLO_1_1']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_0p5_muR_0p5_NLO_muF_0p5_muR_0p5'] = (svars['NNLO_0p5_0p5_NLO_0p5_0p5']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_0p5_muR_0p5_NLO_muF_0p5_muR_1p0'] = (svars['NNLO_0p5_0p5_NLO_1_0p5']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_0p5_muR_0p5_NLO_muF_1p0_muR_0p5'] = (svars['NNLO_0p5_0p5_NLO_0p5_1']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_0p5_muR_0p5_NLO_muF_1p0_muR_2p0'] = (svars['NNLO_0p5_0p5_NLO_2_1']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_0p5_muR_0p5_NLO_muF_2p0_muR_1p0'] = (svars['NNLO_0p5_0p5_NLO_1_2']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']
  cross_sections[stxs_bin]['NNLOPS_muF_0p5_muR_0p5_NLO_muF_2p0_muR_2p0'] = (svars['NNLO_0p5_0p5_NLO_2_2']/svars['NNLO_1_1_NLO_1_1'])*cross_sections[stxs_bin]['nominal']


  


hists['GG2H_PTH_200_300_NNLO_1_1_NLO_1_1'].SetLineColor(1)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_1_1'].Draw("HIST")
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_1_0p5'].SetLineColor(2)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_1_2'].SetLineColor(2)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_1_2'].SetLineStyle(2)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_1_0p5'].Draw("HIST SAME")
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_1_2'].Draw("HIST SAME")
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_0p5_1'].SetLineColor(3)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_2_1'].SetLineColor(3)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_2_1'].SetLineStyle(2)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_0p5_1'].Draw("HIST SAME")
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_2_1'].Draw("HIST SAME")
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_0p5_0p5'].SetLineColor(4)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_2_2'].SetLineColor(4)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_2_2'].SetLineStyle(2)
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_0p5_0p5'].Draw("HIST SAME")
hists['GG2H_PTH_200_300_NNLO_1_1_NLO_2_2'].Draw("HIST SAME")

for stxs_bin in STXS_bins:
  if stxs_bin.split("_")[0] == "GG2H":
    tmp_cnt = od()
    for k,v in counters[stxs_bin].iteritems():
      if k == "nominal": continue
      else:
        tmp_cnt[k] = v
    vmin, kmin = np.asarray(tmp_cnt.values()).min(), tmp_cnt.keys()[np.asarray(tmp_cnt.values()).argmin()]
    vmax, kmax = np.asarray(tmp_cnt.values()).max(), tmp_cnt.keys()[np.asarray(tmp_cnt.values()).argmax()]
    vnom = tmp_cnt['NNLO_1_1_NLO_1_1']
    print " * %-45s ::: min = %.2f (%-21s), max = %.2f (%-21s)"%(stxs_bin,vmin/vnom,kmin,vmax/vnom,kmax)

