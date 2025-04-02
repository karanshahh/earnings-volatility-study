import pandas as pd
import numpy as np
import os
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Create directory for analysis results
os.makedirs('analysis_results', exist_ok=True)

# Load options data
print("Loading options data...")
combined_iv_df = pd.read_csv('options_data/combined_iv_data.csv')

# Load earnings data
print("Loading earnings data...")
earnings_data = {}
target_companies = ['AAPL', 'AMZN', 'META', 'MSFT', 'GOOGL']
for symbol in target_companies:
    try:
        df = pd.read_csv(f'earnings_data/{symbol}_earnings_dates.csv')
        earnings_data[symbol] = df
    except Exception as e:
        print(f"Error loading earnings data for {symbol}: {str(e)}")

# Calculate volatility metrics
print("Calculating volatility metrics...")

# Create a DataFrame to store metrics for each earnings event
metrics_data = []

for symbol in target_companies:
    # Get IV data for this symbol
    symbol_iv = combined_iv_df[combined_iv_df['Symbol'] == symbol]
    
    # Group by earnings date
    for earnings_date in symbol_iv['Earnings_Date'].unique():
        event_data = symbol_iv[symbol_iv['Earnings_Date'] == earnings_date]
        
        # Calculate metrics for this earnings event
        before_iv = event_data[event_data['Period'] == 'Before']['IV'].mean()
        during_iv = event_data[event_data['Period'] == 'During']['IV'].mean()
        after_iv = event_data[event_data['Period'] == 'After']['IV'].mean()
        
        # Calculate volatility changes
        abnormal_change = during_iv - before_iv
        post_earnings_change = after_iv - during_iv
        volatility_impact = (during_iv / before_iv - 1) * 100  # Percentage increase
        volatility_crush = (after_iv / during_iv - 1) * 100    # Percentage decrease
        
        # Get earnings surprise if available
        surprise_percent = None
        if symbol in earnings_data:
            earnings_df = earnings_data[symbol]
            surprise_row = earnings_df[earnings_df['Date'] == earnings_date]
            if not surprise_row.empty and 'Surprise_Percent' in surprise_row.columns:
                surprise_percent = surprise_row['Surprise_Percent'].values[0]
        
        # Store metrics
        metrics_data.append({
            'Symbol': symbol,
            'Earnings_Date': earnings_date,
            'IV_Before': before_iv,
            'IV_During': during_iv,
            'IV_After': after_iv,
            'Abnormal_Change': abnormal_change,
            'Post_Earnings_Change': post_earnings_change,
            'Volatility_Impact_Percent': volatility_impact,
            'Volatility_Crush_Percent': volatility_crush,
            'Earnings_Surprise_Percent': surprise_percent
        })

# Create DataFrame with metrics
metrics_df = pd.DataFrame(metrics_data)

# Save metrics to CSV
metrics_df.to_csv('analysis_results/volatility_metrics.csv', index=False)

# Calculate summary statistics by company
summary_stats = []

for symbol in target_companies:
    symbol_metrics = metrics_df[metrics_df['Symbol'] == symbol]
    
    # Calculate averages
    avg_before = symbol_metrics['IV_Before'].mean()
    avg_during = symbol_metrics['IV_During'].mean()
    avg_after = symbol_metrics['IV_After'].mean()
    avg_abnormal = symbol_metrics['Abnormal_Change'].mean()
    avg_post = symbol_metrics['Post_Earnings_Change'].mean()
    avg_impact = symbol_metrics['Volatility_Impact_Percent'].mean()
    avg_crush = symbol_metrics['Volatility_Crush_Percent'].mean()
    
    # Calculate standard deviations
    std_abnormal = symbol_metrics['Abnormal_Change'].std()
    std_post = symbol_metrics['Post_Earnings_Change'].std()
    
    # Perform t-test to check if abnormal change is statistically significant
    t_stat, p_value = stats.ttest_1samp(symbol_metrics['Abnormal_Change'], 0)
    
    # Store summary statistics
    summary_stats.append({
        'Symbol': symbol,
        'Avg_IV_Before': avg_before,
        'Avg_IV_During': avg_during,
        'Avg_IV_After': avg_after,
        'Avg_Abnormal_Change': avg_abnormal,
        'Avg_Post_Earnings_Change': avg_post,
        'Avg_Volatility_Impact_Percent': avg_impact,
        'Avg_Volatility_Crush_Percent': avg_crush,
        'Std_Abnormal_Change': std_abnormal,
        'Std_Post_Earnings_Change': std_post,
        'T_Statistic': t_stat,
        'P_Value': p_value,
        'Is_Significant': p_value < 0.05
    })

