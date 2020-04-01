#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import os, sys, subprocess
import numpy as np, matplotlib, matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

import pandas as pd
import datetime
#import scipy.signal
import pdb

use_gradient = False
data_dir = 'COVID-19'

def clone_or_pull_dataset():
    if not os.path.exists(data_dir):
        print('No data directory {}). cloning from github'.format(data_dir))
        ret = subprocess.run('git clone https://github.com/CSSEGISandData/COVID-19.git', shell=True)
    else:
        print(f'Existing data directory ({data_dir}). Pulling up-to-date data')
        ret = subprocess.run('cd {}; git pull'.format(data_dir), shell=True)


def load_dataset(_data_rel='csse_covid_19_data/csse_covid_19_time_series'):
    filenames = ['time_series_covid19_{}_global.csv'.format(_w) for _w in ['confirmed', 'deaths', 'recovered']]
    paths = [os.path.join(data_dir, _data_rel, _fn) for _fn in filenames]
    df_conf, df_death, df_recovered = [pd.read_csv(_p) for _p in paths]
    # Columns are Province/State, Country/Region, Lat, Long, time0, ..., time_n
    # Getting timestamps, not sure how smart that is :(
    times = [datetime.datetime.strptime(_t, '%m/%d/%y') for _t in np.array(list(df_conf))[4:]]

    nb_entities, nb_timestamps = df_conf.shape; nb_timestamps-=4
    #print('loaded: {}'.format(filename))
    print('found {} timestamps (from {} to {})'.format(len(times), times[0], times[-1]))
    print('found {} entities'.format(nb_entities))

    return times, df_conf, df_death, df_recovered

        
def _decorate(ax, title=None, xlab=None, ylab=None, legend=None, ytickfmt=None):
    ax.xaxis.grid(color='k', linestyle='-', linewidth=0.2)
    ax.yaxis.grid(color='k', linestyle='-', linewidth=0.2)
    if xlab: ax.xaxis.set_label_text(xlab)
    if ylab: ax.yaxis.set_label_text(ylab)
    if title is not None: ax.set_title(title)
    if legend is not None: ax.legend()
    if ytickfmt is not None: ax.ticklabel_format(style=ytickfmt, axis='y', scilimits=(0,0), useMathText=True)

def _differentiate(_arr): return np.gradient(_arr) if use_gradient else np.diff(_arr, prepend=_arr[0])

  
def get_populations(countries):
    _d = {'France':67e6, 'Italy':60.5e6, 'United Kingdom':66.4e6,
          'US':327.2e6, 'Spain':46.6e6, 'Germany':82.8e6, 'Iran':81.2e6,
          'Switzerland':8.6e6, 'Korea, South':51.5e6 }
    return [_d[_c] for _c in countries]

