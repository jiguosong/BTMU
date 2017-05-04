import sys, math
import numpy as np
import pandas as pd
import datetime as dt
import velidb.btcommon as bt
from velidb.tobcache import tob_cache

# user defined class for preparing data
from DATA import *
from Abstract_Model import Strategy, Portfolio

class MovingAverageCrossStrategy(Strategy):
    """    
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol.
    short_window - Lookback period for short moving average.
    long_window - Lookback period for long moving average."""

    def __init__(self, symbol, bars, short_window=100, long_window=400):
        self.symbol = symbol
        self.bars = bars
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        """Returns the DataFrame of symbols containing the signals
        to go long, short or hold (1, -1 or 0)."""
        signals = pd.DataFrame(index=self.bars.index)
        signals['signal'] = 0.0

        # Create the set of short and long simple moving averages over the
        # respective periods
        signals['short_mavg'] = self.bars['bid'].rolling(self.short_window, min_periods=1).mean()
        signals['long_mavg']  = self.bars['bid'].rolling(self.long_window, min_periods=1).mean()

        # Create a 'signal' (invested or not invested) when the short moving average crosses the long
        # moving average, but only for the period greater than the shortest moving average window
        signals['signal'][self.short_window:] = np.where(signals['short_mavg'][self.short_window:]
            > signals['long_mavg'][self.short_window:], 1.0, 0.0)

        # Take the difference of the signals in order to generate actual trading orders
        signals['positions'] = signals['signal'].diff()

        return signals


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

#
# if __name__ == "__main__":
#     # Obtain daily bars of AAPL from Yahoo Finance for the period
#     # 1st Jan 1990 to 1st Jan 2002 - This is an example from ZipLine
#     symbol = 'AAPL'
#     bars = DataReader(symbol, "yahoo", datetime.datetime(1990, 1, 1), datetime.datetime(2002, 1, 1))
#
#     # Create a Moving Average Cross Strategy instance with a short moving
#     # average window of 100 days and a long window of 400 days
#     mac = MovingAverageCrossStrategy(symbol, bars, short_window=100, long_window=400)
#     signals = mac.generate_signals()
#
#     # Create a portfolio of AAPL, with $100,000 initial capital
#     portfolio = MarketOnClosePortfolio(symbol, bars, signals, initial_capital=100000.0)
#     returns = portfolio.backtest_portfolio()
#
#     # Plot two charts to assess trades and equity curve
#     fig = plt.figure()
#     fig.patch.set_facecolor('white')  # Set the outer colour to white
#     ax1 = fig.add_subplot(211, ylabel='Price in $')
#
#     # Plot the AAPL closing price overlaid with the moving averages
#     bars['Close'].plot(ax=ax1, color='r', lw=2.)
#     signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2.)
#
#     # Plot the "buy" trades against AAPL
#     ax1.plot(signals.ix[signals.positions == 1.0].index,
#              signals.short_mavg[signals.positions == 1.0],
#              '^', markersize=10, color='m')
#
#     # Plot the "sell" trades against AAPL
#     ax1.plot(signals.ix[signals.positions == -1.0].index,
#              signals.short_mavg[signals.positions == -1.0],
#              'v', markersize=10, color='k')
#
#     # Plot the equity curve in dollars
#     ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
#     returns['total'].plot(ax=ax2, lw=2.)
#
#     # Plot the "buy" and "sell" trades against the equity curve
#     ax2.plot(returns.ix[signals.positions == 1.0].index,
#              returns.total[signals.positions == 1.0],
#              '^', markersize=10, color='m')
#     ax2.plot(returns.ix[signals.positions == -1.0].index,
#              returns.total[signals.positions == -1.0],
#              'v', markersize=10, color='k')
#
#     # Plot the figure
#     fig.show()







# the following code is from
# http://wiki.veliosystems.com/display/CORP/Velio+Python+Backtester

