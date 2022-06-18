from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
import matplotlib.pyplot as plt
import threading
import re
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from yahoo_fin import options
import tinkoff.invest as tinvest
from pandas import DataFrame
from datetime import datetime, timedelta

from ta.trend import ema_indicator
from kivy.uix.spinner import Spinner


class TestApp(App):

    def build(self):
        Window.size = (1000, 800)
        self.df_act = None
        self.my_string = None
        self.textInfoLabel = Label(size_hint=[.5, .4])
        gl = GridLayout(cols=3, rows=3)

        gl.add_widget(Label(text='Введите тикер, Таймфрейм' + '\n' + ' и Период анализа', size_hint=[.4, .2]))
        plt.plot()

        self.plt_element = FigureCanvasKivyAgg(plt.gcf(), size_hint=[.5,
                                                                     .4])  # Label(text='График не доступен', size_hint=[.5, .4]) #

        gl.add_widget(self.plt_element)
        # gl.add_widget(Label(text='График', size_hint=[.5, .4]))
        gl.add_widget(self.textInfoLabel)

        self.textInput = TextInput(multiline=False, size_hint=[.1, None], font_size=30)
        self.textInput.bind(text=self.create_string)
        gl.add_widget(self.textInput)

        self.spinnerObject = Spinner(text="TF", values=("day", "hour"), size_hint=[.1, .1])
        gl.add_widget(self.spinnerObject)

        self.spinnerObject2 = Spinner(text="Period", values=("hour", "day", 'month'), size_hint=[.1, .1])
        gl.add_widget(self.spinnerObject2)

        self.buttonGo = Button(text='Выполнить', size_hint=[.1, .1], on_press=self.complete)
        gl.add_widget(self.buttonGo)

        print(self.df_act)
        self.gl = gl
        return gl

    def create_string(self, instance, textInput):
        self.my_string = str(self.textInput.text)

    def print(self, instance):
        print(self.my_string)

    def get_info(self):
        ticker = self.my_string
        token = 't.og8jYwK7ryJy3Ns1EGYcPvOBOFpONQbnNdlOL75ZgJMtXwFWqZXAqD5YEuXJPLKMgF6wAG8ycLhBlClXZg-Ncg'
        with tinvest.Client(token) as client:
            try:
                stocks = DataFrame(
                    client.instruments.shares(
                        instrument_status=tinvest.InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments,
                    columns=['name', 'figi', 'ticker']
                )
                comp_info = stocks[stocks['ticker'] == ticker]
                return comp_info
            except (TypeError, IndexError):
                print('Тикера не существует, или он был введен неправильно.')

    def get_candle(self, figi):  # Полные данные по свечи

        info = []
        candles = []
        token = 't.og8jYwK7ryJy3Ns1EGYcPvOBOFpONQbnNdlOL75ZgJMtXwFWqZXAqD5YEuXJPLKMgF6wAG8ycLhBlClXZg-Ncg'
        with tinvest.Client(token) as client:
            if self.spinnerObject.text == 'hour':
                final_date = datetime.utcnow()
                start_date = datetime.utcnow() - timedelta(days=7)
                for i in range(122):
                    info = client.market_data.get_candles(
                        figi=figi,
                        from_=start_date,
                        to=final_date,
                        interval=tinvest.CandleInterval.CANDLE_INTERVAL_HOUR
                        # Для разных тф свои лимиты: для ТФ день - 365 свечей, для ТФ час - неделя, для ТФ минута - сутки, если потребуется больше свечей - цикл
                    )
                    candles.extend(info.candles)
                    final_date = start_date
                    start_date = final_date - timedelta(days=7)

            elif self.spinnerObject.text == 'day':
                final_date = datetime.utcnow()
                start_date = datetime.utcnow() - timedelta(days=365)
                for i in range(10):
                    info = client.market_data.get_candles(
                        figi=figi,
                        from_=start_date,
                        to=final_date,
                        interval=tinvest.CandleInterval.CANDLE_INTERVAL_DAY
                        # Для разных тф свои лимиты: для ТФ день - 365 свечей, для ТФ час - неделя, для ТФ минута - сутки, если потребуется больше свечей - цикл
                    )

                    candles.extend(info.candles)
                    final_date = start_date
                    start_date = final_date - timedelta(days=365)

        return candles

    def create_dataframe(self, candles):
        df = DataFrame([{
            'time': c.time,
            'volume': c.volume,
            'open': self.money(c.open),
            'close': self.money(c.close),
            'high': self.money(c.high),
            'low': self.money(c.low),
        } for c in candles])
        return df

    def money(self, value):
        return value.units + value.nano / 1e9

    def graph(self, df, name):  # Для того, чтобы программа продолжилась, закрыть график
        ax = df.plot(x='time', y='close')
        df.plot(ax=ax, x='time', y='ema')
        ax.set_title('График компании ' + name)
        plt.show()

    def ema(self, df):
        df['ema'] = ema_indicator(df['close'], window=9)
        return df

    def get_max_activity(self, df):
        """

        """
        self.df_act = df.copy(deep=True)

        if self.spinnerObject2.text == 'hour':
            for i in range(self.df_act.shape[0]):
                self.df_act.loc[i, 'time'] = df.loc[i, 'time'].hour
        elif self.spinnerObject2.text == 'month':
            for i in range(self.df_act.shape[0]):
                self.df_act.loc[i, 'time'] = df.loc[i, 'time'].month
        elif self.spinnerObject2.text == 'day':
            for i in range(self.df_act.shape[0]):
                self.df_act.loc[i, 'time'] = datetime.isoweekday(df.loc[i, 'time'])

        self.df_act = self.df_act.groupby(['time']).agg({'volume': 'mean'}).round(2)
        self.df_act['time'] = self.df_act.index

        plot = plt.plot(self.df_act['time'], self.df_act['volume'])
        # plt.bar(1, 0.8)
        plt.ylabel('volume')
        plt.xlabel('time')
        self.gl.do_layout()
        self.df_act.plot.bar(x='time', y='volume')
        self.thr = threading.Thread(target=plt.show)
        self.thr.run()

    '''tf = input('Введите ТФ ')  # Пока работает только для hour
        max_act = input('Максимальная активность по ')'''

    def create_options(self):

        ticker = self.my_string

        puts = options.get_puts(ticker)
        calls = options.get_calls(ticker)

        self.Calls = calls.shape[0]
        self.Puts = puts.shape[0]

        puts['sma50'] = ema_indicator(puts['Last Trade'], window=50)
        puts['ema100'] = ema_indicator(puts['Last Trade'], window=100)


    def complete(self, instance):
        self.df_act: DataFrame = None

        comp_info = self.get_info()
        candles = self.get_candle(comp_info['figi'].iloc[0])
        df: DataFrame = self.create_dataframe(candles)

        self.get_max_activity(df)
        self.create_options()

        # print(self.df_act)
        # print('Наибольшая активность в ' + str(self.df_act.idxmax()[0]) + ' часов')
        if self.spinnerObject2.text == 'hour':
            self.textInfoLabel.text = f'Час наибольшей активности: {str(self.df_act.idxmax()[0])}  \n  Кол-во Calls: {str(self.Calls)}  \n  Кол-во Puts: {str(self.Puts)} \n MA50: {str(self.MA_50)} \n MA100: {str(self.MA_100)}'
        elif self.spinnerObject2.text == 'month':
            self.textInfoLabel.text = f'Месяц наибольшей активности: {str(self.df_act.idxmax()[0])}  \n  Кол-во Calls: {str(self.Calls)}  \n  Кол-во Puts: {str(self.Puts)} \n MA50: {str(self.MA_50)} \n MA100: {str(self.MA_100)}'
        elif self.spinnerObject2.text == 'day':
            self.textInfoLabel.text = f'День недели с наибольшей активностью: {str(self.df_act.idxmax()[0])}  \n  Кол-во Calls: {str(self.Calls)}  \n  Кол-во Puts: {str(self.Puts)} \n MA50: {str(self.MA_50)} \n MA100: {str(self.MA_100)}'
        df_ema = self.ema(df)
        self.graph(df_ema, comp_info['name'].iloc[0])


if __name__ == "__main__":
    TestApp().run()