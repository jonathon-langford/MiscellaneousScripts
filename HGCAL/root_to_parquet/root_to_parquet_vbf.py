import uproot
import awkward as ak
import pandas as pd
import vector
import re
import os
vector.register_awkward()
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep
mplhep.style.use("CMS")
plt.rcParams["figure.figsize"] = (12.5,10)

from timeit import default_timer as timer

from optparse import OptionParser
def get_options():
    parser = OptionParser()
    parser.add_option('-i','--input-file', dest='input_file', default=None)
    parser.add_option('-o','--out-dir', dest="out_dir", default='.')
    parser.add_option('--gen-particle',dest="gen_particle", default="vbf_jet")
    parser.add_option('--save-tc',dest="save_tc", default=False, action="store_true")
    parser.add_option('--save-PU',dest="save_PU", default=False, action="store_true")
    parser.add_option('--plot-event-display',dest="plot_event_display", default=False, action="store_true")
    parser.add_option('--skip-signal',dest="skip_signal", default=False, action="store_true")
    return parser.parse_args()
(opt,args) = get_options()

if not os.path.isdir(opt.out_dir):
    os.system(f"mkdir -p {opt.out_dir}")

# Common variables
tree_name = "l1tHGCalTriggerNtuplizer/HGCalTriggerNtuple"
genjet_pt_cut = 20
genjet_eta_cut = (1.6,2.9)
cl3d_pt_cut = 2
cl3d_pt_cut_PU = 20

variables = {
    "gen":["pt","eta","phi","pdgid","status"],
    "genjet":["pt","eta","phi","energy"],
    "tc":["energy","pt","x","y","z","layer","eta","phi","multicluster_id"],
    "cl3d":["id","pt","eta","phi","energy"]
}

objects = {}

f = uproot.open(opt.input_file)
t = f[tree_name]
print(" --> Input tree (%s) has variables: "%tree_name, t.keys())

# Extract all event information into awkward array
vars_to_save = []
for var_type in variables:
    for var in variables[var_type]:
        vars_to_save.append("%s_%s"%(var_type,var))
events = t.arrays(vars_to_save, library='ak', how='zip')

# Extract clusters and gen particles in event as four vectors
cl3d = ak.Array( events['cl3d'], with_name="Momentum4D" )
gen = ak.Array( events['gen'], with_name="Momentum4D" )
genjet = ak.Array( events['genjet'], with_name="Momentum4D" )
tc = ak.Array( events['tc'] )

# Give clusters and trigger cells in each event an event id to make sure matching is valid
n_cl3d = ak.to_list(ak.num(cl3d))
ev_id = []
for i, n in enumerate(n_cl3d):
    ev_id.append( i*np.ones(n) )
cl3d['event_id'] = ev_id
cl3d['file_id'] = opt.input_file

n_tc = ak.to_list(ak.num(tc))
ev_id = []
for i, n in enumerate(n_tc):
    ev_id.append( i*np.ones(n) )
tc['event_id'] = ev_id 
tc['file_id'] = opt.input_file

# Kinematic requirements on gen photons
gen_vbf = genjet[genjet.pt>genjet_pt_cut]
gen_vbf = gen_vbf[(abs(gen_vbf.eta)>genjet_eta_cut[0])&(abs(gen_vbf.eta)<genjet_eta_cut[1])]
# Find two outgoing quark lines in gen-collection: 5:7
gen_quarks = gen[:,5:7]
# Apply dR between genjet and outgoing quark lines
pairs = ak.cartesian({"gen_vbf":gen_vbf, "gen_quarks":gen_quarks})
dR_mask = pairs.gen_vbf.deltaR(pairs.gen_quarks) < 0.2
gen_vbf = pairs[dR_mask].gen_vbf
gen_quarks = pairs[dR_mask].gen_quarks

# Kinematic requirements on clusters
cl3d = cl3d[cl3d.pt>cl3d_pt_cut]

