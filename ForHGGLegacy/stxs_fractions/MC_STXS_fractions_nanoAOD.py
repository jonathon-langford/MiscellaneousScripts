# Script to extract MC fractions directly from NANOAOD
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
from STXS import STXS_bins, STXS_stage0, formatSTXS

def get_options():
  parser = OptionParser()
  parser.add_option("--inputJson", dest="inputJson", default='datasets.json', help="Input json storing dataset names")
  parser.add_option("--productionMode", dest="productionMode", default=None, help="Production Mode")
  parser.add_option("--years", dest="years", default='2016,2017,2018', help="Year")
  parser.add_option("--generators", dest="generators", default=None, help="MC generators (comma separated list)")
  parser.add_option("--ext", dest="ext", default='', help="Additional extension to process")
  parser.add_option("--doNNLOPS", dest="doNNLOPS", default=False, action="store_true", help="Do NNLOPS reweighting for ggH")
  return parser.parse_args()
(opt,args) = get_options()

def convert_to_1p2(_1p1,_pt):
  if _1p1 == 101:
    if _pt < 300.: return 101
    elif _pt < 450.: return 102
    elif _pt < 650.: return 103
    else: return 104
  elif( _1p1 >= 102 )&( _1p1 < 190 ): return _1p1+3
  elif _1p1 == 601:
    if _pt < 60: return 601
    elif _pt < 120: return 602
    elif _pt < 200: return 603
    elif _pt < 300: return 604
    else: return 605
  else: return _1p1

def NNLOPS_rwgt(_nnlopsweights,_genweight,_njets,_pt):
  if _njets == 0: return _genweight*_nnlopsweights[0].Eval(min(_pt,125.0))
  elif _njets == 1: return _genweight*_nnlopsweights[1].Eval(min(_pt,625.0))
  elif _njets == 2: return _genweight*_nnlopsweights[2].Eval(min(_pt,800.0))
  elif _njets >= 3: return _genweight*_nnlopsweights[3].Eval(min(_pt,925.0))
  else: return _genweight

pmSplit = od()
pmSplit['ggH'] = ['ggH']
pmSplit['ggZH_qq'] = ['ggZH_qq']
pmSplit['VBF'] = ['VBF']
pmSplit['VH'] = ['VH_had','WH_lep','ZH_lep']
pmSplit['ggZH_ll'] = ['ggZH_ll']
pmSplit['ggZH_nunu'] = ['ggZH_nunu']
pmSplit['ttH'] = ['ttH']
pmSplit['bbH'] = ['bbH']
pmSplit['tHq'] = ['tHq']
pmSplit['tHW'] = ['tHW']

Stage0Identifier = od()
Stage0Identifier['ggH'] = 'GG2H'
Stage0Identifier['ggZH_qq'] = 'GG2H'
Stage0Identifier['VBF'] = 'QQ2HQQ'
Stage0Identifier['VH_had'] = 'QQ2HQQ'
Stage0Identifier['WH_lep'] = 'QQ2HLNU'
Stage0Identifier['ZH_lep'] = 'QQ2HLL'
Stage0Identifier['ggZH_ll'] = 'GG2HLL'
Stage0Identifier['ggZH_nunu'] = 'GG2HLL'
Stage0Identifier['ttH'] = 'TTH'
Stage0Identifier['bbH'] = 'BBH'
Stage0Identifier['tHq'] = 'TH'
Stage0Identifier['tHW'] = 'TH'

# Loads NNLOPS weights
f_NNLOPS = ROOT.TFile("NNLOPS_reweight.root")
NNLOPSWeights_amcatnlo, NNLOPSWeights_powheg = [], [] 
NNLOPSWeights_amcatnlo.append(f_NNLOPS.Get("gr_NNLOPSratio_pt_mcatnlo_0jet"))
NNLOPSWeights_amcatnlo.append(f_NNLOPS.Get("gr_NNLOPSratio_pt_mcatnlo_1jet"))
NNLOPSWeights_amcatnlo.append(f_NNLOPS.Get("gr_NNLOPSratio_pt_mcatnlo_2jet"))
NNLOPSWeights_amcatnlo.append(f_NNLOPS.Get("gr_NNLOPSratio_pt_mcatnlo_3jet"))
NNLOPSWeights_powheg.append(f_NNLOPS.Get("gr_NNLOPSratio_pt_powheg_0jet"))
NNLOPSWeights_powheg.append(f_NNLOPS.Get("gr_NNLOPSratio_pt_powheg_1jet"))
NNLOPSWeights_powheg.append(f_NNLOPS.Get("gr_NNLOPSratio_pt_powheg_2jet"))
NNLOPSWeights_powheg.append(f_NNLOPS.Get("gr_NNLOPSratio_pt_powheg_3jet"))

# Load data samples from json
with open(opt.inputJson) as jsonfile: samples = json.load(jsonfile)

