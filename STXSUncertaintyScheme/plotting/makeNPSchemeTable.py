import ROOT
import json
import pandas as pd
import numpy as np
import re
import os, sys
import math
from optparse import OptionParser
from STXS import STXS_bins
from collections import OrderedDict as od
from array import array

def get_options():
  parser = OptionParser()
  parser.add_option('--inputJson', dest='inputJson', default='', help="Input json file")
  parser.add_option('--doNNLO', dest='doNNLO', default=False, action="store_true", help="Inclue NNLO scale variations")
  parser.add_option("--translateBins", dest="translateBins", default=None, help="JSON to store bin translations")
  parser.add_option("--outputDir", dest="outputDir", default='NPSchemeTables', help="Output dir to store table")
  return parser.parse_args()
(opt,args) = get_options()

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

if not os.path.isdir( opt.outputDir ): os.system("mkdir %s"%opt.outputDir )

# Function to extract delta
def extractDelta(_data,_bins,_svars):
  # Extract nominal xs for bins sets 'a' and 'b'
  s_a_vars, s_b_vars, s_ab_vars = [], [], []
  s_a = _data[_data['stxs_id'].isin(_bins['a'])]['nominal'].sum()
  s_b = _data[_data['stxs_id'].isin(_bins['b'])]['nominal'].sum()
  s_ab = s_a+s_b
  # Extract variations xs for bin sets 'a' and 'b'
  for ivar in _svars:
    s_a_i = data[data['stxs_id'].isin(_bins['a'])][ivar].sum()
    s_b_i = data[data['stxs_id'].isin(_bins['b'])][ivar].sum()
    s_ab_i = s_a_i+s_b_i
    s_a_vars.append(s_a_i)
    s_b_vars.append(s_b_i)
    s_ab_vars.append(s_ab_i)
  # Convert to numpy arrays
  s_a_vars, s_b_vars, s_ab_vars = np.asarray(s_a_vars), np.asarray(s_b_vars), np.asarray(s_ab_vars)
  # Normalise so sum of xs remains constant
  #deltas = s_a*(1-(s_a_vars/s_a)/(s_ab_vars/s_ab))
  deltas = s_a*((s_a_vars/s_a)/(s_ab_vars/s_ab)-1)
  # Return max delta, corresponding variation and relative uncertainties
  delta, svar = deltas[abs(deltas).argmax()], svars[abs(deltas).argmax()]
  u_a, u_b = delta/s_a, (-1*delta)/s_b
  return delta, svar, u_a, u_b 

def Translate(name, ndict):
    return ndict[name] if name in ndict else name

def FixForLatex(name):  
    return name.replace("_","\_")
  
  
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
translateBins = {} if opt.translateBins is None else LoadTranslations(opt.translateBins)

# Function for extracting np variation
def extractNPVariation(df,nps,nuisance,mode='a'):
  x = abs( df[df['stxs_id']==nps[nuisance][mode][0]][nuisance])
  if mode == 'a': return -1*x
  else: return x

def extractNPfromBin(df,nps,nuisance,sb):
  sb_id = df[df['stxs_bin']==sb]['stxs_id'].values[0]
  x = abs( df[df['stxs_bin']==sb][nuisance].values[0])
  if sb_id in nps[nuisance]['a']: return -1*x
  else: return x

def extractJetNPfromBin(df,nuisance,sb):
  return df[df['stxs_bin']==sb][nuisance].values[0]

def extractTotalUnc(df,nps,njps,sb):
  utot = 0
  for np in nps: 
    x = abs( df[df['stxs_bin']==sb][np].values[0])
    utot += x*x
  for njp in njps:
    x = abs( df[df['stxs_bin']==sb][njp].values[0])
    utot += x*x
  return math.sqrt(utot)

ij = opt.inputJson
with open(ij,"r") as jf: xs = json.load(jf)
year = ij.split("/")[-1].split("_")[1]
generator = re.sub(".json","",ij.split("/")[-1].split("_")[2])
NNLOPS = True if "NNLOPS" in ij else False

# Create list of stxs bins to plot
stxs_bins = []
for sb in STXS_bins:
  if(sb in xs)&(sb not in stxs_bins)&('FWDH' not in sb): stxs_bins.append(sb)

# Define list of svars
svars = ['nominal','muF_0p5_muR_0p5', 'muF_2p0_muR_1p0', 'muF_1p0_muR_0p5', 'muF_2p0_muR_2p0', 'muF_1p0_muR_2p0', 'muF_0p5_muR_1p0']
if opt.doNNLO: svars.extend( ['NNLOPS_muF_2p0_muR_2p0','NNLOPS_muF_0p5_muR_0p5'] )
#svars = xs[stxs_bins[0]].keys()