# Create summary DataFrame
summary_df = pd.DataFrame(summary_stats)

# Save summary to CSV
summary_df.to_csv('analysis_results/volatility_summary_by_company.csv', index=False)

# Create a text summary
with open('analysis_results/volatility_metrics_summary.txt', 'w') as f:
    f.write("Earnings Volatility Metrics Summary\n")
    f.write("=================================\n\n")
    
    # Overall statistics
    f.write("Overall Statistics:\n")
    f.write(f"Average IV Before Earnings: {metrics_df['IV_Before'].mean():.2f}%\n")
    f.write(f"Average IV During Earnings: {metrics_df['IV_During'].mean():.2f}%\n")
    f.write(f"Average IV After Earnings: {metrics_df['IV_After'].mean():.2f}%\n")
    f.write(f"Average Abnormal Volatility Change: {metrics_df['Abnormal_Change'].mean():.2f}%\n")
    f.write(f"Average Post-Earnings Volatility Change: {metrics_df['Post_Earnings_Change'].mean():.2f}%\n")
    f.write(f"Average Volatility Impact: {metrics_df['Volatility_Impact_Percent'].mean():.2f}%\n")
    f.write(f"Average Volatility Crush: {metrics_df['Volatility_Crush_Percent'].mean():.2f}%\n\n")
    
    # Company-specific statistics
    for symbol in target_companies:
        symbol_summary = summary_df[summary_df['Symbol'] == symbol].iloc[0]
        
        f.write(f"{symbol} Statistics:\n")
        f.write(f"  Average IV Before Earnings: {symbol_summary['Avg_IV_Before']:.2f}%\n")
        f.write(f"  Average IV During Earnings: {symbol_summary['Avg_IV_During']:.2f}%\n")
        f.write(f"  Average IV After Earnings: {symbol_summary['Avg_IV_After']:.2f}%\n")
        f.write(f"  Average Abnormal Volatility Change: {symbol_summary['Avg_Abnormal_Change']:.2f}%\n")
        f.write(f"  Average Post-Earnings Volatility Change: {symbol_summary['Avg_Post_Earnings_Change']:.2f}%\n")
        f.write(f"  Volatility Impact: {symbol_summary['Avg_Volatility_Impact_Percent']:.2f}%\n")
        f.write(f"  Volatility Crush: {symbol_summary['Avg_Volatility_Crush_Percent']:.2f}%\n")
        
        # Statistical significance
        f.write(f"  Statistical Significance of Abnormal Change: ")
        if symbol_summary['Is_Significant']:
            f.write(f"Significant (p-value: {symbol_summary['P_Value']:.4f})\n\n")
        else:
            f.write(f"Not Significant (p-value: {symbol_summary['P_Value']:.4f})\n\n")

# Calculate event window averages (day-by-day)
print("Calculating event window averages...")

# Create a DataFrame to store day-by-day averages
event_window_data = []

# Days range from -10 to +10 (21 days total)
for days_to_earnings in range(-10, 11):
    # Filter data for this day relative to earnings
    day_data = combined_iv_df[combined_iv_df['Days_To_Earnings'] == days_to_earnings]
    
    # Calculate average IV for each company on this day
    for symbol in target_companies:
        symbol_day_data = day_data[day_data['Symbol'] == symbol]
        if not symbol_day_data.empty:
            avg_iv = symbol_day_data['IV'].mean()
            
            event_window_data.append({
                'Symbol': symbol,
                'Days_To_Earnings': days_to_earnings,
                'Avg_IV': avg_iv
            })

# Create event window DataFrame
event_window_df = pd.DataFrame(event_window_data)

# Save event window data to CSV
event_window_df.to_csv('analysis_results/event_window_averages.csv', index=False)

print("Volatility metrics calculation complete!")
