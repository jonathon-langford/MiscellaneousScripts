import sys
import os

import ROOT
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import mplhep as hep
hep.style.use("CMS")

f_input = ROOT.TFile(sys.argv[1])
t = f_input.Get("limit")

mh = []
sig = []

for ev in t:
    mh.append(getattr(ev, "mh"))
    sig.append(getattr(ev, "limit"))

# Sort for mh in increasing order
args_ordered = np.argsort(mh)
mh_ordered = np.array(mh)[args_ordered]
sig_ordered = np.array(sig)[args_ordered]

if not os.path.isdir(sys.argv[2]):
    os.makedirs(sys.argv[2], exist_ok=False)

fig, ax = plt.subplots()
ax.plot(mh_ordered, sig_ordered, marker='d', color='red', label="Observed (pseudo-toy, s=%s, r=%s)"%(sys.argv[4],sys.argv[5]))
ax.axhline(0, color='grey', alpha=0.5, linestyle='-')
ax.axhline(1, color='grey', alpha=0.5, linestyle='--')
ax.axhline(2, color='grey', alpha=0.5, linestyle='--')
ax.axhline(3, color='grey', alpha=0.5, linestyle='--')
ax.set_xlabel("$m_{h}$ (GeV)")
ax.set_ylabel("Significance ($\\sigma$)")
ax.set_ylim(-0.2, 4)
ax.invert_yaxis()
ax.legend(loc='best')

ext_str = "" if sys.argv[3]=="" else f"_{sys.argv[3]}"
fig.savefig(sys.argv[2] + f"/mh_vs_sig{ext_str}.png", bbox_inches='tight')
ax.cla() 
