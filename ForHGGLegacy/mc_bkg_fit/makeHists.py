import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import json
import math
from collections import OrderedDict as od

def get_options():
  parser = OptionParser()
  parser.add_option('--fit',dest='fit', default="2d_lead_sublead", help='')
  return parser.parse_args()
(opt,args) = get_options()

def prettyName(o):
  o = re.sub("dipho_","",o)
  return o

if opt.fit == "all_lead_sublead": 
  rateParams = {'diphoton':0.515343,'gjet':2.36824,'qcd':1.96056}
  fit_name = "All Diphoton BDT inputs"
elif opt.fit == "all_max_min": 
  rateParams = {'diphoton':1.21774,'gjet':1.56101,'qcd':2.16867}
  fit_name = "All Diphoton BDT inputs (max,min)"
elif opt.fit == "lead_sublead_only": 
  rateParams = {'diphoton':0.336059,'gjet':2.31937,'qcd':2.0507}
  fit_name = "leadIDMVA and subleadIDMVA only"
elif opt.fit == "max_min_only": 
  rateParams = {'diphoton':1.56126,'gjet':0.327762,'qcd':2.74169}
  fit_name = "maxIDMVA and minIDMVA only"
else:
  print " [ERROR] Fit not recognized. Leaving.."
  sys.exit(1)

lumi = {'2016':35.9,'2017':41.5,'2018':59.7}
observables = ['dipho_lead_ptoM','dipho_sublead_ptoM','dipho_leadIDMVA','dipho_subleadIDMVA','dipho_maxIDMVA','dipho_minIDMVA','dipho_leadEta','dipho_subleadEta','CosPhi','vtxprob','sigmarv','sigmawv']

ws = {}
ws['2016'] = ROOT.TFile("output_MC_2016.root").Get("cms_hgg_13TeV")
ws['2017'] = ROOT.TFile("output_MC_2017.root").Get("cms_hgg_13TeV")
ws['2018'] = ROOT.TFile("output_MC_2018.root").Get("cms_hgg_13TeV")
ws['data'] = ROOT.TFile("output_data.root").Get("cms_hgg_13TeV")

# Extract MC hists
hists = {}
for year in ['2016','2017','2018']:
  for mc in ['diphoton','gjet','qcd']:
    for obs in observables:
      xvar = ws[year].var(obs)
      alist = ROOT.RooArgList()
      alist.add(xvar)
      d = ws[year].data("%s_%s_%s"%(mc,year,obs))
      hists["%s_%s_%s"%(mc,year,obs)] = xvar.createHistogram("h_%s_%s_%s"%(mc,year,obs))
      d.fillHistogram(hists["%s_%s_%s"%(mc,year,obs)],alist)
      # Scale according to rate params and lumi
      hists["%s_%s_%s"%(mc,year,obs)].Scale(rateParams[mc]*lumi[year])

# Sum histograms for different years
hists_sum = {}
colorMap = {'diphoton':ROOT.kCyan-4,'gjet':ROOT.kAzure+1,'qcd':ROOT.kBlue-3}
for mc in ['diphoton','gjet','qcd']:
  for obs in observables:
    hists_sum["%s_%s"%(mc,obs)] = hists["%s_2016_%s"%(mc,obs)]+hists["%s_2017_%s"%(mc,obs)]+hists["%s_2018_%s"%(mc,obs)]
    hists_sum["%s_%s"%(mc,obs)].SetLineColor(1)
    hists_sum["%s_%s"%(mc,obs)].SetFillColor(colorMap[mc])
# Make HStacks
hstacks = {}
hists_total = {}
for obs in observables:
  hstacks[obs] = ROOT.THStack("h_%s"%(obs),"")
  for mc in ['diphoton','gjet','qcd']: hstacks[obs].Add(hists_sum["%s_%s"%(mc,obs)])
  hists_total[obs] = hists_sum["diphoton_%s"%obs]+hists_sum["gjet_%s"%obs]+hists_sum["qcd_%s"%obs]

# Extract data hists
histsdata = {}
for obs in observables:
  xvar = ws['data'].var(obs)
  alist = ROOT.RooArgList()
  alist.add(xvar)
  d = ws['data'].data("data_%s"%obs)
  histsdata[obs] = xvar.createHistogram("h_data_%s"%obs)
  d.fillHistogram(histsdata[obs],alist)
  histsdata[obs].SetMarkerColor(ROOT.kRed)
  histsdata[obs].SetMarkerStyle(20)
  histsdata[obs].SetLineColor(1)

# Make ratio hist
histsratio = {}
for obs in observables:
  histsratio[obs] = histsdata[obs].Clone()
  histsratio[obs].Reset()
  for ibin in range(1,histsratio[obs].GetNbinsX()+1):
    dval, derr = histsdata[obs].GetBinContent(ibin), histsdata[obs].GetBinError(ibin)
    mcval = hists_total[obs].GetBinContent(ibin)
    if mcval == 0: continue
    else: 
      r, rerr = float(dval)/mcval, float(derr)/mcval
      histsratio[obs].SetBinContent(ibin,r)
      histsratio[obs].SetBinError(ibin,rerr)
  histsratio[obs].SetMarkerColor(ROOT.kRed)
  histsratio[obs].SetMarkerStyle(20)
  histsratio[obs].SetLineColor(1)

