
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
import copy
from itertools import combinations
import csv
import json
from sqlite3 import Timestamp
from binance.client import Client
import pandas as pd
import copy
import time
import datetime
from datetime import datetime as dtime
from datetime import timedelta
import random 


'''
Access Binance through API, save various dataframes , here want to create a class
used to analyze these dataframes using backtesting, etc, to come up with analysis
'''

warnings.filterwarnings('ignore')

apikey = "ttZV43QBj1MI0yeGn4nFIZQFhiUqmmIZYOXTpohPy9AB0KDFeV1jrfRyR0LBvOzR"
skey = "kIltiqgRuFa5yEctJ6HzWxB8Rnhhy6W9E9X7U6hVEP0YRQZ6KIRd49QKV8VKePqE"

client = Client(api_key=apikey, api_secret=skey, tld='us')
account = client.get_account()


# BTC = coins.loc[coins.coin=='BTC']
class client_coin_finder:
    def __init__(self, name, dataframe):
        self.name = name
        self.dataframe = dataframe
        self.df = self.coin_df()
    def coin_df(self):
        return self.dataframe.loc[self.dataframe.coin==self.name]


# coins = pd.DataFrame(client.get_all_coins_info())
# MATIC = client_coin_finder('MATIC', coins)
# BTC_Price = client.get_symbol_ticker(symbol="BTCUSDT")
# Avg_BTC = client.get_avg_price(symbol='BTCUSDT')

def create_sorted_currency_dict():
    '''
    Creates sorted currency dictionary of all tickers based on their prices
    '''
    prices = client.get_all_tickers()
    PRICE_DF = pd.DataFrame(prices)
    # print(PRICE_DF)
    symbols = PRICE_DF['symbol'].tolist()
    prices = PRICE_DF['price'].tolist()
    float_prices = [float(x) for x in prices]

    sorted_prices = sorted(float_prices, reverse=True)

    Currency_Dict = dict(zip(symbols, float_prices))
    sorted_curr = []

    for val in sorted_prices:
        for curr, price in Currency_Dict.items():
            if price == val:
                sorted_curr.append(curr)
                del Currency_Dict[curr]
                break 
         
    sorted_dict = dict(zip(sorted_curr, sorted_prices))        

    return sorted_dict

def get_earliest(Symbol):
    '''
    Find list of currencies, for each one, find earliest timestamp
    '''

    return client._get_earliest_valid_timestamp(symbol=Symbol, interval='1d')

