from optparse import OptionParser
import ROOT
import pandas
import uproot

def get_options():
  parser = OptionParser()
  parser.add_option('--mode',dest='mode', default="MC", help='')
  parser.add_option('--year',dest='year', default="2016", help='')
  return parser.parse_args()
(opt,args) = get_options()

# Define inputs
inputs_MC = [
  {'name':'diphoton_%s'%opt.year,'file':'/vols/build/cms/jwd18/public/forJonno/%s/Dipho_PAS5_%s.root'%(opt.year,opt.year),'tree':'vbfTagDumper/trees/dipho_13TeV_GeneralDipho'},
  {'name':'gjet_%s'%opt.year,'file':'/vols/build/cms/jwd18/public/forJonno/%s/GJet_PAS5_%s.root'%(opt.year,opt.year),'tree':'vbfTagDumper/trees/gjet_anyfake_13TeV_GeneralDipho'},
  {'name':'qcd_%s'%opt.year,'file':'/vols/build/cms/jwd18/public/forJonno/%s/QCD_PAS5_%s.root'%(opt.year,opt.year),'tree':'vbfTagDumper/trees/qcd_anyfake_13TeV_GeneralDipho'}
]

inputs_data = [
  {'file':'/vols/build/cms/jwd18/public/forJonno/2016/Data_PAS5_2016.root','tree':'vbfTagDumper/trees/Data_13TeV_GeneralDipho'},
  {'file':'/vols/build/cms/jwd18/public/forJonno/2017/Data_PAS5_2017.root','tree':'vbfTagDumper/trees/Data_13TeV_GeneralDipho'},
  {'file':'/vols/build/cms/jwd18/public/forJonno/2018/Data_PAS5_2018.root','tree':'vbfTagDumper/trees/Data_13TeV_GeneralDipho'}
]

if opt.mode == "MC": inputs = inputs_MC
else: inputs = inputs_data

# Initiate output and add vars to workspace
if opt.mode == "MC": fout = ROOT.TFile("output_MC_%s.root"%(opt.year),"RECREATE")
else: fout = ROOT.TFile("output_data.root","RECREATE")
ws = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
wsVars = [
  {'name':"dipho_lead_ptoM", 'default':0., 'minValue':0.2, 'maxValue':1.0, 'bins':40},
  {'name':"dipho_sublead_ptoM", 'default':0., 'minValue':0.2, 'maxValue':0.6, 'bins':40},
  {'name':"dipho_leadIDMVA", 'default':0., 'minValue':-1., 'maxValue':1., 'bins':40},
  {'name':"dipho_subleadIDMVA", 'default':0., 'minValue':-1., 'maxValue':1., 'bins':40},
  {'name':"dipho_maxIDMVA", 'default':0., 'minValue':-1., 'maxValue':1., 'bins':40},
  {'name':"dipho_minIDMVA", 'default':0., 'minValue':-1., 'maxValue':1., 'bins':40},
  {'name':"dipho_leadEta", 'default':0., 'minValue':-3., 'maxValue':3., 'bins':40},
  {'name':"dipho_subleadEta", 'default':0., 'minValue':-3., 'maxValue':3., 'bins':40},
  {'name':"CosPhi", 'default':0., 'minValue':-1., 'maxValue':1., 'bins':40},
  {'name':"vtxprob", 'default':0., 'minValue':0., 'maxValue':1., 'bins':40},
  {'name':"sigmarv", 'default':0., 'minValue':0., 'maxValue':0.1, 'bins':40},
  {'name':"sigmawv", 'default':0., 'minValue':0., 'maxValue':0.1, 'bins':40}
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
df_vars = ['dipho_lead_ptoM','dipho_sublead_ptoM','dipho_leadIDMVA','dipho_subleadIDMVA','dipho_leadEta','dipho_subleadEta','CosPhi','vtxprob','sigmarv','sigmawv','dipho_mass','weight']
queryString = '(dipho_mass>100.) and (dipho_mass<180.) and (dipho_lead_ptoM>0.333) and (dipho_sublead_ptoM>0.25) and (dipho_leadIDMVA>-0.9) and (dipho_subleadIDMVA>-0.9) '

# Define arg sets
args = ['dipho_lead_ptoM','dipho_sublead_ptoM','dipho_leadIDMVA','dipho_subleadIDMVA','dipho_maxIDMVA','dipho_minIDMVA','dipho_leadEta','dipho_subleadEta','CosPhi','vtxprob','sigmarv','sigmawv']
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
    print " --> Processing: %s. Events = %g"%(i['file'],len(preselected_df))
    
    # Make histograms for each arg
    hists = {}
    for a in args: hists[a] = ROOT.RooDataHist("%s_%s"%(i['name'],a),"%s_%s"%(i['name'],a),asets[a])

    # Loop over rows in dataframe and fill histograms
    for ir,r in preselected_df.iterrows():
      for a in args: 
        if a in ['dipho_maxIDMVA','dipho_minIDMVA']: continue
        ws.var(a).setVal(r[a])
      # For max and min
      if r['dipho_leadIDMVA'] >= r['dipho_subleadIDMVA']:
        ws.var("dipho_maxIDMVA").setVal(r['dipho_leadIDMVA'])
        ws.var("dipho_minIDMVA").setVal(r['dipho_subleadIDMVA'])
      else:
        ws.var("dipho_maxIDMVA").setVal(r['dipho_subleadIDMVA'])
        ws.var("dipho_minIDMVA").setVal(r['dipho_leadIDMVA'])
      # Fill
      for a in args: hists[a].add(asets[a],r['weight'])

    # Add histograms to ws
    for a in args: getattr(ws,'import')(hists[a])
  
    # Garbage removal
    del t
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
        if a in ['dipho_maxIDMVA','dipho_minIDMVA']: continue
        ws.var(a).setVal(r[a])
      # For max and min
      if r['dipho_leadIDMVA'] >= r['dipho_subleadIDMVA']:
        ws.var("dipho_maxIDMVA").setVal(r['dipho_leadIDMVA'])
        ws.var("dipho_minIDMVA").setVal(r['dipho_subleadIDMVA'])
      else:
        ws.var("dipho_maxIDMVA").setVal(r['dipho_subleadIDMVA'])
        ws.var("dipho_minIDMVA").setVal(r['dipho_leadIDMVA'])
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


