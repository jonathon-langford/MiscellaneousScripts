from optparse import OptionParser
import ROOT
import pandas
import uproot
import math
from collections import OrderedDict as od

def get_options():
  parser = OptionParser()
  parser.add_option('--mode',dest='mode', default="MC", help='')
  parser.add_option('--preselection',dest='preselection', default="vbf", help='')
  parser.add_option('--year',dest='year', default="2016", help='')
  return parser.parse_args()
(opt,args) = get_options()

# Define inputs
inputs_MC = [
  {'name':'diphoton_%s'%opt.year,'file':'/vols/build/cms/jwd18/public/forJonno/%s/Dipho_PAS5_%s.root'%(opt.year,opt.year),'tree':'vbfTagDumper/trees/dipho_13TeV_GeneralDipho'}
]

if opt.preselection == 'vbf':
  inputs_DD = [
    {'name':'vbf_bkg_dd_%s'%opt.year,'file':'/vols/cms/es811/Stage1categorisation/Legacy/Pass5/all/hdfs/VBF_with_DataDriven_%s_MERGEDFF_NORM_NEW.h5'%opt.year}
    ]
elif opt.preselection == 'vh':
  inputs_DD = [
    {'name':'vh_bkg_dd_%s'%opt.year,'file':'/vols/cms/es811/Stage1categorisation/Legacy/Pass5/all/hdfs/VH_with_DataDriven_%s_MERGEDFF_NORM_NEW.h5'%opt.year}
  ]
else:
  print " --> [ERROR] preselection %s not recognised. Leaving..."%opt.preselection
  sys.exit(1)

inputs_data = [
  {'file':'/vols/build/cms/jwd18/public/forJonno/2016/Data_PAS5_2016.root','tree':'vbfTagDumper/trees/Data_13TeV_GeneralDipho'},
  {'file':'/vols/build/cms/jwd18/public/forJonno/2017/Data_PAS5_2017.root','tree':'vbfTagDumper/trees/Data_13TeV_GeneralDipho'},
  {'file':'/vols/build/cms/jwd18/public/forJonno/2018/Data_PAS5_2018.root','tree':'vbfTagDumper/trees/Data_13TeV_GeneralDipho'}
]

if opt.mode == "MC": inputs = inputs_MC
elif opt.mode == 'DD': inputs = inputs_DD
else: inputs = inputs_data

# Initiate output and add vars to workspace
if opt.mode == "MC": fout = ROOT.TFile("output_presel_%s_MC_%s.root"%(opt.preselection,opt.year),"RECREATE")
elif opt.mode == "DD": fout = ROOT.TFile("output_presel_%s_DD_%s.root"%(opt.preselection,opt.year),"RECREATE")
else: fout = ROOT.TFile("output_presel_%s_data.root"%opt.preselection,"RECREATE")
ws = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
if opt.preselection == 'vbf':
  wsVars = [
    {'name':"dipho_lead_ptoM", 'default':0., 'minValue':0.2, 'maxValue':1.0, 'bins':40},
    {'name':"dipho_sublead_ptoM", 'default':0., 'minValue':0.2, 'maxValue':0.6, 'bins':40},
    {'name':"dijet_LeadJPt", 'default':0., 'minValue':40., 'maxValue':600., 'bins':40},
    {'name':"dijet_SubJPt", 'default':0., 'minValue':30., 'maxValue':400., 'bins':40},
    {'name':"dijet_abs_dEta", 'default':0., 'minValue':0., 'maxValue':6.5, 'bins':40},
    {'name':"dijet_Mjj", 'default':0., 'minValue':0., 'maxValue':1600., 'bins':40},
    {'name':"dijet_centrality", 'default':0., 'minValue':0, 'maxValue':3.2, 'bins':40},
    {'name':"dijet_dphi", 'default':0., 'minValue':0., 'maxValue':3.2, 'bins':40},
    {'name':"dijet_minDRJetPho", 'default':0., 'minValue':0., 'maxValue':3.2, 'bins':40},
    {'name':"dijet_dipho_dphi_trunc", 'default':0., 'minValue':0., 'maxValue':3.2, 'bins':40}
  ]
