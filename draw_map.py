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
import pandemic

def plot_map(df_conf, countries=None, _ts=-1):
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax = plt.axes(projection=ccrs.Mollweide())
    #ax.coastlines()
    ax.set_global()
    # ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.COASTLINE)
    # ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.OCEAN, facecolor='blue')
    ax.outline_patch.set_edgecolor('grey')
    #ax.stock_img()
    # states_provinces = cfeature.NaturalEarthFeature(
    #     category='cultural',
    #     name='admin_1_states_provinces_lines',
    #     scale='50m',
    #     facecolor='none')
    # ax.add_feature(states_provinces, edgecolor='gray')

    print('#\npandemics entities')
    
    if countries is not None:
        _coun_reg = np.array(df_conf.T.loc['Country/Region'])
        _idxs = [np.where(_coun_reg==_c)[0][-1] for _c in countries]
    else:
        countries = np.array(df_conf.T.loc['Country/Region'])
        _idxs = range(len(countries))
    _val_by_country, _min, _max = {}, float('inf'), -float('inf')
    for _c, _i in zip(countries, _idxs):
        lat, lon = df_conf.iloc[_i][2:4]
        confirmed_cases = df_conf.iloc[_i][_ts] 
        print(_c, lat, lon, confirmed_cases)
        _val_by_country[_c] = confirmed_cases
        _min = min(_min, confirmed_cases)
        _max = max(_max, confirmed_cases)
        plt.plot([lon], [lat], color='red', linewidth=2, marker='o', transform=ccrs.Geodetic())
        #plt.text(lon, lat, _c, horizontalalignment='left', transform=ccrs.Geodetic())
    _delta = _max-_min

    print('#\ngetting geometries')
    
    shpfilename = shpreader.natural_earth(resolution='110m',
                                          category='cultural',
                                          name='admin_0_countries')
    reader = shpreader.Reader(shpfilename)
    _countries = reader.records()
    _cmap = plt.get_cmap('viridis')
    for country in _countries:
        #pdb.set_trace()
        #print(country.attributes['SOVEREIGNT'])
        if country.attributes['NAME'] in countries:
            #pdb.set_trace()
            _v = (_val_by_country[country.attributes['NAME']]-_min)/_delta
            #print(country.attributes['SOVEREIGNT'], country.attributes['NAME'], _val_by_country[country.attributes['NAME']])
            ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                              facecolor=_cmap(_v),#'red',
                              label=country.attributes['NAME'],
                              edgecolor='#FFFFFF',
                              linewidth=.25)
        else:
            print('not found {},{}'.format(country.attributes['SOVEREIGNT'], country.attributes['NAME']))
    norm = matplotlib.colors.Normalize(vmin=_min, vmax=_max)
    # cb1 = matplotlib.colorbar.ColorbarBase(ax, cmap=_cmap,
    #                                        norm=norm,
    #                                        orientation='horizontal')
    sm = plt.cm.ScalarMappable(cmap=_cmap,norm=norm)
    sm._A = []
    cb = plt.colorbar(sm,ax=ax, orientation='horizontal')
            
def main():
    if not os.path.exists(pandemic.data_dir) or '-update' in sys.argv: pandemic.clone_or_pull_dataset()

    times, df_conf, df_death, df_recovered = pandemic.load_dataset()

    countries = ['France', 'Italy', 'United Kingdom', 'US', 'Spain', 'Germany']
    plot_map(df_conf, countries=None)
    
    plt.show()

    
if __name__ == "__main__":
    main()
