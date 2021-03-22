import hepdata_lib
from hepdata_lib import Table
from hepdata_lib import Variable
from hepdata_lib import Uncertainty
import numpy as np
import json
from collections import OrderedDict as od
import re

def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
def CopyDataFromJsonFile(jsonfilename='observed.json', model=None, pois=[]):
  res = {}
  with open(jsonfilename) as jsonfile:
    full = json.load(jsonfile)[model]
    for poi in pois: res[poi] = dict(full[poi])
  return res

def make_table():
  params = ['r_ggH', 'r_VBF', 'r_VH', 'r_top']

  # Load results + xsbr data
  inputMode = "mu"
  translatePOIs = LoadTranslations("translate/pois_%s.json"%inputMode)
  with open("/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/OtherScripts/HEPdata/hepdata_lib/hig-19-015/inputs/correlations_mu.json","r") as jf: correlations = json.load(jf)
  with open("/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/OtherScripts/HEPdata/hepdata_lib/hig-19-015/inputs/correlations_expected_mu.json","r") as jf: correlations_exp = json.load(jf)

  # Make table of results
  table = Table("Correlations: production mode signal strength")
  table.description = "Observed and expected correlations between the parameters in the production mode signal strength fit."
  table.location = "Results from additional material"
  table.keywords["reactions"] = ["P P --> H ( --> GAMMA GAMMA ) X"]

  pois_x = Variable("Parameter (x)", is_independent=True, is_binned=False)
  pois_y = Variable("Parameter (y)", is_independent=True, is_binned=False)
  c = Variable("Observed correlation", is_independent=False, is_binned=False)
  c.add_qualifier("SQRT(S)",13,"TeV")
  c.add_qualifier("MH",'125.38',"GeV")
  c_exp = Variable("Expected correlation", is_independent=False, is_binned=False)
  c_exp.add_qualifier("SQRT(S)",13,"TeV")
  c_exp.add_qualifier("MH",'125.38',"GeV")

  poiNames_x = []
  poiNames_y = []
  corr = []
  corr_exp = []
  for ipoi in params: 
    for jpoi in params:
      poiNames_x.append( str(Translate(ipoi,translatePOIs)) ) 
      poiNames_y.append( str(Translate(jpoi,translatePOIs)) ) 
      # Extract correlation coefficient
      corr.append( correlations["%s__%s"%(ipoi,jpoi)] )
      corr_exp.append( correlations_exp["%s__%s"%(ipoi,jpoi)] )
  pois_x.values = poiNames_x
  pois_y.values = poiNames_y
  c.values = np.round(np.array(corr),3)
  c_exp.values = np.round(np.array(corr_exp),3)

  # Add variables to table
  table.add_variable(pois_x)
  table.add_variable(pois_y)
  table.add_variable(c)
  table.add_variable(c_exp)

  # Add figure
  table.add_image("/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/OtherScripts/HEPdata/hepdata_lib/hig-19-015/inputs/perproc_mu_corr.pdf")

  return table
