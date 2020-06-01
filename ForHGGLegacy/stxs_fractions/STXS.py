from collections import OrderedDict as od
import re

def formatSTXS(s):
  if "_" not in s: return s
  s = "_".join(s.split("_")[1:])
  s_format = ''
  # Jet multiplicity
  if 'FWDH' in s:
    s_format += " FWDH, "
    s = re.sub("_FWDH","",s)
  if 'GE2J' in s:
    s_format += " $\geq$2J, "
    s = re.sub("_GE2J","",s)
    s = re.sub("GE2J_","",s)
  elif 'GE1J' in s:
    s_format += " $\geq$1J, "
    s = re.sub("_GE1J","",s)
    s = re.sub("GE1J_","",s)
  elif '1J' in s:
    s_format += " 1J, "
    s = re.sub("_1J","",s)
    s = re.sub("1J_","",s)
  elif '0J' in s:
    s_format += " 0J, "
    s = re.sub("_0J","",s)
    s = re.sub("0J_","",s)
  #Split up remaining iters
  s = s.split("_")
  kin2latex = {"PTV":"p_{\\text{T}}^{\\rm{V}}","PTH":"p_{\\text{T}}^{\\rm{H}}","MJJ":"m_{jj}","PTHJJ":"p_{\\text{T}}^{\\rm{H}jj}"}
  for kinematic in ['PTV','PTH','MJJ','PTHJJ']:
    if kinematic in s:
      kin_idx = s.index(kinematic)
      if "GT" in s[kin_idx+1]: 
	v = re.sub("GT","",s[kin_idx+1])
	s_format += "$%s \\geq %s$, "%(kin2latex[kinematic],v)
      else:
	lv = s[kin_idx+1]
	hv = s[kin_idx+2]
	if lv == "0": s_format += "$%s < %s$, "%(kin2latex[kinematic],hv)
	else: s_format += "%s~$\\leq %s < %s$, "%(lv,kin2latex[kinematic],hv)
  if s_format[-2:] == ", ": s_format = s_format[:-2]
  return s_format

STXS_stage0 = od()
STXS_stage0['ggH'] = [0,10,11]
STXS_stage0['ggZH_qq'] = [0,10,11]
STXS_stage0['VBF'] = [0,20,21]
STXS_stage0['VH_had'] = [0,22,23]
STXS_stage0['WH_lep'] = [0,30,31]
STXS_stage0['ZH_lep'] = [0,40,41]
STXS_stage0['ggZH_ll'] = [0,50,51]
STXS_stage0['ggZH_nunu'] = [0,50,51]
STXS_stage0['ttH'] = [0,60,61]
STXS_stage0['bbH'] = [0,70,71]
STXS_stage0['tHq'] = [0,80,81]
STXS_stage0['tHW'] = [0,80,81]

STXS_bins = od()
STXS_bins["UNKNOWN"] = 0
STXS_bins["GG2H_FWDH"] = 100
STXS_bins["GG2H_PTH_200_300"] = 101
STXS_bins["GG2H_PTH_300_450"] = 102
STXS_bins["GG2H_PTH_450_650"] = 103
STXS_bins["GG2H_PTH_GT650"] = 104
STXS_bins["GG2H_0J_PTH_0_10"] = 105
STXS_bins["GG2H_0J_PTH_GT10"] = 106
STXS_bins["GG2H_1J_PTH_0_60"] = 107
STXS_bins["GG2H_1J_PTH_60_120"] = 108
STXS_bins["GG2H_1J_PTH_120_200"] = 109
STXS_bins["GG2H_GE2J_MJJ_0_350_PTH_0_60"] = 110
STXS_bins["GG2H_GE2J_MJJ_0_350_PTH_60_120"] = 111
STXS_bins["GG2H_GE2J_MJJ_0_350_PTH_120_200"] = 112
STXS_bins["GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 113
STXS_bins["GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 114
STXS_bins["GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 115
STXS_bins["GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 116
STXS_bins["QQ2HQQ_FWDH"] = 200
STXS_bins["QQ2HQQ_0J"] = 201
STXS_bins["QQ2HQQ_1J"] = 202
STXS_bins["QQ2HQQ_GE2J_MJJ_0_60"] = 203
STXS_bins["QQ2HQQ_GE2J_MJJ_60_120"] = 204
STXS_bins["QQ2HQQ_GE2J_MJJ_120_350"] = 205
STXS_bins["QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200"] = 206
STXS_bins["QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 207
STXS_bins["QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 208
STXS_bins["QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 209
STXS_bins["QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 210
STXS_bins["QQ2HLNU_FWDH"] = 300
STXS_bins["QQ2HLNU_PTV_0_75"] = 301
STXS_bins["QQ2HLNU_PTV_75_150"] = 302
STXS_bins["QQ2HLNU_PTV_150_250_0J"] = 303
STXS_bins["QQ2HLNU_PTV_150_250_GE1J"] = 304
STXS_bins["QQ2HLNU_PTV_GT250"] = 305
STXS_bins["QQ2HLL_FWDH"] = 400
STXS_bins["QQ2HLL_PTV_0_75"] = 401
STXS_bins["QQ2HLL_PTV_75_150"] = 402
STXS_bins["QQ2HLL_PTV_150_250_0J"] = 403
STXS_bins["QQ2HLL_PTV_150_250_GE1J"] = 404
STXS_bins["QQ2HLL_PTV_GT250"] = 405
STXS_bins["GG2HLL_FWDH"] = 500
STXS_bins["GG2HLL_PTV_0_75"] = 501
STXS_bins["GG2HLL_PTV_75_150"] = 502
STXS_bins["GG2HLL_PTV_150_250_0J"] = 503
STXS_bins["GG2HLL_PTV_150_250_GE1J"] = 504
STXS_bins["GG2HLL_PTV_GT250"] = 505
STXS_bins["TTH_FWDH"] = 600
STXS_bins["TTH_PTH_0_60"] = 601
STXS_bins["TTH_PTH_60_120"] = 602
STXS_bins["TTH_PTH_120_200"] = 603
STXS_bins["TTH_PTH_200_300"] = 604
STXS_bins["TTH_PTH_GT300"] = 605
STXS_bins["BBH_FWDH"] = 700
STXS_bins["BBH"] = 701
STXS_bins["TH_FWDH"] = 800
STXS_bins["TH"] = 801
