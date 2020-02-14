import ROOT
import re
from optparse import OptionParser
import os, sys

# Categories to separate
catsToSeparate = []

#catsToSeparate = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_PTH_200_300', 'RECO_PTH_300_450', 'RECO_PTH_450_650', 'RECO_PTH_GT650', 'RECO_THQ_LEP']

#catsToDrop = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_PTH_200_300', 'RECO_PTH_300_450', 'RECO_PTH_450_650', 'RECO_PTH_GT650', 'RECO_THQ_LEP']

catsToDrop = ['RECO_TTH_HAD_HIGH_Tag0', 'RECO_TTH_HAD_HIGH_Tag1', 'RECO_TTH_HAD_HIGH_Tag2', 'RECO_TTH_HAD_HIGH_Tag3', 'RECO_TTH_HAD_LOW_Tag0', 'RECO_TTH_HAD_LOW_Tag1', 'RECO_TTH_HAD_LOW_Tag2', 'RECO_TTH_HAD_LOW_Tag3', 'RECO_TTH_LEP_HIGH_Tag0', 'RECO_TTH_LEP_HIGH_Tag1', 'RECO_TTH_LEP_HIGH_Tag2', 'RECO_TTH_LEP_HIGH_Tag3', 'RECO_TTH_LEP_LOW_Tag0', 'RECO_TTH_LEP_LOW_Tag1', 'RECO_TTH_LEP_LOW_Tag2', 'RECO_TTH_LEP_LOW_Tag3', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_ZH_LEP']

parser = OptionParser()
parser.add_option("--inputFile", dest="inputFile", default="allData", help="Input file")
parser.add_option("--year", dest="year", default="2016", help="Dataset year")
(opt,args) = parser.parse_args()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

# Extract input file and ws
inputFile = "./%s_%s.root"%(opt.inputFile,opt.year)
if not os.path.exists( inputFile ): 
  print " --> [ERROR] input file %s does not exist. Leaving..."%inputFile
  sys.exit(1)
f = ROOT.TFile( inputFile )
ws = f.Get("tagsDumper/cms_hgg_13TeV")

# Define output workspace + workaround for importing in pyroot
wsout = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
wsout.imp = getattr(wsout,"import")

# Import all vars from original ws
allVars = {}
for _var in rooiter(ws.allVars()): allVars[_var.GetName()] = _var
for _varName, _var in allVars.iteritems(): 
  wsout.imp(_var, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )

# Extract datasets from original workspace
allData = ws.allData()
# Loop over datasets: if in catsToSeparate then make clone and change name, else clone with same name
for d in allData:
  dcat = re.sub("Data_13TeV_","",d.GetName())
  if dcat in catsToDrop: continue
  if dcat in catsToSeparate: dclone = d.Clone( "%s_%s"%(d.GetName(),opt.year) )
  else: dclone = d.Clone()
  # Add cloned dataset to output ws
  wsout.imp( dclone, ROOT.RooFit.RecycleConflictNodes() )

# Configure output file and write output ws
fout = ROOT.TFile.Open( "./%s_%s_manip.root"%(opt.inputFile,opt.year), "RECREATE")
dir_ws = fout.mkdir("tagsDumper")
dir_ws.cd()
wsout.Write()
