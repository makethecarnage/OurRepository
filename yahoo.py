import yfinance as yf

ticker = input()
ticker= yf.Ticker(ticker)

print(ticker.news)
print(ticker.recommendations['To Grade'].value_counts())
#print(ticker.earnings)
print(ticker.quarterly_earnings)