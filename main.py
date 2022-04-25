import pandas as pd
import pandas_ta as ta
import ccxt
import requests
import schedule
import time
from datetime import datetime


exchange = ccxt.binance()
discord_webhook_url = "https://discord.com/api/webhooks/962754927896195103/rC9nH7foyWOmQGpa9LRBOUF3s390UQe_1Lgs_S9I6FLmCVXvupY9_ZUXDHPuFvA5JxBI"
in_position = False


def add_ta(df):
    
    supertrend = df.ta.supertrend(period=7, multiplier=3)
  
    df_result = pd.concat([df,supertrend], axis=1)
    
    return df_result


def check_buy_sell_signals(df):
    global in_position
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("checking for buy and sell signals")
    print(df.tail(4))
    
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    
    if df['SUPERTd_7_3.0'][previous_row_index] == -1 and df['SUPERTd_7_3.0'][last_row_index] == 1:
        print("changed to uptrend, buy")
        if not in_position:
            # order = exchange.create_market_buy_order('BTC/USDT', 0.05)
            # print(order)
            message1 = f"---------------------------\nat: {now_time} \n**BUY at:** {df['close'][last_row_index]}\n---------------------------"
            payload = {"username": "alertbot","content": message1}
            requests.post(discord_webhook_url, json=payload)
            in_position = True
        else:
            print("already in position, nothing to do")
            message1 = f"---------------------------\nat: {now_time} \n**already in position**, nothing to do \n---------------------------"
            payload = {"username": "alertbot","content": message1}
            requests.post(discord_webhook_url, json=payload)

            
    if df['SUPERTd_7_3.0'][previous_row_index] == 1 and df['SUPERTd_7_3.0'][last_row_index] == -1:
        if in_position:
            print("changed to downtrend, sell")
            # order = exchange.create_market_sell_order('BTC/USDT', 0.05)
            # print(order)
            message1 = f"---------------------------\nat: {now_time} \n**SELL at:** {df['close'][last_row_index]}\n---------------------------"
            payload = {"username": "alertbot","content": message1}
            requests.post(discord_webhook_url, json=payload)            
            in_position = False
        else:
            print("You aren't in position, nothing to sell")
            message1 = f"---------------------------\nat: {now_time} \n**You aren't in position**, nothing to sell \n---------------------------"
            payload = {"username": "alertbot","content": message1}
            requests.post(discord_webhook_url, json=payload)

            
    if df['SUPERTd_7_3.0'][previous_row_index] == df['SUPERTd_7_3.0'][last_row_index]:
        print("Wait for change in trend")
        message1 = f"---------------------------\nat: {now_time} \n**Wait for change in trend**, nothing to do\n---------------------------"
        payload = {"username": "alertbot","content": message1}
        requests.post(discord_webhook_url, json=payload)



def run_bot():
    
    print('Fetching new bars for :')
    print('Iran Time :' ,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print('UTC  Time :' ,datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))   

    
    bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1m', limit=100)
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df_with_ta = add_ta(df)
    
    check_buy_sell_signals(df_with_ta)



schedule.every(20).seconds.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)