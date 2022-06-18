import tinkoff.invest as tinvest
import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from ta.trend import ema_indicator
from yahoo_fin import news
from yahoo_fin import options

token = 't.og8jYwK7ryJy3Ns1EGYcPvOBOFpONQbnNdlOL75ZgJMtXwFWqZXAqD5YEuXJPLKMgF6wAG8ycLhBlClXZg-Ncg'

def get_ticker():
    ticker = input('Введите тикер ')
    return ticker

def get_info(ticker):
    try:
        stocks = DataFrame(
            client.instruments.shares(instrument_status=tinvest.InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments,
            columns=['name', 'figi', 'ticker']
        )
        comp_info = stocks[stocks['ticker'] == ticker]
        return comp_info
    except (TypeError, IndexError):
        print('Тикера не существует, или он был введен неправильно.')

def get_candle(figi, tf):     #Полные данные по свечи

    info = []
    candles = []

    if tf == 'hour':
        final_date = datetime.utcnow()
        start_date = datetime.utcnow() - timedelta(days=7)
        for i in range(122):
            info = client.market_data.get_candles(
                figi=figi,
                from_=start_date,
                to=final_date,
                interval=tinvest.CandleInterval.CANDLE_INTERVAL_HOUR #Для разных тф свои лимиты: для ТФ день - 365 свечей, для ТФ час - неделя, для ТФ минута - сутки, если потребуется больше свечей - цикл
            )
            candles.extend(info.candles)
            final_date = start_date
            start_date = final_date - timedelta(days=7)

    elif tf == 'day':
        final_date = datetime.utcnow()
        start_date = datetime.utcnow() - timedelta(days=365)
        for i in range(10):
            info = client.market_data.get_candles(
                figi=figi,
                from_=start_date,
                to=final_date,
                interval=tinvest.CandleInterval.CANDLE_INTERVAL_DAY #Для разных тф свои лимиты: для ТФ день - 365 свечей, для ТФ час - неделя, для ТФ минута - сутки, если потребуется больше свечей - цикл
            )
            #print(info.candles)
            candles.extend(info.candles)
            final_date = start_date
            start_date = final_date - timedelta(days=365)
        #print(len(candles))

    return candles

def create_dataframe(candles):
    df = DataFrame([{
        'time': c.time,
        'volume': c.volume,
        'open': money(c.open),
        'close': money(c.close),
        'high': money(c.high),
        'low': money(c.low),
    } for c in candles])
    return df

def money(value):
    return value.units + value.nano / 1e9

def graph(df, name):                #Для того, чтобы программа продолжилась, закрыть график
    ax = df.plot(x='time', y='close')
    df.plot(ax=ax, x='time', y='ema')
    ax.set_title('График компании ' + name)
    plt.show()

def ema(df):
    df['ema'] = ema_indicator(df['close'],window=9)
    return df

def get_max_activity(df, max_act):
    df_act = df.copy(deep=True)
    if max_act == 'hour':
        for i in range(df_act.shape[0]):
            df_act.loc[i, 'time'] = df.loc[i,'time'].hour
    elif max_act == 'month':
        for i in range(df_act.shape[0]):
            df_act.loc[i, 'time'] = df.loc[i,'time'].month
    elif max_act == 'day':
        for i in range(df_act.shape[0]):
            df_act.loc[i, 'time'] = datetime.isoweekday(df.loc[i, 'time'])

    df_act = df_act.groupby(['time']).agg({'volume': 'mean'}).round(2)
    df_act['time'] = df_act.index

    df_act.plot.bar(x='time', y='volume')
    plt.show()
    return df_act

if __name__ == "__main__":
    ticker = get_ticker()
    tf = input('Введите ТФ ')  # Пока работает только для hour
    max_act = input('Максимальная активность по ')

    with tinvest.Client(token) as client:
        comp_info = get_info(ticker)
        candles = get_candle(comp_info['figi'].iloc[0], tf)
        df = create_dataframe(candles)
        df_act = get_max_activity(df, max_act)
        print(df_act)
        print('Наибольшая активность в '+ str(df_act.idxmax()[0]) + ' часов')
        df_ema = ema(df)
        #graph(df_ema, comp_info['name'].iloc[0])

    news = news.get_yf_rss(ticker)
    #print(news[0]['published']) #Пример, как узнать время новости
    pd.set_option('display.max_columns', None)
    puts = options.get_puts(ticker)
    calls = options.get_calls(ticker)
    print(puts, calls)
    exp_dates= options.get_expiration_dates(ticker)
