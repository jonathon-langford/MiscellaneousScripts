import re,sys
import ROOT
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--input", dest="fInput", default="",  type="string", help="Input file")
(options, args) = parser.parse_args()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

class W:
  def __init__(self,fileName,wName="wsig_13TeV",mName="ModelConfig"):
    print "Initialising workspace..."
    self.file = ROOT.TFile.Open(fileName)
    print "  --> Opened file: %s"%fileName
    self.ws = self.file.Get(wName)
    print "  --> Retrieved workspace: %s"%wName
    self.allVars = {}
    self.allFunctions = {}
    self.allPdfs = {}
    for _var in rooiter(self.ws.allVars()): self.allVars[_var.GetName()] = _var
    for _func in rooiter(self.ws.allFunctions()): self.allFunctions[_func.GetName()] = _func
    for _pdf in rooiter(self.ws.allPdfs()): self.allPdfs[_pdf.GetName()] = _pdf
    self.allData = self.ws.allData()

    #define output workspce
    self.wsout = ROOT.RooWorkspace("wsig_13TeV","wsig_13TeV")
    #For importing into output ws
    self.wsout.imp = getattr(self.wsout,"import")

    #Import the ZZ e scale nuisance into output workspace
    zz_escale_var = ROOT.RooRealVar("CMS_zz4l_mean_e_sig","CMS_zz4l_mean_e_sig",0.,-5.,5.)
    zz_escale_var.setConstant()
    self.wsout.imp( zz_escale_var, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )
    
    #Re-define CMS_hgg_nuisance_NonLinearity_13TeVscale as RooFormulaVar and import to workspace
    self.formula = ROOT.RooFormulaVar("CMS_hgg_nuisance_NonLinearity_13TeVscale","","0.00075*@0",ROOT.RooArgList(self.wsout.arg("CMS_zz4l_mean_e_sig")))
    self.wsout.imp(self.formula, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )

    #Import all components except NonLinearity
    for _varName, _var in self.allVars.iteritems(): 
      if "NonLinearity" in _varName: continue
      else: self.wsout.imp(_var, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )
    for _funcName, _func in self.allFunctions.iteritems(): 
      if "NonLinearity" in _funcName: continue
      else: self.wsout.imp(_func, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )
    for _pdf in self.allPdfs.itervalues(): self.wsout.imp(_pdf, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )
    for _data in self.allData: self.wsout.imp(_data)
 
#Instantiate class W: reads input ws and creates output ws with modified NonLinearity
combinedWS = W("input_hgg_sig/%s"%options.fInput)
#Write output workspace to file
combinedWS.wsout.writeToFile("output_hgg_sig/%s"%options.fInput)
