from pyhdf.SD import SD, SDC
#import pprint
#from matplotlib import pyplot as plt
import numpy as np
import os
import datetime
import pickle

import pyproj

def ordinal_to_calendar(ord_date):
    """Convert ordinal date in the form YYYYDDD to datetime"""
    date = datetime.datetime.strptime(ord_date, '%Y%j')
    return date
    #return date.strftime('%d/%m/%Y')


def calendar_to_ordinal(cal_date):
    """Convert calendar date in the form DD/MM/YYYY to datetime"""
    date = datetime.datetime.strptime(cal_date, '%d/%m/%Y')
    return date
    #return date.strftime('%Y%j')


def get_modis_coords(data, H, V):
    """Convert from row, col ids in MODIS HDF files to Sinusoidal latitude and
    longitude coords, then return as Google Mercator"""
    # Credit: https://landweb.modaps.eosdis.nasa.gov/QA_WWW/forPage/user_guide/MODISC6FireproudctsUserguide.pdf
    
    R = 6371007.181     # m (idealised radius of the Earth)
    T = 1111950         # m (the height and width of each MODIS tile in the projection plane)
    x_min = -20015109   # m (the western limit of the projection plane)
    y_max = 10007555    # m (the northern limit of the projection plane)
    w = T/1200          # m (the actual size of a "1-km" MODIS sinusoidal grid cell)

    col_ids = np.array([list(range(1200)),]*1200)
    row_ids = np.array([list(range(1200)),]*1200).transpose()

    x_data = (col_ids + 0.5)*w + H*T + x_min
    y_data = y_max - (row_ids + 0.5)*w - V*T

    lat_data = y_data/R
    lon_data = x_data/(R*np.cos(lat_data))
    
    # Define CRS
    #wgs84 = pyproj.CRS("EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
    sinu = pyproj.CRS("+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs") # MODIS Sinusoidal
    google = pyproj.CRS("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs") # Google Mercator
    
    lon_out, lat_out = pyproj.transform(sinu, google, np.degrees(lon_data), np.degrees(lat_data), radians=False, errcheck=True) 
    
    return np.array((lat_out, lon_out, data))


def get_modis_tile(fpath):
    """Read MOD14A2 (Terra) FireMask data tiles"""
    # Credit: https://moonbooks.org/Articles/How-to-read-a-MODIS-HDF-file-using-python-/

    file = SD(fpath, SDC.READ)
    #print( file.info() )
    
    # print SDS names
    #datasets_dic = file.datasets()
    #for idx,sds in enumerate(datasets_dic.keys()):
        #print( idx,sds )
    
    # get data
    sds_obj = file.select('FireMask') # select sds
    data = sds_obj.get() # get sds data
    #print( data )
    
    # get attributes
    #pprint.pprint( sds_obj.attributes() )
    #plt.imshow(data, interpolation='nearest')
    #plt.show()
    
    H = int(fpath.split('.')[2][1:3])
    V = int(fpath.split('.')[2][4:6])

    return get_modis_coords(data, H, V), H, V


def get_modis_data(date, directory='data/MOD14A2/'):
    """Read MODIS tiles with data corresponding to input date"""

    modis_data = []

    for file in os.listdir(directory):
        
         filename = os.fsdecode(file)
         fdate = ordinal_to_calendar(filename.split('.')[1][1:])
         fdate_list = [fdate + datetime.timedelta(days=x) for x in range(8)]
         
         if filename.endswith(".hdf") and datetime.datetime.strptime(date,'%d/%m/%Y') in fdate_list:
             
             fpath = os.path.join(directory, filename)
             tile, H, V = get_modis_tile(fpath)
             modis_data.append(tile)
             continue
         
         else:
             continue

    return modis_data


def pickle_modis_data(directory='data/MOD14A2/'):
    """Convert MODIS tiles to pickle format"""
    # Unused
    
    modis_data = []

    for file in os.listdir(directory):
        
         filename = os.fsdecode(file)
         fdate = ordinal_to_calendar(filename.split('.')[1][1:])
         
         if filename.endswith(".hdf"):
             
             fpath = os.path.join(directory, filename)
             tile, H, V = get_modis_tile(fpath)
             modis_data.append((fdate, tile))
             
             continue
         
         else:
             continue

    with open('modis_pickle', 'wb') as f:
        pickle.dump(modis_data, f)

    return modis_data
