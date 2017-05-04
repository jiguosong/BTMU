import matplotlib.pyplot as plt
import sys, math
import numpy as np
import pandas as pd
import datetime as dt
from dateutil import parser
import velidb.btcommon as bt
from velidb.tobcache import tob_cache

import DATA  as my_data

class Visualizer(object):
    def __init__(self):
        pass

    def preview(self, data):
        # this is only used for view the time characteristics
        mill_data = {}
        for col in data.dfs:
            mill_data[col] = my_data.DataStream(data.dfs[col], col).arrival_in_ms(norm=True)
            plt.hist(mill_data[col], bins=100, normed=1, facecolor='green')
            plt.xlabel('Milliseconds')
            plt.ylabel('Frequency')
            plt.title('Histgram of ms of Tick Arrival %s' % col)
            plt.grid(True)
            plt.show()

    def df_hist(self, sd):   # TOdo: this needs to rewrite
        # the histogram of the data
        plt.hist(sd.data, bins=100, normed=1, facecolor='green')
        plt.xlabel('Milliseconds')
        plt.ylabel('Frequency')
        plt.title('Histgram of ms of Tick Arrival %s' % sd.name)
        plt.grid(True)
        plt.show()

    def df_normal(self, sd):
        plt.plot(sd.data.timestamp, sd.data.bid)
        plt.plot(sd.data.timestamp, sd.data.offer)
        plt.title('Price vs TimeStamp %s' % sd.name)
        plt.legend(loc='best')
        plt.show()
        #plt.xlim([0,100])
        #pd.options.display.max_rows = 200
