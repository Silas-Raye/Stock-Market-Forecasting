from pyfinviz.quote import Quote
import pandas as pd

quote = Quote(ticker="MSFT")
news_df = quote.outer_news_df
df = pd.DataFrame(news_df)

# Set display options to show all columns without truncation
pd.set_option('display.max_columns', None)  # None means no limit to the number of columns
pd.set_option('display.width', None)  # None means no limit to the display width

print(df)