# Make pandas dataframe to store xsvars
_columns = ['stxs_bin','stxs_id']
for svar in svars: _columns.append(svar)
data = pd.DataFrame(columns=_columns)
for sb in stxs_bins:
  if "FWDH" in sb: continue
  vals = [sb,STXS_bins[sb]]
  for svar in svars: vals.append( xs[sb][svar] )
  data.loc[len(data)] = vals

# Define different nuisance params
NuisanceParams = od()
NuisanceParams['PTH_200'] = {'a':[105,106,107,108,109,110,111,112,113,114,115,116],'b':[101,102,103,104]}
NuisanceParams['PTH_300'] = {'a':[101],'b':[102,103,104]}
NuisanceParams['PTH_450'] = {'a':[102],'b':[103,104]}
NuisanceParams['PTH_650'] = {'a':[103],'b':[104]}
NuisanceParams['0J_PTH_10'] = {'a':[105],'b':[106]}
NuisanceParams['1J_PTH_60'] = {'a':[107],'b':[108,109]}
NuisanceParams['1J_PTH_120'] = {'a':[108],'b':[109]}
NuisanceParams['MJJ_350'] = {'a':[110,111,112],'b':[113,114,115,116]}
NuisanceParams['MJJ_700'] = {'a':[113,114],'b':[115,116]}
NuisanceParams['2J_PTH_60'] = {'a':[110],'b':[111,112]}
NuisanceParams['2J_PTH_120'] = {'a':[111],'b':[112]}
NuisanceParams['LOWMJJ_PTHJJ_25'] = {'a':[113],'b':[114]}
NuisanceParams['HIGHMJJ_PTHJJ_25'] = {'a':[115],'b':[116]}


# Loop over nuisances and extract uncertainties
for NP, bins in NuisanceParams.iteritems():
  data[NP] = 0.
  delta, sv, ua, ub = extractDelta(data,bins,svars)
  data.loc[data['stxs_id'].isin(bins['a']),NP] = ua
  data.loc[data['stxs_id'].isin(bins['b']),NP] = ub 
  print "%s: delta = %.4f (%s) --> u(a) = %.4f, u(b) = %.4f"%(NP,delta,sv,ua,ub)

# FIXME: updated pTHjj nuisances, lifting 20% variation for nJet=2->3
bins = NuisanceParams['LOWMJJ_PTHJJ_25']
data.loc[data['stxs_id'].isin(bins['a']),'LOWMJJ_PTHJJ_25'] = -0.313007
data.loc[data['stxs_id'].isin(bins['b']),'LOWMJJ_PTHJJ_25'] = 0.200
bins = NuisanceParams['HIGHMJJ_PTHJJ_25']
data.loc[data['stxs_id'].isin(bins['a']),'HIGHMJJ_PTHJJ_25'] = -0.321294
data.loc[data['stxs_id'].isin(bins['b']),'HIGHMJJ_PTHJJ_25'] = 0.200


# Add jet uncertainties
NJetBins = {'inclusive':[101,102,103,104],
            '0J':[105,106],
            '1J':[107,108,109],
            'GE2J':[110,111,112,113,114,115,116]
           }
NJetParams = od()
# Additional flat 15% uncertainty for boosted region (==inclusive)
NJetParams['BOOSTED'] = {'inclusive':0.150,'0J':0.0,'1J':0.0,'GE2J':0.0}
NJetParams['YIELD']   = {'inclusive':0.0453,'0J':0.0381,'1J':0.0523,'GE2J':0.0887}
NJetParams['RES']     = {'inclusive':0.0209,'0J':0.0010,'1J':0.0451,'GE2J':0.0887}
NJetParams['MIG01']   = {'inclusive':0.0000,'0J':-0.0415,'1J':0.0792,'GE2J':0.0444}
NJetParams['MIG12']   = {'inclusive':0.0000,'0J':0.000,'1J':-0.0681,'GE2J':0.182}
for NP in NJetParams: data[NP] = 0
data['jbin'] = '-'
for ir,r in data.iterrows():
  for k,v in NJetBins.iteritems():
    if r['stxs_id'] in v: data.at[ir,'jbin'] = k

for k in NJetBins:
  for NP, vals in NJetParams.iteritems(): data.loc[data['jbin']==k,NP] = vals[k]

