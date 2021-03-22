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
  params = ['r_ggH_0J_low', 'r_ggH_0J_high', 'r_ggH_1J_low', 'r_ggH_1J_med', 'r_ggH_1J_high', 'r_ggH_2J_low', 'r_ggH_2J_med', 'r_ggH_2J_high', 'r_ggH_VBFlike', 'r_ggH_BSM', 'r_qqH_VBFlike', 'r_qqH_VHhad', 'r_qqH_BSM', 'r_WH_lep', 'r_ZH_lep', 'r_ttH', 'r_tH']

  # Load results + xsbr data
  inputXSBRjson = "/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/flashggFinalFit/Plots/jsons/xsbr_theory_stage1p2_maximal_125p38.json"
  inputExpResultsJson = '/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/flashggFinalFit/Plots/expected_UL_redo.json'
  inputObsResultsJson = '/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/flashggFinalFit/Plots/observed_UL_redo.json'
  inputMode = "stage1p2_maximal"

  translatePOIs = LoadTranslations("translate/pois_%s.json"%inputMode)
  with open(inputXSBRjson,"r") as jsonfile: xsbr_theory = json.load(jsonfile)
  observed = CopyDataFromJsonFile(inputObsResultsJson,inputMode,params)
  expected = CopyDataFromJsonFile(inputExpResultsJson,inputMode,params)
  mh = float(re.sub("p",".",inputXSBRjson.split("_")[-1].split(".json")[0]))

  # Make table of results
  table = Table("STXS stage 1.2 maximal merging scheme")
  table.description = "Results of the maximal merging scheme STXS fit. The best fit cross sections are shown together with the respective 68% C.L. intervals. The uncertainty is decomposed into the systematic and statistical components. The expected uncertainties on the fitted parameters are given in brackets. Also listed are the SM predictions for the cross sections and the theoretical uncertainty in those predictions."
  table.location = "Results from Figure 18 and Table 12"
  table.keywords["reactions"] = ["P P --> H ( --> GAMMA GAMMA ) X"]

  pois = Variable("STXS region", is_independent=True, is_binned=False)
  poiNames = []
  for poi in params: poiNames.append( str(Translate(poi,translatePOIs)) )
  pois.values = poiNames

  # Dependent variables

  # SM predict
  xsbr_sm = Variable("SM predicted cross section times branching ratio", is_independent=False, is_binned=False, units='fb')
  xsbr_sm.add_qualifier("SQRT(S)",13,"TeV")
  xsbr_sm.add_qualifier("ABS(YRAP(HIGGS))",'<2.5')
  xsbr_sm.add_qualifier("MH",'125.38',"GeV")
  theory = Uncertainty("Theory", is_symmetric=False)
  xsbr_vals = []
  xsbr_hi_th, xsbr_lo_th = [], []
  for poi in params:
    xsbr_vals.append(xsbr_theory[poi]['nominal'])
    xsbr_hi_th.append(xsbr_theory[poi]['High01Sigma'])
    xsbr_lo_th.append(-1*abs(xsbr_theory[poi]['Low01Sigma']))
  xsbr_sm.values = np.round(np.array(xsbr_vals),3)
  theory.values = zip( np.round(np.array(xsbr_lo_th),3), np.round(np.array(xsbr_hi_th),3) )
  xsbr_sm.add_uncertainty( theory )

  # Observed cross section
  xsbr = Variable("Observed cross section times branching ratio", is_independent=False, is_binned=False, units='fb')
  xsbr.add_qualifier("SQRT(S)",13,"TeV")
  xsbr.add_qualifier("ABS(YRAP(HIGGS))",'<2.5')
  xsbr.add_qualifier("MH",'125.38',"GeV")
  # Add uncertainties
  tot = Uncertainty("Total", is_symmetric=False)
  stat = Uncertainty("Stat only", is_symmetric=False)
  syst = Uncertainty("Syst", is_symmetric=False)

  xsbr_vals = []
  xsbr_hi_tot, xsbr_lo_tot = [], []
  xsbr_hi_stat, xsbr_lo_stat = [], []
  xsbr_hi_syst, xsbr_lo_syst = [], []
  for poi in params:
    xsbr_vals.append(xsbr_theory[poi]['nominal']*observed[poi]['Val'])
    xsbr_hi_tot.append(abs(xsbr_theory[poi]['nominal']*observed[poi]['ErrorHi']))
    xsbr_lo_tot.append(-1*abs(xsbr_theory[poi]['nominal']*observed[poi]['ErrorLo']))
    xsbr_hi_stat.append(abs(xsbr_theory[poi]['nominal']*observed[poi]['StatHi']))
    xsbr_lo_stat.append(-1*abs(xsbr_theory[poi]['nominal']*observed[poi]['StatLo']))
    xsbr_hi_syst.append(abs(xsbr_theory[poi]['nominal']*observed[poi]['SystHi']))
    xsbr_lo_syst.append(-1*abs(xsbr_theory[poi]['nominal']*observed[poi]['SystLo']))

  tot.values = zip( np.round(np.array(xsbr_lo_tot),3), np.round(np.array(xsbr_hi_tot),3) )
  stat.values = zip( np.round(np.array(xsbr_lo_stat),3), np.round(np.array(xsbr_hi_stat),3) )
  syst.values = zip( np.round(np.array(xsbr_lo_syst),3), np.round(np.array(xsbr_hi_syst),3) )

  xsbr.values = np.round(np.array(xsbr_vals),3)
  xsbr.add_uncertainty(tot)
  xsbr.add_uncertainty(stat)
  xsbr.add_uncertainty(syst)

  # Observed ratio to SM
  xsbrr = Variable("Observed ratio to SM", is_independent=False, is_binned=False, units='')
  xsbrr.add_qualifier("SQRT(S)",13,"TeV")
  xsbrr.add_qualifier("ABS(YRAP(HIGGS))",'<2.5')
  xsbrr.add_qualifier("MH",'125.38',"GeV")
  # Add uncertainties
  totr = Uncertainty("Total", is_symmetric=False)
  statr = Uncertainty("Stat only", is_symmetric=False)
  systr = Uncertainty("Syst", is_symmetric=False)

  xsbr_vals = []
  xsbr_hi_tot, xsbr_lo_tot = [], []
  xsbr_hi_stat, xsbr_lo_stat = [], []
  xsbr_hi_syst, xsbr_lo_syst = [], []
  for poi in params:
    xsbr_vals.append(observed[poi]['Val'])
    xsbr_hi_tot.append(abs(observed[poi]['ErrorHi']))
    xsbr_lo_tot.append(-1*abs(observed[poi]['ErrorLo']))
    xsbr_hi_stat.append(abs(observed[poi]['StatHi']))
    xsbr_lo_stat.append(-1*abs(observed[poi]['StatLo']))
    xsbr_hi_syst.append(abs(observed[poi]['SystHi']))
    xsbr_lo_syst.append(-1*abs(observed[poi]['SystLo']))

  totr.values = zip( np.round(np.array(xsbr_lo_tot),3), np.round(np.array(xsbr_hi_tot),3) )
  statr.values = zip( np.round(np.array(xsbr_lo_stat),3), np.round(np.array(xsbr_hi_stat),3) )
  systr.values = zip( np.round(np.array(xsbr_lo_syst),3), np.round(np.array(xsbr_hi_syst),3) )

  xsbrr.values = np.round(np.array(xsbr_vals),3)
  xsbrr.add_uncertainty(totr)
  xsbrr.add_uncertainty(statr)
  xsbrr.add_uncertainty(systr)


  # Expected cross section
  xsbr_exp = Variable("Expected cross section times branching ratio", is_independent=False, is_binned=False, units='fb')
  xsbr_exp.add_qualifier("SQRT(S)",13,"TeV")
  xsbr_exp.add_qualifier("ABS(YRAP(HIGGS))",'<2.5')
  xsbr_exp.add_qualifier("MH",'125.38',"GeV")
  # Add uncertainties
  tot_exp = Uncertainty("Total", is_symmetric=False)
  stat_exp = Uncertainty("Stat only", is_symmetric=False)
  syst_exp = Uncertainty("Syst", is_symmetric=False)

  xsbr_vals = []
  xsbr_hi_tot, xsbr_lo_tot = [], []
  xsbr_hi_stat, xsbr_lo_stat = [], []
  xsbr_hi_syst, xsbr_lo_syst = [], []
  for poi in params:
    xsbr_vals.append(xsbr_theory[poi]['nominal'])
    xsbr_hi_tot.append(abs(xsbr_theory[poi]['nominal']*expected[poi]['ErrorHi']))
    xsbr_lo_tot.append(-1*abs(xsbr_theory[poi]['nominal']*expected[poi]['ErrorLo']))
    xsbr_hi_stat.append(abs(xsbr_theory[poi]['nominal']*expected[poi]['StatHi']))
    xsbr_lo_stat.append(-1*abs(xsbr_theory[poi]['nominal']*expected[poi]['StatLo']))
    xsbr_hi_syst.append(abs(xsbr_theory[poi]['nominal']*expected[poi]['SystHi']))
    xsbr_lo_syst.append(-1*abs(xsbr_theory[poi]['nominal']*expected[poi]['SystLo']))

  tot_exp.values = zip( np.round(np.array(xsbr_lo_tot),3), np.round(np.array(xsbr_hi_tot),3) )
  stat_exp.values = zip( np.round(np.array(xsbr_lo_stat),3), np.round(np.array(xsbr_hi_stat),3) )
  syst_exp.values = zip( np.round(np.array(xsbr_lo_syst),3), np.round(np.array(xsbr_hi_syst),3) )

  xsbr_exp.values = np.round(np.array(xsbr_vals),3)
  xsbr_exp.add_uncertainty(tot_exp)
  xsbr_exp.add_uncertainty(stat_exp)
  xsbr_exp.add_uncertainty(syst_exp)

  # Expected ratio to SM
  xsbrr_exp = Variable("Expected ratio to SM", is_independent=False, is_binned=False, units='')
  xsbrr_exp.add_qualifier("SQRT(S)",13,"TeV")
  xsbrr_exp.add_qualifier("ABS(YRAP(HIGGS))",'<2.5')
  xsbrr_exp.add_qualifier("MH",'125.38',"GeV")
  # Add uncertainties
  totr_exp = Uncertainty("Total", is_symmetric=False)
  statr_exp = Uncertainty("Stat only", is_symmetric=False)
  systr_exp = Uncertainty("Syst", is_symmetric=False)

  xsbr_vals = []
  xsbr_hi_tot, xsbr_lo_tot = [], []
  xsbr_hi_stat, xsbr_lo_stat = [], []
  xsbr_hi_syst, xsbr_lo_syst = [], []
  for poi in params:
    xsbr_vals.append(1.00)
    xsbr_hi_tot.append(abs(expected[poi]['ErrorHi']))
    xsbr_lo_tot.append(-1*abs(expected[poi]['ErrorLo']))
    xsbr_hi_stat.append(abs(expected[poi]['StatHi']))
    xsbr_lo_stat.append(-1*abs(expected[poi]['StatLo']))
    xsbr_hi_syst.append(abs(expected[poi]['SystHi']))
    xsbr_lo_syst.append(-1*abs(expected[poi]['SystLo']))

  totr_exp.values = zip( np.round(np.array(xsbr_lo_tot),3), np.round(np.array(xsbr_hi_tot),3) )
  statr_exp.values = zip( np.round(np.array(xsbr_lo_stat),3), np.round(np.array(xsbr_hi_stat),3) )
  systr_exp.values = zip( np.round(np.array(xsbr_lo_syst),3), np.round(np.array(xsbr_hi_syst),3) )

  xsbrr_exp.values = np.round(np.array(xsbr_vals),3)
  xsbrr_exp.add_uncertainty(totr_exp)
  xsbrr_exp.add_uncertainty(statr_exp)
  xsbrr_exp.add_uncertainty(systr_exp)

  # Add variables to table
  table.add_variable(pois)
  table.add_variable(xsbr_sm)
  table.add_variable(xsbr)
  table.add_variable(xsbrr)
  table.add_variable(xsbr_exp)
  table.add_variable(xsbrr_exp)


  # Add figure
  table.add_image("/afs/cern.ch/work/j/jlangfor/hgg/legacy/FinalFits/UL/Dec20/CMSSW_10_2_13/src/OtherScripts/HEPdata/hepdata_lib/hig-19-015/inputs/stxs_dist_stage1p2_maximal.pdf")

  return table
