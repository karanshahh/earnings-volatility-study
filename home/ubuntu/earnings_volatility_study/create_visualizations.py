import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create directory for visualizations
os.makedirs('visualizations', exist_ok=True)

# Set style for plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

# Load data
print("Loading data for visualization...")
metrics_df = pd.read_csv('analysis_results/volatility_metrics.csv')
event_window_df = pd.read_csv('analysis_results/event_window_averages.csv')
combined_iv_df = pd.read_csv('options_data/combined_iv_data.csv')

# Define target companies
target_companies = ['AAPL', 'AMZN', 'META', 'MSFT', 'GOOGL']

# 1. Volatility Event Window Plot (IV around earnings)
print("Creating volatility event window plot...")
plt.figure(figsize=(12, 8))

for symbol in target_companies:
    symbol_data = event_window_df[event_window_df['Symbol'] == symbol]
    plt.plot(symbol_data['Days_To_Earnings'], symbol_data['Avg_IV'], marker='o', label=symbol)

plt.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Earnings Day')
plt.grid(True, alpha=0.3)
plt.xlabel('Days Relative to Earnings Announcement', fontsize=12)
plt.ylabel('Average Implied Volatility (%)', fontsize=12)
plt.title('Implied Volatility Around Earnings Announcements', fontsize=16)
plt.legend(title='Company', fontsize=10)
plt.tight_layout()
plt.savefig('visualizations/iv_event_window.png', dpi=300)
plt.close()

# 2. Volatility Changes by Company (Bar Chart)
print("Creating volatility changes bar chart...")
plt.figure(figsize=(12, 8))

# Calculate average metrics by company
company_avg = metrics_df.groupby('Symbol').agg({
    'Abnormal_Change': 'mean',
    'Post_Earnings_Change': 'mean',
    'Volatility_Impact_Percent': 'mean',
    'Volatility_Crush_Percent': 'mean'
}).reset_index()

# Plot abnormal change
plt.subplot(2, 2, 1)
sns.barplot(x='Symbol', y='Abnormal_Change', data=company_avg)
plt.title('Average Abnormal Volatility Change', fontsize=12)
plt.ylabel('Change in IV (%)', fontsize=10)
plt.grid(axis='y', alpha=0.3)

# Plot post-earnings change
plt.subplot(2, 2, 2)
sns.barplot(x='Symbol', y='Post_Earnings_Change', data=company_avg)
plt.title('Average Post-Earnings Volatility Change', fontsize=12)
plt.ylabel('Change in IV (%)', fontsize=10)
plt.grid(axis='y', alpha=0.3)

# Plot volatility impact
plt.subplot(2, 2, 3)
sns.barplot(x='Symbol', y='Volatility_Impact_Percent', data=company_avg)
plt.title('Average Volatility Impact (%)', fontsize=12)
plt.ylabel('Percent Change (%)', fontsize=10)
plt.grid(axis='y', alpha=0.3)

# Plot volatility crush
plt.subplot(2, 2, 4)
sns.barplot(x='Symbol', y='Volatility_Crush_Percent', data=company_avg)
plt.title('Average Volatility Crush (%)', fontsize=12)
plt.ylabel('Percent Change (%)', fontsize=10)
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('visualizations/volatility_changes_by_company.png', dpi=300)
plt.close()

# 3. Correlation Heatmap
print("Creating correlation heatmap...")
plt.figure(figsize=(10, 8))

# Select numeric columns for correlation
numeric_cols = ['IV_Before', 'IV_During', 'IV_After', 
               'Abnormal_Change', 'Post_Earnings_Change', 
               'Volatility_Impact_Percent', 'Volatility_Crush_Percent']

# Calculate correlation matrix
corr_matrix = metrics_df[numeric_cols].corr()

# Create heatmap
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt='.2f')
plt.title('Correlation Matrix of Volatility Metrics', fontsize=16)
plt.tight_layout()
plt.savefig('visualizations/correlation_heatmap.png', dpi=300)
plt.close()

# 4. Earnings Surprise vs. Volatility Change Scatter Plot
print("Creating earnings surprise scatter plot...")
plt.figure(figsize=(12, 6))

# Drop rows with missing earnings surprise data
scatter_df = metrics_df.dropna(subset=['Earnings_Surprise_Percent'])

# Plot for Abnormal Change
plt.subplot(1, 2, 1)
sns.scatterplot(x='Earnings_Surprise_Percent', y='Abnormal_Change', 
                hue='Symbol', data=scatter_df, s=100, alpha=0.7)
plt.grid(True, alpha=0.3)
plt.xlabel('Earnings Surprise (%)', fontsize=12)
plt.ylabel('Abnormal Volatility Change (%)', fontsize=12)
plt.title('Earnings Surprise vs. Abnormal Volatility Change', fontsize=14)

# Add regression line
sns.regplot(x='Earnings_Surprise_Percent', y='Abnormal_Change', 
            data=scatter_df, scatter=False, ci=None, color='red')

