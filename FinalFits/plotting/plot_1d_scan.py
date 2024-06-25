import subprocess
import os
import numpy as np
import re
from optparse import OptionParser
import json
import ROOT
from scipy.interpolate import interp1d

from plotting_tools import *

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep
mplhep.style.use("CMS")

comb_path = os.environ['CMSSW_BASE']+"/src/summer21"
poi = "CMS_hgg_pdfWeight_26_shape"
#poi = "CMS_hgg_SigmaEOverEShift"
plot_path = "/eos/user/j/jlangfor/www/CMS/icrf/hgg/debug/ER3/ImpactsScans"

f = ROOT.TFile(f"higgsCombine_paramFit_Test_{poi}.MultiDimFit.mH125.38.root")
t = f.Get("limit")

scans = {}
scans[poi] = build_scan(t,poi,extract_info=True,spline="linear",spline_points=100000,track_params=['r'])

fig = plt.figure(figsize=(8,8))
left, width = 0.15, 0.8
bottom = 0.15
height=0.9-bottom
ax = fig.add_axes([left,bottom,width,height])
axs = []
axs.append(ax)
axs[0].plot(scans[poi]['graph'][0], scans[poi]['graph'][1], color='cornflowerblue', ls='None', marker='o')
axs[0].plot(scans[poi]['spline'][0], scans[poi]['spline'][1], color='cornflowerblue', linewidth=4)
axs[0].set_ylabel("2NLL", color='cornflowerblue')
axs[0].set_ylim(0,4)
axs[0].axhline(1, color='grey', alpha=0.5, ls='--')
axs[0].axvline(scans[poi]['bestfit'], color='mediumblue')
axs[0].axvline(scans[poi]['cross_1sig']['lo'], color='mediumblue', alpha=0.5)
axs[0].axvline(scans[poi]['cross_1sig']['hi'], color='mediumblue', alpha=0.5)

axs[0].tick_params(axis='y', labelcolor='cornflowerblue')
axs[0].set_xlabel(poi)

axr = axs[0].twinx()
axs.append(axr)
axs[-1].plot(scans[poi]['graph'][0], scans[poi]['track_params']['r'], color='red', alpha=0.5, ls='None', marker='o')
axs[-1].plot(scans[poi]['spline'][0], scans[poi]['track_params_splines']['r'], color='red', alpha=0.5)
axs[-1].set_ylabel("r", color='red')
axs[-1].tick_params(axis='y', labelcolor='red')

# Find crossings for impacts
graph_invert = (scans[poi]['track_params']['r'],scans[poi]['graph'][0])
spline_invert = (scans[poi]['track_params_splines']['r'], scans[poi]['spline'][0])
r_lo = find_crossings(graph_invert,spline_invert,scans[poi]['cross_1sig']['lo'])[0]['hi']
r_hi = find_crossings(graph_invert,spline_invert,scans[poi]['cross_1sig']['hi'])[0]['hi']
r_bf = find_crossings(graph_invert,spline_invert,np.round(scans[poi]['bestfit'], decimals=8))[0]['hi']
axs[-1].axhline(r_lo, color='maroon', alpha=0.5)
axs[-1].axhline(r_hi, color='maroon', alpha=0.5)
axs[-1].axhline(r_bf, color='maroon')

fig.savefig(f"{plot_path}/{poi}.png", bbox_inches="tight")