# class movingavg(object):
#     def __init__(self, data, period):
#         self.period = period
#         self.data = data
#
#     def initialized(self):
#         return len(self.data) >= self.period
#
#     def value(self):
#         return np.average(self.data[-self.period:])
#
#     def moving_average(a, n=3):
#         ret = np.cumsum(a, dtype=float)
#         ret[n:] = ret[n:] - ret[:-n]
#         return ret[n - 1:] / n
#
#
#
# class ma_state(object):
#     not_ready = 0
#     fast_below = 1
#     fast_above = 2
#     pending_order = 3
#     long = 4
#     short = 5
#     flat = 6
#
# class MATest(bt.tradeSystem):
#     def __init__(self, context):
#         self.context = context
#         self.data = []
#         self.stats = []
#         self.fast = movingavg(self.data, 50)
#         self.slow = movingavg(self.data, 100)
#         self.position = 0
#         self.state = ma_state.not_ready
#
#     def closePosition(self, tob):
#         if self.position > 0:
#             rate = tob.bid.price
#             side = bt.price_side.offer
#             sell = True
#         else:
#             rate = tob.offer.price
#             side = bt.price_side.bid
#             sell = True
#         self.state = ma_state.pending_order
#         o = bt.order_message(msg_type=bt.order_msg_type.neworder, order_id=job.newOrderId(), instrument=tob.instrument,
#                              rate=rate, amount=abs(self.position), side=side, order_type=bt.expire_type.gtc_limit)
#         self.context.sendOrder(o)
#         return (not sell, sell)
#
#     def openPosition(self, tob, side):
#         if side == bt.price_side.bid:
#             rate = tob.offer.price
#             amt = 1
#         else:
#             rate = tob.bid.price
#             amt = 1
#         self.state = ma_state.pending_order
#
#         o = bt.order_message(msg_type=bt.order_msg_type.neworder, order_id=job.newOrderId(), instrument=tob.instrument,
#                              rate=rate, amount=amt, side=side, order_type=bt.expire_type.gtc_limit)
#         self.context.sendOrder(o)
#
#     def record(self, time, stats):
#         stats['time'] = time
#         self.stats.append(stats)
#
#     def onTOB(self, tob):
#         if tob.bid and tob.offer:
#             # Calc the midpoint and generate a moving average
#             mid = (tob.bid.price + tob.offer.price) / 2
#             # Save the last XX events
#             self.data.append(mid)
#
#             if self.slow.initialized():
#                 slow = self.slow.value()
#                 fast = self.fast.value()
#                 buy = False
#                 sell = False
#                 if self.state == ma_state.not_ready or self.state == ma_state.flat:
#                     if fast > slow:
#                         self.state = ma_state.fast_above
#                     else:
#                         self.state = ma_state.fast_below
#                 elif self.state == ma_state.fast_below:
#                     if fast > slow:
#                         self.openPosition(tob, bt.price_side.bid)
#                         buy = True
#                 elif self.state == ma_state.fast_above:
#                     if fast < slow:
#                         self.openPosition(tob, bt.price_side.offer)
#                         sell = True
#                 elif self.state == ma_state.long:
#                     if fast < slow:
#                         buy, sell = self.closePosition(tob)
#                 elif self.state == ma_state.short:
#                     if fast > slow:
#                         buy, sell = self.closePosition(tob)
#
#                 pnl = self.context.getProfit(tob)
#                 stats = {'mid': mid, 'slow': slow, 'fast': fast, 'buy': buy, 'sell': sell, 'pnl': pnl}
#                 self.record(tob.time, stats)
#
#     def onTicker(self, tick):
#         print('%s:TIC %s %d@%f ' % (tick.time, tick.instrument.symbol, int(tick.amount), tick.price,))
#
#     def onExeReport(self, exe):
#         self.position += exe.amount
#         if self.position > 0:
#             self.state = ma_state.long
#         elif self.position < 0:
#             self.state = ma_state.short
#         else:
#             self.state = ma_state.flat
#             # print '%s PNL=%s' % (exe.instrument, self.context.getPNL(exe.instrument))
#             # print '%s:TRD %s %d@%f ' % (exe.time,  exe.instrument.symbol, int(exe.amount), exe.rate)
#
#     def initialize(self):
#         print('initialized')
#         self.counter = 0
#
#     def job_complete(self):
#         print('complete')