# Plot event schematic
if opt.plot_event_display:
    # Plot first 20 events with at-least two VBF jets
    events_to_plot = list(np.where(ak.num(gen_vbf)>=2)[0])[:20]
    fig, ax = plt.subplots()
    for i in events_to_plot:
        print(f"--> Plotting event: {i}")
        ax.scatter(np.array(gen_vbf[i].eta), np.array(gen_vbf[i].phi), label="VBF jet (genjet)", s=5*gen_vbf[i].pt, c='red')
        ax.set_xlim(-3.5,3.5)
        ax.set_ylim(-3.14,3.14)
        for v in [-3,-1.5,1.5,3]:
            ax.axvline(v, c='grey')
        # Add boxes for gen-fiducial region
        point = (-2.9,-3.14)
        rect = matplotlib.patches.Rectangle(point, 1.3, 2*3.14, color='grey', alpha=0.2) 
        ax.add_patch(rect)
        point = (1.6,-3.14)
        rect = matplotlib.patches.Rectangle(point, 1.3, 2*3.14, color='grey', alpha=0.2) 
        ax.add_patch(rect)
        # Add circles dR
        for j in range(len(gen_vbf[i])):
            point = (gen_vbf[i][j].eta, gen_vbf[i][j].phi)
            circ = matplotlib.patches.Circle(point, 0.4, ec='red', ls='--', fc='None')
            ax.add_patch(circ)
            circ = matplotlib.patches.Circle(point, 0.2, ec='orange', ls='--', fc='None')
            ax.add_patch(circ)
        ax.scatter(np.array(cl3d[i].eta), np.array(cl3d[i].phi), label="Clusters", s=5*cl3d[i].pt, ec='blue', fc='None')
        ax.scatter(np.array(gen_quarks[i].eta), np.array(gen_quarks[i].phi), label="VBF outgoing quark (gen)", marker='x', c='black')
    
        ax.set_xlabel("$\\eta$", fontsize=20)
        ax.set_ylabel("$\\phi$", fontsize=20)

        handles, labels = ax.get_legend_handles_labels()
        circ = matplotlib.patches.Circle((0,0), 0.4, ec='red', ls='--', fc='None')
        handles.append(circ)
        labels.append("dR < 0.4")
        circ = matplotlib.patches.Circle((0,0), 0.2, ec='orange', ls='--', fc='None')
        handles.append(circ)
        labels.append("dR < 0.2")
        rect = matplotlib.patches.Rectangle((0,0), 1, 1, color='grey', alpha=0.2) 
        handles.append(rect)
        labels.append("Genjet fiducial region")

        ax.legend(handles, labels,loc='best')
    
        fig.savefig(f"{opt.out_dir}/event_{i}.pdf")
        fig.savefig(f"{opt.out_dir}/event_{i}.png")
    
        ax.cla()

# Matching to define signal clusters

# Signal clusters: require dR < 0.2 with respect to VBF genjets
pairs = ak.cartesian({"gen":gen_vbf, "cl3d":cl3d})
pairs_arg = ak.argcartesian({"gen":gen_vbf, "cl3d":cl3d})
dR_mask_sig = pairs.gen.deltaR( pairs.cl3d ) < 0.2
pairs_gm = pairs[dR_mask_sig]
pairs_arg_gm = pairs_arg[dR_mask_sig]

# If multiple clusters pass requirement then define cluster with closest (typically largest) pt as "Truth cluster"
pt_diff = abs(pairs_gm.gen.pt-pairs_gm.cl3d.pt)
order = ak.argsort( pt_diff, ascending=True, axis=1 )
pt_diff = pt_diff[order]
pairs_gm_ptdiff_ordered = pairs_gm[order]
pairs_arg_gm_ptdiff_ordered = pairs_arg_gm[order]
# Skim up to max number of genjets in events
n_gen_max = ak.max( ak.num( gen_vbf ) )
arr = []
for i_gen in range( n_gen_max ):
    # Select clusters with same gen VBF jet id
    mask = pairs_arg_gm_ptdiff_ordered.gen == i_gen
    # Find cluster with smallest pt difference and add to array
    firsts = ak.firsts( pairs_gm_ptdiff_ordered[mask], axis=1 )
    # Remove nones
    firsts = firsts[~ak.is_none(firsts)]
    arr.append(firsts)

# Add gen information into one array
arr = ak.concatenate(arr)
cs = arr.cl3d
cs['genjetpt'] = arr.gen.pt
cs['genjeteta'] = arr.gen.eta
cs['genjetphi'] = arr.gen.phi
cs['genjetenergy'] = arr.gen.energy
cs['label'] = opt.gen_particle

