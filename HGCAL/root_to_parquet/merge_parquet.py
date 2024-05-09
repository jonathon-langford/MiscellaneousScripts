import pandas as pd
import re
import glob

from optparse import OptionParser
def get_options():
    parser = OptionParser()
    parser.add_option('-i','--in-dir', dest='in_dir', default=None)
    parser.add_option('-e','--ext', dest='ext', default=None)
    parser.add_option('--do-cl3d', dest='do_cl3d', default=False, action="store_true")
    parser.add_option('--do-tc', dest='do_tc', default=False, action="store_true")
    return parser.parse_args()
(opt,args) = get_options()

# Cl3d files
if opt.do_cl3d:
    files = glob.glob("%s/*%s_cl3d.parquet"%(opt.in_dir,opt.ext))
    dfs = []
    for f in files:
        print(" --> Merging file: %s"%f)
        dfs.append( pd.read_parquet(f, engine="pyarrow") )
    df = pd.concat(dfs)
    out_file = "%s/%s_cl3d_merged.parquet"%(opt.in_dir,opt.ext)
    df.to_parquet( out_file, engine="pyarrow" )
    print(" --> Successfully merged cl3d files: %s"%out_file)
    
if opt.do_tc:
    # TC files
    files = glob.glob("%s/*%s_tc.parquet"%(opt.in_dir,opt.ext))
    dfs = []
    for f in files:
        print(" --> Merging file: %s"%f)
        d = pd.read_parquet(f, engine="pyarrow")
        dfs.append( d )
    df = pd.concat(dfs)
    out_file = "%s/%s_tc_merged.parquet"%(opt.in_dir,opt.ext)
    df.to_parquet( out_file, engine="pyarrow" )
    print(" --> Successfully merged tc files: %s"%out_file)



