import tinkoff.invest as tinvest
from pandas import DataFrame

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



if __name__ == "__main__":
    with tinvest.Client(token) as client:
