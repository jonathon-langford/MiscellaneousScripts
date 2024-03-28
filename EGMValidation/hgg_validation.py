import os
import re
from optparse import OptionParser
import json

import pandas as pd
import numpy as np
import awkward as ak

import matplotlib 
matplotlib.use("Agg") 
import matplotlib.pyplot as plt 
import mplhep 
mplhep.style.use("CMS")

from validation_tools import *
from hep_ml.reweight import BinsReweighter

fontsize_map = {
    "legend" : 18,
    "x_label": 24,
    "y_label": 24,
    "x_tick_label": 16,
    "y_tick_label": 22,
    "values": 10,
    "values_title": 14,
    "cms_title": 22
}

plot_options_map = {
    "total_linewidth" : 2,
    "data_linewidth" : 2
}

def get_options():
    parser = OptionParser()
    parser.add_option('-s','--mc', dest='mc', default=None, help="Comma-sep list of MC parquet files")
    parser.add_option('-x','--xvars', dest='xvars', default=None, help="Comma-sep list of x variables")
    parser.add_option('--plot-path', dest='plot_path', default=".", help="Plot path")
    parser.add_option('--ext', dest='ext', default="", help="Extension for saving")
    parser.add_option('--do-correction-factor-plot', dest='do_correction_factor_plot', default=False, action="store_true", help="Plot histogram of correction factors")
    parser.add_option('--do-plots', dest='do_plots', default=False, action="store_true", help="Plots")
    parser.add_option('--skip-norm-fix', dest='skip_norm_fix', default=False, action="store_true", help="Skip norm fix")
    parser.add_option('--do-single-norm-fix', dest='do_single_norm_fix', default=False, action="store_true", help="Do norm fix over both photons")
    parser.add_option('--ratio-lim', dest='ratio_lim', default=None, help="y-axis range e.g. -0.1,2. If None will estimate from data")
    parser.add_option('--figsize', dest='figsize', default="10,12", help="Figure size")
    parser.add_option('--fontsize', dest='fontsize', default="cms_title:22", help="Comma-separated list")
    parser.add_option('--plot-options', dest='plot_options', default="values_title_pad:0.75", help="Comma-separated list")
    parser.add_option('--cms-label', dest='cms_label', default="Work in Progress", help="CMS sub-label")
    return parser.parse_args()
(opt,args) = get_options()

# Change fontsize map according to input
for fontsize_opt in opt.fontsize.split(","):
    fontsize_map[fontsize_opt.split(":")[0]] = float(fontsize_opt.split(":")[1])
# Change plot_options map according to input
for plot_options_opt in opt.plot_options.split(","):
    if plot_options_opt.split(":")[0] == "unit":
        plot_options_map[plot_options_opt.split(":")[0]] = plot_options_opt.split(":")[1]
    else:
        plot_options_map[plot_options_opt.split(":")[0]] = float(plot_options_opt.split(":")[1])

# Load dataframes
dfs = {
    "mc" : []
}

print(" --> Loading MC")
for file_mc in opt.mc.split(","):
    df = pd.read_parquet(file_mc, engine="pyarrow")
    # Apply cuts:
    mask = df['pt']==df['pt']
    # Append to list
    dfs['mc'].append(df[mask])
dfs['mc'] = pd.concat(dfs['mc'], ignore_index=True)

# Remove NaNs
mask = dfs['mc']['fixedGridRhoAll'] == dfs['mc']['fixedGridRhoAll']
dfs['mc'] = dfs['mc'][mask]
          
