#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import os, sys
import numpy as np, matplotlib, matplotlib.pyplot as plt
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
    #_idxs = [np.where(_coun_reg==_c)[0][-1] for _c in countries]
    _idxs = [np.where(_coun_reg==_c)[0] for _c in countries]
    fig, axs = plt.subplots(2, sharex=True, figsize=(25.60, 10.24), tight_layout=True)
    _relative = (populations is not None)
    populations = np.ones(len(countries)) if populations is None else populations
    for _c, _is, _p in zip(countries, _idxs, populations):
        _confirmed = np.sum([np.array(data.iloc[_i1][4+skip:]) for _i1 in _is], axis=0)
        if _relative: _confirmed /=_p*100.
        axs[0].plot(times1[skip:], _confirmed, '-', marker='*', label=_c)
        daily_confirmed = pandemic._differentiate(_confirmed)
        axs[1].plot(times1[skip:], daily_confirmed, '--', marker='*', label=_c)
    ylab = '% of population' if _relative else "persons"
    pandemic._decorate(axs[0], 'Total {}'.format(desc), ylab=ylab, legend=True, ytickfmt='sci')
    pandemic._decorate(axs[1], 'Daily {}'.format(desc), ylab=ylab+' per day', legend=True, ytickfmt='sci')
        
  
def plot_world_chronogramms(times, df_conf, df_death, skip):
    plot_world(times, df_conf, 'confirmed cases', skip)
    plot_world(times, df_death, 'death', skip)

def main(skip=37):
    if not os.path.exists(pandemic.data_dir) or '-update' in sys.argv: pandemic.clone_or_pull_dataset()

    times, df_conf, df_death, df_recovered = pandemic.load_dataset()
    pandemic.print_countries(df_conf)

    if '-world' in sys.argv: plot_world_chronogramms(times, df_conf, df_death, skip)

    countries = ['France', 'Italy', 'United Kingdom', 'US', 'Spain', 'Germany']#, 'China']
    #countries = ['France', 'Italy', 'US', 'Iran', 'Switzerland']
    #countries = ['France', 'United Kingdom']
    populations = pandemic.get_populations(countries) if '-relative' in sys.argv else None
    if '-countries' in sys.argv:
        plot_countries(times, df_conf, 'confirmed cases', countries, populations, skip)
        plot_countries(times, df_death,'death', countries, populations, skip)
    
    plt.show()


if __name__ == "__main__":
    main()
