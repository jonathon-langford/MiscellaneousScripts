# IC hadding

This repo contains a couple of scripts used to efficiently hadd flashgg signal workspaces using the IC lx machines. 
The basic usage is described below.

## Default workflow

Go to the directory with the output signal files, with a structure like the following
```
cd /vols/cms/es811/HggGeneral/WorkspaceTest/Pass3/2016/Sig/Raw/
```
where you can copy / clone / set up these scripts.

Next, you can try to hadd the files for each process (i.e. ggH, VBF, etc) in one go:
```
./doHadding.py --doSetting
./doHadding.py --doHadding
```
this submits jobs to the batch to do the hadding; wait for the jobs to end.
Usually it works, but sometimes the output file has not been written properly. 
For now this has to be checked manually (normally just for the ggH and VBF 125 mass point, by going into the output workspace and checking you can print it), but would ideally be automated in future.
If this has worked, continue as below. Otherwise see the later section on the backup script.

Continue by splitting into the individual STXS bins (again wait for jobs on batch to finish, this is the step which takes the longest).
Once that is done (not known to fail) the final step is to move the output files back up to the directory not described as raw.
```
./doHadding.py --doSplitting
./doHadding.py --doMoving
```

Hopefully you now have the ready-for-use workspaces, which you can copy to your input directory ready for signal and background modelling.

## Backup workflow

In case the hadding step above fails for whatever reason, you should have a set of files with the word intermediate in the name. 
First check that these are at least ok for use. 
If they are, then this alternative workflow will do the splitting into STXS bins first, before hadding at the end, to avoid truly massive files along the way.

To use, go into the individual process directory where the hadding has failed, then run the splitting for the individual files.
```
cd ggH/
./backupHadding.py --doSplitting
```
as before, this will submit jobs to do the splitting, which can take a little while.

Once the jobs are done, rearrange the files into their bins before hadding them.
```
./backupHadding.py --doMoving
./backupHadding.py --doHadding
```

Wait for those jobs to finish, then move the files back. You're done, hopefully.
```
./backupHadding.py --doFinalMove
```
