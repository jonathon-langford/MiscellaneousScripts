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
  params = ['r_ggH', 'r_VBF', 'r_VH', 'r_top', 'r_inclusive']

  # Load results + xsbr data
  inputExpResultsJson = '/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/flashggFinalFit/Plots/expected_UL_redo.json'
  inputObsResultsJson = '/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/flashggFinalFit/Plots/observed_UL_redo.json'
  inputMode = "mu"

  translatePOIs = LoadTranslations("translate/pois_%s.json"%inputMode)
  observed = CopyDataFromJsonFile(inputObsResultsJson,inputMode,params)
  expected = CopyDataFromJsonFile(inputExpResultsJson,inputMode,params)

  # Make table of results
  table = Table("Signal strengths")
  table.description = "Best-fit values and 68% confidence intervals for the signal strength modifiers. The uncertainty is decomposed ino the theoretical systematic, experimental systematic and statistical components. Additionally, the expected uncertainties derived using an asimov dataset are provided."
  table.location = "Results from Figure 16"
  table.keywords["reactions"] = ["P P --> H ( --> GAMMA GAMMA ) X"]

  pois = Variable("Parameter", is_independent=True, is_binned=False)
  poiNames = []
  for poi in params: poiNames.append( str(Translate(poi,translatePOIs)) )
  pois.values = poiNames

  # Dependent variables

  # Observed values
  obs = Variable("Observed", is_independent=False, is_binned=False, units='')
  obs.add_qualifier("SQRT(S)",13,"TeV")
  obs.add_qualifier("MH",'125.38',"GeV")
  # Add uncertainties
  tot = Uncertainty("Total", is_symmetric=False)
  th = Uncertainty("Th. syst", is_symmetric=False)
  exp = Uncertainty("Exp. syst", is_symmetric=False)
  stat = Uncertainty("Stat only", is_symmetric=False)

  vals = []
  hi_tot, lo_tot = [], []
  hi_th, lo_th = [], []
  hi_exp, lo_exp = [], []
  hi_stat, lo_stat = [], []
  for poi in params:
    vals.append(observed[poi]['Val'])
    hi_tot.append(abs(observed[poi]['ErrorHi']))
    lo_tot.append(-1*abs(observed[poi]['ErrorLo']))
    hi_th.append(abs(observed[poi]['TheoryHi']))
    lo_th.append(-1*abs(observed[poi]['TheoryLo']))
    hi_exp.append(abs(observed[poi]['SystHi']))
    lo_exp.append(-1*abs(observed[poi]['SystLo']))
    hi_stat.append(abs(observed[poi]['StatHi']))
    lo_stat.append(-1*abs(observed[poi]['StatLo']))

  tot.values = zip( np.round(np.array(lo_tot),3), np.round(np.array(hi_tot),3) )
  th.values = zip( np.round(np.array(lo_th),3), np.round(np.array(hi_th),3) )
  exp.values = zip( np.round(np.array(lo_exp),3), np.round(np.array(hi_exp),3) )
  stat.values = zip( np.round(np.array(lo_stat),3), np.round(np.array(hi_stat),3) )

  obs.values = np.round(np.array(vals),3)
  obs.add_uncertainty(tot)
  obs.add_uncertainty(th)
  obs.add_uncertainty(exp)
  obs.add_uncertainty(stat)

  # Expected values
  ex = Variable("Expected", is_independent=False, is_binned=False, units='')
  ex.add_qualifier("SQRT(S)",13,"TeV")
  ex.add_qualifier("MH",'125.38',"GeV")
  # Add uncertainties
  etot = Uncertainty("Total", is_symmetric=False)
  eth = Uncertainty("Th. syst", is_symmetric=False)
  eexp = Uncertainty("Exp. syst", is_symmetric=False)
  estat = Uncertainty("Stat only", is_symmetric=False)

  vals = []
  hi_tot, lo_tot = [], []
  hi_th, lo_th = [], []
  hi_exp, lo_exp = [], []
  hi_stat, lo_stat = [], []
  for poi in params:
    vals.append(1.00)
    hi_tot.append(abs(expected[poi]['ErrorHi']))
    lo_tot.append(-1*abs(expected[poi]['ErrorLo']))
    hi_th.append(abs(expected[poi]['TheoryHi']))
    lo_th.append(-1*abs(expected[poi]['TheoryLo']))
    hi_exp.append(abs(expected[poi]['SystHi']))
    lo_exp.append(-1*abs(expected[poi]['SystLo']))
    hi_stat.append(abs(expected[poi]['StatHi']))
    lo_stat.append(-1*abs(expected[poi]['StatLo']))

  etot.values = zip( np.round(np.array(lo_tot),3), np.round(np.array(hi_tot),3) )
  eth.values = zip( np.round(np.array(lo_th),3), np.round(np.array(hi_th),3) )
  eexp.values = zip( np.round(np.array(lo_exp),3), np.round(np.array(hi_exp),3) )
  estat.values = zip( np.round(np.array(lo_stat),3), np.round(np.array(hi_stat),3) )

  ex.values = np.round(np.array(vals),3)
  ex.add_uncertainty(etot)
  ex.add_uncertainty(eth)
  ex.add_uncertainty(eexp)
  ex.add_uncertainty(estat)

  # Add variables to table
  table.add_variable(pois)
  table.add_variable(obs)
  table.add_variable(ex)

  # Add figure
  table.add_image("/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/OtherScripts/HEPdata/hepdata_lib/hig-19-015/inputs/perproc_mu_coloured.pdf")

  return table
