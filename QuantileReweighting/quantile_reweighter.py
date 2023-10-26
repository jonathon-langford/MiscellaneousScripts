import pandas as pd
import sys
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep 
mplhep.style.use("CMS")
import numpy as np

#features = ['probe_pt','probe_eta','probe_phi','fixedGridRhoAll']
features = ['probe_pt','probe_eta','fixedGridRhoAll']

# Read in dataframes
columns = ['probe_pt','probe_eta','probe_phi','fixedGridRhoAll','weight']
dy = pd.read_parquet("DY_2022_merged.parquet", engine="pyarrow", columns=columns)
data = pd.read_parquet("Data_Run2022F_merged.parquet", engine="pyarrow", columns=columns[:-1])
data['weight'] = 1.
# Reweight total MC to data
dy['weight'] = dy['weight']*(np.sum(data['weight'])/np.sum(dy['weight']))

# Calculate quantiles in data
# FIXME: add option to do different quantiles for each feature, or fixed for e.g. eta
n_quantiles = 20
quantiles = np.linspace(0,1,n_quantiles+1)

plot_ext = f"q{n_quantiles}_incRho"

def unbound_list(x):
    x[0], x[-1] = -np.inf, np.inf
    return x

def get_conditional_quantiles(df, features, quantiles, history=[]):
    if len(features) == 1:
        res = []
        x_quantiles = unbound_list( list(df[features[0]].quantile(q=quantiles)) )
        for i in range(len(quantiles)-1):
            res.append( history+[x_quantiles[i],x_quantiles[i+1]] )
        return res
    else:
        res = []
        x_quantiles = unbound_list( list(df[features[0]].quantile(q=quantiles)) )
        for i in range(len(quantiles)-1):
            mask = (df[features[0]]>=x_quantiles[i])&(df[features[0]]<x_quantiles[i+1])
            res.append( get_conditional_quantiles(df[mask], features[1:], quantiles, history=history+[x_quantiles[i],x_quantiles[i+1]]) )
        return res

def get_yields(df, features, mask_list):
    if len(features) == 1:
        yields, ind = [], []
        for i in range(len(mask_list)):
            mask_info = mask_list[i]
            lo, hi = mask_info[-2], mask_info[-1]
            mask = (df[features[0]]>=lo)&(df[features[0]]<hi)
            yields.append( df[mask]['weight'].sum() )
            ind.append(df[mask].index)
        return yields, ind
    else:
        yields, ind = [], []
        for i in range(len(mask_list)):
            mask_list_new = mask_list[i]
            lo, hi = mask_list_new.flatten()[-2*len(features)], mask_list_new.flatten()[-2*len(features)+1]
            mask = (df[features[0]]>=lo)&(df[features[0]]<hi)
            result = get_yields(df[mask], features[1:], mask_list_new)
            yields.append( result[0] )
            ind.append( result[1] )
        return yields, ind

def get_reweight_factors(df, scale_factors, index):
    rwgt = np.zeros_like(df['weight'])
    scale_factors = scale_factors.flatten()
    index = np.array(index).flatten()
    for i in range(len(scale_factors)):
        sf = scale_factors[i]
        ind = np.array(index[i])
        np.put(rwgt, ind, sf)
    return rwgt
 
print(" --> Extracting conditional quantiles in data:", features)
res = np.array(get_conditional_quantiles(data, features, quantiles))

print(" --> Calculating yields in quantiles (data)")
yields_data, ind_data = get_yields(data, features, res)

print(" --> Calculating yields in quantiles (MC)")
yields_mc, ind_dy = get_yields(dy, features, res)
sf = np.array(yields_data)/np.array(yields_mc)

print(" --> Extracting reweighting factors")
rwgt = get_reweight_factors(dy, sf, ind_dy)
# Add reweighted column
dy['weight_rwgt'] = dy['weight']*rwgt

# Plot histograms
plot_map = {
    "probe_pt": [50,(0,100),"Probe $p_T$ [GeV]"],
    "probe_eta": [50,(-4,4),"Probe $\\eta$"],
    "probe_phi": [50,(-4,4),"Probe $\\phi$"],
    "fixedGridRhoAll": [50,(0,100),"$\\rho$"]
}

fig, ax = plt.subplots()
for feature in columns[:-1]:
    po = plot_map[feature]
    bin_edges = ax.hist(dy[feature], bins=po[0], range=po[1], label="DY (nominal)", color='grey', alpha=0.5, weights=dy['weight'])
    ax.hist(dy[feature], bins=po[0], range=po[1], label="DY (rwgt)", color='red', histtype='step', weights=dy['weight_rwgt'])
    bin_centres = (bin_edges[1][:-1] + bin_edges[1][1:]) / 2
    data_hist = np.histogram(data[feature], bins=po[0], range=po[1])[0]
    data_err = np.sqrt(data_hist)
    ax.errorbar(x=bin_centres, y=data_hist, yerr=data_err, fmt='o', capsize=2, color='black', label="Data")
    ax.set_xlabel(po[2])
    ax.set_ylabel("Events")
    ax.legend(loc="best")
    fig.savefig(f"plots/{feature}_{plot_ext}.pdf", bbox_inches="tight")
    fig.savefig(f"plots/{feature}_{plot_ext}.png", bbox_inches="tight")
    ax.cla()
