# Script to extract MC fractions directly from NANOAOD
from collections import OrderedDict as od
import json
import os, sys
import re
from optparse import OptionParser
from cross_sections import *
from info import samples_info, stxs_info

def get_options():
  parser = OptionParser()
  #parser.add_option("--ext", dest="ext", default='', help="Additional extension for saving")
  return parser.parse_args()
(opt,args) = get_options()

if not os.path.isdir("./stxsFractions"): os.system("mkdir ./stxsFractions")

tables = od()
tables['GG2H'] = ['ggH','ggZH_had']
tables['QQ2HQQ'] = ['qqH','WH_had','ZH_had']
tables['VHLEP'] = ['WH_lep','ZH_lep','ggZH_lep']
tables['OTHER'] = ['ttH','tHq','tHW','bbH']

# Calculate total XSBR
xsbr = od()
for pms in tables.itervalues():
  for pm in pms:
    pm_v = 0
    for s,v in stxs_xs.iteritems():
      if pm == "ggZH_lep":
        if "ggZH_ll" in s: pm_v += v
        elif "ggZH_nunu" in s: pm_v += v
      else:
        if pm in s: pm_v += v
    xsbr[pm] = pm_v*1000 #in fb

for k, pms in tables.iteritems():
  fout = open("./stxsFractions/%s.txt"%k,"w")
  #fout.write("\\begin{table}[htb]\n")
  #fout.write("    \\centering\n")
  #fout.write("    \\scriptsize\n")
  #fout.write("    \\renewcommand{\\arraystretch}{1.5}\n")
  #fout.write("    \\setlength{\\tabcolsep}{3pt}\n")

  # Tabular
  ucolumns = ['\\textbf{Production mode}','\\textbf{Order of $\\sigma$ calc}','\\multicolumn{%g}{c}{\\begin{tabular}[c]{@{}c@{}}\\textbf{\\boldmath{$\\sigma\\cdot\\rm{BR}$}~[fb]} \\\\ \\textbf{13~TeV, \\boldmath{$m_H$}~=~125~GeV}\\end{tabular}}'%(len(pms)+1)]

  if k == "VHLEP": columns = ['\\multirow{2}{*}{\\textbf{STXS region}}','\\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}\\textbf{Definition}\\\\ \\textbf{units of $p_T^V$ in GeV}\\end{tabular}}']
  elif k == "OTHER": columns = ['\\multirow{2}{*}{\\textbf{STXS region}}','\\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}\\textbf{Definition}\\\\ \\textbf{units of $p_T^H$ in GeV}\\end{tabular}}']
  else: columns = ['\\multirow{2}{*}{\\textbf{STXS region}}','\\multirow{2}{*}{\\begin{tabular}[c]{@{}c@{}}\\textbf{Definition}\\\\ \\textbf{units of $p_T^H$, $m_{jj}$ and $p_T^{Hjj}$ in GeV}\\end{tabular}}']
  columns.append('\\multicolumn{%g}{c|}{\\textbf{Fraction of total}}'%len(pms))
  columns.append('\\multirow{2}{*}{\\textbf{\\boldmath{$\\sigma\\cdot\\rm{BR}$}~[fb]}}')
  fcolumns = ['','']
  for pm in pms: fcolumns.append("\\textbf{%s}"%samples_info[pm]['title'])
  fcolumns.append('')
  fout.write("\\begin{tabular}{l%s}\n"%(("|c"*(len(fcolumns)-1))))
  fout.write("   \\hline \\hline\n")
  if k == "GG2H": fout.write("   \\multicolumn{%g}{c}{\\footnotesize{\\textbf{ggH STXS stage 1.2}}} \\\\ \\hline  \\hline \n"%len(fcolumns))
  elif k == "QQ2HQQ": fout.write("   \\multicolumn{%g}{c}{\\footnotesize{\\textbf{qqH STXS stage 1.2}}} \\\\ \\hline  \\hline \n"%len(fcolumns))
  elif k == "VHLEP": fout.write("   \\multicolumn{%g}{c}{\\footnotesize{\\textbf{VH leptonic STXS stage 1.2}}} \\\\ \\hline  \\hline \n"%len(fcolumns))
  else: fout.write("   \\multicolumn{%g}{c}{\\footnotesize{\\textbf{ttH, tH and bbH STXS stage 1.2}}} \\\\ \\hline  \\hline \n"%len(fcolumns))
  ucolumns_str = "%s"%ucolumns[0]
  columns_str = "%s"%columns[0]
  fcolumns_str = "%s"%fcolumns[0]
  for col in ucolumns[1:]: ucolumns_str += " & %s"%col
  for col in columns[1:]: columns_str += " & %s"%col
  for col in fcolumns[1:]: fcolumns_str += " & %s"%col
  fout.write("   %s \\\\ \\hline \n"%ucolumns_str)
  for pm in pms:
    if k in ['VHLEP','OTHER']: info = [samples_info[pm]['title'],samples_info[pm]['order'],"\\multicolumn{%g}{c}{%.3f}"%(len(pms)+1,xsbr[pm])]
    else: info = [samples_info[pm]['title'],samples_info[pm]['order'],"\\multicolumn{%g}{c}{%.2f}"%(len(pms)+1,xsbr[pm])]
    info_str = "%s"%info[0]
    for col in info[1:]: info_str += " & %s"%col
    fout.write("   %s \\\\ \\hline \n"%info_str)
    
  fout.write("   \\hline \n")
  fout.write("   %s \\\\ \n"%columns_str)
  fout.write("   %s \\\\ \\hline\n"%fcolumns_str)

  if k =="VHLEP":
    # 1) FWDH
    wh_fwdh = ['WH lep forward','\\multirow{3}{*}{$|Y_H| > 2.5$}','%.2f\\%%'%(100*(1000*stxs_xs['WH_lep_FWDH']/xsbr['WH_lep'])),'-','-','%.3f'%(stxs_xs['WH_lep_FWDH']*1000)] 
    zh_fwdh = ['ZH lep forward','','-','%.2f\\%%'%(100*(1000*stxs_xs['ZH_lep_FWDH']/xsbr['ZH_lep'])),'-','%.3f'%(stxs_xs['ZH_lep_FWDH']*1000)] 
    ggzh_fwdh = ['ggZH lep forward','','-','-','%.2f\\%%'%(100*(1000*(stxs_xs['ggZH_ll_FWDH']+stxs_xs['ggZH_nunu_FWDH'])/xsbr['ggZH_lep'])),'%.3f'%((stxs_xs['ggZH_nunu_FWDH']+stxs_xs['ggZH_ll_FWDH'])*1000)] 
    for f in [wh_fwdh,zh_fwdh,ggzh_fwdh]:
      fwdh_str = "%s"%f[0]
      for col in f[1:]: fwdh_str += "& %s"%col
      if f == ggzh_fwdh: fout.write("   %s \\\\ \\hline \n"%fwdh_str)
      else: fout.write("   %s \\\\ \\cline{0-0}\\cline{3-6} \n"%fwdh_str)
    # 2) Other bins 
    fout.write("   \\multicolumn{%g}{c}{$|Y_H| < 2.5$} \\\\ \\hline\n"%len(fcolumns))
    for pm_idx in range(len(pms)):
      pm = pms[pm_idx]
      for b in samples_info[pm]['bins']:
        if "FWDH" in b: continue
        row = [stxs_info[pm][b][0],stxs_info[pm][b][1]]
        if pm_idx == 0: row.extend(['%.2f\\%%'%(100*(1000*stxs_xs['%s_%s'%(pm,b)]/xsbr[pm])),'-','-','%.3f'%(stxs_xs['%s_%s'%(pm,b)]*1000)])
        elif pm_idx == 1: row.extend(['-','%.2f\\%%'%(100*(1000*stxs_xs['%s_%s'%(pm,b)]/xsbr[pm])),'-','%.3f'%(stxs_xs['%s_%s'%(pm,b)]*1000)])
        else: row.extend(['-','-','%.2f\\%%'%(100*(1000*(stxs_xs['ggZH_ll_%s'%b]+stxs_xs['ggZH_nunu_%s'%b])/xsbr['ggZH_lep'])),'%.3f'%((stxs_xs['ggZH_nunu_%s'%b]+stxs_xs['ggZH_ll_%s'%b])*1000)])
        row_str = "%s"%row[0]
        for col in row[1:]: row_str += " & %s"%col
        fout.write("   %s \\\\ \\hline \n"%row_str)
    fout.write("    \\hline\n")

  elif k == "OTHER":
    tth_fwdh = ['ttH forward','\\multirow{3}{*}{$|Y_H| > 2.5$}','%.2f\\%%'%(100*(1000*stxs_xs['ttH_FWDH']/xsbr['ttH'])),'-','-','-','%.3f'%(stxs_xs['ttH_FWDH']*1000)]
    th_fwdh = ['tH forward','','-','%.2f\\%%'%(100*(1000*stxs_xs['tHq_FWDH']/xsbr['tHq'])),'%.2f\\%%'%(100*(1000*stxs_xs['tHW_FWDH']/xsbr['tHW'])),'-','%.3f'%((stxs_xs['tHq_FWDH']+stxs_xs['tHW_FWDH'])*1000)]
    bbh_fwdh = ['bbH forward','','-','-','-','%.2f\\%%'%(100*(1000*stxs_xs['bbH_FWDH']/xsbr['bbH'])),'%.3f'%(stxs_xs['bbH_FWDH']*1000)]
    for f in [tth_fwdh,th_fwdh,bbh_fwdh]:
      fwdh_str = "%s"%f[0]
      for col in f[1:]: fwdh_str += "& %s"%col
      if f == bbh_fwdh: fout.write("   %s \\\\ \\hline \n"%fwdh_str)
      else: fout.write("   %s \\\\ \\cline{0-0}\\cline{3-7} \n"%fwdh_str)
    # 2) Other bins 
    fout.write("   \\multicolumn{%g}{c}{$|Y_H| < 2.5$} \\\\ \\hline\n"%len(fcolumns))
    for pm in ['ttH','tH','bbH']:
      if pm == 'ttH':
        for b in samples_info[pm]['bins']:
          if "FWDH" in b: continue
          row = [stxs_info[pm][b][0],stxs_info[pm][b][1]]
          row.extend(['%.2f\\%%'%(100*(1000*stxs_xs['%s_%s'%(pm,b)]/xsbr[pm])),'-','-','-','%.3f'%(stxs_xs['%s_%s'%(pm,b)]*1000)])
          row_str = "%s"%row[0]
          for col in row[1:]: row_str += " & %s"%col
          fout.write("   %s \\\\ \\hline \n"%row_str)
      elif pm == "bbH":
        row = ['bbH','No additional requirements','-','-','-','%.2f\\%%'%(100*(1000*stxs_xs['bbH']/xsbr['bbH'])),'%.3f'%(stxs_xs['bbH']*1000)]
        row_str = "%s"%row[0]
        for col in row[1:]: row_str += " & %s"%col
        fout.write("   %s \\\\ \\hline \n"%row_str)
      else:
        row = ['tH','No additional requirements','-','%.2f\\%%'%(100*(1000*stxs_xs['tHq']/xsbr['tHq'])),'%.2f\\%%'%(100*(1000*stxs_xs['tHW']/xsbr['tHW'])),'-','%.3f'%((stxs_xs['tHq']+stxs_xs['tHW'])*1000)]
        row_str = "%s"%row[0]
        for col in row[1:]: row_str += " & %s"%col
        fout.write("   %s \\\\ \\hline \n"%row_str)
    fout.write("   \\hline \n")

  else:
    # Add values
    # 1) FWDH
    if k == "GG2H": fwdh = ['ggH Forward','$|Y_H| > 2.5$']
    elif k == "QQ2HQQ": fwdh = ['qqH Forward','$|Y_H| > 2.5$']
    else: fwdh = ['Forward','$|Y_H| > 2.5$']
    for pm in pms: fwdh.append('%.2f\\%%'%(100*(1000*stxs_xs['%s_FWDH'%pm]/xsbr[pm])))
    xsbr_v = 0
    for pm in pms: xsbr_v += stxs_xs['%s_FWDH'%pm]*1000
    fwdh.append('%.2f'%xsbr_v)
    fwdh_str = "%s"%fwdh[0]
    for col in fwdh[1:]: fwdh_str += " & %s"%col
    fout.write("   %s \\\\ \\hline\n"%fwdh_str)
    # 2) Other bins 
    fout.write("   \\multicolumn{%g}{c}{$|Y_H| < 2.5$} \\\\ \\hline\n"%len(fcolumns))
    # Take first pm
    pm0 = pms[0]
    for b in samples_info[pm0]['bins']:
      if "FWDH" in b: continue
      row = [stxs_info[pm0][b][0],stxs_info[pm0][b][1]]
      for pm in pms: row.append('%.2f\\%%'%(100*(1000*stxs_xs['%s_%s'%(pm,b)]/xsbr[pm])))
      xsbr_v = 0
      for pm in pms: xsbr_v += stxs_xs['%s_%s'%(pm,b)]*1000
      row.append('%.2f'%xsbr_v)
      row_str = "%s"%row[0]
      for col in row[1:]: row_str += " & %s"%col
      fout.write("   %s \\\\ \\hline \n"%row_str)
    fout.write("   \\hline\n")

  fout.write("\\end{tabular}\n")
