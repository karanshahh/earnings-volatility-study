import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Create directory for statistical analysis
os.makedirs('statistical_analysis', exist_ok=True)

# Load volatility metrics data
print("Loading volatility metrics data...")
metrics_df = pd.read_csv('analysis_results/volatility_metrics.csv')

# Load event window data
print("Loading event window data...")
event_window_df = pd.read_csv('analysis_results/event_window_averages.csv')

# 1. Regression Analysis: Earnings Surprise vs. Volatility Changes
print("Performing regression analysis...")

# Drop rows with missing earnings surprise data
regression_df = metrics_df.dropna(subset=['Earnings_Surprise_Percent'])

# Create a text file to store regression results
with open('statistical_analysis/regression_results.txt', 'w') as f:
    f.write("Regression Analysis Results\n")
    f.write("==========================\n\n")
    
    # Overall regression: Earnings Surprise vs. Abnormal Volatility Change
    f.write("1. Earnings Surprise vs. Abnormal Volatility Change\n")
    f.write("--------------------------------------------------\n")
    
    X = sm.add_constant(regression_df['Earnings_Surprise_Percent'])
    y = regression_df['Abnormal_Change']
    model = sm.OLS(y, X).fit()
    
    f.write(model.summary().as_text())
    f.write("\n\n")
    
    # Overall regression: Earnings Surprise vs. Post-Earnings Volatility Change
    f.write("2. Earnings Surprise vs. Post-Earnings Volatility Change\n")
    f.write("-----------------------------------------------------\n")
    
    X = sm.add_constant(regression_df['Earnings_Surprise_Percent'])
    y = regression_df['Post_Earnings_Change']
    model = sm.OLS(y, X).fit()
    
    f.write(model.summary().as_text())
    f.write("\n\n")
    
    # Company-specific regressions
    f.write("3. Company-Specific Regression Analysis\n")
    f.write("------------------------------------\n\n")
    
    for symbol in regression_df['Symbol'].unique():
        symbol_df = regression_df[regression_df['Symbol'] == symbol]
        
        if len(symbol_df) >= 5:  # Only perform regression if we have enough data points
            f.write(f"{symbol}: Earnings Surprise vs. Abnormal Volatility Change\n")
            
            X = sm.add_constant(symbol_df['Earnings_Surprise_Percent'])
            y = symbol_df['Abnormal_Change']
            model = sm.OLS(y, X).fit()
            
            f.write(model.summary().as_text())
            f.write("\n\n")
        else:
            f.write(f"{symbol}: Insufficient data for regression analysis\n\n")

# 2. ANOVA: Compare volatility changes across companies
print("Performing ANOVA analysis...")

# One-way ANOVA for Abnormal Volatility Change across companies
anova_result = stats.f_oneway(
    metrics_df[metrics_df['Symbol'] == 'AAPL']['Abnormal_Change'],
    metrics_df[metrics_df['Symbol'] == 'AMZN']['Abnormal_Change'],
    metrics_df[metrics_df['Symbol'] == 'META']['Abnormal_Change'],
    metrics_df[metrics_df['Symbol'] == 'MSFT']['Abnormal_Change'],
    metrics_df[metrics_df['Symbol'] == 'GOOGL']['Abnormal_Change']
)

# Save ANOVA results
with open('statistical_analysis/anova_results.txt', 'w') as f:
    f.write("ANOVA Analysis Results\n")
    f.write("=====================\n\n")
    
    f.write("1. One-way ANOVA: Abnormal Volatility Change across Companies\n")
    f.write("----------------------------------------------------------\n")
    f.write(f"F-statistic: {anova_result.statistic:.4f}\n")
    f.write(f"p-value: {anova_result.pvalue:.4f}\n")
    f.write(f"Significant difference: {anova_result.pvalue < 0.05}\n\n")
    
    # One-way ANOVA for Post-Earnings Volatility Change across companies
    anova_result = stats.f_oneway(
        metrics_df[metrics_df['Symbol'] == 'AAPL']['Post_Earnings_Change'],
        metrics_df[metrics_df['Symbol'] == 'AMZN']['Post_Earnings_Change'],
        metrics_df[metrics_df['Symbol'] == 'META']['Post_Earnings_Change'],
        metrics_df[metrics_df['Symbol'] == 'MSFT']['Post_Earnings_Change'],
        metrics_df[metrics_df['Symbol'] == 'GOOGL']['Post_Earnings_Change']
    )
    
    f.write("2. One-way ANOVA: Post-Earnings Volatility Change across Companies\n")
    f.write("--------------------------------------------------------------\n")
    f.write(f"F-statistic: {anova_result.statistic:.4f}\n")
    f.write(f"p-value: {anova_result.pvalue:.4f}\n")
    f.write(f"Significant difference: {anova_result.pvalue < 0.05}\n\n")

