from collections import OrderedDict as od

mg5 = "\\textsc{Madgraph5\\_aMC@NLO}"
powheg = "\\textsc{Powheg}"
pythia = "\\textsc{Pythia8}"

samples_info = od()
samples_info['ggH'] = {
  "title":"ggH",
  "generator":mg5,
  "showering":pythia,
  "notes":"NNLOPS reweighting",
  "PDF":"-",
  "bins":['FWDH', 'PTH_200_300', 'PTH_300_450', 'PTH_450_650', 'PTH_GT650', '0J_PTH_0_10', '0J_PTH_GT10', '1J_PTH_0_60', '1J_PTH_60_120', '1J_PTH_120_200', 'GE2J_MJJ_0_350_PTH_0_60', 'GE2J_MJJ_0_350_PTH_60_120', 'GE2J_MJJ_0_350_PTH_120_200', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
  "order":"N$^{\\rm{3}}$LO(QCD)+NLO(EW)"
}
samples_info['ggZH_had'] = {
  "title":"gg$\\rightarrow$Z(qq)H",
  "generator":powheg,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', 'PTH_200_300', 'PTH_300_450', 'PTH_450_650', 'PTH_GT650', '0J_PTH_0_10', '0J_PTH_GT10', '1J_PTH_0_60', '1J_PTH_60_120', '1J_PTH_120_200', 'GE2J_MJJ_0_350_PTH_0_60', 'GE2J_MJJ_0_350_PTH_60_120', 'GE2J_MJJ_0_350_PTH_120_200', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
  "order":"NNLO(QCD)+NLO(EW)"
}
samples_info['qqH'] = {
  "title":"VBF",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', '0J', '1J', 'GE2J_MJJ_0_60', 'GE2J_MJJ_60_120', 'GE2J_MJJ_120_350', 'GE2J_MJJ_GT350_PTH_GT200', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
  "order":"NNLO(QCD)+NLO(EW)"
}
samples_info['WH_had'] = {
  "title":"qq$\\rightarrow$W(qq)H",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', '0J', '1J', 'GE2J_MJJ_0_60', 'GE2J_MJJ_60_120', 'GE2J_MJJ_120_350', 'GE2J_MJJ_GT350_PTH_GT200', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
  "order":"NNLO(QCD)+NLO(EW)"
}
samples_info['ZH_had'] = {
  "title":"qq$\\rightarrow$Z(qq)H",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', '0J', '1J', 'GE2J_MJJ_0_60', 'GE2J_MJJ_60_120', 'GE2J_MJJ_120_350', 'GE2J_MJJ_GT350_PTH_GT200', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
  "order":"NNLO(QCD)+NLO(EW)"
}
samples_info['WH_lep'] = {
  "title":"qq$\\rightarrow$W($\\ell\\nu$)H",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', 'PTV_0_75', 'PTV_75_150', 'PTV_150_250_0J', 'PTV_150_250_GE1J', 'PTV_GT250'],
  "order":"NNLO(QCD)+NLO(EW)"
}
samples_info['ZH_lep'] = {
  "title":"qq$\\rightarrow$Z($\\ell\\ell/\\nu\\nu$)H",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', 'PTV_0_75', 'PTV_75_150', 'PTV_150_250_0J', 'PTV_150_250_GE1J', 'PTV_GT250'],
  "order":"NNLO(QCD)+NLO(EW)"
}
samples_info['ggZH_lep'] = {
  "title":"gg$\\rightarrow$Z($\\ell\\ell/\\nu\\nu$)H",
  "generator":powheg,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', 'PTV_0_75', 'PTV_75_150', 'PTV_150_250_0J', 'PTV_150_250_GE1J', 'PTV_GT250'],
  "order":"NNLO(QCD)+NLO(EW)"
}
samples_info['ttH'] = {
  "title":"ttH",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', 'PTH_0_60', 'PTH_60_120', 'PTH_120_200', 'PTH_200_300', 'PTH_GT300'],
  "order":"NLO(QCD)+NLO(EW)"
}
samples_info['tHq'] = {
  "title":"tHq",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', ''],
  "order":"NLO(QCD) in 5FS"
}
samples_info['tHW'] = {
  "title":"tHW",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', ''],
  "order":"NLO(QCD) in 5FS"
}
samples_info['bbH'] = {
  "title":"bbH",
  "generator":mg5,
  "showering":pythia,
  "notes":"-",
  "PDF":"-",
  "bins":['FWDH', ''],
  "order":"NNLO(5FS)+NLO(4FS)"
}

stxs_info = od()
stxs_info['ggH'] = od()
stxs_info['ggH']['PTH_200_300'] = ['ggH 200~$<$~$p_T^{H}$~$<$~300','No jet requirements, 200~$<$~$p_T^{H}$~$<$~300']
stxs_info['ggH']['PTH_300_450'] = ['ggH 300~$<$~$p_T^{H}$~$<$~450','No jet requirements, 300~$<$~$p_T^{H}$~$<$~450']
stxs_info['ggH']['PTH_450_650'] = ['ggH 450~$<$~$p_T^{H}$~$<$~650','No jet requirements, 450~$<$~$p_T^{H}$~$<$~650']
stxs_info['ggH']['PTH_GT650'] = ['ggH $p_T^{H}$~$>$~650','No jet requirements, $p_T^{H}$~$>$~650']            
stxs_info['ggH']['0J_PTH_0_10'] = ['ggH 0J low $p_{T}^{H}$','Exactly 0 jets, $p_{T}^{H}$~$<$~10']
stxs_info['ggH']['0J_PTH_GT10'] = ['ggH 0J high $p_{T}^{H}$','Exactly 0 jets, $p_{T}^{H}$~$>$~10']
stxs_info['ggH']['1J_PTH_0_60'] = ['ggH 1J low $p_{T}^{H}$','Exactly 1 jet, $p_{T}^{H}$~$<$~60']
stxs_info['ggH']['1J_PTH_60_120'] = ['ggH 1J med $p_{T}^{H}$','Exactly 1 jet, 60~$<$~$p_{T}^{H}$~$<$~120']
stxs_info['ggH']['1J_PTH_120_200'] = ['ggH 1J high $p_{T}^{H}$','Exactly 1 jet, 120~$<$~$p_{T}^{H}$~$<$~200']
stxs_info['ggH']['GE2J_MJJ_0_350_PTH_0_60'] = ['ggH $\\geq$2J low $p_{T}^{H}$','At-least 2 jets, $p_{T}^{H}$~$<$~60, $m_{jj}$~$<$~350']
stxs_info['ggH']['GE2J_MJJ_0_350_PTH_60_120'] = ['ggH $\\geq$2J med $p_{T}^{H}$','At-least 2 jets, 60~$<$~$p_{T}^{H}$~$<$~120, $m_{jj}$~$<$~350']
stxs_info['ggH']['GE2J_MJJ_0_350_PTH_120_200'] = ['ggH $\\geq$2J high $p_{T}^{H}$','At-least 2 jets, 120~$<$~$p_{T}^{H}$~$<$~200, $m_{jj}$~$<$~350']
stxs_info['ggH']['GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = ['ggH VBF-like low $m_{jj}$ low $p_T^{Hjj}$','\\begin{tabular}[c]{@{}c@{}}At least 2 jets, $p_{T}^{H}$~$<$~200,\\\\ 350~$<$~$m_{jj}$~$<$~700, $p_T^{Hjj}$~$<$~25\\end{tabular}']
stxs_info['ggH']['GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = ['ggH VBF-like low $m_{jj}$ high $p_T^{Hjj}$','\\begin{tabular}[c]{@{}c@{}}At least 2 jets, $p_{T}^{H}$~$<$~200,\\\\ 350~$<$~$m_{jj}$~$<$~700, $p_T^{Hjj}$~$>$~25\\end{tabular}']
stxs_info['ggH']['GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = ['ggH VBF-like high $m_{jj}$ low $p_T^{Hjj}$','\\begin{tabular}[c]{@{}c@{}}At least 2 jets, $p_{T}^{H}$~$<$~200,\\\\ $m_{jj}$~$>$~700, $p_T^{Hjj}$~$<$~25\\end{tabular}']
stxs_info['ggH']['GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = ['ggH VBF-like high $m_{jj}$ high $p_T^{Hjj}$','\\begin{tabular}[c]{@{}c@{}}At least 2 jets, $p_{T}^{H}$~$<$~200,\\\\ $m_{jj}$~$>$~700, $p_T^{Hjj}$~$>$~25\\end{tabular}']

stxs_info['qqH'] = od()
stxs_info['qqH']['0J'] = ['qqH 0J','Exactly 0 jets']
stxs_info['qqH']['1J'] = ['qqH 1J','Exactly 1 jet']
stxs_info['qqH']['GE2J_MJJ_0_60'] = ['qqH $m_{jj}$~$<$~60','At least 2 jets, $m_{jj}$~$<$~60']
stxs_info['qqH']['GE2J_MJJ_60_120'] = ['qqH VH-like','At least 2 jets, 60~$<$~$m_{jj}$~$<$~120']
stxs_info['qqH']['GE2J_MJJ_120_350'] = ['qqH 120~$<$~$m_{jj}$~$<$~350','At least 2 jets, 120~$<$~$m_{jj}$~$<$~350']
stxs_info['qqH']['GE2J_MJJ_GT350_PTH_GT200'] = ['qqH BSM','At least 2 jets, $m_{jj}$~$>$~350, $p_T^H$~$>$~200']
stxs_info['qqH']['GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = ['qqH VBF-like low $m_{jj}$ low $p_T^{Hjj}$','\\begin{tabular}[c]{@{}c@{}}At least 2 jets, $p_{T}^{H}$~$<$~200,\\\\ 350~$<$~$m_{jj}$~$<$~700, $p_T^{Hjj}$~$<$~25\\end{tabular}']
stxs_info['qqH']['GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = ['qqH VBF-like low $m_{jj}$ high $p_T^{Hjj}$','\\begin{tabular}[c]{@{}c@{}}At least 2 jets, $p_{T}^{H}$~$<$~200,\\\\ 350~$<$~$m_{jj}$~$<$~700, $p_T^{Hjj}$~$>$~25\\end{tabular}']
stxs_info['qqH']['GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = ['qqH VBF-like high $m_{jj}$ low $p_T^{Hjj}$','\\begin{tabular}[c]{@{}c@{}}At least 2 jets, $p_{T}^{H}$~$<$~200,\\\\ $m_{jj}$~$>$~700, $p_T^{Hjj}$~$<$~25\\end{tabular}']
stxs_info['qqH']['GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = ['qqH VBF-like high $m_{jj}$ high $p_T^{Hjj}$','\\begin{tabular}[c]{@{}c@{}}At least 2 jets, $p_{T}^{H}$~$<$~200,\\\\ $m_{jj}$~$>$~700, $p_T^{Hjj}$~$>$~25\\end{tabular}']

stxs_info['WH_lep'] = od()
stxs_info['WH_lep']['PTV_0_75'] = ['WH lep $p_T^V$~$<$~75','No jet requirements, $p_T^{V}$~$<$~75']
stxs_info['WH_lep']['PTV_75_150'] = ['WH lep 75~$<$~$p_T^V$~$<$~150','No jet requirements, 75~$<$~$p_T^{V}$~$<$~150']
stxs_info['WH_lep']['PTV_150_250_0J'] = ['WH lep 0J 150~$<$~$p_T^V$~$<$~250','Exactly 0 jets, 150~$<$~$p_T^{V}$~$<$~250']
stxs_info['WH_lep']['PTV_150_250_GE1J'] = ['WH lep $\\geq$1J 150~$<$~$p_T^V$~$<$~250','At least 1 jet, 150~$<$~$p_T^{V}$~$<$~250']
stxs_info['WH_lep']['PTV_GT250'] = ['WH lep $p_T^V$~$>$~250','No jet requirements, $p_T^{V}$~$>$~250']

stxs_info['ZH_lep'] = od()
stxs_info['ZH_lep']['PTV_0_75'] = ['ZH lep $p_T^V$~$<$~75','No jet requirements, $p_T^{V}$~$<$~75']
stxs_info['ZH_lep']['PTV_75_150'] = ['ZH lep 75~$<$~$p_T^V$~$<$~150','No jet requirements, 75~$<$~$p_T^{V}$~$<$~150']
stxs_info['ZH_lep']['PTV_150_250_0J'] = ['ZH lep 0J 150~$<$~$p_T^V$~$<$~250','Exactly 0 jets, 150~$<$~$p_T^{V}$~$<$~250']
stxs_info['ZH_lep']['PTV_150_250_GE1J'] = ['ZH lep $\\geq$1J 150~$<$~$p_T^V$~$<$~250','At least 1 jet, 150~$<$~$p_T^{V}$~$<$~250']
stxs_info['ZH_lep']['PTV_GT250'] = ['ZH lep $p_T^V$~$>$~250','No jet requirements, $p_T^{V}$~$>$~250']

stxs_info['ggZH_lep'] = od()
stxs_info['ggZH_lep']['PTV_0_75'] = ['ggZH lep $p_T^V$~$<$~75','No jet requirements, $p_T^{V}$~$<$~75']
stxs_info['ggZH_lep']['PTV_75_150'] = ['ggZH lep 75~$<$~$p_T^V$~$<$~150','No jet requirements, 75~$<$~$p_T^{V}$~$<$~150']
stxs_info['ggZH_lep']['PTV_150_250_0J'] = ['ggZH lep 0J 150~$<$~$p_T^V$~$<$~250','Exactly 0 jets, 150~$<$~$p_T^{V}$~$<$~250']
stxs_info['ggZH_lep']['PTV_150_250_GE1J'] = ['ggZH lep $\\geq$1J 150~$<$~$p_T^V$~$<$~250','At least 1 jet, 150~$<$~$p_T^{V}$~$<$~250']
stxs_info['ggZH_lep']['PTV_GT250'] = ['ggZH lep $p_T^V$~$>$~250','No jet requirements, $p_T^{V}$~$>$~250']

stxs_info['ttH'] = od()
stxs_info['ttH']['PTH_0_60'] = ['ttH $p_T^{H}$~$<$~60','No jet requirements, $p_T^{H}$~$<$~60']
stxs_info['ttH']['PTH_60_120'] = ['ttH 60~$<$~$p_T^{H}$~$<$~120','No jet requirements, 60~$<$~$p_T^{H}$~$<$~120']
stxs_info['ttH']['PTH_120_200'] = ['ttH 120~$<$~$p_T^{H}$~$<$~200','No jet requirements, 120~$<$~$p_T^{H}$~$<$~200']
stxs_info['ttH']['PTH_200_300'] = ['ttH 200~$<$~$p_T^{H}$~$<$~300','No jet requirements, 200~$<$~$p_T^{H}$~$<$~300']
stxs_info['ttH']['PTH_GT300'] = ['ttH $p_T^{H}$~$>$~300','No jet requirements, $p_T^{H}$~$>$~300']
