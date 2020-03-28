#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import os, sys, subprocess
import numpy as np, matplotlib, matplotlib.pyplot as plt
import pandas as pd
import datetime
#import scipy.signal
import pdb

use_gradient = False

data_dir = 'COVID-19'

def clone_or_pull_dataset():
    if not os.path.exists(data_dir):
        print('No data directory (). cloning from github'.format(data_dir))
        ret = subprocess.run('git clone https://github.com/CSSEGISandData/COVID-19.git', shell=True)
    else:
        print('Existing data directory (). Pulling up to date data'.format(data_dir))
        ret = subprocess.run('cd {}; git pull'.format(data_dir), shell=True)

def load_dataset(_data_dir_rel='csse_covid_19_data/csse_covid_19_time_series'):
    filename = os.path.join(data_dir, _data_dir_rel, 'time_series_covid19_confirmed_global.csv')
    df_conf = pd.read_csv(filename)
    # Columns are Province/State   Country/Region  Lat Long time0 ... time_n

    # getting timestamps, not sure how smart that is :(
    times = [datetime.datetime.strptime(_t, '%m/%d/%y') for _t in np.array(list(df_conf))[4:]]

    nb_entities, nb_timestamps = df_conf.shape;  nb_timestamps-=4
    print('loaded: {}'.format(filename))
    print('found {} timestamps (from {} to {})'.format(len(times), times[0], times[-1]))
    print('found {} entities'.format(nb_entities))

    filename =  os.path.join(data_dir, _data_dir_rel, 'time_series_covid19_deaths_global.csv')
    df_death = pd.read_csv(filename)
    print('loaded: {}'.format(filename))
    #filename =  os.path.join(data_dir, _data_dir_rel, 'time_series_covid19_recovered_global.csv')
    #df_recovered = pd.read_csv(filename)
    #print('loaded: {}'.format(filename))
    return times, df_conf, df_death#, df_recovered

        
def _decorate(ax, title=None, xlab=None, ylab=None, legend=None, ytickfmt=None):
    ax.xaxis.grid(color='k', linestyle='-', linewidth=0.2)
    ax.yaxis.grid(color='k', linestyle='-', linewidth=0.2)
    if xlab: ax.xaxis.set_label_text(xlab)
    if ylab: ax.yaxis.set_label_text(ylab)
    if title is not None: ax.set_title(title)
    if legend is not None: ax.legend()
    if ytickfmt is not None: ax.ticklabel_format(style=ytickfmt, axis='y', scilimits=(0,0), useMathText=True)

def _differentiate(_arr): return np.gradient(_arr) if use_gradient else np.diff(_arr, prepend=_arr[0])

    
def plot_world(times1, data, desc, skip=0):
    #spp = matplotlib.figure.SubplotParams(left=0.033)
    #fig, axs = plt.subplots(2, sharex=True, figsize=(25.60, 10.24), subplotpars=spp)#, left=0.033)#; plt.tight_layout() 0.033
    fig, axs = plt.subplots(2, sharex=True, figsize=(25.60, 10.24), tight_layout=True)
    all_confirmed = data.sum()[2+skip:]
    axs[0].plot(times1[skip:], all_confirmed)
    _title = 'Total {} ({:.3f} % of world population)'.format(desc, np.max(all_confirmed)/8.5e9*100)
    _decorate(axs[0], _title, ylab='persons')#, ytickfmt='sci')
    
    daily_confirmed = _differentiate(all_confirmed)
    axs[1].bar(times1[skip:], daily_confirmed)
    _decorate(axs[1], 'Daily {}'.format(desc), ylab='persons')
    

def plot_countries(times1, data, desc, countries = ['France'], populations=None, skip=0):
    _prov_sta = np.array(data.T.loc['Province/State'])
    _coun_reg = np.array(data.T.loc['Country/Region'])
    _idxs = [np.where(_coun_reg==_c)[0][-1] for _c in countries]
    fig, axs = plt.subplots(2, sharex=True, figsize=(25.60, 10.24), tight_layout=True)
    if populations is not None:
        for _c, _i, _p in zip(countries, _idxs, populations):
            _confirmed = np.array(data.iloc[_i][4+skip:])/_p
            axs[0].plot(times1[skip:], _confirmed*100, '-', marker='*', label=_c)
            daily_confirmed = _differentiate(_confirmed)
            axs[1].plot(times1[skip:], daily_confirmed*100, '--', marker='*', label=_c)
        _decorate(axs[0], 'Total {}'.format(desc), ylab="% of population", legend=True)
        _decorate(axs[1], 'Daily {}'.format(desc), ylab="% of population per day", legend=True)
    else:
        for _c, _i in zip(countries, _idxs):
            _confirmed = np.array(data.iloc[_i][4+skip:])
            axs[0].plot(times1[skip:], _confirmed, '-', marker='*', label=_c)
            daily_confirmed = _differentiate(_confirmed)
            axs[1].plot(times1[skip:], daily_confirmed, '--', marker='*', label=_c)
        _decorate(axs[0], 'Total {}'.format(desc), ylab="persons", legend=True)
        _decorate(axs[1], 'Daily {}'.format(desc), ylab="persons per day", legend=True)
        
  
def get_populations(countries):
    _d = {'France':67e6, 'Italy':60.5e6, 'United Kingdom':66.4e6,
          'US':327.2e6, 'Spain':46.6e6, 'Germany':82.8e6, 'Iran':81.2e6, 'Switzerland':8.6e6 }
    return [_d[_c] for _c in countries]
#coree du sud 51.47 

def plot_world_chronogramms(times, df_conf, df_death):
    plot_world(times, df_conf, 'confirmed cases', skip=30)
    plot_world(times, df_death, 'death', skip=30)
      
def main():
    if '-update' in sys.argv: clone_or_pull_dataset()

    times, df_conf, df_death = load_dataset()

    plot_world_chronogramms(times, df_conf, df_death)
    countries = ['France', 'Italy', 'United Kingdom', 'US', 'Spain', 'Germany']
    #countries = ['France', 'Italy', 'US', 'Iran', 'Switzerland']
    populations = get_populations(countries) if '-relative' in sys.argv else None
    plot_countries(times, df_conf, 'confirmed cases', countries, populations, skip=30)
    plot_countries(times, df_death,'death', countries, populations, skip=30)
    
    plt.show()

    
if __name__ == "__main__":
    main()
