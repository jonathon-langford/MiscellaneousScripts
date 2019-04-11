import ROOT
import sys

#Open ROOT File
f_in = ROOT.TFile.Open("CMS-HGG_sigfit_mva_TTH_TTHHadronicTag_0.root")

#Extract workspace from file
ws = f_in.Get("wsig_13TeV")

#Extract RooAddPdf (Signal model) and normalisation from workspace
proc = "TTH"
category = "TTHHadronicTag_0"
print "Plotting signal model: (process,category) = (%s,%s)"%(proc,category)
sig = ws.function("hggpdfsmrel_13TeV_%s_%s"%(proc,category))
norm = ws.function("hggpdfsmrel_13TeV_%s_%s_normThisLumi"%(proc,category))

#Extract variable MH
mgg = ws.var("CMS_hgg_mass")
#Create frame to plot on
pl = mgg.frame()

#Loop over mH values
mh = ws.var("MH")
for val in range(120,130):
  mh.setVal(val)
  print "  --> Adding model for MH = %4.1f. Normalisation = %5.4f"%(val,norm.getVal())
  sig.plotOn(pl)

pl.Draw()
