import sys, os
import datetime as dt
import velidb.btcommon as bt
import logging
from velidb.tobcache import tob_cache
from dateutil import parser
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


year = 2016
month = 10
date = 10
days = 5

source = ['BTMU_HC_1', 'EBS_ULTRA_NY_A', 'EBS_LIVE_NY_XML_A']
currency = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDHCHF', 'EURCHF', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDMZN', 'EURSEK',
            'USDHKD', 'USDZAR', 'EURNOK', 'EURCZK', 'EURDKK', 'EURHUF', 'USDCNH', 'EURPLN']

for s in source:
    for c in currency:
        for day in range(0, days):
            cac = tob_cache('/home/jsong/tob_cache', logger)
            start = d = dt.datetime(year, month, date + day, 0)
#print("done")