# Ensure MC yield remains unchanged after EGM reweighting correction factors
# Method A: Keep norm fixed in each eta region for each photon (how it has been applied so far)
# Method B: Keep norm fixed overall
if not opt.skip_norm_fix:
    mask_lead_eb = abs(dfs['mc']['lead_ScEta']) < 1.5
    new_weights_eb = dfs['mc']['weight'][mask_lead_eb] * dfs['mc']['lead_egmReweightingFactor'][mask_lead_eb]
    norm_sf_eb = dfs['mc']['weight'][mask_lead_eb].sum() / new_weights_eb.sum()   
 
    mask_lead_eeplus = dfs['mc']['lead_ScEta'] > 1.5
    new_weights_eeplus = dfs['mc']['weight'][mask_lead_eeplus] * dfs['mc']['lead_egmReweightingFactor'][mask_lead_eeplus]
    norm_sf_eeplus = dfs['mc']['weight'][mask_lead_eeplus].sum() / new_weights_eeplus.sum()   

    mask_lead_eeminus = dfs['mc']['lead_ScEta'] < -1.5
    new_weights_eeminus = dfs['mc']['weight'][mask_lead_eeminus] * dfs['mc']['lead_egmReweightingFactor'][mask_lead_eeminus]
    norm_sf_eeminus = dfs['mc']['weight'][mask_lead_eeminus].sum() / new_weights_eeminus.sum()   

    norm_sf = mask_lead_eb*norm_sf_eb + mask_lead_eeplus*norm_sf_eeplus + mask_lead_eeminus*norm_sf_eeminus
    dfs['mc']['lead_egmReweightingFactor_unnorm'] = dfs['mc']['lead_egmReweightingFactor']
    dfs['mc']['lead_egmReweightingFactor'] = dfs['mc']['lead_egmReweightingFactor']*norm_sf

    mask_sublead_eb = abs(dfs['mc']['sublead_ScEta']) < 1.5
    new_weights_eb = dfs['mc']['weight'][mask_sublead_eb] * dfs['mc']['sublead_egmReweightingFactor'][mask_sublead_eb]
    norm_sf_eb = dfs['mc']['weight'][mask_sublead_eb].sum() / new_weights_eb.sum()   
 
    mask_sublead_eeplus = dfs['mc']['sublead_ScEta'] > 1.5
    new_weights_eeplus = dfs['mc']['weight'][mask_sublead_eeplus] * dfs['mc']['sublead_egmReweightingFactor'][mask_sublead_eeplus]
    norm_sf_eeplus = dfs['mc']['weight'][mask_sublead_eeplus].sum() / new_weights_eeplus.sum()   

    mask_sublead_eeminus = dfs['mc']['sublead_ScEta'] < -1.5
    new_weights_eeminus = dfs['mc']['weight'][mask_sublead_eeminus] * dfs['mc']['sublead_egmReweightingFactor'][mask_sublead_eeminus]
    norm_sf_eeminus = dfs['mc']['weight'][mask_sublead_eeminus].sum() / new_weights_eeminus.sum()   

    norm_sf = mask_sublead_eb*norm_sf_eb + mask_sublead_eeplus*norm_sf_eeplus + mask_sublead_eeminus*norm_sf_eeminus
    dfs['mc']['sublead_egmReweightingFactor_unnorm'] = dfs['mc']['sublead_egmReweightingFactor']
    dfs['mc']['sublead_egmReweightingFactor'] = dfs['mc']['sublead_egmReweightingFactor']*norm_sf


# Plot correction histogram
if opt.do_correction_factor_plot:
    xvar_name = 'photon_egmReweightingFactor'
    for pho in ['lead','sublead']:
        xvar_name = f"{pho}_egmReweightingFactor"
        for eta_region in ['EB','EEplus','EEminus']:
            if eta_region == "EB":
                mask = abs(dfs['mc'][f'{pho}_ScEta']) < 1.5
            elif eta_region == "EEplus":
                mask = dfs['mc'][f'{pho}_ScEta'] > 1.5
            elif eta_region == "EEminus":
                mask = dfs['mc'][f'{pho}_ScEta'] < -1.5
 
            w = dfs['mc'][mask]['weight']
            wmean = (dfs['mc'][mask][xvar_name]*w).sum() / w.sum()
            fig, ax = plt.subplots()
            ax.hist(dfs['mc'][mask][xvar_name], bins=50, range=(0,3), weights=w, label=f"H$\\rightarrow\\gamma\\gamma$, $\\eta$-region: {eta_region} (Weighted mean = {wmean:.3f})", color=color_map['mc_pre'])
            ax.set_ylabel("Weighted events")
            ax.set_xlabel("EGM NN reweight")
            ax.axvline(wmean, color='red', alpha=0.5)
            ax.legend(loc='best', fontsize=fontsize_map['legend'], facecolor='white', edgecolor='black', frameon=True)
            # Add text values to plot 
            mplhep.cms.label(llabel=f"Simulation {opt.cms_label}", ax=ax, rlabel="2022 postEE (13 TeV)", fontsize=0.8*fontsize_map['cms_title'])
            # Save plot 
            ext_str = f".{opt.ext}" if opt.ext != "" else ""
            fig.savefig(f"{opt.plot_path}/hgg.{eta_region}.{xvar_name}{ext_str}.pdf", bbox_inches="tight")
            fig.savefig(f"{opt.plot_path}/hgg.{eta_region}.{xvar_name}{ext_str}.png", bbox_inches="tight")
        
            ax.cla()

            ax.hist(dfs['mc'][mask][xvar_name], bins=50, range=(0,12), weights=w, label=f"H$\\rightarrow\\gamma\\gamma$, $\\eta$-region: {eta_region} (Weighted mean = {wmean:.3f})", color=color_map['mc_pre'])
            ax.set_ylabel("Weighted events")
            ax.set_yscale("log")
            ax.set_xlabel("EGM NN reweight")
            ax.axvline(wmean, color='red', alpha=0.5)
            ax.legend(loc='best', fontsize=fontsize_map['legend'], facecolor='white', edgecolor='black', frameon=True)
            # Add text values to plot 
            mplhep.cms.label(llabel=f"Simulation {opt.cms_label}", ax=ax, rlabel="2022 postEE (13 TeV)", fontsize=0.8*fontsize_map['cms_title'])
            # Save plot 
            ext_str = f".{opt.ext}" if opt.ext != "" else ""
            fig.savefig(f"{opt.plot_path}/hgg.{eta_region}.{xvar_name}{ext_str}.log.pdf", bbox_inches="tight")
            fig.savefig(f"{opt.plot_path}/hgg.{eta_region}.{xvar_name}{ext_str}.log.png", bbox_inches="tight")

