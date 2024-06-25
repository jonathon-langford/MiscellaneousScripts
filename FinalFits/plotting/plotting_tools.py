import subprocess
import os
import numpy as np
import re
from optparse import OptionParser
import json
import ROOT
from scipy.interpolate import interp1d

def data_to_axis(ax, point):
    return (ax.transAxes + ax.transData.inverted()).inverted().transform(point)

def Translate(name, ndict):
    return ndict[name] if name in ndict else name

def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)

def find_crossings(graph, spline, yval):
    crossings, intervals = [], []
    current = None

    for i in range(len(graph[0])-1):
        if (graph[1][i]-yval)*(graph[1][i+1]-yval) < 0.:
            # Find crossing as inverse of spline between two x points
            mask = (spline[0]>graph[0][i])&(spline[0]<=graph[0][i+1])
            f_inv = interp1d(spline[1][mask],spline[0][mask])

            # Find crossing point for catch when yval is out of domain of spline points (unlikely)
            if yval > spline[1][mask].max(): cross = f_inv(spline[1][mask].max())
            elif yval <= spline[1][mask].min(): cross = f_inv(spline[1][mask].min())
            else: cross = f_inv(yval)

            # Add information for crossings
            if ((graph[1][i]-yval) > 0.)&( current is None ):
                current = {
                    'lo':cross,
                    'hi':graph[0][-1],
                    'valid_lo': True,
                    'valid_hi': False
                }
            if ((graph[1][i]-yval) < 0.)&( current is None ):
                current = {
                    'lo':graph[0][0],
                    'hi':cross,
                    'valid_lo': False,
                    'valid_hi': True
                }
            if ((graph[1][i]-yval) < 0.)&( current is not None ):
                current['hi'] = cross
                current['valid_hi'] = True
                intervals.append(current)
                current = None

            crossings.append(cross)

    if current is not None:
        intervals.append(current)

    if len(intervals) == 0:
        current = {
            'lo':graph[0][0],
            'hi':graph[0][-1],
            'valid_lo': False,
            'valid_hi': False
        }
        intervals.append(current)

    return intervals


# TODO: option for saving other parameter value
def build_scan(t, poi, extract_info=False, do_2sig=False, remin=False, qmin=-9999, qmax=9999, spline='cubic', spline_points=1000, track_params=[]):
    res = {}

    # Extract info from TTree
    r = np.array([getattr(ev,poi) for ev in t])
    q = np.array([2*getattr(ev,"deltaNLL") for ev in t])
    qe = np.array([getattr(ev,"quantileExpected") for ev in t])
    # Track parameters
    tracking = {}
    for tp in track_params:
        tracking[tp] = np.array([getattr(ev,tp) for ev in t])

    # Apply masks
    mask = (qe > -1.5) & (q > qmin) & (q < qmax)
    r = r[mask]
    q = q[mask]
    for tp in track_params:
        tracking[tp] = tracking[tp][mask]

    # Remove duplicates
    r, i = np.unique(r, return_index=True)
    q = q[i]
    for tp in track_params:
        tracking[tp] = tracking[tp][i]

    # Build spline
    f = interp1d(r,q,kind=spline)
    r_spline = np.linspace(r.min(),r.max(),spline_points)
    q_spline = f(r_spline)
    tracking_splines = {}
    for tp in track_params:
        f = interp1d(r,tracking[tp],kind=spline)
        tracking_splines[tp] = f(r_spline)

    # Remin: adds point to graph
    if remin:
        if q_spline.min() < 0:
            q = q-q_spline.min()
            q_spline -= q_spline.min()
            # Add new point to graph
            r = np.append(r,r_spline[np.argmin(q_spline)])
            q = np.append(q,0.)
            # Re-sort
            i_sort = np.argsort(r)
            r = r[i_sort]
            q = q[i_sort]

    res['bestfit'] = r[q==0][0]
    res['graph'] = (r,q)
    res['spline'] = (r_spline,q_spline)
    res['track_params'] = tracking
    res['track_params_splines'] = tracking_splines

    # Find best-fit and crossings
    if extract_info:
        res['val'], res['cross_1sig'], res['other_1sig'] = None, None, []
        intervals_1sig = find_crossings(res['graph'],res['spline'],1.)
        for interval in intervals_1sig:
            interval['contains_bf'] = False
            if (interval['lo']<=res['bestfit'])&(interval['hi']>=res['bestfit']): interval['contains_bf'] = True
        for interval in intervals_1sig:
            if interval['contains_bf']:
                res['val'] = (res['bestfit'], interval['hi']-res['bestfit'], interval['lo']-res['bestfit'])
                res['cross_1sig'] = interval
            else:
                res['other_1sig'].append(interval)

        if do_2sig:
            res['val_2sig'], res['cross_2sig'], res['other_2sig'] = None, None, []
            intervals_2sig = find_crossings(res['graph'],res['spline'],4.)
            for interval in intervals_2sig:
                interval['contains_bf'] = False
                if (interval['lo']<=res['bestfit'])&(interval['hi']>=res['bestfit']): interval['contains_bf'] = True
            for interval in intervals_2sig:
                if interval['contains_bf']:
                    res['val_2sig'] = (res['bestfit'], interval['hi']-res['bestfit'], interval['lo']-res['bestfit'])
                    res['cross_2sig'] = interval
                else:
                    res['other_2sig'].append(interval)

    return res

