import ROOT
ROOT.gROOT.SetBatch(True)
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

plot_dir = "/eos/user/j/jlangfor/www/CMS/postdoc/hcomb/ScienceGateway/initial_checks_v2"

# Load workspace
f = ROOT.TFile("/afs/cern.ch/work/j/jlangfor/postdoc/hcomb/combination/Aug22/CMSSW_11_2_0/src/summer21/initialfit/hzz/higgsCombine.initial.hzz.A1_mu.observed.MultiDimFit.mH125.38.123456.root")
w = f.Get("w")
# With postfit then loadSnapshot
w.loadSnapshot("MultiDimFit")

#m_sig = w.pdf("model_s")
#all_pdfs = w.allPdfs()

# Extract pdfs for all categories
cat = w.cat("CMS_channel")
n_cats = cat.size()

cats = []
for i in range(n_cats): 
    cat.setIndex(i)
    cats.append( cat.getLabel() )

# Define variables
mass = w.var("ZZMass")
#dkin = w.var("dbkg_kin")

pdfs, norms = {}, {}

#cats_to_process = ['ch1_ch37']
#for cat in cats_to_process:

for i,cat in enumerate(cats):
    print(" --> Processing cat: %s [%g/%g]"%(cat,i+1,len(cats)))

    #pdfs[cat] = w.pdf("pdf_bin%s"%cat)
    pdf = w.pdf("pdf_bin%s"%cat)
    #norms[cat] = ROOT.RooRealVar("norm_%s"%cat,"norm_%s"%cat,pdfs[cat].expectedEvents(mass))
    #norms[cat].setConstant(True)

    # Pick a certain channel
    #channel = "ch1_ch37" # Targets ggH_0j_pTH_0_10
    # Select pdf
    #pdf = pdfs[channel]
    fr = mass.frame()
    pdf.plotOn(fr)
    can = ROOT.TCanvas()
    fr.Draw()
    can.SaveAs("%s/pdf_postfit_%s.pdf"%(plot_dir,cat))
    can.SaveAs("%s/pdf_postfit_%s.png"%(plot_dir,cat))

    # Obtain cdf and its inverse
    cdf = pdf.createCdf(ROOT.RooArgSet(mass))
    x = np.linspace(mass.getMin(), mass.getMax(), 1000)
    y = []
    for ix in x:
        mass.setVal(ix)
        y.append( cdf.getVal() )
    y = np.array(y)
    # Spline of inverse cdf
    cdf_inv = CubicSpline(y,x)

    # Plot
    fig, ax = plt.subplots()
    ax.plot(x,y,label="CDF")
    ax.set_xlabel("$m_{4l}$ [GeV]", fontsize=16)
    ax.legend(loc='best')
    fig.savefig("%s/cdf_postfit_%s.pdf"%(plot_dir,cat))
    fig.savefig("%s/cdf_postfit_%s.png"%(plot_dir,cat))
    ax.cla()

    ax.plot(y,x,label="Inverse CDF")
    ax.set_ylabel("$m_{4l}$ [GeV]", fontsize=16)
    ax.legend(loc='best')
    fig.savefig("%s/cdf_inv_postfit_%s.pdf"%(plot_dir,cat))
    fig.savefig("%s/cdf_inv_postfit_%s.png"%(plot_dir,cat))
    ax.cla()

# Asimov generation: equally spaced 25 events according to cdf
n_tubes = 6 # number of bins
N = 25 # number of events

# Find cdf points between 110 and 133
lo,hi = 110,133
mass.setVal(lo)
cdf_lo = cdf.getVal()
mass.setVal(hi)
cdf_hi = cdf.getVal()
# Find 25 equally spaced points in cdf between these values
cdf_points = np.linspace(cdf_lo, cdf_hi, N+1)
# Add half the spacing so not always starting at same number
cdf_points = cdf_points[:-1]+0.5*(cdf_points[1]-cdf_points[0])

mass_points_asimov = cdf_inv(cdf_points)
# Shuffle mass points
np.random.shuffle(mass_points_asimov)

fig, ax = plt.subplots()
ax.hist( mass_points_asimov, bins=n_tubes, range=(lo,hi), label="Asimov dataset")
ax.set_xlabel("$m_{4l}$ [GeV]", fontsize=16)
ax.set_ylabel("Counts", fontsize=16)
ax.legend(loc='best')
fig.savefig("%s/hist_asimov_postfit.pdf"%plot_dir)
fig.savefig("%s/hist_asimov_postfit.png"%plot_dir)

exit(0)


# Generation
# Using inverse of CDF, generate uniform random numbers and populate PDF
N_events = 100000
data = cdf_inv(np.random.rand(N_events))

ax.hist( data, bins=70, range=(105,140), label="Toy: %g events"%N_events)
ax.set_xlabel("$m_{4l}$ [GeV]", fontsize=16)
ax.set_ylabel("Counts", fontsize=16)
ax.legend(loc='best')
fig.savefig("%s/hist_postfit.pdf"%plot_dir)
fig.savefig("%s/hist_postfit.png"%plot_dir)

exit(0)

# Make combined pdf
pdfs_alist = ROOT.RooArgList()
coeffs_alist = ROOT.RooArgList()

for cat in cats:
    pdfs_alist.add(pdfs[cat])
    coeffs_alist.add(norms[cat])

pdf_tot = ROOT.RooAddPdf("pdf_tot","pdf_tot", pdfs_alist, coeffs_alist)


#fr_dkin = dkin.frame()
#pdf_tot.plotOn(fr_dkin)
#fr_dkin.Draw()