# Print table
pcols = ['stxs_bin','nominal']
for NP in NuisanceParams: pcols.append(NP)
for NP in NJetParams: pcols.append(NP)
print data[pcols]

# Make latex table
fout = open("%s/summary_table.txt"%opt.outputDir,"w")
fout.write("\\begin{tabular}{l|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c|c}\n")
cols = "STXS bin"
for NP in NJetParams: cols += " & {\\tiny{%s}}"%re.sub("_","",NP)
for NP in NuisanceParams: cols += " & {\\tiny{%s}}"%re.sub("_","",NP)
cols += " & {\\tiny{Total}}"
fout.write("  %s \\\\ \\hline \n"%cols)
# Loop over stxs ibins
for sb in stxs_bins:
  col = "{\\tiny{%s}}"% FixForLatex(Translate(sb,translateBins))
  for NP in NJetParams: 
    x = 100*extractJetNPfromBin(data,NP,sb)
    if x == 0: col += " & -"
    else: col += " & %.1f"%(100*extractJetNPfromBin(data,NP,sb))
  for NP in NuisanceParams: 
    x = 100*extractNPfromBin(data,NuisanceParams,NP,sb)
    if x == 0: col += " & -"
    else: col += " & %.1f"%(100*extractNPfromBin(data,NuisanceParams,NP,sb)) 
  col += " & %.1f"%(100*extractTotalUnc(data,NuisanceParams,NJetParams,sb))
  fout.write("  %s \\\\ \n"%col)
fout.write("\\end{tabular}\n")
fout.close()





fout = open("%s/summary_table_2lines.txt"%opt.outputDir,"w")
fout.write("\\begin{tabular}{l|c|c|c|c|c|c|c|c|c|c}\n")
cols = "STXS bin"
count=0
for NP in NJetParams:
  count +=1
  if count < 10:
    cols += " & {\\tiny{%s}}"%re.sub("_","",NP)
for NP in NuisanceParams: 
  count +=1
  if count < 10:
    cols += " & {\\tiny{%s}}"%re.sub("_","",NP)
cols += " & {\\tiny{Total}}"
fout.write("  %s \\\\ \\hline \n"%cols)
# Loop over stxs ibins
for sb in stxs_bins:
  col = "{\\tiny{%s}}"% FixForLatex(Translate(sb,translateBins))
  count=0
  for NP in NJetParams: 
    count +=1
    if count < 10:
      x = 100*extractJetNPfromBin(data,NP,sb)
      if x == 0: col += " & -"
      else: col += " & %.1f"%(100*extractJetNPfromBin(data,NP,sb))  
  for NP in NuisanceParams:
    count +=1
    if count < 10:
      x = 100*extractNPfromBin(data,NuisanceParams,NP,sb)
      if x == 0: col += " & -"
      else: col += " & %.1f"%(100*extractNPfromBin(data,NuisanceParams,NP,sb)) 
  col += " & %.1f"%(100*extractTotalUnc(data,NuisanceParams,NJetParams,sb))
  fout.write("  %s \\\\ \n"%col)
fout.write("\\end{tabular}\n")


fout.write("\n\n\n\n\n\n")

fout.write("\\begin{tabular}{l|c|c|c|c|c|c|c|c|c|c}\n")
cols = "STXS bin"
count=0
for NP in NJetParams:
  count +=1
  if count >= 10:
    cols += " & {\\tiny{%s}}"%re.sub("_","",NP)
for NP in NuisanceParams: 
  count +=1
  if count >= 10:
    cols += " & {\\tiny{%s}}"%re.sub("_","",NP)
cols += " & {\\tiny{Total}}"
fout.write("  %s \\\\ \\hline \n"%cols)
# Loop over stxs ibins
for sb in stxs_bins:
  col = "{\\tiny{%s}}"% FixForLatex(Translate(sb,translateBins))
  count=0
  for NP in NJetParams: 
    count +=1
    if count >= 10:
      x = 100*extractJetNPfromBin(data,NP,sb)
      if x == 0: col += " & -"
      else: col += " & %.1f"%(100*extractJetNPfromBin(data,NP,sb))  
  for NP in NuisanceParams:
    count +=1
    if count >= 10:
      x = 100*extractNPfromBin(data,NuisanceParams,NP,sb)
      if x == 0: col += " & -"
      else: col += " & %.1f"%(100*extractNPfromBin(data,NuisanceParams,NP,sb)) 
  col += " & %.1f"%(100*extractTotalUnc(data,NuisanceParams,NJetParams,sb))
  fout.write("  %s \\\\ \n"%col)
fout.write("\\end{tabular}\n")


fout.close()

