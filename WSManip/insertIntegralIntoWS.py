import ROOT
import re
from collections import OrderedDict as od
from optparse import OptionParser


# Function to extract the sigma effective of a histogram
def getEffSigma(_h):
  nbins, binw, xmin = _h.GetXaxis().GetNbins(), _h.GetXaxis().GetBinWidth(1), _h.GetXaxis().GetXmin()
  mu, rms, total = _h.GetMean(), _h.GetRMS(), _h.Integral()
  # Scan round window of mean: window RMS/binWidth (cannot be bigger than 0.1*number of bins)
  nWindow = int(rms/binw) if (rms/binw) < 0.1*nbins else int(0.1*nbins)
  # Determine minimum width of distribution which holds 0.693 of total
  rlim = 0.683*total
  wmin, iscanmin = 9999999, -999
  for iscan in range(-1*nWindow,nWindow+1):
    # Find bin idx in scan: iscan from mean
    i_centre = int((mu-xmin)/binw+1+iscan)
    x_centre = (i_centre-0.5)*binw+xmin # * 0.5 for bin centre
    x_up, x_down = x_centre, x_centre
    i_up, i_down = i_centre, i_centre
    # Define counter for yield in bins: stop when counter > rlim
    y = _h.GetBinContent(i_centre) # Central bin height
    r = y
    reachedLimit = False
    for j in range(1,nbins):
      if reachedLimit: continue
      # Up:
      if(i_up < nbins)&(not reachedLimit):
        i_up+=1
        x_up+=binw
        y = _h.GetBinContent(i_up) # Current bin height
        r+=y
        if r>rlim: reachedLimit = True
      else:
        print " --> Reach nBins in effSigma calc: %s. Returning 0 for effSigma"%_h.GetName()
        return 0
      # Down:
      if( not reachedLimit ):
        if(i_down > 0):
          i_down-=1
          x_down-=binw
          y = _h.GetBinContent(i_down) #Current bin height
          r+=y
          if r>rlim: reachedLimit = True
        else:
          print " --> Reach 0 in effSigma calc: %s. Returning 0 for effSigma"%_h.GetName()
          return 0
    # Calculate fractional width in bin takes above limt (assume linear)
    if y == 0.: dx = 0.
    else: dx = (r-rlim)*(binw/y)
    # Total width: half of peak
    w = (x_up-x_down+binw-dx)*0.5
    if w < wmin:
      wmin = w
      iscanmin = iscan
  # Return effSigma
  return wmin

def get_options():
  parser = OptionParser()
  # Take inputs from config file
  parser.add_option('--inputWSFile', dest='inputWSFile', default='cms_HHbbgg_datacard_BulkGraviton800_18_01_2021_2016_2017_2018_DoubleHTag_0_13TeV.root', help="Name of input WS file (if specified will ignore other options)")
  parser.add_option('--MH', dest='MH', default=125.0, type='float', help="Higgs mass value")
  parser.add_option('--cat', dest='cat', default='ch1_DoubleHTag_0_13TeV', help="Analysis category")
  parser.add_option('--years', dest='years', default='2016,2017,2018', help="Comma separated list of years")
  parser.add_option('--proc', dest='proc', default='BulkGravitonhh800', help="Signal processes to extract effSigma")
  return parser.parse_args()
(opt,args) = get_options()


# Open workspace file and load workspace
f = ROOT.TFile(opt.inputWSFile)
w = f.Get("w")
xvar = w.var("CMS_hgg_mass")

# Set Higgs mass
w.var("MH").setVal(opt.MH)
# Category name
cat = opt.cat
catStripped = re.sub("_13TeV","","_".join(cat.split("_")[1:]))

years = opt.years.split(",")
proc = opt.proc

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Extract effSigma of signal for range in which to calculate B integral
pdfNBins = 1600
pdfName = "hggpdfsmrel_13TeV_%s_YEAR_%s"%(proc,catStripped)
normName = "n_exp_final_bin%s_proc_%s_YEAR"%(cat,proc)

hists = od()

# Build histogram of signal pdfs to extract effSigma
for year in years:
  pdf = w.pdf(re.sub("YEAR",year,pdfName))
  norm = w.function(re.sub("YEAR",year,normName)).getVal()
  hists[year] = pdf.createHistogram("h_%s"%year,xvar,ROOT.RooFit.Binning(pdfNBins))
  # Scale histograms
  hists[year].Scale(norm)

# Add histograms together
h_signal = None
for k,v in hists.iteritems():
  if h_signal is None:
    h_signal = v.Clone()
  else:
    h_signal += v

# Extract effSigma
effSigma = getEffSigma(h_signal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# Create integral of multipdf

# First set range as MHval +- effSigma
xvar.setRange("effSigma_%s"%cat,w.var("MH").getVal()-effSigma,w.var("MH").getVal()+effSigma)
xvar_argset = ROOT.RooArgSet(xvar)

# Load multipdf for category and create integral
multipdf = w.pdf("shapeBkg_bkg_mass_%s"%cat)
multipdfIntegral = multipdf.createIntegral(xvar_argset,xvar_argset,"effSigma_%s"%cat)
multipdfIntegral.SetName("shapeBkg_bkg_mass_%s_integral"%cat)

# Also create integral scaled by total number of Bkg events (actual integral)
bnorm = w.var("shapeBkg_bkg_mass_%s__norm"%cat)
# Create product of norm with integral
prod = ROOT.RooProduct("shapeBkg_bkg_mass_%s_integral_extended"%cat,"Integral of B under peak %s"%cat,ROOT.RooArgList(multipdfIntegral,bnorm))

# Add integral to workspace
w.imp = getattr(w,"import")
w.imp(prod,ROOT.RooFit.RecycleConflictNodes(),ROOT.RooFit.Silence())

# Save workspace to new file
fout = re.sub("13TeV","13TeV_wIntegral",opt.inputWSFile)
fout = ROOT.TFile(fout,"RECREATE")
w.Write()
fout.Close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Print out the truth Bkg integral for each pdfIndex
idxname = "pdfindex_%s"%"_".join(cat.split("_")[1:])
pdfindex = w.cat(idxname)
for i in range(multipdf.getNumPdfs()):
  pdfindex.setIndex(i)
  b = prod.getVal()
  print " * %g: Truth Integral(B) = %.6f"%(i,b)



