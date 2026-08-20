import sys
import os

import ROOT
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
hep.style.use("CMS")

params = ['deltaNLL', sys.argv[3]]

f_input = ROOT.TFile(sys.argv[1])
t = f_input.Get("limit")

r = []
vals = {}
for p in params:
    vals[p] = []

for ev in t:
    r.append(getattr(t, "r"))
    for p in params:
        if "pdfindex" in p:
            p_str = f"trackedIndex_{p}"
        elif p in ['deltaNLL', 'mh', 'r']:
            p_str = p
        else:
            p_str = f"trackedParam_{p}"

        vals[p].append(getattr(t, p_str))

# Sort r in increasing order
args_ordered = np.argsort(r)
r_ordered = np.array(r)[args_ordered]
vals_ordered = {}
for p in params:
    vals_ordered[p] = np.array(vals[p])[args_ordered]

if not os.path.isdir(sys.argv[2]):
    os.makedirs(sys.argv[2], exist_ok=False)

fig, ax = plt.subplots()
for p in params:
    ax.plot(r_ordered, vals_ordered[p], c='#5790fc', marker='o', linestyle='--', label=sys.argv[2].split("/")[-1])
    ax.set_xlabel("r")
    ax.set_ylabel(p)
    ax.legend(loc='best')
    fig.savefig(sys.argv[2] + f"/r_vs_{p}.png", bbox_inches='tight')
    ax.cla()
