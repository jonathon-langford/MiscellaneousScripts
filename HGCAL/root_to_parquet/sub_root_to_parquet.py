import subprocess
import os
import re

def write_preamble(_file):
    _file.write("#!/bin/bash\n")
    _file.write("ulimit -s unlimited\n")
    _file.write("source ~/.bashrc\n")
    _file.write("cd %s\n"%os.environ['PWD'])
    _file.write("conda activate hgcal-l1t-analysis-jet\n")

from optparse import OptionParser
def get_options():
    parser = OptionParser()
    parser.add_option('-i','--in-dir', dest='in_dir', default=None)
    parser.add_option('-s','--sub-dir', dest="sub_dir", default='.')
    parser.add_option('-o','--out-dir', dest="out_dir", default='.')
    parser.add_option('-e','--ext', dest="ext", default='')
    parser.add_option('--gen-particle',dest="gen_particle", default="photon")
    parser.add_option('--save-tc',dest="save_tc", default=False, action="store_true")
    parser.add_option('--save-PU',dest="save_PU", default=False, action="store_true")
    parser.add_option('--skip-signal',dest="skip_signal", default=False, action="store_true")
    parser.add_option('--do-merge',dest="do_merge", default=False, action="store_true")
    parser.add_option('-n', '--nJobs', dest="nJobs", default=-1, type='int')
    return parser.parse_args()
(opt,args) = get_options()

do_merge = opt.do_merge
sub_dir = opt.sub_dir
ext_str = "_%s"%opt.ext if opt.ext != '' else ''

option_str = "--gen-particle %s"%opt.gen_particle
if opt.save_tc: option_str += " --save-tc"
if opt.save_PU: option_str += " --save-PU"
if opt.skip_signal: option_str += " --skip-signal"

file_list = subprocess.getoutput("xrdfs root://gfe02.grid.hep.ph.ic.ac.uk:1097 ls %s"%opt.in_dir).split("\n")

if not os.path.isdir(sub_dir): os.system("mkdir -p %s"%sub_dir)

#if do_merge:
#    f_sub = open("%s/sub_merge.sh"%sub_dir, "w" )
#    write_preamble(f_sub)
#    f_sub.write("python merge_parquet.py -i %s --gen-particle %s --do-cl3d --do-tc"%(opt.out_dir,opt.gen_particle))
#    f_sub.close()
#
#    os.system("chmod 775 %s/sub_merge.sh"%(sub_dir)
#
#    f_sub_name = "%s/%s/sub_merge.sh"%(os.environ['PWD'],sub_dir)
#    f_out_name = re.sub("\.sh",".out",f_sub_name)
#    f_err_name = re.sub("\.sh",".err",f_sub_name)
#    cmd = "qsub -q hep.q -l h_rt=1:0:0 -l h_vmem=24G -pe hep.pe 2 -o %s -e %s %s"%(f_out_name,f_err_name,f_sub_name)
#    print(cmd)
#    os.system(cmd)

file_itr = 0
files_to_submit = []
for i, f in enumerate(file_list):

    if( file_itr > opt.nJobs )&( opt.nJobs != -1 ): continue

    if ".root" not in f.split("/")[-1]: continue

    ff = "root://gfe02.grid.hep.ph.ic.ac.uk:1097/%s"%f
    f_sub = open( "%s/sub_%g%s.sh"%(sub_dir,i,ext_str), "w" )
    write_preamble(f_sub)
    f_sub.write("python root_to_parquet.py -i %s -o %s %s"%(ff,opt.out_dir,option_str))
    f_sub.close()

    files_to_submit.append( file_itr )
    file_itr += 1

os.system("chmod 775 %s/*%s.sh"%(sub_dir,ext_str))
    
for i in files_to_submit:
    f_sub_name = "%s/%s/sub_%g%s.sh"%(os.environ['PWD'],sub_dir,i,ext_str)
    f_out_name = re.sub("\.sh",".out",f_sub_name)
    f_err_name = re.sub("\.sh",".err",f_sub_name)
    cmd = "qsub -q hep.q -l h_rt=0:20:0 -o %s -e %s %s"%(f_out_name,f_err_name,f_sub_name)
    print(cmd)
    os.system(cmd)