# Build pandas dataframe and save
if not opt.skip_signal:
    df_arrays = {}
    df_arrays['file_id'] = np.array( getattr(cs,"file_id") )
    df_arrays['event_id'] = np.array( getattr(cs,"event_id") )
    for var in vars_to_save:
        if "cl3d" not in var: continue
        v = var.split("_")[-1]
        df_arrays["cl3d_%s"%v] = np.array( getattr(cs,v) )
    for v in ['genjetpt','genjeteta','genjetphi','genjetenergy','label']:
        df_arrays[v] = np.array( getattr(cs,v) )
    df = pd.DataFrame(df_arrays)
    
    # Save dataframe as parquet file
    output_file_name = "%s/%s"%(opt.out_dir, re.sub(".root","_%s_cl3d.parquet"%opt.gen_particle,opt.input_file.split("/")[-1]) )
    df.to_parquet(output_file_name, engine="pyarrow" )
    print(" --> Saved cl3d output to: %s"%output_file_name )
    
    # Build pandas dataframe for TCs
    if opt.save_tc:
        tcs = []
        for c in cs:
            x = ak.flatten( tc[ (tc.multicluster_id == c.id)&(tc.event_id == c.event_id ) ] )
            x['label'] = opt.gen_particle
            tcs.append(x)
        tcs = ak.concatenate(tcs)
    
        df_arrays = {}
        df_arrays["file_id"] = np.array( getattr(tcs,"file_id") )
        df_arrays["event_id"] = np.array( getattr(tcs,"event_id") )
        for var in vars_to_save:
            if var.split("_")[0] == "tc":
                v = "_".join( var.split("_")[1:] )
                df_arrays["tc_%s"%v] = np.array( getattr(tcs,v) )
        df_arrays["label"] = np.array( tcs.label )
        df = pd.DataFrame(df_arrays)
    
        # Save dataframe as parquet file
        output_file_name = "%s/%s"%(opt.out_dir, re.sub(".root","_%s_tc.parquet"%opt.gen_particle,opt.input_file.split("/")[-1]) )
        df.to_parquet(output_file_name, engine="pyarrow" )
        print(" --> Saved tc output to: %s"%output_file_name )

# Save PU clusters
if opt.save_PU:
    # Apply tighter pt requirement on PU clusters otherwise outputs are too large
    cl3d = cl3d[cl3d.pt>cl3d_pt_cut_PU]
    # PU clusters: require dR > 1 with respect to gen particles
    masks = []
    # Loop over events (TODO: replace with columnar approach)
    arr = []
    for i_event in range(len(cl3d)):
        cl3d_event = cl3d[i_event]
        gen_vbf_event = gen_vbf[i_event]
        mask = cl3d_event==cl3d_event
        for gp in gen_vbf_event:
            mask = mask * gp.deltaR(cl3d_event) > 1.0
        
        # Store clusters passing in array
        arr.append(cl3d_event[mask])
    cb = ak.flatten(arr)
    cb['genjetpt'] = -999
    cb['genjeteta'] = -999
    cb['genjetphi'] = -999
    cb['genjetenergy'] = -999
    cb['label'] = "PU"

    # Build pandas dataframe
    df_arrays = {}
    df_arrays['file_id'] = np.array( getattr(cb,"file_id") )
    df_arrays['event_id'] = np.array( getattr(cb,"event_id") )
    for var in vars_to_save:
        if "cl3d" not in var: continue
        v = var.split("_")[-1]
        df_arrays["cl3d_%s"%v] = np.array( getattr(cb,v) )
    for v in ['genjetpt','genjeteta','genjetphi','genjetenergy','label']:
        df_arrays[v] = np.array( getattr(cb,v) )
    df = pd.DataFrame(df_arrays)
    
    # Save dataframe as parquet file
    output_file_name = "%s/%s"%(opt.out_dir, re.sub(".root","_PU_cl3d.parquet",opt.input_file.split("/")[-1]))
    df.to_parquet(output_file_name, engine="pyarrow" )
    print(" --> Saved PU cl3d output to: %s"%output_file_name )

    if opt.save_tc:
        tcb = []
        for c in cb:
            x = ak.flatten( tc[ (tc.multicluster_id == c.id)&(tc.event_id == c.event_id ) ] )
            x['label'] = "PU"
            tcb.append(x)
        tcb = ak.concatenate(tcb)
    
        df_arrays = {}
        df_arrays["file_id"] = np.array( getattr(tcb,"file_id") )
        df_arrays["event_id"] = np.array( getattr(tcb,"event_id") )
        for var in vars_to_save:
            if var.split("_")[0] == "tc":
                v = "_".join( var.split("_")[1:] )
                df_arrays["tc_%s"%v] = np.array( getattr(tcb,v) )
        df_arrays["label"] = np.array( tcb.label )
        df = pd.DataFrame(df_arrays)
    
        # Save dataframe as parquet file
        output_file_name = "%s/%s"%(opt.out_dir, re.sub(".root","_PU_tc.parquet",opt.input_file.split("/")[-1]) )
        df.to_parquet(output_file_name, engine="pyarrow" )
        print(" --> Saved PU tc output to: %s"%output_file_name )


