import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil

def scrape_csv():
    # URL to scrape
    url = "http://openinsider.com/latest-cluster-buys"

    # Fetch the web page
    response = requests.get(url)
    html = response.content

    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Find the table by its class
    table = soup.find('table', {'class': 'tinytable'})

    if table:
        rows = table.findAll('tr')

        data = []  # Create a list to store the table data
        for row in rows:
            csv_row = []
            for cell in row.findAll(['td', 'th']):
                # Get the text content and strip any leading/trailing whitespace
                csv_row.append(cell.get_text(strip=True))
            data.append(csv_row)

        # Create a DataFrame from the table data
        columns = data[0]  # Assuming the first row contains column headers
        insider_trades_df = pd.DataFrame(data[1:], columns=columns)

        # Cleaning and converting price column
        insider_trades_df['Price'] = insider_trades_df['Price'].str.replace('$', '').str.replace(',', '').astype(float)

        # Rename 'Trade\xa0Date' to 'Trade Date' and do the same for other cols
        insider_trades_df.rename(columns={'Trade\xa0Date': 'Trade Date'}, inplace=True)
        insider_trades_df.rename(columns={'Filing\xa0Date': 'Filing Date'}, inplace=True)
        insider_trades_df.rename(columns={'Company\xa0Name': 'Company Name'}, inplace=True)
        insider_trades_df.rename(columns={'Trade\xa0Type': 'Trade Type'}, inplace=True)

        # Convert 'Trade Date' to datetime
        insider_trades_df['Trade Date'] = pd.to_datetime(insider_trades_df['Trade Date'])

        # Sort the DataFrame by 'Trade Date'
        insider_trades_df.sort_values(by='Trade Date', inplace=True)

        # Set the display option to show all rows
        pd.set_option('display.max_rows', None)

        # Output the results to a new CSV file
        output_file_path = 'cluster_buys.csv'  # Replace with your desired output file path
        insider_trades_df.to_csv(output_file_path, index=False)

        # Return the DataFrame for further processing
        return insider_trades_df
    else:
        print("Table not found on the page")
        return None

def compare_csvs(new_csv='cluster_buys.csv', old_csv='old_cluster_buys.csv'):
    if not os.path.exists(old_csv):
        print("No previous CSV to compare with.")
        return
    
    new_df = pd.read_csv(new_csv)
    old_df = pd.read_csv(old_csv)
    
    # Finding new entries
    new_entries = pd.concat([new_df, old_df]).drop_duplicates(keep=False)
    
    if not new_entries.empty:
        print("New entries found.")
        tickers = new_entries['Ticker'].tolist()
        return tickers
    else:
        print("No new entries found.")
        return []

# Run the scraping function
scrape_csv()

# Compare the new CSV with the previous one
tickers = compare_csvs()

if tickers is not None:
    for ticker in tickers:
        print(ticker)

# Backup the new CSV for the next comparison
if os.path.exists('cluster_buys.csv'):
    shutil.copy('cluster_buys.csv', 'old_cluster_buys.csv')