# Open file to write table to
if not os.path.isdir("./fractions"): os.system("mkdir fractions")
filesout = {}
bins = {}
for pm in pmSplit[opt.productionMode]:
  filesout[pm] = open("./fractions/%s.txt"%pm,"w")
  # Extract bins
  bins[pm] = []
  for b in STXS_bins:
    if(b.split("_")[0] == Stage0Identifier[pm]): bins[pm].append(b)
  tabProp = "|"+"c|"*(len(bins[pm])+1)
  tabColumns = "Sample"
  #for b in bins[pm]: tabColumns += " & %s"%formatSTXS(b)
  for b in bins[pm]: tabColumns += " & %s"%STXS_bins[b]
  # Add preamble
  filesout[pm].write("\\begin{table}[htb]\n")
  filesout[pm].write("    \\centering\n")
  filesout[pm].write("    \\footnotesize\n")
  filesout[pm].write("    \\begin{tabular}{%s}\n"%tabProp)
  filesout[pm].write("        \\hline\n")
  filesout[pm].write("        %s \\\\ \\hline\n"%tabColumns)
  
for gen in opt.generators.split(","):
  for year in opt.years.split(","):
    proc = "%s_%s_%s%s"%(opt.productionMode,year,gen,opt.ext)
    das_sample = samples[proc]
    if das_sample == "NA":
      print " --> (%s,%s,%s): Sample not available"%(opt.productionMode,year,gen)
      # Add column to table
      for pm in pmSplit[opt.productionMode]:
        if gen == "mg": sampleColumns = 'amc@NLO (%s)'%year
        else: sampleColumns = 'POWHEG (%s)'%year
        for b in bins[pm]: sampleColumns += " & -"
        filesout[pm].write("        %s \\\\ \\hline\n"%sampleColumns)
    else:
      # Create list of files from datasample
      files = []
      for fdata in das_query("file dataset=%s"%das_sample, cmd="dasgoclient --dasmaps=./")['data']: files.append("root://cms-xrd-global.cern.ch/%s"%fdata['file'][0]['name'])

      # Create list of dataframes
      frs = []
      _vars = ['genWeight','HTXS_stage_0','HTXS_stage1_1_cat_pTjet30GeV','HTXS_Higgs_pt','HTXS_njets30']
      for fname in files:
	f_upr = upr.open(fname)
	t = f_upr['Events']
	frs.append( t.pandas.df(_vars) )
      fr = pd.concat( frs, sort=False )
      # Add 1.2 bins
      fr['HTXS_stage1_2_cat_pTjet30GeV'] = fr.apply(lambda x: convert_to_1p2(x['HTXS_stage1_1_cat_pTjet30GeV'],x['HTXS_Higgs_pt']), axis=1)
      # If production mode is ggH, add NNLOPS reweighting
      if(opt.doNNLOPS)&(opt.productionMode == 'ggH'):
        if gen == "mg": fr['genWeight_NNLOPS'] = fr.apply(lambda x: NNLOPS_rwgt(NNLOPSWeights_amcatnlo,x['genWeight'],x['HTXS_njets30'],x['HTXS_Higgs_pt']), axis=1)
        elif gen == "powheg": fr['genWeight_NNLOPS'] = fr.apply(lambda x: NNLOPS_rwgt(NNLOPSWeights_powheg,x['genWeight'],x['HTXS_njets30'],x['HTXS_Higgs_pt']), axis=1)
        else: 
          print " [ERROR] gen %s not supported for NNLOPS reweighting"%gen
          sys.exit(1)
        weightVar = "genWeight_NNLOPS"
      else: weightVar = "genWeight"

      # Calculate fractions
      for pm in pmSplit[opt.productionMode]:
	print " --> (%s,%s,%s)"%(pm,year,gen)
	for b,v in STXS_bins.iteritems():
	  if(b.split("_")[0] != Stage0Identifier[pm]): continue
	  pc = 100*(fr[fr['HTXS_stage1_2_cat_pTjet30GeV']==v][weightVar].sum()/fr[fr['HTXS_stage_0'].isin(STXS_stage0[pm])][weightVar].sum())
	  if pc != 0.: print " %s = %.2f%%"%(b,pc)
	print "\n"

      # Add column to table
      for pm in pmSplit[opt.productionMode]:
        if gen == "mg": sampleColumns = 'amc@NLO (%s)'%year
        else: sampleColumns = 'POWHEG (%s)'%year
        for b in bins[pm]: 
          pc = 100*(fr[fr['HTXS_stage1_2_cat_pTjet30GeV']==STXS_bins[b]][weightVar].sum()/fr[fr['HTXS_stage_0'].isin(STXS_stage0[pm])][weightVar].sum())
          sampleColumns += " & %.2f\\%%"%pc
        filesout[pm].write("        %s \\\\ \\hline\n"%sampleColumns)

      # Delete dataframe
      del(fr)

# Add postamble and close file
for pm in pmSplit[opt.productionMode]:
  filesout[pm].write("    \\end{tabular}\n")
  filesout[pm].write("\\end{table}\n")

  # Add key table
  filesout[pm].write("\n\n")
  filesout[pm].write("\\begin{table}[htb]\n")
  filesout[pm].write("    \\centering\n")
  filesout[pm].write("    \\footnotesize\n")
  filesout[pm].write("    \\begin{tabular}{|c|c|}\n")
  filesout[pm].write("        \\hline\n")
  filesout[pm].write("        Key & STXS bin (%s) \\\\ \\hline\n"%Stage0Identifier[pm])
  for b in bins[pm]: filesout[pm].write("        %s & %s \\\\ \\hline\n"%(STXS_bins[b],formatSTXS(b)))
  filesout[pm].write("    \\end{tabular}\n")
  filesout[pm].write("\\end{table}\n")
  filesout[pm].close()
