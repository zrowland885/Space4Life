# Data handling
import numpy as np
from netCDF4 import Dataset
import xarray as xr
import pandas as pd

# Mapping
from bokeh.models import *
from bokeh.plotting import *
from bokeh.io import *
from bokeh.tile_providers import *
from bokeh.palettes import *
from bokeh.transform import *
from bokeh.layouts import *


def wgs84_to_web_mercator(lon, lat, df=None):
    """Converts decimal longitude/latitude to Web Mercator format"""
    k = 6378137
    
    if isinstance(df, pd.DataFrame):
        df['MERC_LON'] = pd.to_numeric(df[lon], errors='coerce') * (k * np.pi/180.0)
        df['MERC_LAT'] = np.log(np.tan((90 + pd.to_numeric(df[lat], errors='coerce').astype(float)) * np.pi/360.0)) * k
        return df
    else:
        lonMER = lon.astype(float) * (k * np.pi/180.0)
        latMER = np.log(np.tan((90 + lat.astype(float)) * np.pi/360.0)) * k
        return pd.DataFrame({'LAT': latMER, 'LON': lonMER}) 


def getMap():
    
    """FIGURE"""
    
    tile_provider = get_provider(Vendors.STAMEN_TERRAIN)

    plot = figure(
        title='Space4Life',
        match_aspect=True,
        tools='wheel_zoom,pan,reset,save',
        x_axis_type='mercator',
        y_axis_type='mercator',
        plot_width=1000,
        plot_height=750
        )

    plot.grid.visible=True
    map = plot.add_tile(tile_provider)
    map.level = 'underlay'

    plot.xaxis.visible = True
    plot.yaxis.visible = True
    
    
    """PRECIPITATION LAYER"""
    
    def create_plot_precip(plot, source, color):
        plot.circle(x='LON', y='LAT', size=5, fill_color=color, line_color = color, fill_alpha=0.5, line_alpha=0., source=source)
    
    date_user = "20150701"
    data = xr.open_dataset('data/Dataset_precipitation/3B-DAY.MS.MRG.3IMERG.'+date_user+'-S000000-E235959.V06.nc4.nc4')
    
    # Range 1 : 20 to 80
    data1 = (data['precipitationCal'].values > 20) & (data['precipitationCal'].values < 80)
    # Range 2: 80 to 150
    data2 = (data['precipitationCal'].values >= 80) & (data['precipitationCal'].values < 150)
    # Range 3: 150 to 250
    data3 = (data['precipitationCal'].values >= 150) & (data['precipitationCal'].values < 250)
    # Range 4: 250 to 350
    data4 = (data['precipitationCal'].values >= 250) & (data['precipitationCal'].values < 350)
    # Range 5: 350 to 450
    data5 = (data['precipitationCal'].values >= 350) & (data['precipitationCal'].values < 450)
    # Range 6: greater than 450
    data6 = (data['precipitationCal'].values >= 450) 
    
    # Range 1
    # tripla1[0] corresponds to time coord, tripla1[1] corresponds to lon, tripla1[2] corresponds to lat
    tripla1 = np.where(data1 == True)
    lon1 = data.lon.values[tripla1[1]]
    lat1 = data.lat.values[tripla1[2]]
    # Range 2
    tripla2 = np.where(data2 == True)
    lon2 = data.lon.values[tripla2[1]]
    lat2 = data.lat.values[tripla2[2]]
    # Range 3
    tripla3 = np.where(data3 == True)
    lon3 = data.lon.values[tripla3[1]]
    lat3 = data.lat.values[tripla3[2]]
    # Range 4
    tripla4 = np.where(data4 == True)
    lon4 = data.lon.values[tripla4[1]]
    lat4 = data.lat.values[tripla4[2]]
    # Range 5
    tripla5 = np.where(data5 == True)
    lon5 = data.lon.values[tripla5[1]]
    lat5 = data.lat.values[tripla5[2]]
    # Range 6
    tripla6 = np.where(data6 == True)
    lon6 = data.lon.values[tripla6[1]]
    lat6 = data.lat.values[tripla6[2]]

    source1 = ColumnDataSource(
    data=wgs84_to_web_mercator(lon1, lat1))
    source2 = ColumnDataSource(
        data=wgs84_to_web_mercator(lon2, lat2))
    source3 = ColumnDataSource(
        data=wgs84_to_web_mercator(lon3, lat3))
    source4 = ColumnDataSource(
        data=wgs84_to_web_mercator(lon4, lat4))
    source5 = ColumnDataSource(
        data=wgs84_to_web_mercator(lon5, lat5))
    source6 = ColumnDataSource(
        data=wgs84_to_web_mercator(lon6, lat6))

    create_plot_precip(plot, source1,"#CAF2EF")
    create_plot_precip(plot, source2,'#7FD7D1')
    create_plot_precip(plot, source3,'#60C0CA')
    create_plot_precip(plot, source4,'#479AC8')
    create_plot_precip(plot, source5,'#327FAA')
    create_plot_precip(plot, source6,'#306B8B')
    
    
    """MOVEBANK LAYER"""
    
    dfAnimals = pd.read_csv('data/movebank/Brown pelican data from Lamb et al. (2017).csv')
    
    dfAnimals['timestamp'] = pd.to_datetime(dfAnimals['timestamp'], errors = 'coerce')
    dfAnimals = dfAnimals.sort_values('timestamp')
    dfAnimals = wgs84_to_web_mercator('location-long', 'location-lat', dfAnimals)
    
    datemask = (dfAnimals['timestamp'] >= '2015-6-1') & (dfAnimals['timestamp'] < '2015-12-1')
    dfAnimals = dfAnimals.loc[datemask]
    
    animal_ids = dfAnimals['individual-local-identifier'].unique().tolist()
    
    cut = 10
    
    cut_animal_ids = animal_ids[:cut]
    
    dfAnimals = dfAnimals[dfAnimals['individual-local-identifier'].isin(cut_animal_ids)]
    
    source = ColumnDataSource(dfAnimals)
    
    color=factor_cmap('individual-local-identifier', palette=magma(len(cut_animal_ids)), factors=animal_ids)

    plot.scatter(x='MERC_LON', y='MERC_LAT', source=source, size=5, marker='x', color=color, name='animals')
    
    plot.add_tools(HoverTool(names=['animals'],
        tooltips=[
            ('id', '@{individual-local-identifier}'), # use @{ } for field names with spaces
            ('timestamp', '@{timestamp}{%Y-%m-%d %H:%M:%S}'),
        ],
        formatters={
            '@{individual-local-identifier}': 'printf',
            '@{timestamp}': 'datetime',
        },
    mode = 'mouse'
))

    return plot
