from flask import Flask, render_template, request
import sys
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Imports MAP
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
#Mapping
from bokeh.models import *
from bokeh.plotting import *
from bokeh.io import *
from bokeh.tile_providers import *
from bokeh.palettes import *
from bokeh.transform import *
from bokeh.layouts import *
from bokeh.resources import CDN
from bokeh.embed import file_html





app = Flask(__name__)

@app.route('/')
def index():
    print('Before render_template', file=sys.stdout)
    return render_template("index.html")
    
   
    
@app.route('/', methods=['POST','GET'])
def msg_management():
    selectedValue = request.form['options']
    if selectedValue == "hurricanes":
        print('selectedvalue =', file=sys.stdout)
        print(selectedValue)
        html = file_html(getMap(), CDN, "my plot")
        return render_template('index.html', plot=html)       
    
    else:
        print("fires\n")              
        return render_template("index.html")
    


def wgs84_to_web_mercator(longitude, latitude):
    """Converts decimal longitude/latitude to Web Mercator format"""
    k = 6378137
    lonMER = longitude.astype(float) * (k * np.pi/180.0)
    latMER = np.log(np.tan((90 + latitude.astype(float)) * np.pi/360.0)) * k
    return pd.DataFrame({'LAT': latMER, 'LON': lonMER}) 
    
def create_plot(plot, source, color):
    plot.circle(x='LON', y='LAT', size=5, fill_color=color, line_color = color, fill_alpha=0.8, source=source)

 
def getMap():
    output_notebook()
    date_user = "20150701"
    data = xr.open_dataset('/mnt/D_DRIVE/Space_Apps/Dataset_precipitation/3B-DAY.MS.MRG.3IMERG.'+date_user+'-S000000-E235959.V06.nc4.nc4')
    
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

    tile_provider = get_provider(Vendors.STAMEN_TERRAIN)

    plot = figure(
        title='title',
        match_aspect=True,
        tools='wheel_zoom,pan,reset,save',
        x_axis_type='mercator',
        y_axis_type='mercator'
        )

    plot.grid.visible=True
    map = plot.add_tile(tile_provider)
    map.level = 'underlay'

    plot.xaxis.visible = True
    plot.yaxis.visible = True

    create_plot(plot, source1,"#CAF2EF")
    create_plot(plot, source2,'#7FD7D1')
    create_plot(plot, source3,'#60C0CA')
    create_plot(plot, source4,'#479AC8')
    create_plot(plot, source5,'#327FAA')
    create_plot(plot, source6,'#306B8B')
    return plot
    
    
    
if __name__ == '__main__':
  # Threaded option to enable multiple instances for multiple user access support
  app.run(threaded=True, port=5000)