def get_breakdown(scans, breakdown):
    breakdown = breakdown.split(",")

    # Extract hi/lo 1 sigma errors for each scan
    v_hi = [scans['main']['val'][1]]
    v_lo = [scans['main']['val'][2]]
    for k, res in scans.items():
        if k == 'main': continue
        v_hi.append(res['val'][1])
        v_lo.append(res['val'][2])

    assert(len(v_hi) == len(breakdown))

    breakdown_label = " = $%.3f"%scans['main']['val'][0]
    breakdown_info = {}

    for i, br in enumerate(breakdown):
        if i < (len(breakdown)-1):
            if(abs(v_hi[i+1]) > abs(v_hi[i])):
                print("[WARNING] Error subtraction for (%s,hi) is negative. Fill with 0.000"%br)
                hi = 0.
            else:
                hi = np.sqrt(v_hi[i]**2 -v_hi[i+1]**2)

            if(abs(v_lo[i+1]) > abs(v_lo[i])):
                print("[WARNING] Error subtraction for (%s,lo) is negative. Fill with 0.000"%br)
                lo = 0.
            else:
                lo = np.sqrt(v_lo[i]**2 -v_lo[i+1]**2)

        else:
            hi = v_hi[i]
            lo = v_lo[i]

        breakdown_label += "{}^{+%.3f}_{-%.3f}(%s)"%(hi,abs(lo),br)
        breakdown_info["%sHi"%br] = hi
        breakdown_info["%sLo"%br] = abs(lo)*-1.

    return breakdown_info, breakdown_label+"$"


def add_info_to_json(json_file, scans, model, poi, do_2sig=False):
    if os.path.isfile(json_file):
        with open(json_file) as jf:
            res = json.load(jf)
    else:
        res = {}

    if model not in res:
        res[model] = {}

    res[model][poi] = {
        "Val": scans['main']['val'][0],
        "ErrorHi": scans['main']['val'][1],
        "ErrorLo": scans['main']['val'][2],
        "ValidErrorHi": scans['main']['cross_1sig']['valid_hi'],
        "ValidErrorLo": scans['main']['cross_1sig']['valid_lo']
    }

    if do_2sig:
        res[model][poi]['2sig_ErrorHi'] = scans['main']['val_2sig'][1]
        res[model][poi]['2sig_ErrorLo'] = scans['main']['val_2sig'][2]
        res[model][poi]['2sig_ValidErrorHi'] = scans['main']['cross_2sig']['valid_hi']
        res[model][poi]['2sig_ValidErrorLo'] = scans['main']['cross_2sig']['valid_lo']

    if 'breakdown_info' in scans['main']:
        res[model][poi].update(scans['main']['breakdown_info'])

    with open(json_file, 'w') as jf:
        json.dump(res, jf, sort_keys=True, indent=4, separators=(',', ': '))
