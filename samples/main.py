#!/usr/bin/env python
# -*- coding: utf-8 -*-

import barchart
from barchart import getHistory, getQuote, CONFIG


# API key setup
# =============
#barchart.API_KEY = 'YOURAPIKEY'
#You can also set an environment variable using Bash
#export BARCHART_API_KEY="YOURAPIKEY"


# requests_cache is optional
# use it to have a cache mechanism
# a session parameter can be pass to functions
# =============================================
import datetime
import requests_cache
session = requests_cache.CachedSession(cache_name='cache',
    backend='sqlite', expire_after=datetime.timedelta(days=1))
#session = None # pass a None session to avoid caching queries


"""
# getQuote with ONE symbol
# ========================
symbol = "^EURUSD"
quote = getQuote(symbol, session=session)
print(quote) # quote is a dict


# getQuote with SEVERAL symbols
# =============================
symbols = ["ZC*1", "IBM", "GOOGL" , "^EURUSD"]
quotes = getQuote(symbols, session=session)
print(quotes) # quotes is a Pandas DataFrame
#print(quotes.dtypes)
#print(type(quotes['serverTimestamp'][0])) # should be a pandas.tslib.Timestamp

CONFIG.output_pandas = False
quotes = getQuote(symbols, session=session)
print(quotes) # quotes is a Pandas DataFrame
CONFIG.output_pandas = True

# getHistory with ONE symbol
# ==========================
symbol = 'IBM'
history = getHistory(symbol, typ='daily', startDate='20140928000000')
print(history)
print(history.dtypes)
print(type(history['timestamp'][0])) # should be a pandas.tslib.Timestamp
print(type(history['tradingDay'][0])) # should be a pandas.tslib.Timestamp
"""


# getHistory with SEVERAL symbols
# ===============================
symbols = ["ZC*1", "IBM", "GOOGL" , "^EURUSD"]
histories = getHistory(symbols, typ='daily', startDate='20140928000000')
print(histories)
print(histories.dtypes)
#print(type(histories['timestamp'][0])) # should be a pandas.tslib.Timestamp