else:
  wsVars = [
    {'name':"dipho_lead_ptoM", 'default':0., 'minValue':0.2, 'maxValue':1.0, 'bins':40},
    {'name':"dipho_sublead_ptoM", 'default':0., 'minValue':0.2, 'maxValue':0.6, 'bins':40},
    {'name':"dijet_leadEta", 'default':0., 'minValue':-3., 'maxValue':3., 'bins':40},
    {'name':"dijet_subleadEta", 'default':0., 'minValue':-3., 'maxValue':3., 'bins':40},
    {'name':"dijet_LeadJPt", 'default':0., 'minValue':40., 'maxValue':440., 'bins':40},
    {'name':"dijet_SubJPt", 'default':0., 'minValue':30., 'maxValue':300., 'bins':40},
    {'name':"dijet_Mjj", 'default':0., 'minValue':60., 'maxValue':120., 'bins':40},
    {'name':"dijet_abs_dEta", 'default':0., 'minValue':0., 'maxValue':3.0, 'bins':40},
    {'name':"cosThetaStar", 'default':0., 'minValue':-1.0, 'maxValue':1.0, 'bins':40},
  ]


def add_vars_to_workspace(_ws,_wsVars):
  # Add weight var
  weight = ROOT.RooRealVar("weight","weight",0)
  getattr(_ws, 'import')(weight)
  # Loop over vars to enter workspace
  _vars = {}
  for var in _wsVars:
    _vars[var['name']] = ROOT.RooRealVar( var['name'], var['name'], var['default'], var['minValue'], var['maxValue'] )
    if 'bins' in var: _vars[var['name']].setBins(var['bins'])
    getattr(_ws, 'import')( _vars[var['name']], ROOT.RooFit.Silence())
add_vars_to_workspace(ws,wsVars)

# Define df vars
df_vars = ['dipho_leadIDMVA', 'dipho_subleadIDMVA', 'dipho_lead_ptoM', 'dipho_sublead_ptoM', 'dipho_pt', 'dipho_leadEta', 'dipho_subleadEta','dijet_leadEta', 'dijet_subleadEta', 'dijet_LeadJPt', 'dijet_SubJPt', 'dijet_abs_dEta', 'dijet_Mjj', 'dijet_nj', 'dipho_dijet_ptHjj', 'dijet_dipho_dphi_trunc','cosThetaStar', 'dipho_cosphi', 'vtxprob', 'sigmarv', 'sigmawv', 'weight', 'dipho_mass', 'dijet_dphi', 'dijet_minDRJetPho', 'dijet_Zep','weight']

if opt.preselection == 'vbf':
  queryString_DD = '(dipho_mass>100.) and (dipho_mass<180.) and (dipho_lead_ptoM>0.333) and (dipho_sublead_ptoM>0.25) and (dijet_LeadJPt>40.) and (dijet_SubJPt>30.) and (dijet_Mjj>250.)'
  queryString = '(dipho_mass>100.) and (dipho_mass<180.) and (dipho_leadIDMVA>-0.2) and (dipho_subleadIDMVA>-0.2) and (dipho_lead_ptoM>0.333) and (dipho_sublead_ptoM>0.25) and (dijet_LeadJPt>40.) and (dijet_SubJPt>30.) and (dijet_Mjj>250.)'
else:
  queryString_DD = '(dipho_mass>100.) and (dipho_mass<180.) and (dipho_lead_ptoM>0.333) and (dipho_sublead_ptoM>0.25) and (dijet_LeadJPt>30.) and (dijet_SubJPt>30.) and (dijet_Mjj>60.) and (dijet_Mjj<120.) and (dijet_leadEta>-2.4) and (dijet_subleadEta>-2.4) and (dijet_leadEta<2.4) and (dijet_subleadEta<2.4) and (cosThetaStar >= -1.)'
  queryString = queryString_DD + ' and (dipho_leadIDMVA>-0.2) and (dipho_subleadIDMVA>-0.2)'

