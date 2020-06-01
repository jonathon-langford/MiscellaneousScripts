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
tables['OTHER'] = ['ttH','bbH','tHq','tHW']

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
  fout.write("\\begin{table}[htb]\n")
  fout.write("    \\centering\n")
  fout.write("    \\footnotesize\n")
  fout.write("    \\renewcommand{\\arraystretch}{1.3}\n")

  # Top tabular
  if k == "GG2H": columns = ['Production Mode','Generator','Showering','PDF','Notes','\\begin{tabular}[c]{@{}c@{}}$\\sigma\\cdot\\rm{BR}$~[fb] \\\\ \\footnotesize{13~TeV, $m_H$~=~125~GeV}\\end{tabular}','Order of $\\sigma$ calc']
  else: columns = ['Production Mode','Generator','Showering','PDF', '\\begin{tabular}[c]{@{}c@{}}$\\sigma\\cdot\\rm{BR}$~[fb] \\\\ \\footnotesize{13~TeV, $m_H$~=~125~GeV}\\end{tabular}','Order of $\\sigma$ calc']
  
  fout.write("    \\begin{tabular}{%s}\n"%(("c|"*len(columns))[:-1]))
  columns_str = "%s"%columns[0]
  for col in columns[1:]: columns_str += " & %s"%col
  fout.write("       %s \\\\ \\hline\n"%columns_str)
 
  for pm in pms:
    if k == "GG2H": info = [samples_info[pm]['title'],samples_info[pm]['generator'],samples_info[pm]['showering'],samples_info[pm]['PDF'],samples_info[pm]['notes'],"%.2f"%xsbr[pm],samples_info[pm]['order']] 
    elif k in ["VHLEP","OTHER"]: info = [samples_info[pm]['title'],samples_info[pm]['generator'],samples_info[pm]['showering'],samples_info[pm]['PDF'],"%.3f"%xsbr[pm],samples_info[pm]['order']]
    else: info = [samples_info[pm]['title'],samples_info[pm]['generator'],samples_info[pm]['showering'],samples_info[pm]['PDF'],"%.2f"%xsbr[pm],samples_info[pm]['order']]
    info_str = "%s"%info[0]
    for col in info[1:]: info_str += " & %s"%col
    fout.write("       %s \\\\ \n"%info_str)
  fout.write("       \\hline\n")
  fout.write("    \\end{tabular}\n")

  # Bottom tabular
  if k == "VHLEP": columns = ['STXS region','Definition, units of $p_T^V$ in GeV']
  elif k == "OTHER": columns = ['STXS region','Definition, units of $p_T^H$ in GeV']
  else: columns = ['STXS region','Definition, units of $p_T^H$, $m_{jj}$ and $p_T^{Hjj}$ in GeV']
  if len(pms) == 1: columns.append('Fraction')
  else:
    for pm in pms: columns.append('\\begin{tabular}[c]{@{}c@{}}Fraction of total\\\\%s\\end{tabular}'%samples_info[pm]['title'])
  columns.append('Total $\\sigma\\cdot\\rm{BR}$~[fb]')
  fout.write("    \\begin{tabular}{%s}\n"%(("c|"*len(columns))[:-1]))
  fout.write("      \\multicolumn{%g}{c}{} \\\\ \n"%len(columns))
  columns_str = "%s"%columns[0]
  for col in columns[1:]: columns_str += " & %s"%col
  fout.write("       %s \\\\ \\hline\n"%columns_str)
  if k =="VHLEP":
    # 1) FWDH
    wh_fwdh = ['WH lep forward','\\multirow{3}{*}{$|Y_H| > 2.5$}','%.2f\\%%'%(100*(1000*stxs_xs['WH_lep_FWDH']/xsbr['WH_lep'])),'-','-','%.3f'%(stxs_xs['WH_lep_FWDH']*1000)] 
    zh_fwdh = ['ZH lep forward','','-','%.2f\\%%'%(100*(1000*stxs_xs['ZH_lep_FWDH']/xsbr['ZH_lep'])),'-','%.3f'%(stxs_xs['ZH_lep_FWDH']*1000)] 
    ggzh_fwdh = ['ggZH lep forward','','-','-','%.2f\\%%'%(100*(1000*(stxs_xs['ggZH_ll_FWDH']+stxs_xs['ggZH_nunu_FWDH'])/xsbr['ggZH_lep'])),'%.3f'%((stxs_xs['ggZH_nunu_FWDH']+stxs_xs['ggZH_ll_FWDH'])*1000)] 
    for f in [wh_fwdh,zh_fwdh,ggzh_fwdh]:
      fwdh_str = "%s"%f[0]
      for col in f[1:]: fwdh_str += "& %s"%col
      fout.write("       %s \\\\ \n"%fwdh_str)
    fout.write("       \\hline \n")
    # 2) Other bins 
    fout.write("       \\multicolumn{%g}{c}{$|Y_H| < 2.5$} \\\\ \\hline\n"%len(columns))
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
        fout.write("       %s \\\\ \n"%row_str)
      fout.write("         \\hline\n")

  elif k == "OTHER":
    tth_fwdh = ['ttH forward','\\multirow{3}{*}{$|Y_H| > 2.5$}','%.2f\\%%'%(100*(1000*stxs_xs['ttH_FWDH']/xsbr['ttH'])),'-','-','-','%.3f'%(stxs_xs['ttH_FWDH']*1000)]
    bbh_fwdh = ['bbH forward','','-','%.2f\\%%'%(100*(1000*stxs_xs['bbH_FWDH']/xsbr['bbH'])),'-','-','%.3f'%(stxs_xs['bbH_FWDH']*1000)]
    th_fwdh = ['tH forward','','-','-','%.2f\\%%'%(100*(1000*stxs_xs['tHq_FWDH']/xsbr['tHq'])),'%.2f\\%%'%(100*(1000*stxs_xs['tHW_FWDH']/xsbr['tHW'])),'%.3f'%((stxs_xs['tHq_FWDH']+stxs_xs['tHW_FWDH'])*1000)]
    for f in [tth_fwdh,bbh_fwdh,th_fwdh]:
      fwdh_str = "%s"%f[0]
      for col in f[1:]: fwdh_str += "& %s"%col
      fout.write("       %s \\\\ \n"%fwdh_str)
    fout.write("       \\hline \n")
    # 2) Other bins 
    fout.write("       \\multicolumn{%g}{c}{$|Y_H| < 2.5$} \\\\ \\hline\n"%len(columns))
    for pm in pms[:-1]:
      if pm == 'ttH':
        for b in samples_info[pm]['bins']:
          if "FWDH" in b: continue
          row = [stxs_info[pm][b][0],stxs_info[pm][b][1]]
          row.extend(['%.2f\\%%'%(100*(1000*stxs_xs['%s_%s'%(pm,b)]/xsbr[pm])),'-','-','-','%.3f'%(stxs_xs['%s_%s'%(pm,b)]*1000)])
          row_str = "%s"%row[0]
          for col in row[1:]: row_str += " & %s"%col
          fout.write("       %s \\\\ \n"%row_str)
      elif pm == "bbH":
        row = ['bbH','No additional requirements','-','%.2f\\%%'%(100*(1000*stxs_xs['bbH']/xsbr['bbH'])),'-','-','%.3f'%(stxs_xs['bbH']*1000)]
        row_str = "%s"%row[0]
        for col in row[1:]: row_str += " & %s"%col
        fout.write("       %s \\\\ \n"%row_str)
      else:
        row = ['bbH','No additional requirements','-','-','%.2f\\%%'%(100*(1000*stxs_xs['tHq']/xsbr['tHq'])),'%.2f\\%%'%(100*(1000*stxs_xs['tHW']/xsbr['tHW'])),'%.3f'%((stxs_xs['tHq']+stxs_xs['tHW'])*1000)]
        row_str = "%s"%row[0]
        for col in row[1:]: row_str += " & %s"%col
        fout.write("       %s \\\\ \n"%row_str)
      fout.write("         \\hline\n")

  else:
    # Add values
    # 1) FWDH
    fwdh = ['Forward','$|Y_H| > 2.5$']
    for pm in pms: fwdh.append('%.2f\\%%'%(100*(1000*stxs_xs['%s_FWDH'%pm]/xsbr[pm])))
    xsbr_v = 0
    for pm in pms: xsbr_v += stxs_xs['%s_FWDH'%pm]*1000
    fwdh.append('%.2f'%xsbr_v)
    fwdh_str = "%s"%fwdh[0]
    for col in fwdh[1:]: fwdh_str += " & %s"%col
    fout.write("       %s \\\\ \\hline\n"%fwdh_str)
    # 2) Other bins 
    fout.write("       \\multicolumn{%g}{c}{$|Y_H| < 2.5$} \\\\ \\hline\n"%len(columns))
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
      fout.write("       %s \\\\ \n"%row_str)
    fout.write("       \\hline\n")

  fout.write("    \\end{tabular}\n")
  fout.write("\\end{table}\n")
