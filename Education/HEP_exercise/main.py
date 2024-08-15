import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import uproot
import awkward as ak

from tools import *

# Load data, signal and background
dfs = [pd.read_csv('data_0.csv'), pd.read_csv('data_1.csv')]
data = pd.concat(dfs)
signal = pd.read_csv('signal.csv')
background = pd.read_csv('background.csv')

# Apply selection
#data_sel = apply_selection(data, nominal_label="Data", print_yield=True)
#signal_sel = apply_selection(signal, nominal_label="Signal (ttbar)", print_yield=True)
#background_sel = apply_selection(background, nominal_label="Background", print_yield=True)

# Add high-level variables
# Calculate invariant mass of muon pair
#data_sel.loc[:,'Dimuon_mass'] = calc_invariant_mass_pair(data_sel, pair=['Muon0','Muon1'])
#signal_sel.loc[:,'Dimuon_mass'] = calc_invariant_mass_pair(signal_sel, pair=['Muon0','Muon1'])
#background_sel.loc[:,'Dimuon_mass'] = calc_invariant_mass_pair(background_sel, pair=['Muon0','Muon1'])

# Machine learning ????

# Make plot
# Two histograms: one showing simulation (sig+bkg) vs data, other showing sig vs bkg
#xvar = "Dimuon_mass"
#nbins = 40
#x_range = (0,200)

#fig, axs = plt.subplots(1,2, figsize=(12,6))
# Plot data
#n_data, edges = np.histogram(data_sel[xvar], bins=nbins, range=x_range)
#bin_centers = (edges[:-1]+edges[1:])/2
#axs[0].errorbar(bin_centers, n_data, np.sqrt(n_data), fmt="ko", label="Data")
# Plot signal and background in a stacked histogram
#x_stack, col_stack, label_stack, weight_stack = [], [], [], []
# Loop over different types of background
#for bkg in np.unique(background_sel['label']):
#    mask = background_sel['label'] == bkg
#    x_stack.append(background_sel[mask][xvar])
#    col_stack.append(color_map[bkg])
#    label_stack.append(bkg)
#    weight_stack.append(background_sel[mask]['EventWeight'])
# Signal
#x_stack.append(signal_sel[xvar])
#col_stack.append(color_map['ttbar'])
#label_stack.append('ttbar')
#weight_stack.append(signal_sel['EventWeight'])
# Add axis labels and legend
#axs[0].hist( x_stack, bins=nbins, range=x_range, color=col_stack, label=label_stack, weights=weight_stack, stacked=True)
#axs[0].set_yscale("log")
#axs[0].legend(loc='best')
#axs[0].set_xlabel(xvar)
#axs[0].set_ylabel("Events")

# Second axis: plot sig vs background comparison
#axs[1].hist( background_sel[xvar], bins=nbins, range=x_range, histtype='step', color='grey', label='Background', weights=background_sel['EventWeight']/background_sel['EventWeight'].sum())
#axs[1].hist( signal_sel[xvar], bins=nbins, range=x_range, histtype='step', color='red', label='Signal', weights=signal_sel['EventWeight']/signal_sel['EventWeight'].sum())
#axs[1].set_yscale("log")
#axs[1].legend(loc='best')
#axs[1].set_xlabel(xvar)
#axs[1].set_ylabel("Fraction of events")

#fig.show()

