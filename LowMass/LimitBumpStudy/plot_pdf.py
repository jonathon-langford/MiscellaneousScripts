import os
import sys

import ROOT
import numpy as np
import matplotlib.pyplot as plt
import mplhep

mplhep.style.use("CMS")

cat = "UntaggedTag_3_2022EE"

# Open result file with workspace
f = ROOT.TFile(sys.argv[1])
w = f.Get("w")
w.loadSnapshot("MultiDimFit")

xvar = w.var("CMS_hgg_mass")
xvar_arglist = ROOT.RooArgList(xvar)
xvar_argset = ROOT.RooArgSet(xvar)
chan = w.cat("CMS_channel")

sb_model = w.pdf("model_s")

# Set signal strength to input value
w.var("r").setVal(int(sys.argv[4]))

# Extract pseudo-toy dataset
d_toy = w.data("data_obs")

# ---------------------------------------------------------
# DATA HISTOGRAM
# ---------------------------------------------------------

h_data = xvar.createHistogram(
    "h_data",
    ROOT.RooFit.Binning(55, 65, 120)
)
h_data.SetBinErrorOption(ROOT.TH1.kPoisson)
d_toy.fillHistogram(h_data, xvar_arglist)

nbins = h_data.GetNbinsX()

edges = np.array([
    h_data.GetBinLowEdge(i)
    for i in range(1, nbins + 2)
])

centers = 0.5 * (edges[:-1] + edges[1:])

contents = np.array([
    h_data.GetBinContent(i)
    for i in range(1, nbins + 1)
])

errors = np.sqrt(contents)


# ---------------------------------------------------------
# GENERATING MODEL
# ---------------------------------------------------------

pdf = sb_model.getPdf(cat)

h_pdf = pdf.createHistogram(
    "h_pdf",
    xvar,
    ROOT.RooFit.Binning(2200, 65, 120)
)

norm_factor = pdf.expectedEvents(xvar_argset)

nbins_pdf = h_pdf.GetNbinsX()

edges_pdf = np.array([
    h_pdf.GetBinLowEdge(i)
    for i in range(1, nbins_pdf + 2)
])

centers_pdf = 0.5 * (edges_pdf[:-1] + edges_pdf[1:])

contents_pdf = np.array([
    h_pdf.GetBinContent(i)
    for i in range(1, nbins_pdf + 1)
])

# Normalise to expected number of events
contents_pdf = (
    contents_pdf
    * (norm_factor / contents_pdf.sum())
    * (len(contents_pdf) / len(contents))
)


# ---------------------------------------------------------
# BACKGROUND PDF
# ---------------------------------------------------------

bkg_pdf = w.pdf(f"shapeBkg_bkg_mass_{cat}")

pdfindex = w.cat(f"pdfindex_{cat}")
func_idx = pdfindex.getIndex()

bkg_pdf_component = bkg_pdf.getPdf(func_idx)

func_pdf = (
    bkg_pdf_component.GetName()
    .split("2022EE_")[-1]
)

# Create fine-grained histogram of background PDF
h_bkg = bkg_pdf_component.createHistogram(
    "h_bkg",
    xvar,
    ROOT.RooFit.Binning(2200, 65, 120)
)

# Expected number of background events
# Use the background PDF normalisation where available.
#
# If expectedEvents is not defined for this component,
# this can instead be obtained from the corresponding
# RooAbsReal yield in the workspace.
norm_factor_bkg = bkg_pdf_component.expectedEvents(xvar_argset)

nbins_bkg = h_bkg.GetNbinsX()

edges_bkg = np.array([
    h_bkg.GetBinLowEdge(i)
    for i in range(1, nbins_bkg + 2)
])

centers_bkg = 0.5 * (edges_bkg[:-1] + edges_bkg[1:])

contents_bkg = np.array([
    h_bkg.GetBinContent(i)
    for i in range(1, nbins_bkg + 1)
])

# Normalise background PDF
contents_bkg = (
    contents_bkg
    * (norm_factor_bkg / contents_bkg.sum())
    * (len(contents_bkg) / len(contents))
)


# ---------------------------------------------------------
# BIN BACKGROUND MODEL TO DATA BINNING
# ---------------------------------------------------------

# Use the same 55-bin binning as the data
h_bkg_bins = bkg_pdf_component.createHistogram(
    "h_bkg_bins",
    xvar,
    ROOT.RooFit.Binning(55, 65, 120)
)

contents_bkg_bins = np.array([
    h_bkg_bins.GetBinContent(i)
    for i in range(1, h_bkg_bins.GetNbinsX() + 1)
])

contents_bkg_bins = (
    contents_bkg_bins
    * (norm_factor_bkg / contents_bkg_bins.sum())
)


# ---------------------------------------------------------
# BACKGROUND-SUBTRACTED DATA
# ---------------------------------------------------------

# Absolute residual:
residual = contents - (contents_bkg_bins*contents.sum())

# ---------------------------------------------------------
# PLOT
# ---------------------------------------------------------

fig, (ax, rax) = plt.subplots(
    2,
    1,
    figsize=(8, 10),
    gridspec_kw={
        "height_ratios": [2, 1],
        "hspace": 0.05
    },
    sharex=True
)

# Main panel
ax.errorbar(
    centers,
    contents,
    yerr=errors,
    fmt="o",
    label="Pseudo toy (s=%s, r=%s)" % (
        sys.argv[3],
        sys.argv[4]
    ),
    color="black",
    ls="None"
)

ax.plot(
    centers_pdf,
    contents_pdf,
    marker="None",
    label="Generating function ($\\hat{r}$=%s): f=%s (%s)" % (
        sys.argv[4],
        func_pdf,
        func_idx
    ),
    color="red"
)

ax.set_ylabel("Entries")
ax.legend(loc="best", fontsize=16)
ax.set_xlim(65,120)


# Ratio / residual panel
rax.errorbar(
    centers,
    residual,
    yerr=errors,
    fmt="o",
    color="black",
    ls="None"
)

rax.axhline(
    0,
    linestyle="--",
    color="red"
)

rax.set_xlabel("$m_{\\gamma\\gamma}$ (GeV)")
rax.set_ylabel(r"Residual")
rax.set_ylim(-1*max(abs(residual+1.1*errors)), max(abs(residual+1.1*errors)))
rax.set_xlim(65, 120)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

if not os.path.isdir(sys.argv[2]):
    os.makedirs(sys.argv[2], exist_ok=False)

fig.savefig(
    "%s/pdf_pseudoToy%s_expectSignal%s.png" % (
        sys.argv[2],
        sys.argv[3],
        sys.argv[4]
    ),
    bbox_inches="tight"
)
