import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import pandas as pd
import os
from datetime import datetime, timedelta
import json

# Initialize API client
client = ApiClient()

# Define target companies
target_companies = ['AAPL', 'AMZN', 'META', 'MSFT', 'GOOGL']

# Calculate date ranges (2 years of data)
end_date = datetime.now()
start_date = end_date - timedelta(days=730)  # Approximately 2 years

# Convert to epoch timestamps
period1 = int(start_date.timestamp())
period2 = int(end_date.timestamp())

# Create directory for stock data
os.makedirs('stock_data', exist_ok=True)

# Collect data for each company
all_stock_data = {}

for symbol in target_companies:
    print(f"Collecting data for {symbol}...")
    
    # Get stock chart data using YahooFinance API
    stock_data = client.call_api('YahooFinance/get_stock_chart', query={
        'symbol': symbol,
        'region': 'US',
        'interval': '1d',  # Daily data
        'period1': str(period1),
        'period2': str(period2),
        'includeAdjustedClose': True
    })
    
    # Save raw data
    with open(f'stock_data/{symbol}_raw_data.json', 'w') as f:
        json.dump(stock_data, f, indent=4)
    
    # Process and extract relevant data
    if 'chart' in stock_data and 'result' in stock_data['chart'] and len(stock_data['chart']['result']) > 0:
        result = stock_data['chart']['result'][0]
        
        # Extract timestamps and convert to dates
        timestamps = result.get('timestamp', [])
        dates = [datetime.fromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps]
        
        # Extract price data
        indicators = result.get('indicators', {})
        quote_data = indicators.get('quote', [{}])[0]
        
        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Open': quote_data.get('open', []),
            'High': quote_data.get('high', []),
            'Low': quote_data.get('low', []),
            'Close': quote_data.get('close', []),
            'Volume': quote_data.get('volume', [])
        })
        
        # Add adjusted close if available
        if 'adjclose' in indicators and len(indicators['adjclose']) > 0:
            df['Adj_Close'] = indicators['adjclose'][0].get('adjclose', [])
        
        # Clean data (remove rows with NaN values)
        df = df.dropna()
        
        # Save to CSV
        df.to_csv(f'stock_data/{symbol}_daily_prices.csv', index=False)
        
        # Store in dictionary
        all_stock_data[symbol] = df
        
        print(f"Successfully saved data for {symbol}")
    else:
        print(f"Failed to retrieve data for {symbol}")

# Create a summary file
with open('stock_data/collection_summary.txt', 'w') as f:
    f.write(f"Stock Data Collection Summary\n")
    f.write(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\n")
    
    for symbol in target_companies:
        if symbol in all_stock_data:
            df = all_stock_data[symbol]
            f.write(f"{symbol}: {len(df)} trading days collected\n")
            f.write(f"  First date: {df['Date'].iloc[0]}\n")
            f.write(f"  Last date: {df['Date'].iloc[-1]}\n")
            f.write(f"  Price range: ${min(df['Low']):.2f} - ${max(df['High']):.2f}\n\n")
        else:
            f.write(f"{symbol}: Data collection failed\n\n")

print("Stock data collection complete!")
