from pyhdf.SD import SD, SDC
import pprint
#from matplotlib import pyplot as plt
import numpy as np
import os
import datetime
import pickle

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
    
    # https://landweb.modaps.eosdis.nasa.gov/QA_WWW/forPage/user_guide/MODISC6FireproudctsUserguide.pdf
    
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
    
    return np.array((np.degrees(lat_data), np.degrees(lon_data), data))


def get_modis_tile(fpath):

    # https://moonbooks.org/Articles/How-to-read-a-MODIS-HDF-file-using-python-/

    file = SD(fpath, SDC.READ)
    print( file.info() )
    
    # print SDS names
    datasets_dic = file.datasets()
    for idx,sds in enumerate(datasets_dic.keys()):
        print( idx,sds )
    
    # get data
    sds_obj = file.select('FireMask') # select sds
    data = sds_obj.get() # get sds data
    print( data )
    
    # get attributes
    pprint.pprint( sds_obj.attributes() )
    #plt.imshow(data, interpolation='nearest')
    #plt.show()
    
    H = int(fpath.split('.')[2][1:3])
    V = int(fpath.split('.')[2][4:6])

    return get_modis_coords(data, H, V), H, V


def get_modis_data(date, directory='data/MOD14A2/'):

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
