import sys
import os
import glob

import ROOT
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import mplhep as hep
hep.style.use("CMS")

# Extract significance from pseudoToys
sig_pseudo_array = []
files_pseudo = glob.glob(sys.argv[1] + "higgsCombine.significance*")
for i, file_pseudo in enumerate(files_pseudo):
    print("Opening file [%s/%s]: %s"%(i+1,len(files_pseudo),file_pseudo))
    f_pseudo = ROOT.TFile(file_pseudo)
    t = f_pseudo.Get("limit")
    mh_pseudo = []
    sig_pseudo = []
    for ev in t:
        # Only save "observed" limit
        mh_pseudo.append(getattr(ev, "mh"))
        sig_pseudo.append(getattr(ev, "limit"))
    args_ordered = np.argsort(mh_pseudo)
    mh_ordered = np.array(mh_pseudo)[args_ordered]
    sig_pseudo_ordered = np.array(sig_pseudo)[args_ordered]
    sig_pseudo_array.append(sig_pseudo_ordered)

sig_pseudo_array = np.array(sig_pseudo_array)

# Calculate fraction of toys with z > z_thr
z_thresholds = [0, 1, 2, 3]

fracs = {}
err = {}
for z_thr in z_thresholds:
    fracs[z_thr] = []
    err[z_thr] = []
    for i in range(len(mh_ordered)):
        fracs[z_thr].append(np.mean(sig_pseudo_array[:,i] > z_thr))
        # Bayesian error estimate for efficiency
        k = np.sum(sig_pseudo_array[:,i] > z_thr)
        n = len(sig_pseudo_array[:,i])
        err[z_thr].append(np.sqrt((((k+1)*(k+2))/((n+2)*(n+3))) - (((k+1)*(k+1))/((n+2)*(n+2)))))

if not os.path.isdir(sys.argv[2]):
    os.makedirs(sys.argv[2], exist_ok=False)

fig, ax = plt.subplots()

# Observed limits
ax.errorbar(mh_ordered, fracs[0], yerr=err[0], marker='o', color='black', label="$Z > 0\\sigma$", linestyle='None')
ax.axhline(0.5, color='black', linestyle='--')
ax.errorbar(mh_ordered, fracs[1], yerr=err[1], marker='o', color='#5790fc', label="$Z > 1\\sigma$", linestyle='None')
ax.axhline(0.1585, color='#5790fc', linestyle='--')
ax.errorbar(mh_ordered, fracs[2], yerr=err[2], marker='o', color='#e42536', label="$Z > 2\\sigma$", linestyle='None')
ax.axhline(0.023, color='#e42536', linestyle='--')


ax.set_xlabel("$m_{h}$ (GeV)")
ax.set_ylabel("Fraction of toys with $Z > Z_{thr}$")
ax.set_ylim(1e-3,1)
ax.set_yscale('log')

handles, labels = ax.get_legend_handles_labels()
line = matplotlib.lines.Line2D([],[], linestyle='--', marker='None', color='grey')
handles.append(line)
labels.append(f"Asymptotic approx")
ax.legend(handles, labels, loc='best', fontsize=16)

ext_str = "" if sys.argv[3]=="" else f"_{sys.argv[3]}"
fig.savefig(sys.argv[2] + f"/sig_threshold{ext_str}.png", bbox_inches='tight')
fig.savefig(sys.argv[2] + f"/sig_threshold{ext_str}.pdf", bbox_inches='tight')
ax.cla() 
