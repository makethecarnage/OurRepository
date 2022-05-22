import tinkoff.invest as tinvest
from pandas import DataFrame
from datetime import datetime, timedelta

token = 't.og8jYwK7ryJy3Ns1EGYcPvOBOFpONQbnNdlOL75ZgJMtXwFWqZXAqD5YEuXJPLKMgF6wAG8ycLhBlClXZg-Ncg'

def get_ticker():
    ticker = input()
    return ticker

def get_figi():
    try:
        stocks = DataFrame(
            client.instruments.shares(instrument_status=tinvest.InstrumentStatus.INSTRUMENT_STATUS_BASE).instruments,
            columns=['figi', 'ticker']
        )
        figi = stocks[stocks['ticker'] == get_ticker()]['figi'].iloc[0]
        return figi
    except (TypeError, IndexError):
        print('Тикера не существует, или он был введен неправильно.')

def get_candle():
    candles = client.market_data.get_candles(
        figi=get_figi(),
        from_=datetime.utcnow()-timedelta(days=5),
        to=datetime.utcnow(),
        interval=tinvest.CandleInterval.CANDLE_INTERVAL_HOUR
    )
    df = DataFrame([{
        'time': c.time,
        'volume': c.volume,
        'open': money(c.open),
        'close': money(c.close),
        'high': money(c.high),
        'low': money(c.low),
    } for c in candles.candles])
    return df

def money(value):
    return value.units + value.nano / 1e9

if __name__ == "__main__":
    with tinvest.Client(token) as client:
        print(get_candle())