# Plot for Post-Earnings Change
plt.subplot(1, 2, 2)
sns.scatterplot(x='Earnings_Surprise_Percent', y='Post_Earnings_Change', 
                hue='Symbol', data=scatter_df, s=100, alpha=0.7)
plt.grid(True, alpha=0.3)
plt.xlabel('Earnings Surprise (%)', fontsize=12)
plt.ylabel('Post-Earnings Volatility Change (%)', fontsize=12)
plt.title('Earnings Surprise vs. Post-Earnings Volatility Change', fontsize=14)

# Add regression line
sns.regplot(x='Earnings_Surprise_Percent', y='Post_Earnings_Change', 
            data=scatter_df, scatter=False, ci=None, color='red')

plt.tight_layout()
plt.savefig('visualizations/earnings_surprise_scatter.png', dpi=300)
plt.close()

# 5. Volatility Dynamics Heatmap
print("Creating volatility dynamics heatmap...")
plt.figure(figsize=(14, 8))

# Pivot the data to create a matrix of Days_To_Earnings vs Symbol
pivot_data = event_window_df.pivot(index='Days_To_Earnings', columns='Symbol', values='Avg_IV')

# Create heatmap
sns.heatmap(pivot_data, cmap='viridis', annot=False, fmt='.1f')
plt.title('Implied Volatility Dynamics Around Earnings', fontsize=16)
plt.xlabel('Company', fontsize=12)
plt.ylabel('Days Relative to Earnings (0 = Earnings Day)', fontsize=12)
plt.tight_layout()
plt.savefig('visualizations/volatility_dynamics_heatmap.png', dpi=300)
plt.close()

# 6. Before-During-After Volatility Comparison
print("Creating before-during-after comparison plot...")
plt.figure(figsize=(14, 8))

# Prepare data for grouped bar chart
periods = ['IV_Before', 'IV_During', 'IV_After']
period_labels = ['Before Earnings', 'During Earnings', 'After Earnings']

# Calculate average IV for each period and company
period_data = []
for symbol in target_companies:
    symbol_metrics = metrics_df[metrics_df['Symbol'] == symbol]
    for period in periods:
        period_data.append({
            'Symbol': symbol,
            'Period': period.replace('IV_', ''),
            'Average_IV': symbol_metrics[period].mean()
        })

period_df = pd.DataFrame(period_data)

# Create grouped bar chart
sns.barplot(x='Symbol', y='Average_IV', hue='Period', data=period_df)
plt.title('Comparison of Implied Volatility Before, During, and After Earnings', fontsize=16)
plt.xlabel('Company', fontsize=12)
plt.ylabel('Average Implied Volatility (%)', fontsize=12)
plt.legend(title='Period', fontsize=10)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('visualizations/before_during_after_comparison.png', dpi=300)
plt.close()

# 7. Volatility Term Structure
print("Creating volatility term structure plot...")
plt.figure(figsize=(12, 8))

# For each company, plot the average IV for each day in the event window
for symbol in target_companies:
    symbol_data = combined_iv_df[combined_iv_df['Symbol'] == symbol]
    
    # Group by days to earnings and calculate average IV
    avg_iv = symbol_data.groupby('Days_To_Earnings')['IV'].mean()
    
    # Plot the term structure
    plt.plot(avg_iv.index, avg_iv.values, marker='o', label=symbol)

plt.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Earnings Day')
plt.grid(True, alpha=0.3)
plt.xlabel('Days Relative to Earnings', fontsize=12)
plt.ylabel('Implied Volatility (%)', fontsize=12)
plt.title('Volatility Term Structure Around Earnings', fontsize=16)
plt.legend(title='Company', fontsize=10)
plt.tight_layout()
plt.savefig('visualizations/volatility_term_structure.png', dpi=300)
plt.close()

# 8. Volatility Crush Visualization
print("Creating volatility crush visualization...")
plt.figure(figsize=(12, 8))

# Calculate average volatility crush for each company
crush_data = []
for symbol in target_companies:
    symbol_metrics = metrics_df[metrics_df['Symbol'] == symbol]
    
    # Get average values
    avg_before = symbol_metrics['IV_Before'].mean()
    avg_during = symbol_metrics['IV_During'].mean()
    avg_after = symbol_metrics['IV_After'].mean()
    
    # Store data for plotting
    crush_data.append({
        'Symbol': symbol,
        'Before': avg_before,
        'During': avg_during,
        'After': avg_after
    })

crush_df = pd.DataFrame(crush_data)

# Create a line plot showing the volatility crush
for i, row in crush_df.iterrows():
    plt.plot(['Before', 'During', 'After'], 
             [row['Before'], row['During'], row['After']], 
             marker='o', markersize=10, linewidth=2, label=row['Symbol'])

plt.grid(True, alpha=0.3)
plt.xlabel('Earnings Period', fontsize=12)
plt.ylabel('Average Implied Volatility (%)', fontsize=12)
plt.title('Volatility Crush Around Earnings Announcements', fontsize=16)
plt.legend(title='Company', fontsize=10)
plt.tight_layout()
plt.savefig('visualizations/volatility_crush_visualization.png', dpi=300)
plt.close()

print("Visualization creation complete!")
