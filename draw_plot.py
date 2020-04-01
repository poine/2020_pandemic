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
import pandemic
import pdb


    
def plot_world(times1, data, desc, skip=0):
    fig, axs = plt.subplots(2, sharex=True, figsize=(25.60, 10.24), tight_layout=True)
    all_confirmed = data.sum()[2+skip:]
    axs[0].plot(times1[skip:], all_confirmed)
    _title = 'Total {} ({:.3f} % of world population)'.format(desc, np.max(all_confirmed)/8.5e9*100)
    pandemic._decorate(axs[0], _title, ylab='persons')#, ytickfmt='sci')
    
    daily_confirmed = pandemic._differentiate(all_confirmed)
    axs[1].bar(times1[skip:], daily_confirmed)
    pandemic._decorate(axs[1], 'Daily {}'.format(desc), ylab='persons')
    

def plot_countries(times1, data, desc, countries = ['France'], populations=None, skip=0):
    _prov_sta = np.array(data.T.loc['Province/State'])
    _coun_reg = np.array(data.T.loc['Country/Region'])
    _idxs = [np.where(_coun_reg==_c)[0][-1] for _c in countries]
    fig, axs = plt.subplots(2, sharex=True, figsize=(25.60, 10.24), tight_layout=True)
    if populations is not None:
        for _c, _i, _p in zip(countries, _idxs, populations):
            _confirmed = np.array(data.iloc[_i][4+skip:])/_p
            axs[0].plot(times1[skip:], _confirmed*100, '-', marker='*', label=_c)
            daily_confirmed = pandemic._differentiate(_confirmed)
            axs[1].plot(times1[skip:], daily_confirmed*100, '--', marker='*', label=_c)
        pandemic._decorate(axs[0], 'Total {}'.format(desc), ylab="% of population", legend=True)
        pandemic._decorate(axs[1], 'Daily {}'.format(desc), ylab="% of population per day", legend=True)
    else:
        for _c, _i in zip(countries, _idxs):
            _confirmed = np.array(data.iloc[_i][4+skip:])
            axs[0].plot(times1[skip:], _confirmed, '-', marker='*', label=_c)
            daily_confirmed = pandemic._differentiate(_confirmed)
            axs[1].plot(times1[skip:], daily_confirmed, '--', marker='*', label=_c)
        pandemic._decorate(axs[0], 'Total {}'.format(desc), ylab="persons", legend=True)
        pandemic._decorate(axs[1], 'Daily {}'.format(desc), ylab="persons per day", legend=True)
        
  
def plot_world_chronogramms(times, df_conf, df_death):
    plot_world(times, df_conf, 'confirmed cases', skip=30)
    plot_world(times, df_death, 'death', skip=30)

def main():
    if not os.path.exists(pandemic.data_dir) or '-update' in sys.argv: pandemic.clone_or_pull_dataset()

    times, df_conf, df_death, df_recovered = pandemic.load_dataset()


    if '-world' in sys.argv: plot_world_chronogramms(times, df_conf, df_death)

    countries = ['France', 'Italy', 'United Kingdom', 'US', 'Spain', 'Germany']
    #countries = ['France', 'Italy', 'US', 'Iran', 'Switzerland']
    populations = pandemic.get_populations(countries) if '-relative' in sys.argv else None
    if '-countries' in sys.argv:
        plot_countries(times, df_conf, 'confirmed cases', countries, populations, skip=30)
        plot_countries(times, df_death,'death', countries, populations, skip=30)
    
    plt.show()

    
if __name__ == "__main__":
    main()
