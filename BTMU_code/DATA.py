import sys, math
import numpy as np
import pandas as pd
import datetime as dt
import velidb.btcommon as bt
from velidb.tobcache import tob_cache
import os.path
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#import CONFIGURATION as my_config

class DataStream(object):
    def __init__(self, data, name, config):
        self.data      = data   # data frame
        self.name      = name   # data frame name (feed's name)
        self.shape     = data.shape   # save this for initialize the same sized df
        self.config    = config      # note: each data stream might have different configuration

        #self.sampled   = False  # whether the data frame is sampled or the raw
        # if config.sampling_rule:
        #     self.sampled_data = self.sampling_all(self, config)
        #     self.sampled = True

    def sampling(self, data):  # the data could be masked (either DataFrame or Series)
        # filename = self.name + '_' + self.config.sampling_rule + '_' + str(self.config.computing_window) + '.h5'
        # print(type(data))
        # print(data)
        # tmp_from = self.stream_from.sampling(self.stream_from.data[col].loc[mask])
        # assert(0)
        #sampled_data = pd.Series()
        sampled_data = data.resample(self.config.sampling_rule, closed='right').mean()
        return sampled_data

    # resample ALL data. Not chunk specified.
    @staticmethod
    def sampling_all(self):
        filename = self.name + '_' + self.config.sampling_rule + '_' + str(self.config.computing_window) + '.h5'
        sampled_data = pd.DataFrame()

        if (os.path.isfile(filename)):
            # load
            print ("reading file..." + filename)
            store = pd.HDFStore(filename, mode='r')
            for column in self.data:
                tmp = pd.DataFrame(store[column])
                sampled_data = pd.concat([sampled_data, tmp], axis=1)
            store.close()
        else:
            # save
            print("saving file..." + filename)
            #store = pd.HDFStore(filename, 'w')
            for column in self.data:
                sampled_data[column] = self.data[column].resample(self.config.sampling_rule, closed='right').mean()
                self.save_hdf3(sampled_data[column], column, filename)
            #store.close()
        return sampled_data

    def arrival_in_ms(self, norm=True):
        floor = np.vectorize(math.floor)
        if norm == True:
            aim = self.data.index.microsecond / 1000 - floor(self.data.index.microsecond / 100000) * 100  # normalize
        else:
            aim = self.data.index.microsecond / 1000
        return aim

    @staticmethod
    def save_hdf1(col_data, col_name, filename):
        # writes in a PyTables Array format
        store = pd.HDFStore(filename, mode='a')
        store[col_name] = col_data
        store.close()

    @staticmethod
    def save_hdf2(col_data, col_name, filename):
        # Write in the Table format, using PyTables Table format. Do not create an index
        store = pd.HDFStore(filename, mode='a')
        store.append(col_name, col_data, index=False)
        store.close()

    @staticmethod
    def save_hdf3(col_data, col_name, filename):
        # Write in the Table format, using PyTables Table format. Create an index
        store = pd.HDFStore(filename, mode='a')
        store.append(col_name, col_data)
        store.close()


class Init_Data(object):
    def __init__(self, config):
        self.start    = config.start_time
        self.end      = config.end_time
        self.feeds    = config.feeds
        self.days     = config.days
        self.currency = config.currency
        self.dfs      = {}  # intilize the dictionary. E.g., 'BTMU_HC_1':data frame

        self.load(self)     # load all day's data, the resolution is 'day'
        # define some time range for debug purpose
        if config.debug_data:
            self.load_debug() # unit-step loading, the resolution is user defined. Example: config.second can be set

    @staticmethod
    def load(self):
        for s in self.feeds:
            for c in self.currency:
                newdf = pd.DataFrame()
                for d in range(0, self.days):
                    cac = tob_cache('/home/jsong/notebooks/tob_cache', logger)
                    tmp = cac.getData(bt.asset_class.FX, s, c, self.start + dt.timedelta(d))
                    newdf = newdf.append(tmp, ignore_index=False)
                self.dfs[s] = newdf

    def load_debug(self):
        # make sure that load() has been invoked
        for s in self.feeds:
            date_mask = (self.dfs[s].index > self.start) & (self.dfs[s].index < self.end)
            dates = self.dfs[s].index[date_mask]
            self.dfs[s] = self.dfs[s].loc[dates]

    def data_info(self, ds):
        # DataFrame info functions
        d = ds.data
        print("Name: %s" % ds.name)
        print("\nDescribe: ")
        print(d.describe())
        print("\nHead5: ")
        print(d.head(5))
        print("\nDtypes: ")
        print(d.dtypes)
        print("\nShape: ")
        print(d.shape)
        print("\nColumns: ")
        print(d.columns)
        # print (df.info)
        for colname in d.columns:
            print(colname)

    # if isDataFrame is False, we need call this function to convert
    def to_dataframe(self, data):
        out = []
        tmptime = 0
        for x in data.iterrows():
            temp = x
            if x["timestamp"] == tmptime:
                x["timestamp"] = x["timestamp"] + 1
                out.append([x["timestamp"], x["bid"], x["bid_size"], x["offer"], x["offer_size"]])
                tmptime = x["timestamp"]
            else:
                out.append([x["timestamp"], x["bid"], x["bid_size"], x["offer"], x["offer_size"]])
                tmptime = x["timestamp"]
        out = pd.DataFrame(out)
        out.columns = ['timestamp', 'bid', 'bid_size', 'offer', 'offer_size']

        ind = np.array(out['timestamp'].duplicated())
        while any(ind):
            # Note: here 9 is a hard coding activity. len(str(x)) does not work
            out['timestamp'][ind] = out['timestamp'][ind].map(lambda x: x + 1)
            ind = np.array(out['timestamp'].duplicated())

        return (out)