# Loop over histograms and make a canvas
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)
for obs in observables:
  canv = ROOT.TCanvas("canv_%s"%obs,"canv_%s"%obs,800,700)
  lat = ROOT.TLatex()
  lat.SetTextFont(42)
  lat.SetTextAlign(11)
  lat.SetNDC()
  lat.SetTextSize(0.045)
  lat.DrawLatex(0.1,0.92,"#bf{CMS} #it{Preliminary}")
  lat.DrawLatex(0.64,0.92,"137 fb^{-1} (13 TeV)")

  pad1 = ROOT.TPad("pad1_%s"%obs,"pad1_%s"%obs,0,0.15,1,0.9)
  pad1.SetTickx()
  pad1.SetTicky()
  pad1.SetBottomMargin(0.22)
  pad1.SetTopMargin(0.000001)
  pad1.SetLogy()
  pad1.Draw()
  pad2 = ROOT.TPad("pad2_%s"%obs,"pad2_%s"%obs,0,0,1,0.3)
  pad2.SetTickx()
  pad2.SetTicky()
  pad2.SetTopMargin(0.000001)
  pad2.SetBottomMargin(0.25)
  pad2.Draw()
  padSizeRatio = 0.85/0.3

  # Nominal plot
  pad1.cd()
  h_axes = hists_total[obs].Clone()
  h_axes.Reset()
  h_axes.SetMaximum(8e6)
  h_axes.SetMinimum(1e3)
  h_axes.SetTitle("")
  h_axes.GetXaxis().SetTitle("")
  h_axes.GetXaxis().SetLabelSize(0)
  h_axes.GetYaxis().SetTitle("Events")
  h_axes.GetYaxis().SetTitleSize(0.05)
  h_axes.GetYaxis().SetTitleOffset(0.9)
  h_axes.GetYaxis().SetLabelSize(0.035)
  h_axes.GetYaxis().SetLabelOffset(0.007)
  h_axes.Draw()
  hstacks[obs].Draw("Same H")
  histsdata[obs].Draw("Same PE")
  h_axes.Draw("SAME AXIS")
  # Add latex and legend
  lat = ROOT.TLatex()
  lat.SetTextFont(42)
  lat.SetTextAlign(11)
  lat.SetNDC()
  lat.SetTextSize(0.045)
  lat.DrawLatex(0.15,0.93,"%s"%fit_name)
  lat.DrawLatex(0.15,0.87,"#hat{#mu}_{#gamma-#gamma}=%.2f, #hat{#mu}_{#gamma-j}=%.2f, #hat{#mu}_{j-j}=%.2f"%(rateParams['diphoton'],rateParams['gjet'],rateParams['qcd']))
  # Legend
  leg = ROOT.TLegend(0.7,0.73,0.88,0.98)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)
  leg.SetLineWidth(0)
  leg.SetTextSize(0.045)
  leg.AddEntry(histsdata[obs],"Data","ep")
  leg.AddEntry(hists_sum['diphoton_%s'%obs],"#gamma-#gamma","F")
  leg.AddEntry(hists_sum['gjet_%s'%obs],"#gamma-j","F")
  leg.AddEntry(hists_sum['qcd_%s'%obs],"j-j","F")
  leg.Draw("Same")
  
  # Ratio plot
  pad2.cd()
  hr_axes = histsratio[obs].Clone()
  hr_axes.Reset()
  hr_axes.SetMaximum(1.99)
  hr_axes.SetMinimum(0.01)
  hr_axes.SetTitle("")
  hr_axes.GetXaxis().SetTitle(prettyName(obs))
  hr_axes.GetXaxis().SetTitleSize(0.04*padSizeRatio)
  hr_axes.GetXaxis().SetTitleOffset(0.8)
  hr_axes.GetXaxis().SetLabelSize(0.03*padSizeRatio)
  hr_axes.GetYaxis().SetTitle("Data/MC")
  hr_axes.GetYaxis().CenterTitle()
  hr_axes.GetYaxis().SetTitleSize(0.04*padSizeRatio)
  hr_axes.GetYaxis().SetTitleOffset(1.0/padSizeRatio)
  hr_axes.GetYaxis().SetLabelSize(0.025*padSizeRatio)
  hr_axes.GetYaxis().SetLabelOffset(0.007)
  hr_axes.Draw()
  # Draw lines
  hlines = {}
  hvals = [0.2,0.4,0.6,0.8,1.0,1.2,1.4,1.6,1.8]
  for i in range(len(hvals)):
    v = hvals[i]
    hlines['line_%g'%i] = ROOT.TLine(hr_axes.GetXaxis().GetXmin(),v,hr_axes.GetXaxis().GetXmax(),v)
    if v == 1.: hlines['line_%g'%i].SetLineColor(ROOT.kBlack)
    else: hlines['line_%g'%i].SetLineColorAlpha(ROOT.kGray,0.5)
    hlines['line_%g'%i].Draw("SAME")
  histsratio[obs].Draw("Same PE")

  # Save canvas
  canv.Print("./Plots/%s_fit_%s.pdf"%(obs,opt.fit))
  canv.Print("./Plots/%s_fit_%s.png"%(obs,opt.fit))

