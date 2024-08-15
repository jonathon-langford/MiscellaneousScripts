import numpy as np
import pandas as pd


# Print yields
def print_yields(df, nominal_label="Data", cut_string="before selection"):
    yields = {}
    yields['tot'] = df['EventWeight'].sum()
    # Per-process yields
    labels = np.unique(df['label'])
    for l in labels:
        yields[l] = df[df['label'] == l]['EventWeight'].sum()

    print(f" * {nominal_label} {cut_string}  : yield = {yields['tot']:.1f}")
    if len(labels) > 1:
        for l in labels:
            print(f"     * Process {l} : yield = {yields[l]:.1f}")

    return yields


# Apply selection to dataframes
# Default set for di-muon selection
def apply_selection(df, nominal_label="Data", print_yield=True):
    if print_yield:
        print_yields(df, nominal_label=nominal_label)

    # Trigger cut
    trigger_mask = df['triggerIsoMu24'] == 1
    if print_yield:
        print_yields(df[trigger_mask],
                     nominal_label=nominal_label,
                     cut_string="trigger cut")

    # nMuons >=2
    nmuon_mask = df['NMuon'] >= 2
    tot_mask = trigger_mask & nmuon_mask
    if print_yield:
        print_yields(df[tot_mask],
                     nominal_label=nominal_label,
                     cut_string="nMuon>=2 cut")

    # Opposite sign muons
    muon_charge_mask = df['Muon0_Charge'] * df['Muon1_Charge'] == -1
    tot_mask = trigger_mask & nmuon_mask & muon_charge_mask
    if print_yield:
        print_yields(df[tot_mask],
                     nominal_label=nominal_label,
                     cut_string="Opposite charged muons")

    # Selected dataframe
    if print_yield: print("")
    return df[tot_mask]


# Calculate dimuon pair invariant mass
def calc_invariant_mass_pair(df, pair=['Muon0', 'Muon1']):
    px = df[f'{pair[0]}_Px'] + df[f'{pair[1]}_Px']
    py = df[f'{pair[0]}_Py'] + df[f'{pair[1]}_Py']
    pz = df[f'{pair[0]}_Pz'] + df[f'{pair[1]}_Pz']
    E = df[f'{pair[0]}_E'] + df[f'{pair[1]}_E']
    M = (E**2 - px**2 - py**2 - pz**2)**0.5
    return M


color_map = {
    "dy": "yellow",
    "qcd": "brown",
    "wz": "orange",
    "single_top": "blue",
    "ww": "green",
    "zz": "purple",
    "wjets": "skyblue",
    "ttbar": "red"
}
