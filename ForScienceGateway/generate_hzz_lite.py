import ROOT
ROOT.gROOT.SetBatch(True)
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import json

plot_dir = "/eos/user/j/jlangfor/www/CMS/postdoc/hcomb/ScienceGateway/category_plots"

# Load workspace
f = ROOT.TFile("/afs/cern.ch/work/j/jlangfor/postdoc/hcomb/combination/Aug22/CMSSW_11_2_0/src/summer21/initialfit/hzz/higgsCombine.initial.hzz.A1_mu.observed.MultiDimFit.mH125.38.123456.root")
w = f.Get("w")
# With postfit then loadSnapshot
w.loadSnapshot("MultiDimFit")

# Extract pdfs for all categories
cat = w.cat("CMS_channel")
n_cats = cat.size()
cats = []
for i in range(n_cats): 
    cat.setIndex(i)
    cats.append( cat.getLabel() )

# Define variables
mass = w.var("ZZMass")

# Asimov generation: parameters
N = 25 # number of events
n_tubes = 6 # number of tubes (bins)
lo,hi = 110,133 # tube range

# Mass points to write to json file
mass_points_file = {}

# Build matplotlib figure
fig, ax = plt.subplots()

for i,cat in enumerate(cats):
    print("\n\n\n --> Processing cat: %s [%g/%g]"%(cat,i+1,len(cats)))

    pdf = w.pdf("pdf_bin%s"%cat)

    # Plot pdf
    fr = mass.frame()
    pdf.plotOn(fr)
    can = ROOT.TCanvas()
    fr.Draw()
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

    # Plot cdf and inverse
    ax.plot(x,y,label="CDF")
    ax.set_xlabel("$m_{4l}$ [GeV]", fontsize=16)
    ax.legend(loc='best')
    fig.savefig("%s/cdf_postfit_%s.png"%(plot_dir,cat))
    ax.cla()

    ax.plot(y,x,label="Inverse CDF")
    ax.set_ylabel("$m_{4l}$ [GeV]", fontsize=16)
    ax.legend(loc='best')
    fig.savefig("%s/cdf_inv_postfit_%s.png"%(plot_dir,cat))
    ax.cla()

    # Find 25 equally spaced points in cdf inmass range
    mass.setVal(lo)
    cdf_lo = cdf.getVal()
    mass.setVal(hi)
    cdf_hi = cdf.getVal()
    cdf_points = np.linspace(cdf_lo, cdf_hi, N+1)
    # Add half the spacing so not always starting at same number
    cdf_points = cdf_points[:-1]+0.5*(cdf_points[1]-cdf_points[0])

    # Generate the asimov mass points from the inverse cdf and shuffle
    mass_points_asimov = cdf_inv(cdf_points)
    # Shuffle mass points
    np.random.shuffle(mass_points_asimov)

    # Plot histogram
    ax.hist( mass_points_asimov, bins=n_tubes, range=(lo,hi), label="Asimov dataset")
    ax.set_xlabel("$m_{4l}$ [GeV]", fontsize=16)
    ax.set_ylabel("Counts", fontsize=16)
    ax.legend(loc='best')
    fig.savefig("%s/hist_asimov_postfit_%s.png"%(plot_dir,cat))
    ax.cla()

    # Write out mass values to file
    mass_points_file[cat] = list(mass_points_asimov)

# Write out mass points to json file
with open("asimov_m4l_n%s_tubes%s.json"%(N,n_tubes), "w") as jf:
    json.dump(mass_points_file, jf, indent=True)


