import pandas as pd
import pandas_ta as ta
import ccxt
import requests
from datetime import datetime


discord_webhook_url = "https://discord.com/api/webhooks/962754927896195103/rC9nH7foyWOmQGpa9LRBOUF3s390UQe_1Lgs_S9I6FLmCVXvupY9_ZUXDHPuFvA5JxBI"
exchange = ccxt.binance()
symbol = 'BTC/USDT'
interval = '5m'

def get_ohlcv(symbol, interval, limit=1000) -> pd.DataFrame:

    # headers
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

    # get candles from exchange
    bars = exchange.fetch_ohlcv(symbol, timeframe=interval, limit=limit)

    # convert list of list to pandas dataframe and delete last row
    df = pd.DataFrame(bars[:-1], columns=columns)

    # convert millisecond to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df


df_start = get_ohlcv(symbol, interval)


supertrend = df_start.ta.supertrend(period=7, multiplier=3)
macd = df_start.ta.macd(fast=14, slow=28)
rsi = df_start.ta.rsi()
adx = df_start.ta.adx()
df_end = pd.concat([df_start,supertrend,macd,rsi,adx], axis=1)


last_row = df_end.iloc[-1]


if last_row['SUPERTd_7_3.0'] == 1:
    if last_row['ADX_14'] < 25:
        message1 = f"---------------------------\nat: {last_row['timestamp']} \nSupertrend Signal: **Buy** \nADX Signal: **NO TREND** \n**WAIT**\n---------------------------"
        print(message1)
    
    if last_row['ADX_14'] >= 25:
        if last_row['DMP_14'] > last_row['DMN_14']:
            message1 = f"---------------------------\nat: {last_row['timestamp']} \nSupertrend Signal: **Buy** \nADX Signal: **STRONG UPTREND** \n**BUY at {last_row['close']}**\n---------------------------"
            print(message1)    
        if last_row['DMN_14'] > last_row['DMP_14']:
            message1 = f"---------------------------\nat: {last_row['timestamp']} \nSupertrend Signal: **Buy** \nADX Signal: **STRONG DOWNTREND** \n**WTF**\n---------------------------"
            print(message1)
        

    
if last_row['SUPERTd_7_3.0'] == 0:
    if last_row['ADX_14'] < 25:
        message1 = f"---------------------------\nat: {last_row['timestamp']} \nSupertrend Signal: **SELL** \nADX Signal: **NO TREND** \n**WAIT**\n---------------------------"
        print(message1)
    
    if last_row['ADX_14'] >= 25:
        if last_row['DMP_14'] > last_row['DMN_14']:
            message1 = f"---------------------------\nat: {last_row['timestamp']} \nSupertrend Signal: **SELL** \nADX Signal: **STRONG UPTREND** \n**WTF**\n---------------------------"
            print(message1)    
        if last_row['DMN_14'] > last_row['DMP_14']:
            message1 = f"---------------------------\nat: {last_row['timestamp']} \nSupertrend Signal: **SELL** \nADX Signal: **STRONG DOWNTREND** \n**SELL at {last_row['close']}**\n---------------------------"
            print(message1)


payload = {"username": "alertbot","content": message1 }
requests.post(discord_webhook_url, json=payload)