# 3. Correlation Analysis
print("Performing correlation analysis...")

# Select only numeric columns for correlation analysis
numeric_cols = ['IV_Before', 'IV_During', 'IV_After', 
               'Abnormal_Change', 'Post_Earnings_Change', 
               'Volatility_Impact_Percent', 'Volatility_Crush_Percent']

# Calculate correlation matrix
correlation_matrix = metrics_df[numeric_cols].corr()

# Save correlation matrix
correlation_matrix.to_csv('statistical_analysis/correlation_matrix.csv')

# Save correlation analysis results
with open('statistical_analysis/correlation_analysis.txt', 'w') as f:
    f.write("Correlation Analysis Results\n")
    f.write("===========================\n\n")
    
    f.write("Correlation Matrix:\n")
    f.write(correlation_matrix.to_string())
    f.write("\n\n")
    
    # Key correlations
    f.write("Key Correlations:\n")
    f.write(f"1. IV_Before vs. Abnormal_Change: {correlation_matrix.loc['IV_Before', 'Abnormal_Change']:.4f}\n")
    f.write(f"2. IV_During vs. Post_Earnings_Change: {correlation_matrix.loc['IV_During', 'Post_Earnings_Change']:.4f}\n")
    f.write(f"3. Abnormal_Change vs. Post_Earnings_Change: {correlation_matrix.loc['Abnormal_Change', 'Post_Earnings_Change']:.4f}\n")
    
    # Correlation with earnings surprise (if available)
    if 'Earnings_Surprise_Percent' in metrics_df.columns:
        # Create a separate dataframe for surprise correlation
        surprise_df = metrics_df.dropna(subset=['Earnings_Surprise_Percent'])
        # Only include numeric columns
        surprise_cols = numeric_cols + ['Earnings_Surprise_Percent']
        surprise_corr = surprise_df[surprise_cols].corr()
        
        f.write("\nCorrelations with Earnings Surprise:\n")
        f.write(f"1. Earnings_Surprise_Percent vs. Abnormal_Change: {surprise_corr.loc['Earnings_Surprise_Percent', 'Abnormal_Change']:.4f}\n")
        f.write(f"2. Earnings_Surprise_Percent vs. Post_Earnings_Change: {surprise_corr.loc['Earnings_Surprise_Percent', 'Post_Earnings_Change']:.4f}\n")
        f.write(f"3. Earnings_Surprise_Percent vs. Volatility_Impact_Percent: {surprise_corr.loc['Earnings_Surprise_Percent', 'Volatility_Impact_Percent']:.4f}\n")

# 4. Multiple Regression Analysis
print("Performing multiple regression analysis...")

# Create a formula for multiple regression
formula = 'Abnormal_Change ~ Earnings_Surprise_Percent + IV_Before'

# Fit the model
model = ols(formula, data=regression_df).fit()

# Save multiple regression results
with open('statistical_analysis/multiple_regression_results.txt', 'w') as f:
    f.write("Multiple Regression Analysis Results\n")
    f.write("==================================\n\n")
    
    f.write("Model: Abnormal_Change ~ Earnings_Surprise_Percent + IV_Before\n\n")
    f.write(model.summary().as_text())

# 5. Summary of Statistical Findings
print("Generating statistical findings summary...")

with open('statistical_analysis/statistical_findings_summary.txt', 'w') as f:
    f.write("Summary of Statistical Findings\n")
    f.write("=============================\n\n")
    
    # T-test results
    f.write("1. T-test Results for Abnormal Volatility Changes\n")
    f.write("----------------------------------------------\n")
    
    for symbol in metrics_df['Symbol'].unique():
        symbol_metrics = metrics_df[metrics_df['Symbol'] == symbol]
        t_stat, p_value = stats.ttest_1samp(symbol_metrics['Abnormal_Change'], 0)
        
        f.write(f"{symbol}:\n")
        f.write(f"  Average Abnormal Change: {symbol_metrics['Abnormal_Change'].mean():.2f}%\n")
        f.write(f"  T-statistic: {t_stat:.4f}\n")
        f.write(f"  P-value: {p_value:.4f}\n")
        f.write(f"  Statistically Significant: {p_value < 0.05}\n\n")
    
    # Regression findings
    f.write("2. Regression Analysis Findings\n")
    f.write("----------------------------\n")
    
    # Load regression results for summary
    X = sm.add_constant(regression_df['Earnings_Surprise_Percent'])
    y = regression_df['Abnormal_Change']
    model = sm.OLS(y, X).fit()
    
    f.write("Earnings Surprise vs. Abnormal Volatility Change:\n")
    f.write(f"  Coefficient: {model.params[1]:.4f}\n")
    f.write(f"  P-value: {model.pvalues[1]:.4f}\n")
    f.write(f"  R-squared: {model.rsquared:.4f}\n")
    f.write(f"  Significant Relationship: {model.pvalues[1] < 0.05}\n\n")
    
    # ANOVA findings
    f.write("3. ANOVA Findings\n")
    f.write("---------------\n")
    
    anova_result = stats.f_oneway(
        metrics_df[metrics_df['Symbol'] == 'AAPL']['Abnormal_Change'],
        metrics_df[metrics_df['Symbol'] == 'AMZN']['Abnormal_Change'],
        metrics_df[metrics_df['Symbol'] == 'META']['Abnormal_Change'],
        metrics_df[metrics_df['Symbol'] == 'MSFT']['Abnormal_Change'],
        metrics_df[metrics_df['Symbol'] == 'GOOGL']['Abnormal_Change']
    )
    
    f.write("Differences in Abnormal Volatility Change across Companies:\n")
    f.write(f"  F-statistic: {anova_result.statistic:.4f}\n")
    f.write(f"  P-value: {anova_result.pvalue:.4f}\n")
    f.write(f"  Significant Difference: {anova_result.pvalue < 0.05}\n\n")
    
    # Correlation findings
    f.write("4. Correlation Analysis Findings\n")
    f.write("-----------------------------\n")
    
    f.write("Key Correlations:\n")
    f.write(f"  IV_Before vs. Abnormal_Change: {correlation_matrix.loc['IV_Before', 'Abnormal_Change']:.4f}\n")
    f.write(f"  IV_During vs. Post_Earnings_Change: {correlation_matrix.loc['IV_During', 'Post_Earnings_Change']:.4f}\n")
    f.write(f"  Abnormal_Change vs. Post_Earnings_Change: {correlation_matrix.loc['Abnormal_Change', 'Post_Earnings_Change']:.4f}\n\n")
    
    # Overall conclusions
    f.write("5. Overall Statistical Conclusions\n")
    f.write("-------------------------------\n")
    
    # Calculate overall significance
    overall_t_stat, overall_p_value = stats.ttest_1samp(metrics_df['Abnormal_Change'], 0)
    
    f.write(f"1. Earnings announcements have a {overall_p_value < 0.05 and 'statistically significant' or 'non-significant'} impact on options implied volatility.\n")
    f.write(f"2. The average abnormal volatility change around earnings is {metrics_df['Abnormal_Change'].mean():.2f}%.\n")
    f.write(f"3. The average post-earnings volatility change is {metrics_df['Post_Earnings_Change'].mean():.2f}%.\n")
    
    # Relationship with earnings surprises
    if 'Earnings_Surprise_Percent' in metrics_df.columns:
        # Create a separate dataframe for surprise correlation
        surprise_df = metrics_df.dropna(subset=['Earnings_Surprise_Percent'])
        # Only include numeric columns
        surprise_cols = numeric_cols + ['Earnings_Surprise_Percent']
        surprise_corr = surprise_df[surprise_cols].corr()
        
        surprise_correlation = surprise_corr.loc['Earnings_Surprise_Percent', 'Abnormal_Change']
        f.write(f"4. The correlation between earnings surprises and abnormal volatility changes is {surprise_correlation:.4f}, indicating a {abs(surprise_correlation) > 0.3 and 'moderate' or 'weak'} relationship.\n")

print("Statistical analysis complete!")