def get_historical_info(Symbol, Interval, start, end=None):
    '''
    Gets historical info for a symbol using an interval, 
    can use string datetime, or timestamp
    '''    
    if type(start)!= int:
        start = int(datetime.datetime.strptime(start, "%d/%m/%Y").timestamp()*1000)
    if end!=None:
        if type(end)!=int:
            end = int(datetime.datetime.strptime(end, "%d/%m/%Y").timestamp()*1000)


    bars = client.get_historical_klines(symbol=Symbol,\
        interval=Interval, start_str=start, end_str=end, limit=1000)
    # print(bars)
    DF = pd.DataFrame(bars)
    if len(DF.columns)>0:

        DF['Date']= pd.to_datetime(DF.iloc[:,0], unit='ms')
        DF.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',\
            'Close Time', 'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume',\
                'Taker Buy Quote Asset Volume', 'Ignore', 'Date']
        df = DF[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.set_index('Date', inplace=True)

        for column in df.columns:
            df[column]= pd.to_numeric(df[column], errors='coerce')
        
        return df

class Find_possible_strategies:
    '''
    Takes in list of range of parameters, creates one condensed list with all possible combinations
    '''
    def __init__(self, return_range, vol_low, vol_high ):
        self.return_range = return_range
        self.vol_low = vol_low 
        self.vol_high = vol_high
        
    def create_strat_list(self):
        combos = []
        for x in range(self.return_range[0],self.return_range[1]):
            for y in range(self.vol_low[0], self.vol_low[1]):
                for z in range(self.vol_high[0], self.vol_high[1]):
                    combos.append((x,y,z))

        return combos

class Backtest:
    '''
    Using previous data, parameters, trading costs, can find specific trades
    and backtest in various ways
    '''
    def __init__(self, currency, start, end, parameters, trading_cost):
        self.currency = currency
        self.start = start
        self.end = end   
        self.df =  get_historical_info(currency, '1d', start=self.start, end=self.end)
        self.data = self.create_df()
        self.failed_df = False
        self.copy_df = copy.deepcopy(self.data)
        self.parameters = Find_possible_strategies(parameters[0], parameters[1], parameters[2]).create_strat_list()
        self.trading_cost = trading_cost
        self.param_dict = {}
        self.backtest_dict = {}   

    def create_df(self):
        '''
        Creates a new dataframe using the historical data
        '''
        
        if type(self.df) !=type(None):
            df = self.df       
        

            df['returns'] = np.log(df.Close / df.Close.shift(1))
            df = df[['Close', 'Volume', 'returns']]
            df['vol_ch']= np.log(df.Volume.div(df.Volume.shift(1)))
            df.loc[df.vol_ch >3, "vol_ch"] =np.nan
            df.loc[df.vol_ch <-3, 'vol_ch'] = np.nan
            return df 
        else:
            self.failed_df = True
            return
    def set_trading_parameters(self, index):
        '''
        Stores DF object at index in the param_dict, based on specified parameters using given index
        from the parameter list, filters dataframe to meet conditions, stores df in param_dict
        '''
        params = self.parameters[index]
        return_thresh = np.percentile(self.data.returns.dropna(), params[0])
        cond1 = self.data.returns >= return_thresh
        volume_thresh = np.percentile(self.data.vol_ch.dropna(), [params[1], params[2]])
        cond2 = self.data.vol_ch.between(volume_thresh[0], volume_thresh[1])
        self.data['position']=1
        self.data.loc[cond1 & cond2, 'position']= 0
        self.param_dict[index] = copy.deepcopy(self.data)
        self.data = self.copy_df 
        
    def backtest(self, index):
        '''
        Testing individual strategy based on index of the param dict, which stores dataframe object
        '''
        df = self.param_dict[index]
        df['strategy']= df.position.shift(1) * df['returns']
        df['trades'] = df.position.diff().fillna(0).abs()
        df.strategy = df.strategy + df.trades*self.trading_cost
        df['creturns'] = df['returns'].cumsum().apply(np.exp)
        df['cstrategy'] = df['strategy'].cumsum().apply(np.exp)

        end = len(df.index)
        self.backtest_dict[index] = df.cstrategy[end-1]

    def create_backtest_dict(self):
        '''
        Testing each parameter combination using param_dictionary objects,
        Saving each combination to backtest dictionary
        '''
        for i in range(len(self.parameters)):
            self.set_trading_parameters(i)
            self.backtest(i)
    
    def find_best_strat(self):
        '''
        Finding best return from all possible strategies in the backtest dictionary
        '''
        key = int(max(self.backtest_dict, key=self.backtest_dict.get))
        return self.parameters[key]  



count = 0
curr_date_list = []
for curr in create_sorted_currency_dict().keys():
    date = get_earliest(curr)
    curr_date_list.append((curr,date))
    count +=1
    if count ==10:
        break 

for x in range(len(curr_date_list)):

    Curr = curr_date_list[x][0]
    Start = curr_date_list[x][1]
    B = Backtest(Curr,Start,'01/01/2021',[(65,75), (15,25), (15,25)], -.005)
    if B.failed_df == False:
        
        print(B.data)
    # B.create_backtest_dict()
    # print(B.find_best_strat())

# gets all currencies in descending order based on price
# currencies = [x for x in create_sorted_currency_dict()]
# print(currencies)

# B = Backtest('BTCUSD',get_earliest('BTCUSD'),'01/01/2021',[(60,75), (5,25), (10,25)], -.005)
# B.create_backtest_dict()
# print(B.find_best_strat())
 











