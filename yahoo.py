from yahoo_fin import news


ticker = input()
news = news.get_yf_rss(ticker)
print(news[0]['published'])
print(news[19]['published'])