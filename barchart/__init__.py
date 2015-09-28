#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A Python library for Barchart API
http://freemarketdataapi.barchartondemand.com/.
"""

import os
import json
import datetime
import requests
import six
from collections import OrderedDict

try:
    import pandas as pd
except ImportError:
    _PANDAS_INSTALLED = False
else:
    _PANDAS_INSTALLED = True

URL_BASE = 'http://marketdata.websol.barchart.com'
TIMESTAMP_FMT = '%Y-%m-%dT%H:%M:%S%z'
DATE_FMT = '%Y-%m-%d'
TIMESTAMP_NOSEP_FMT = '%Y%m%d%H%M%S'

try:
    API_KEY = os.environ['BARCHART_API_KEY']
except:
    API_KEY = ''


class Config(object):
    output_pandas = True


CONFIG = Config()


def _create_from(session):
    """
    Returns a requests.Session (if session is None)
    or session (requests_cache.CachedSession)
    """
    if session is None:
        return requests.Session()
    else:
        return session


def _parse_json_response(response):
    """
    Parse JSON response
    """
    status_code = response.status_code
    status_code_expected = 200
    if status_code == status_code_expected:
        response = response.json()
        try:
            if response['status']['code'] == status_code_expected:
                return response
            else:
                raise NotImplementedError("Error code: %d - %s" % (response['status']['code'], response['status']['message']))
        except Exception as e:
            raise e
    else:
        raise NotImplementedError("HTTP status code is %d instead of %d" % (status_code, status_code_expected))


def _parse_timestamp(result, cols, timestamp_fmt=TIMESTAMP_FMT):
    """
    Returns a result where string timestamp have been parsed
    """
    for col in cols:
        s = result[col]
        result[col] = datetime.datetime.strptime(
            s[0:19] + s[19:].replace(':', ''), timestamp_fmt)
    return result


def _parse_date(result, cols, date_fmt=DATE_FMT):
    """
    Returns a result where string date have been parsed
    """
    for col in cols:
        s = result[col]
        result[col] = datetime.datetime.strptime(s, date_fmt).date()
    return result


def getQuote(symbols, session=None):
    """
    Returns quote for one (or several) symbol(s)
    getQuote sample query: http://marketdata.websol.barchart.com/getQuote.json?key=YOURAPIKEY&symbols=ZC*1,IBM,GOOGL,^EURUSD
    """

    def parse_result(result):
        for col in ['serverTimestamp', 'tradeTimestamp']:
            s = result[col]
            result[col] = datetime.datetime.strptime(
                s[0:19] + s[19:].replace(':', ''), TIMESTAMP_FMT)
        return result

    endpoint = '/getQuote.json'
    url = URL_BASE + endpoint
    params = {
        'key': API_KEY,
        'symbols': ",".join(symbols),
    }
    session = _create_from(session)
    response = session.get(url, params=params)
    response = _parse_json_response(response)
    timestamp_cols = ['serverTimestamp', 'tradeTimestamp']
    if _PANDAS_INSTALLED and CONFIG.output_pandas and not isinstance(symbols, six.string_types):
        df = pd.DataFrame(response['results'])
        for col in timestamp_cols:
            df[col] = pd.to_datetime(df[col])
        return df # returns a Pandas DataFrame
    else:
        results = response['results']
        if isinstance(symbols, six.string_types):
            d = results[0]
            d = _parse_timestamp(d, timestamp_cols)
            return d # returns a dict
        else:
            for i, d in enumerate(results):
                d = _parse_timestamp(d, timestamp_cols)
            return results # returns a list


def _getHistory_one_symbol(symbol, startDate, typ='daily', session=None):
    """
    getHistory sample query: http://marketdata.websol.barchart.com/getHistory.json?key=YOURAPIKEY&symbol=IBM&type=daily&startDate=20140928000000
    """

    endpoint = '/getHistory.json'
    url = URL_BASE + endpoint
    params = {
        'key': API_KEY,
        'symbol': symbol,
        'type': typ,
        'startDate': startDate
    }
    session = _create_from(session)
    response = session.get(url, params=params)
    response = _parse_json_response(response)
    if _PANDAS_INSTALLED and CONFIG.output_pandas:
        timestamp_cols = ['timestamp', 'tradingDay']
        df = pd.DataFrame(response['results'])
        for col in timestamp_cols:
            df[col] = pd.to_datetime(df[col])
        #df['tradingDay'] = df['tradingDay'].map(lambda s: datetime.datetime.strptime(s, DATE_FMT).date())
        df = df.set_index('timestamp')
        return df # returns a Pandas DataFrame
    else:
        d = response['results']
        timestamp_cols = ['timestamp']
        date_cols = ['tradingDay']
        d = _parse_timestamp(d, timestamp_cols)
        d = _parse_date(d, date_cols)
        return d


def getHistory(symbols, startDate, typ='daily', session=None):
    """
    Returns history for ONE (or SEVERAL) symbol(s)
    """
    try:
        startDate = startDate.dt.strftime(TIMESTAMP_NOSEP_FMT)
    except:
        pass

    if isinstance(symbols, six.string_types):
        result = _getHistory_one_symbol(symbols, startDate, typ, session)
        return result # returns a Pandas Panel
    else:
        d = OrderedDict()
        for symbol in symbols:
            d[symbol] = _getHistory_one_symbol(symbol, startDate, typ, session)
        if _PANDAS_INSTALLED and CONFIG.output_pandas:
            panel = pd.Panel.from_dict(d)
            return panel # returns a Pandas Panel
        else:
            return d # returns an OrderedDict
