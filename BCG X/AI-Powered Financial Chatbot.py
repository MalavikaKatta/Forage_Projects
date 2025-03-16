#!/usr/bin/env python
# coding: utf-8

# In[28]:


import pandas as pd


# In[29]:


df = pd.read_csv(r'C:\Users\malav\OneDrive\Desktop\10K_Filings.csv')


# In[30]:


cols_to_convert = ['Total Revenue', 'Net Income', 'Total Assets', 'Total Liabilities', 'Cash Flow']
for col in cols_to_convert:
    df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)


# In[31]:


df['Revenue Growth (%)'] = df.groupby('Company')['Total Revenue'].pct_change() * 100
df['Income Growth (%)'] = df.groupby('Company')['Net Income'].pct_change() * 100
df.fillna(0, inplace=True)
print(df)


# In[32]:


summary = df.groupby('Company').agg({
    'Revenue Growth (%)': 'mean',
    'Income Growth (%)': 'mean',
}).reset_index()
print(summary)


# In[22]:


get_ipython().system('pip install pandas flask')


# In[52]:


import re

def simple_chatbot(user_query, df, summary):
    user_query = user_query.lower()

    # Define financial metrics and their corresponding column names
    financial_metrics = {
        "total revenue": "Total Revenue",
        "net income": "Net Income",
        "total assets": "Total Assets",
        "total liabilities": "Total Liabilities",
        "cash flow": "Cash Flow",
        "revenue growth": "Revenue Growth (%)",
        "income growth": "Income Growth (%)",
    }

    # Extract the year if mentioned in the query
    year_match = re.search(r'\b(20\d{2})\b', user_query)
    year = int(year_match.group(0)) if year_match else None

    # Check if the query is asking about a change in financial metrics
    if "changed over the last year" in user_query or "compare" in user_query:
        # Identify if a company is mentioned in the query
        matched_company = None
        for company in summary['Company'].values:
            if company.lower() in user_query:
                matched_company = company
                break

        # Process the query for the change in financial metrics
        for metric_key, column_name in financial_metrics.items():
            if metric_key in user_query:
                if matched_company:
                    # Get data for the company
                    company_data = df[df['Company'] == matched_company]
                    last_year_data = company_data[company_data['Year'] == company_data['Year'].max() - 1]
                    current_year_data = company_data[company_data['Year'] == company_data['Year'].max()]
                    if last_year_data.empty or current_year_data.empty:
                        return f"No data found for {metric_key} of {matched_company} for the last two years."

                    last_year_value = last_year_data[column_name].sum()
                    current_year_value = current_year_data[column_name].sum()
                    change = current_year_value - last_year_value
                    change_message = "increased" if change > 0 else "decreased"
                    return f"The {metric_key} for {matched_company} has {change_message} by {abs(change):,.2f} million over the last year."

                else:
                    # Sum for all companies
                    total_last_year = df[df['Year'] == df['Year'].max() - 1][column_name].sum()
                    total_current_year = df[df['Year'] == df['Year'].max()][column_name].sum()
                    change = total_current_year - total_last_year
                    change_message = "increased" if change > 0 else "decreased"
                    return f"The {metric_key} has {change_message} by {abs(change):,.2f} million over the last year."

    # Rest of your code for other queries like highest/lowest, total revenue, etc.
    for metric_key, column_name in financial_metrics.items():
        if any(keyword in user_query for keyword in [f"highest {metric_key}", f"largest {metric_key}", f"most {metric_key}"]):
            find_max = True
        elif any(keyword in user_query for keyword in [f"lowest {metric_key}", f"smallest {metric_key}", f"least {metric_key}"]):
            find_max = False
        else:
            continue  # If neither, move to the next metric

        # Filter data for the requested year or use the latest available
        if year:
            year_data = df[df["Year"] == year]
            if year_data.empty:
                return f"No data found for {metric_key} in {year}."
        else:
            year_data = df[df["Year"] == df["Year"].max()]  # Latest available year

        # Find the company with the highest or lowest value for the metric
        top_company = year_data.loc[year_data[column_name].idxmax()] if find_max else year_data.loc[year_data[column_name].idxmin()]
        comparison_word = "highest" if find_max else "lowest"

        return f"The company with the {comparison_word} {metric_key} in {year if year else top_company['Year']} is {top_company['Company']} with {top_company[column_name]:,.2f} million."

    # Identify the company in the query
    matched_company = None
    for company in summary['Company'].values:
        if company.lower() in user_query:
            matched_company = company
            break

    if matched_company:
        # Get the most recent data for the matched company
        latest_data = df[df['Company'] == matched_company].sort_values('Year', ascending=False).iloc[0]

        # Check if the user is asking for a specific metric for a company
        for metric_key, column_name in financial_metrics.items():
            if metric_key in user_query:
                # Fetch data for the requested year or the latest available
                if year:
                    year_data = df[(df['Company'] == matched_company) & (df['Year'] == year)]
                    if year_data.empty:
                        return f"No data found for {metric_key} of {matched_company} in {year}."
                    value = year_data.iloc[0][column_name]
                else:
                    value = latest_data[column_name]

                return f"The {metric_key} for {matched_company} in {year} is {value:,.2f} million." if year else f"The {metric_key} for {matched_company} in 2024 is {value:,.2f} million."
    else:
        # If no company is mentioned, calculate the sum of all companies for the requested metric
        for metric_key, column_name in financial_metrics.items():
            if metric_key in user_query:
                # Sum for all companies, optionally filtered by year
                if year:
                    year_data = df[df["Year"] == year]
                    total_value = year_data[column_name].sum()
                    return f"The total {metric_key} for all companies in {year} is {total_value:,.2f} million."
                else:
                    total_value = df[column_name].sum()
                    return f"The total {metric_key} for all companies is {total_value:,.2f} million."


# Get user input for the number of questions
n = int(input('Enter how many questions you want to ask: '))

for i in range(n):
    user_query = input(f"Ask financial question {i+1}: ")
    response = simple_chatbot(user_query, df, summary)
    print(response)

