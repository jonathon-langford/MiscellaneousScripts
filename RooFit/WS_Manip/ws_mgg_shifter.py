import ROOT
import re
from optparse import OptionParser
import os, sys

parser = OptionParser()
parser.add_option("--inputFile", dest="inputFile", default="/vols/cms/es811/FinalFits/ws_ReweighAndNewggHweights/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_GG2H.root", help="Input file")
parser.add_option("--inputMass", dest="inputMass", default=125, type='int', help="Input mass")
parser.add_option("--targetMass", dest="targetMass", default=130, type='int', help="Target mass")
(opt,args) = parser.parse_args()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

if not os.path.exists( opt.inputFile ): 
  print " --> [ERROR] input file %s does not exist. Leaving..."%(opt.inputFile)
  sys.exit(1)

if str(opt.inputMass) not in opt.inputFile: 
  print " --> [ERROR] input file %s does not correspond to input mass (%s). Leaving..."%(opt.inputFile,str(opt.inputMass))
  
# Extract input file and workspace
f = ROOT.TFile( opt.inputFile )
ws = f.Get("tagsDumper/cms_hgg_13TeV")

# Define output workspace + workaround for importing in pyroot
wsout = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
wsout.imp = getattr(wsout,"import")

# Import all vars from original ws
allVars = {}
for _var in rooiter(ws.allVars()): allVars[_var.GetName()] = _var
for _varName, _var in allVars.iteritems():  
  wsout.imp(_var, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )

#allFunctions = {}
#for _func in rooiter(ws.allFunctions()): allFunctions[_func.GetName()] = _func
#for _funcName, _func in allFunctions.iteritems(): 
#  wsout.imp(_func, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )
#allPdfs = {}
#for _pdf in rooiter(ws.allPdfs()): allPdfs[_pdf.GetName()] = _pdf
#for _pdf in allPdfs.itervalues(): 
#  wsout.imp(_pdf, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )

# Extract datasets from original workspace
allData = ws.allData()

# Loop over datasets and define new shifted datasets
shifted_datasets = {}
weight = ROOT.RooRealVar("weight","weight",-100000,1000000)
for d_orig in allData:

  # Extract names of original an shifted datasets
  n_orig = d_orig.GetName()
  n_shift = re.sub(str(opt.inputMass),str(opt.targetMass),n_orig)

  print "%s --> %s"%(n_orig,n_shift)

  # Create an empty clone of original dataset
  shifted_datasets[n_shift] = d_shift = d_orig.emptyClone( n_shift )

  # Loop over entries in original dataset
  for i in range(d_orig.numEntries()):

    # Clone datapoint, shift mass and add to new shifted dataset
    p = d_orig.get(i).Clone()
    shift = float(opt.inputMass-opt.targetMass)
    p.setRealValue("CMS_hgg_mass", (d_orig.get(i).getRealValue("CMS_hgg_mass")-shift) )

    # Extract weight
    weight.setVal(d_orig.weight())

    # Add shifted dataset to dictionary
    shifted_datasets[n_shift].add(p,weight.getVal())

# Import all shifted datasets to output ws
for d_shift in shifted_datasets.itervalues(): wsout.imp( d_shift, ROOT.RooFit.RecycleConflictNodes() )

# Configure output file and write output ws
if not os.path.isdir("./shifted_ws"): os.system("mkdir ./shifted_ws")
fout_name = re.sub( str(opt.inputMass), str(opt.targetMass), opt.inputFile.split("/")[-1] )
fout = ROOT.TFile.Open("./shifted_ws/%s"%fout_name, "RECREATE")
dir_ws = fout.mkdir("tagsDumper")
dir_ws.cd()
wsout.Write()