# another piece code from
# http://wiki.veliosystems.com/display/CORP/Using+Velidb+and+Pandas+for+Time+Series+Prediction


# # This is an example of using pandas and velidb for researching trading models
# # This example avoids iteration to create a very fast mechanism for testing and optimizing models.
# # Note: For the sake of simplicity this model does not account for bid/offer spread...
#
# import datetime as dt
# import pandas as pd
# from multiprocessing import Pool
#
# import velibt.btcommon as bt
# import velibt.velidb as vdb
#
#
# class EMATest():
#     def __init__(self, start, end):
#
#         inst = bt.instrument(bt.assetClass.FT, 'CME', 'CL')
#         v = vdb.vdbCF(vdb.dataType.tob, start, end, inst)
#         tab = v.getData()
#         self.tick = vdb.tab2pandas(tab)
#
#         # Convert to 1 sec bars to make math easy
#         self.tick = self.tick.groupby(level=0).first()
#         self.tick = self.tick.asfreq(freq='1S', method='pad')
#
#     def calc(self, fastp, slowp, lookahead):
#         tick = self.tick.copy()
#         # Calc the averages
#         fast = pd.ewma(tick.bid, span=fastp)
#         slow = pd.ewma(tick.bid, span=slowp)
#
#         # Find buy and sell signals as bool arrays
#         buy = (fast > slow) & (fast.shift(-1) < slow)
#         sell = (fast < slow) & (fast.shift(-1) > slow)
#
#         tick['longexit'] = tick.shift(freq=pd.offsets.Second(lookahead))['bid']
#         tick['shortexit'] = tick.shift(freq=pd.offsets.Second(lookahead))['offer']
#
#         tick['longprice'] = tick.ix[buy]['offer']
#         tick['shortprice'] = tick.ix[sell]['bid']
#
#
#         # Quick performance check
#         #print 'Avergage Buy/Sell', tick['longprice'].mean(), tick['shortprice'].mean()
#
#         # Now if we assume an exit lookahead seconds after then signal and check PnL
#         # For buy entries
#         tmp = tick.dropna(subset=['longprice'])
#         long_pnl = (tmp.longexit - tmp.longprice).sum()
#
#         # For buy entries
#         tmp = tick.dropna(subset=['shortprice'])
#         short_pnl = (tmp.shortprice - tmp.shortexit).sum()
#         return (long_pnl, short_pnl, long_pnl+short_pnl)
#
#
# def runmod(start, end, fast, slow, look):
#     mod = EMATest(start, end)
#     long_pnl, short_pnl, total = mod.calc(fast, slow, look)
#     #print 'fast(%d) slow(%d) look(%d) PnL %f/%f total=%f' % (fast, slow, look, long_pnl, short_pnl, total)
#     return (fast, slow, look, long_pnl, short_pnl, total)
#
#
# if __name__ == '__main__':
#     pool = Pool(processes=4)              # start 4 worker processes
#     results = []
#     start = dt.datetime(2014, 1, 3)
#     end = dt.datetime(2014, 1, 4)
#     #mod = EMATest(start, end)
#
#     for fast in range(50, 200, 20):
#         for slow in range(50, 400, 20):
#             if fast >= slow:
#                 continue
#             for look in range(10, 100, 20):
#                 #long_pnl, short_pnl, total = mod.calc(fast, slow, look)
#                 result = pool.apply_async(runmod, [start, end, fast, slow, look])    # evaluate "f(10)" asynchronously
#                 results.append(result)
#                 #print result.get(timeout=1)           # prints "100" unless your computer is *very* slow
#                 #print pool.map(f, range(10))          # prints "[0, 1, 4,..., 81]"
#     for result in results:
#         fast, slow, look, long_pnl, short_pnl, total = result.get()
#         print 'fast(%d) slow(%d) look(%d) PnL %f/%f total=%f' % (fast, slow, look, long_pnl, short_pnl, total)