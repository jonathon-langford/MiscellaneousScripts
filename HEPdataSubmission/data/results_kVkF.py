import hepdata_lib
from hepdata_lib import Table
from hepdata_lib import Variable
from hepdata_lib import Uncertainty
import numpy as np
import json
from collections import OrderedDict as od
import re
import ROOT

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

  xparam = 'kappa_V'
  yparam = 'kappa_F'

  # Load results + xsbr data
  inputMode = "kappas"
  translatePOIs = LoadTranslations("translate/pois_%s.json"%inputMode)

  # Extract observed results
  fobs = "/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/flashggFinalFit/Combine/runFits_UL_redo_kVkF/output_scan2D_syst_fixedMH_v2_obs_kappa_V_vs_kappa_F.root"
  f_in = ROOT.TFile(fobs)
  t_in = f_in.Get("limit")
  xvals, yvals, deltaNLL = [], [], []
  ev_idx = 0
  for ev in t_in:
    xvals.append( getattr(ev,xparam) )
    yvals.append( getattr(ev,yparam) )
    deltaNLL.append( getattr(ev,"deltaNLL") )

  # Convert to numpy arrays as required for interpolation
  x = np.asarray(xvals)
  y = np.asarray(yvals)
  dnll = np.asarray(deltaNLL)
  v = 2*(deltaNLL-np.min(deltaNLL))

  # Make table of results
  table = Table("Kappas 2D: vector boson and fermion")
  table.description = "Observed likelihood surface."
  table.location = "Results from Figure 22"
  table.keywords["reactions"] = ["P P --> H ( --> GAMMA GAMMA ) X"]

  pois_x = Variable(str(Translate(xparam,translatePOIs)), is_independent=True, is_binned=False)
  pois_y = Variable(str(Translate(yparam,translatePOIs)), is_independent=True, is_binned=False)
  q = Variable("Observed -2$\\Delta$NLL", is_independent=False, is_binned=False)
  q.add_qualifier("SQRT(S)",13,"TeV")
  q.add_qualifier("MH",'125.38',"GeV")

  pois_x.values = x
  pois_y.values = y
  q.values = np.round(np.array(v),2)

  # Add variables to table
  table.add_variable(pois_x)
  table.add_variable(pois_y)
  table.add_variable(q)

  # Add figure
  table.add_image("/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/OtherScripts/HEPdata/hepdata_lib/hig-19-015/inputs/scan2D_syst_obs_kappa_V_vs_kappa_F.pdf")

  return table