global_features = ['fixedGridRhoAll']

if opt.do_plots:
    # Build figure and axes`
    axs = []
    fig_width, fig_height = float(opt.figsize.split(",")[0]),float(opt.figsize.split(",")[1])
    fig = plt.figure(figsize=(fig_width,fig_height))
    left, width = 0.1, 0.88
    bottom = 0.1
    # Ratio plot
    height = 0.2
    ax = fig.add_axes([left,bottom,width,height])
    axs.append(ax)
    # Main plot
    bottom += height + 0.05
    height = 0.63
    ax = fig.add_axes([left,bottom,width,height])
    axs.append(ax)
    
    for xvar in opt.xvars.split(","):

        print(f" --> Plotting variable: {xvar}")
        for pho in ['lead','sublead']:

            if xvar in global_features:
                xvar_to_plot = xvar
                xvar_for_plot_details = xvar
            else:
                xvar_to_plot = f"{pho}_{xvar}"
                xvar_for_plot_details = f"probe_{xvar}"

            for eta_region in ['EB','EEplus','EEminus']:

                bins = xvar_bin_map[xvar_for_plot_details]
                if xvar not in ['pt','eta','fixedGridRhoAll']:
                   if eta_region in ['EEplus','EEminus']:
                       bins = 20

                if xvar_for_plot_details in xvar_range_map[eta_region]:
                    xrange = xvar_range_map[eta_region][xvar_for_plot_details]
                else:
                    xrange = (dfs['mc'][xvar_to_plot].min(),dfs['mc'][xvar_to_plot].max())

                if eta_region == "EB":
                    mask = abs(dfs['mc'][f'{pho}_ScEta']) < 1.5
                elif eta_region == "EEplus":
                    mask = dfs['mc'][f'{pho}_ScEta'] > 1.5
                elif eta_region == "EEminus":
                    mask = dfs['mc'][f'{pho}_ScEta'] < -1.5
        
                hists = {}
        
                if xvar in ['pt','eta','fixedGridRhoAll']:
                    mc_types = ['pre','nn']
                else:
                    mc_types = ['pre','nn','flow']
        
                weights = {}
                for mc_type in mc_types:
                    if mc_type == "pre": 
                        xvar_name = translate(xvar, xvar_input_name_map)
                        xvar_to_plot_name = re.sub(xvar, xvar_name, xvar_to_plot) 
                        weights[mc_type] = dfs['mc']['weight']
                
                    elif mc_type == "nn":
                        xvar_name = translate(xvar, xvar_input_name_map)
                        xvar_to_plot_name = re.sub(xvar, xvar_name, xvar_to_plot) 
                        weights[mc_type] = dfs['mc']['weight']*dfs['mc']['lead_egmReweightingFactor']*dfs['mc']['sublead_egmReweightingFactor']
        
                    elif mc_type == "flow":
                        xvar_to_plot_name = xvar_to_plot
                        weights[mc_type] = dfs['mc']['weight']

                    weights[mc_type] = weights[mc_type][mask]
                    hists[f"mc_{mc_type}"] = axs[1].hist(dfs['mc'][xvar_to_plot_name][mask], bins=bins, range=xrange, weights=weights[mc_type], color=color_map[f'mc_{mc_type}'], histtype='step')
                    hists[f"mc_{mc_type}_sumw2"] = np.histogram(dfs['mc'][xvar_to_plot_name][mask], bins=bins, range=xrange, weights=weights[mc_type]**2)
                    bin_centers = (hists[f"mc_{mc_type}"][1][:-1]+hists[f"mc_{mc_type}"][1][1:])/2
                    bin_widths = (hists[f"mc_{mc_type}"][1][1:]-hists[f"mc_{mc_type}"][1][:-1])/2
    
        
                    # Add stat unc boxes
                    for i in range(len(bin_widths)):
                        point = (bin_centers[i]-bin_widths[i],hists[f"mc_{mc_type}"][0][i]-hists[f"mc_{mc_type}_sumw2"][0][i]**0.5)
                        rect = matplotlib.patches.Rectangle(point, 2*bin_widths[i], 2*hists[f"mc_{mc_type}_sumw2"][0][i]**0.5, color=color_map[f'mc_{mc_type}'], alpha=0.3)
                        axs[1].add_patch(rect)
        
                    # Add ratio 
                    ratio = hists[f"mc_{mc_type}"][0]/hists["mc_pre"][0]
                    err = hists[f"mc_{mc_type}_sumw2"][0]**0.5/hists["mc_pre"][0]
                    for i in range(len(bin_widths)):
                        x = (bin_centers[i]-bin_widths[i], bin_centers[i]+bin_widths[i])
                        y = (ratio[i],ratio[i])
                        axs[0].plot(x, y, color=color_map[f'mc_{mc_type}'])
                        point = (bin_centers[i]-bin_widths[i], ratio[i]-err[i])
                        rect = matplotlib.patches.Rectangle(point, 2*bin_widths[i], 2*err[i], color=color_map[f'mc_{mc_type}'], alpha=0.3)
                        axs[0].add_patch(rect)
        
                axs[0].set_xlim(xrange)
                axs[1].set_xlim(xrange)
                if xvar in logy_variables:
                    axs[1].set_ylim(1e3,axs[1].get_ylim()[1]*2)
                    axs[1].set_yscale("log")
                else:
                    axs[1].set_ylim(0,axs[1].get_ylim()[1]*1.1)
                axs[0].set_xlabel(translate(xvar_to_plot,xvar_label_map))
                axs[0].set_ylabel("MC$_{corr}$ / MC ", fontsize=fontsize_map['y_label'], loc='center')
                axs[1].set_ylabel("Events", fontsize=fontsize_map['y_label'])
                if opt.ratio_lim is not None:
                    rmin, rmax = float(opt.ratio_lim.split(",")[0]), float(opt.ratio_lim.split(",")[1])
                    axs[0].set_ylim(rmin,rmax)
                else:
                    axs[0].set_ylim(0.75,1.25)
                axs[0].axhline(1, color='grey', alpha=0.5)
        
                # Add legend
                handles, labels = [], []
                for mc_type in mc_types:
                    line = matplotlib.lines.Line2D([],[], color=color_map[f'mc_{mc_type}'], linewidth=2)
                    rect = matplotlib.patches.Rectangle((0,0), 0, 0, facecolor=color_map[f'mc_{mc_type}'], alpha=0.3)
                    handle = (line,rect)
                    handles.append(handle)
                    if mc_type == "pre":
                        labels.append("MC nominal")
                    else:
                        labels.append(label_map[mc_type])
                # Add dummy for eta region
                line = matplotlib.lines.Line2D([],[], color="white", linewidth=0)
                handles.append(line)
                eta_region_str = "H$\\rightarrow\\gamma\\gamma$, $\\eta$ region: "
                if eta_region == "inclusive":
                    eta_region_str += "inclusive"
                elif eta_region == "EB":
                    eta_region_str += "EB"
                elif eta_region == "EEplus":
                    eta_region_str += "EE+"
                elif eta_region == "EEminus":
                    eta_region_str += "EE-"
                eta_region_str += f" ({pho})"
                labels.append(eta_region_str)
                axs[1].legend(handles, labels, loc='best', fontsize=fontsize_map['legend'], facecolor='white', edgecolor='black', frameon=True)
                
                # Add text values to plot 
                mplhep.cms.label(llabel=opt.cms_label, ax=axs[1], rlabel="26.67 fb$^{-1}$, 2022 postEE (13 TeV)", fontsize=fontsize_map['cms_title'])
                
                # Save plot 
                ext_str = f".{opt.ext}" if opt.ext != "" else ""
                fig.savefig(f"{opt.plot_path}/hgg.{pho}.{eta_region}.{xvar_to_plot_name}{ext_str}.pdf", bbox_inches="tight")
                fig.savefig(f"{opt.plot_path}/hgg.{pho}.{eta_region}.{xvar_to_plot_name}{ext_str}.png", bbox_inches="tight")
        
                axs[0].cla()
                axs[1].cla()
        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
