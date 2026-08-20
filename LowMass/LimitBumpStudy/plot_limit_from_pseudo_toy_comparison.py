import sys
import os
import glob

import ROOT
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import mplhep as hep
hep.style.use("CMS")

# Limit from asymptotic toy
f_input = ROOT.TFile(sys.argv[1])
t = f_input.Get("limit")
mh = []
limits = {}
for ev in t:
    if getattr(ev, "quantileExpected") not in limits:
        limits[getattr(ev, "quantileExpected")] = []
    if getattr(ev, "mh") not in mh:
        mh.append(getattr(ev, "mh"))
    limits[getattr(ev, "quantileExpected")].append(getattr(ev, "limit"))

# Sort for mh in increasing order
args_ordered = np.argsort(mh)
mh_ordered = np.array(mh)[args_ordered]
limits_ordered = {}
for l in limits.keys():
    limits_ordered["%.3f"%l] = np.array(limits[l])[args_ordered]

# Extract observed limits from pseudoToys
limits_pseudo_array = []
files_pseudo = glob.glob(sys.argv[2] + "higgsCombine.limit*")
for file_pseudo in files_pseudo:
    f_pseudo = ROOT.TFile(file_pseudo)
    t = f_pseudo.Get("limit")
    mh_pseudo = []
    limits_pseudo = []
    for ev in t:
        # Only save "observed" limit
        if getattr(ev, "quantileExpected") == -1:
            mh_pseudo.append(getattr(ev, "mh"))
            limits_pseudo.append(getattr(ev, "limit"))
    args_ordered = np.argsort(mh_pseudo)
    limits_pseudo_ordered = np.array(limits_pseudo)[args_ordered]
    limits_pseudo_array.append(limits_pseudo_ordered)

limits_pseudo_array = np.array(limits_pseudo_array)
limits_pseudo_ordered = {}
for l in limits_ordered.keys():
    pc = float(l)*100
    limits_pseudo_ordered[l] = []
    for i in range(len(mh)):
        limits_pseudo_ordered[l].append(np.percentile(limits_pseudo_array[:,i], pc))


fig, ax = plt.subplots()

# Observed limits
ax.plot(mh_ordered, limits_pseudo_ordered['0.500'], marker='None', color='black', label="Median pseudo-toys", linestyle='--')
ax.plot(mh_ordered, limits_pseudo_ordered['0.160'], marker='None', color='#228b22', label="68% pseudo-toys", linestyle='--')
ax.plot(mh_ordered, limits_pseudo_ordered['0.840'], marker='None', color='#228b22', linestyle='--')
ax.plot(mh_ordered, limits_pseudo_ordered['0.025'], marker='None', color='#ffcc00', label="95% pseudo-toys", linestyle='--')
ax.plot(mh_ordered, limits_pseudo_ordered['0.975'], marker='None', color='#ffcc00', linestyle='--')


# Asimov limits
ax.plot(mh_ordered, limits_ordered['0.500'], marker='None', color='black', label="Median expected")
ax.plot(mh_ordered, limits_ordered['0.160'], marker='None', color='#228b22', label="68% expected")
ax.plot(mh_ordered, limits_ordered['0.840'], marker='None', color='#228b22')
ax.plot(mh_ordered, limits_ordered['0.025'], marker='None', color='#ffcc00', label="95% expected")
ax.plot(mh_ordered, limits_ordered['0.975'], marker='None', color='#ffcc00')

ax.set_xlabel("$m_{h}$ (GeV)")
ax.set_ylabel("$r$")

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, loc='upper right', fontsize=16)

if not os.path.isdir(sys.argv[3]):
    os.makedirs(sys.argv[3], exist_ok=False)

ext_str = "" if sys.argv[4]=="" else f"_{sys.argv[4]}"
fig.savefig(sys.argv[3] + f"/mh_vs_limit_from_pseudo_toys{ext_str}.png", bbox_inches='tight')
ax.cla() 
