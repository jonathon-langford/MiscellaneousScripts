import uproot
import awkward as ak
import pandas as pd
import vector
import re
vector.register_awkward()
import numpy as np

from timeit import default_timer as timer

from optparse import OptionParser
def get_options():
    parser = OptionParser()
    parser.add_option('-i','--input-file', dest='input_file', default=None)
    parser.add_option('-o','--out-dir', dest="out_dir", default='.')
    parser.add_option('--gen-particle',dest="gen_particle", default="photon")
    parser.add_option('--save-tc',dest="save_tc", default=False, action="store_true")
    parser.add_option('--save-PU',dest="save_PU", default=False, action="store_true")
    parser.add_option('--skip-signal',dest="skip_signal", default=False, action="store_true")
    return parser.parse_args()
(opt,args) = get_options()

# Gen pid dict
gen_pid = {
    "photon":22,
    "charged_pion":211
}

# Common variables
tree_name = "l1tHGCalTriggerNtuplizer/HGCalTriggerNtuple"
gen_pt_cut = 15
gen_eta_cut = (1.6,2.9)
cl3d_pt_cut = 10

variables = {
    "gen":["pt","eta","phi","pdgid","status"],
    "tc":["energy","pt","x","y","z","layer","eta","phi","multicluster_id"],
    "cl3d":["id","pt","eta","phi"]
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
tc = ak.Array( events['tc'] )

# Give clusters and trigger cells in each event an event id to make sure matching is valid
n_cl3d = ak.to_list(ak.num(cl3d))
ev_id = []
for i, n in enumerate(n_cl3d):
    ev_id.append( i*np.ones(n) )
cl3d['event_id'] = ev_id
cl3d['file_id'] = int( opt.input_file.split("_")[-1].split(".root")[0] )

n_tc = ak.to_list(ak.num(tc))
ev_id = []
for i, n in enumerate(n_tc):
    ev_id.append( i*np.ones(n) )
tc['event_id'] = ev_id 
tc['file_id'] = int( opt.input_file.split("_")[-1].split(".root")[0] )

# Kinematic requirements on gen photons
gen_particle = gen[(abs(gen.pdgid)==gen_pid[opt.gen_particle])&(gen.status==1)]
gen_particle = gen_particle[gen_particle.pt>gen_pt_cut]
gen_particle = gen_particle[(abs(gen_particle.eta)>gen_eta_cut[0])&(abs(gen_particle.eta)<gen_eta_cut[1])]

# Kinematic requirements on clusters
cl3d = cl3d[cl3d.pt>cl3d_pt_cut]

# Signal clusters: require dR < 0.2 with respect to gen particles
# If multiple clusters pass requirement then select cluster with minimum dR
pairs = ak.cartesian({"gen":gen_particle, "cl3d":cl3d})
pairs_arg = ak.argcartesian({"gen":gen_particle, "cl3d":cl3d})
dR_mask_sig = pairs.gen.deltaR( pairs.cl3d ) < 0.2
pairs_gm = pairs[dR_mask_sig]
pairs_arg_gm = pairs_arg[dR_mask_sig]

# Extrack min dR between cluster and gen particle
dR = pairs_gm.gen.deltaR( pairs_gm.cl3d )
order = ak.argsort( dR, ascending=True, axis=1 )
dR = dR[order]
pairs_gm_dR_ordered = pairs_gm[order]
pairs_arg_gm_dR_ordered = pairs_arg_gm[order]
# Skim up to max number of gen particles in events
n_gen_max = ak.max( ak.num( gen_particle ) )
arr = []
for i_gen in range( n_gen_max ):
    # Select clusters with same gen particle id
    mask = pairs_arg_gm_dR_ordered.gen == i_gen
    # Find cluster with smallest dR and add to array
    firsts = ak.firsts( pairs_gm_dR_ordered[mask], axis=1 )
    # Remove nones
    firsts = firsts[~ak.is_none(firsts)]
    arr.append(firsts)

# Add gen information into one array
arr = ak.concatenate(arr)
cs = arr.cl3d
cs['genpt'] = arr.gen.pt
cs['geneta'] = arr.gen.eta
cs['genphi'] = arr.gen.phi
cs['matched_pid'] = arr.gen.pdgid
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
    for v in ['genpt','geneta','genphi','matched_pid','label']:
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
    # PU clusters: require dR > 1 with respect to gen particles
    masks = []
    n_gen_max = ak.max( ak.num( gen ) )
    for i_gen in range( n_gen_max ):
        gp = gen[ak.argcartesian({"gen":gen}).gen == i_gen]
        a = ak.cartesian({"cl3d":cl3d, "gp":gp})
        masks.append( a.gp.deltaR(a.cl3d) > 1.0 )
    # Total mask
    mask = masks[0]
    for m in masks[1:]: mask = mask * m
    cb = ak.flatten( cl3d[mask] )
    cb['genpt'] = -999
    cb['geneta'] = -999
    cb['genphi'] = -999
    cb['matched_pid'] = -999
    cb['label'] = "PU"

    # Build pandas dataframe
    df_arrays = {}
    df_arrays['file_id'] = np.array( getattr(cb,"file_id") )
    df_arrays['event_id'] = np.array( getattr(cb,"event_id") )
    for var in vars_to_save:
        if "cl3d" not in var: continue
        v = var.split("_")[-1]
        df_arrays["cl3d_%s"%v] = np.array( getattr(cb,v) )
    for v in ['genpt','geneta','genphi','matched_pid','label']:
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
