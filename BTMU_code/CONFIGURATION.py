import sys, math
import numpy as np
import pandas as pd
import datetime as dt
import velidb.btcommon as bt
from velidb.tobcache import tob_cache

from Abstract_Model import Configuration

class ModelConfiguration(Configuration):
    def __init__(self,
                 sampling_rule='',
                 computing_window=10,
                 sliding_window=1,
                 start_time=0,
                 days=0,
                 hours = 0,
                 minutes = 0,
                 seconds = 0,
                 feeds = [],
                 currency = [],
                 debug_plot=False,
                 debug_data=False):

        self.sampling_rule    = sampling_rule
        self.computing_window = computing_window
        self.sliding_window   = sliding_window
        self.start_time       = start_time
        self.days             = days
        self.hours            = hours
        self.minutes          = minutes
        self.seconds          = seconds
        self.feeds            = feeds
        self.currency         = currency
        self.debug_plot       = debug_plot
        self.debug_data       = debug_data
        self.end_time         = start_time + pd.to_timedelta(1000*seconds, unit='ms')  # can be used for debug