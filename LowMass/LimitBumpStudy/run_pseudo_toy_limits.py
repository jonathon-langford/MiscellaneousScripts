import os, sys                                                                              
import re                                                                                   
from optparse import OptionParser                                                           
import ROOT

def run(cmd):
  print("%s\n\n"%cmd)
  os.system(cmd)

def write_preamble(_file):
  _file.write("#!/bin/bash\n")
  _file.write("ulimit -s unlimited\n")
  _file.write("set -e\n")
  _file.write("cd %s/src\n"%os.environ['CMSSW_BASE'])
  _file.write("export SCRAM_ARCH=%s\n"%os.environ['SCRAM_ARCH'])
  _file.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
  _file.write("eval `scramv1 runtime -sh`\n")
  _file.write("cd %s\n"%os.environ['PWD'])

def write_condor_sub(_file,_exec,_queue,_nJobs,_jobOpts='',doHoldOnFailure=True,doPeriodicRetry=True):
  _file.write("executable = %s.sh\n"%_exec)
  _file.write("arguments  = $(ProcId)\n")
  _file.write(f"output     = %s.$(ClusterId).$(ProcId).out\n"%_exec)
  _file.write(f"error      = %s.$(ClusterId).$(ProcId).err\n"%_exec)
  _file.write(f"log       = %s.$(ClusterId).log\n\n"%_exec)
  if _jobOpts != '': 
    _file.write("# User specified job options\n")
    for jo in _jobOpts.split(":"): _file.write("%s\n"%jo)
    _file.write("\n")
  if doHoldOnFailure:
    _file.write("# Send the job to Held state on failure\n")
    _file.write("on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)\n\n")
  if doPeriodicRetry:
    _file.write("# Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.\n")
    _file.write("periodic_release =  (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > 600)\n\n")
    _file.write("+JobFlavour = \"%s\"\n"%_queue)
  _file.write("queue %g"%_nJobs)

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input RooWorkspace file. If loading snapshot then use a post-fit workspace where the option --saveWorkspace was set")
  parser.add_option("--loadSnapshot", dest="loadSnapshot", default=None, help="Load best-fit snapshot name")
  parser.add_option('--mass', dest='mass', default='125.38', help="Higgs mass")
  parser.add_option('--expectSignal', dest='expectSignal', default='0', help="Expected signal strength. Default = 0")
  parser.add_option('--nToys', dest='nToys', default=10, type='int', help="Number of toys")
  parser.add_option('--queue', dest='queue', default='longlunch', help="Condor queue")
  parser.add_option('--ext', dest='ext', default='', help="Extension")
  parser.add_option('--freezePdfIndex', dest='freezePdfIndex', default=False, action="store_true", help="Add commands for freezing PDF indices")
  parser.add_option('--dry-run', dest='dry_run', default=False, action="store_true", help="No submission")
  return parser.parse_args()
(opt,args) = get_options()

# Make job directory
ext_str = "" if opt.ext == "" else f"_{opt.ext}"
jobdir = f"jobdir_expectSignal{opt.expectSignal}{ext_str}"
os.makedirs(jobdir, exist_ok=True)

executable = f"condor_pseudo_toy_study{ext_str}"
f = open(f"{jobdir}/{executable}.sh", "w")
write_preamble(f)

loadSnapshot_str = f"--snapshotName {opt.loadSnapshot}" if opt.loadSnapshot is not None else ""
pdfindex_str = ",".join([cat.GetName() for cat in ROOT.TFile(opt.inputWSFile).Get("w").allCats() if "pdfindex" in cat.GetName()])
freeze_param_str = "MH"
if opt.freezePdfIndex:
    freeze_param_str += f",{pdfindex_str}"

pwd = os.environ['PWD']

for i_toy in range(opt.nToys):
    seed = 123 + i_toy
    f.write("if [ $1 -eq %g ]; then\n"%i_toy)
    f.write(f"    cd {jobdir}\n")
    f.write(f"    combine {pwd}/{opt.inputWSFile} -m {opt.mass} -M GenerateOnly -t 1 -s {seed} -n _gen_pseudo_toy_{seed} --saveToys --expectSignal {opt.expectSignal} {loadSnapshot_str}\n")

    # Extract toy file name
    pseudo_toy_file = f"higgsCombine_gen_pseudo_toy_{seed}.GenerateOnly.mH{opt.mass}.{seed}.root"

    # Make scratch_dir for running limits
    scratch_dir = f"scratch_pseudo_toy_{seed}"
    f.write(f"    mkdir -p {scratch_dir}; mv {pseudo_toy_file} {scratch_dir}/; cd {scratch_dir}\n")
    f.write("    for mh in {70..115}; do combine --freezeParameters %s --cminDefaultMinimizerStrategy 0 -M AsymptoticLimits -m ${mh} -d %s/%s %s --setParameters MH=${mh} --setParameterRanges r=-1,10 -n .limits_pseudo_toy_%s --X-rtd MINIMIZER_freezeDisassociatedParams --trackPdfIndex %s --toysFile %s -t 1; done\n"%(freeze_param_str,pwd,opt.inputWSFile,loadSnapshot_str,seed,pdfindex_str,pseudo_toy_file))
    f.write("    for mh in {70..115}; do combine --freezeParameters %s --cminDefaultMinimizerStrategy 0 -M Significance -m ${mh} -d %s/%s %s --setParameters MH=${mh} --setParameterRanges r=-1,10 -n .significance_pseudo_toy_%s --X-rtd MINIMIZER_freezeDisassociatedParams --toysFile %s -t 1; done\n"%(freeze_param_str,pwd,opt.inputWSFile,loadSnapshot_str,seed,pseudo_toy_file))

    # Hadd and move up one directory
    f.write("    cd ..\n")
    f.write("    hadd -f higgsCombine.limits_pseudo_toy_%s%s.AsymptoticLimits.root %s/higgsCombine.limits_pseudo_toy_%s.AsymptoticLimits.mH*\n"%(seed,ext_str,scratch_dir,seed))
    f.write("    hadd -f higgsCombine.significance_pseudo_toy_%s%s.Significance.root %s/higgsCombine.significance_pseudo_toy_%s.Significance.mH*\n"%(seed,ext_str,scratch_dir,seed))
    # Move toy back
    f.write(f"    mv {scratch_dir}/{pseudo_toy_file} .\n")

    # Delete scratch directory
    f.write("    rm -Rf %s\n"%scratch_dir)

    # Make limits + significance plots
    f.write(f"     python3 {pwd}/plot_significance_vs_mh.py higgsCombine.significance_pseudo_toy_{seed}{ext_str}.Significance.root plots_significance pseudo_toy_{seed}{ext_str} {seed} {opt.expectSignal}\n")

    f.write("fi\n")

# Close executable file and set permissions
f.close()
os.system(f"chmod 775 {jobdir}/{executable}.sh")

# Condor submission file
fsub = open(f"{jobdir}/{executable}.sub", "w")
write_condor_sub(fsub, executable, opt.queue, opt.nToys)
fsub.close()

if not opt.dry_run:
    sub_cmd = f"cd {jobdir}; condor_submit {executable}.sub; cd .."
    run(sub_cmd)
    print("  --> Finished submitting jobs")

