# this is the main model file that does the analysis
# try to detect when BTMU MA corsses EBS MA

import sys, math
import numpy as np
import pandas as pd
import datetime as dt
import velidb.btcommon as bt
from velidb.tobcache import tob_cache

# user defined class for preparing data
import DATA          as my_data
from Abstract_Model import Strategy, Portfolio
import CONFIGURATION as my_config

class MovingAverageCrossStrategy(Strategy):
    def __init__(self, stream_from, stream_to, config):
        #default slide window is 20, and the period on the data signal is 10ms. See the model

        # if stream_from.sampled and stream_to.sampled:
        #     self.bars_from = stream_from.sampled_data
        #     self.bars_to = stream_to.sampled_data
        # else:
        #     self.bars_from = stream_from.data
        #     self.bars_to   = stream_to.data

        self.stream_from      = stream_from
        self.stream_to        = stream_to
        self.name_from        = stream_from.name
        self.name_to          = stream_to.name
        self.sliding_window   = config.sliding_window
        self.computing_window = pd.to_timedelta(config.computing_window, unit='ms')

        # NOTE: there are some NA in the signals. We need take care of that as well
        self.stream_from.data = self.stream_from.data.fillna(method='backfill')
        self.stream_to.data   = self.stream_to.data.fillna(method='backfill')

        # initialize the signals
        self.signals = pd.DataFrame(index=self.stream_from.data.index)
        self.signals['bid'] = 0.0
        self.signals['offer'] = 0.0


    @staticmethod
    def compute_macrossing_signals(self, from_v, to_v):
        # from_v and to_v are Seires
        a = from_v.rolling(self.sliding_window).mean()
        b = to_v.rolling(self.sliding_window).mean()

        print(a)

        # create a 'signal' when the one's bid/offer cross another one's bid/offer
        # from_feed is BTMU, which is usually above the ebs one. So we use "<"
        s = np.where(a[self.sliding_window:] < b[self.sliding_window:], 1.0, 0.0)

        print("AAAAAA")
        print(a[self.sliding_window:])
        print(b[self.sliding_window:])
        print(s.shape)
        assert(0)
        # s is ndarray, a/b is Series
        return s, a, b

    def generate_signals(self):
        """Returns the DataFrame of symbols containing the signals"""

        # Create the set of short and long simple moving averages over the respective periods
        for col in self.stream_from.data:
            if col != 'bid' and col != 'offer':
                continue
            from_name = self.name_from + '_mavg_' + col
            to_name   = self.name_to + '_mavg_' + col
            self.signals[from_name] = 0.0
            self.signals[to_name]   = 0.0

            # initialize the start time and end time
            start_time = self.stream_from.data.index[0]
            end_time = start_time + self.computing_window
            tmp_cms  = []
            tmp_fromma = []
            tmp_toma = []
            print('start computing... ' + col)

            while True:
                # check the time
                if self.stream_from.data.tail(1).index[0] < end_time:
                    print(self.stream_from.data.tail(1).index[0])
                    print(end_time)
                    assert(0)
                    break

                # generate the mask, then do the resampling on these data
                mask = (self.stream_from.data.index >= start_time) & (self.stream_from.data.index < end_time)
                print("This is mask")
                print(type(mask))
                print(mask)
                print(mask.shape)
                print("This is masked data")
                print(type(self.stream_from.data[col].loc[mask]))
                print(self.stream_from.data[col])
                print(self.stream_from.data[col].loc[mask])
                print(self.stream_from.data[col].loc[mask].shape)

                assert(0)

                # tmp_from, tmp_to are Series
                tmp_from = self.stream_from.sampling(self.stream_from.data[col].loc[mask])
                tmp_to   = self.stream_to.sampling(self.stream_to.data[col].loc[mask])


                print(self.stream_from.data[col].loc[mask])
                print(self.stream_to.data[col].loc[mask])
                print(tmp_from)
                print(tmp_to)

                s, from_ma, to_ma = self.compute_macrossing_signals(self, tmp_from, tmp_to)

                tmp_cms    = np.append(tmp_cms, s)
                tmp_fromma = np.append(tmp_fromma, from_ma)
                tmp_toma   = np.append(tmp_toma, to_ma)

                print(tmp_fromma.shape)
                print(tmp_toma.shape)

                assert(0)

                #signals[from_name] = signals[from_name].append(from_ma)
                #signals[to_name] = signals[to_name].append(to_ma)
                # print(tmp_cms.shape)
                # print(" ")

                start_time = end_time
                end_date = start_time + self.computing_window

            # print(tmp_cms.shape)
            # print(signals[col + '_signal'][self.sliding_window:self.sliding_window+tmp_cms.shape[0]].shape)
            self.signals[col][self.sliding_window:self.sliding_window + tmp_cms.shape[0]] = tmp_cms
            print(col + ".... done")

            self.signals[from_name][0:tmp_fromma.shape[0]] = tmp_fromma
            self.signals[to_name][0:tmp_toma.shape[0]] = tmp_toma

            # print(signals.shape)
            # print(self.sliding_window)
            # print(tmp_cms.shape[0])
            # print(tmp_fromma.shape)

            # assert(0)
            # signals[from_name] = tmp_fromma

            # Take the difference of the signals in order to generate actual trading orders
            # signals['positions'] = signals['signal'].diff()

        # print(signals)
        # assert(0)
        return self.signals

class MarketOnClosePortfolio(Portfolio):
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, signals, initial_capital=100000.0):
        self.symbol = symbol
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()

    def generate_positions(self):
        positions = pd.DataFrame(index=signals.index).fillna(0.0)
        positions[self.symbol] = 100 * signals['signal']  # This strategy buys 100 shares
        return positions

    def backtest_portfolio(self):
        portfolio = self.positions * self.bars['bid']
        pos_diff = self.positions.diff()

        portfolio['holdings'] = (self.positions * self.bars['bid']).sum(axis=1)
        portfolio['cash'] = self.initial_capital - (pos_diff * self.bars['bid']).sum(axis=1).cumsum()

        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()
        return portfolio


class BTMUAnalysis(object):
    def __init__(self, data):
        self.data = data

    def analysis(self):
        print("all the analysis will go here")
        occs = 10
        statis = 100
        return (occs, statis)
