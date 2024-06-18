import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

data = yf.download('MSFT', start='2023-10-30', end='2023-11-03', interval='1m')

plt.figure(figsize=(14, 7))
plt.plot(data['Close'])
plt.title('MSFT Performance from 2023-10-30 to 2023-11-03')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.grid(True)

# I want to add to the plot above

df = pd.read_csv('my_data.csv')
df = df.drop(columns=['Unnamed: 0', 'Headline'])
df['Date'] = pd.to_datetime(df['Date'])
# remaining columns are named 'Date' and 'Close'

df_positive = df[df['Prediction'] == 1]
df_negative = df[df['Prediction'] == -1]

# Plot df_positive in green points
plt.scatter(df_positive['Date'], [315] * len(df_positive), color='green')

# Plot df_negative in red points
plt.scatter(df_negative['Date'], [315] * len(df_negative), color='red')


# Create custom legend entries
custom_legend = [
    Line2D([0], [0], color='green', marker='o', markersize=5, label='Good News'),
    Line2D([0], [0], color='red', marker='o', markersize=5, label='Bad News')
]

# Add a legend with custom entries
plt.legend(handles=custom_legend)

# Save the plot as an image (e.g., PNG format)
plt.savefig('stock_performance_plot.png')

plt.show()