# Define arg sets
args = []
for v in wsVars: args.append(v['name'])
asets = {}
for a in args:
  asets[a] = ROOT.RooArgSet()
  asets[a].add(ws.var(a))

# For MC: loop over inputs
if opt.mode == "MC":
  for i in inputs:
    f = uproot.open(i['file'])
    t = f[i['tree']]
    preselected_df = t.pandas.df(df_vars).query(queryString)
    # Drop nans
    preselected_df = preselected_df.dropna()
    print " --> Processing: %s. Events = %g"%(i['file'],len(preselected_df))
    
    # Make histograms for each arg
    hists = {}
    for a in args: hists[a] = ROOT.RooDataHist("%s_%s"%(i['name'],a),"%s_%s"%(i['name'],a),asets[a])

    # Loop over rows in dataframe and fill histograms
    for ir,r in preselected_df.iterrows():
      for a in args: 
        if a == 'dijet_centrality':
          ws.var(a).setVal( math.exp(-4.*((r['dijet_Zep']/r['dijet_abs_dEta'])**2)) )
        else:
          ws.var(a).setVal(r[a])
      # Fill
      for a in args: hists[a].add(asets[a],r['weight'])

    # Add histograms to ws
    for a in args: getattr(ws,'import')(hists[a])
  
    # Garbage removal
    del t
    del preselected_df
    for a in args: hists[a].Delete()

# For DD: extract from h5 file
elif opt.mode == "DD":
  for i in inputs:
    preselected_df = pandas.read_hdf(i['file']).query(queryString_DD)
    preselected_df = preselected_df[preselected_df['sample']=='QCD']
    # Drop nans
    preselected_df = preselected_df.dropna()
    print " --> Processing: %s. Events = %g"%(i['file'],len(preselected_df))

    # Make histograms for each arg
    hists = {}
    for a in args: hists[a] = ROOT.RooDataHist("%s_%s"%(i['name'],a),"%s_%s"%(i['name'],a),asets[a])

    # Loop over rows in dataframe and fill histograms
    for ir,r in preselected_df.iterrows():
      for a in args:
        if a == 'dijet_centrality':
          ws.var(a).setVal( math.exp(-4.*((r['dijet_Zep']/r['dijet_abs_dEta'])**2)) )
        else:
          ws.var(a).setVal(r[a])
      # Fill
      for a in args: hists[a].add(asets[a],r['weight'])

    # Add histograms to ws
    for a in args: getattr(ws,'import')(hists[a])

    # Garbage removal
    del preselected_df
    for a in args: hists[a].Delete()

# For data
else:
  # Define histograms
  hists = {}
  for a in args: hists[a] = ROOT.RooDataHist("data_%s"%a,"data_%s"%a,asets[a])
  # Loop over inputs
  for i in inputs:
    f = uproot.open(i['file'])
    t = f[i['tree']]
    preselected_df = t.pandas.df(df_vars).query(queryString)
    print " --> Processing: %s. Events = %g"%(i['file'],len(preselected_df))

    # Loop over rows in dataframe and fill histograms
    for ir,r in preselected_df.iterrows():
      for a in args:
        if a == 'dijet_centrality':
          ws.var(a).setVal( math.exp(-4.*((r['dijet_Zep']/r['dijet_abs_dEta'])**2)) )
        else:
          ws.var(a).setVal(r[a])
      # Fill
      for a in args: hists[a].add(asets[a],r['weight'])

    # Garbage removal
    del t
    del preselected_df

  # Add histograms to ws
  for a in args: 
    getattr(ws,'import')(hists[a])
    hists[a].Delete()

# Write workspace to file
ws.Write()
fout.Close() 
ws.Delete()
