"""
Sales Data Analysis - Week 3 Project
------------------------------------
Loads sales_data.csv with pandas, explores and cleans it, calculates
sales metrics, prints a formatted report and saves it as analysis_report.md.

Run:  python sales_analysis.py
"""

import pandas as pd

# ---------------------------------------------------------------
# DAY 1: SETUP & LOAD DATA
# ---------------------------------------------------------------
# Read the CSV file into a DataFrame (like opening an Excel sheet)
df = pd.read_csv("sales_data.csv")

print("=" * 60)
print("STEP 1: FIRST 5 ROWS")
print("=" * 60)
print(df.head())

# ---------------------------------------------------------------
# DAY 2: EXPLORE DATA
# ---------------------------------------------------------------
rows, cols = df.shape  # shape returns (number of rows, number of columns)
print("\n" + "=" * 60)
print("STEP 2: DATASET INFORMATION")
print("=" * 60)
print(f"Rows: {rows} | Columns: {cols}")
print(f"Columns: {list(df.columns)}")
print("\nData types:")
print(df.dtypes)
print("\nBasic statistics of numeric columns:")
print(df.describe())

# ---------------------------------------------------------------
# DAY 3: CLEAN DATA
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 3: DATA CLEANING")
print("=" * 60)

# 3a. Check for missing values in every column
missing_before = df.isnull().sum()
print("Missing values per column (before cleaning):")
print(missing_before)

# 3b. Handle missing values appropriately
#     - Numeric columns  -> fill with the median (robust to outliers)
#     - Text columns     -> fill with the most common value (mode)
for col in df.columns:
    if df[col].isnull().any():
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode()[0])

# 3c. Remove duplicate rows
duplicates = int(df.duplicated().sum())
df = df.drop_duplicates()
print(f"Duplicate rows removed: {duplicates}")

# 3d. Convert the Date column from text to a real date type
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# 3e. Validate Total_Sales (should equal Quantity x Price).
#     Any mismatched row is recalculated so the revenue figures are reliable.
calculated = df["Quantity"] * df["Price"]
mismatches = int((calculated != df["Total_Sales"]).sum())
df["Total_Sales"] = calculated
print(f"Total_Sales mismatches fixed: {mismatches}")
print(f"Rows after cleaning: {len(df)}")

# ---------------------------------------------------------------
# DAY 4: ANALYZE SALES
# ---------------------------------------------------------------
# Metric 1: Total revenue
total_revenue = df["Total_Sales"].sum()

# Metric 2: Average, highest and lowest sale value
avg_sale = df["Total_Sales"].mean()
max_sale = df["Total_Sales"].max()
min_sale = df["Total_Sales"].min()
max_row = df.loc[df["Total_Sales"].idxmax()]
min_row = df.loc[df["Total_Sales"].idxmin()]

# Metric 3: Best-selling product (by revenue and by units sold)
product_summary = (
    df.groupby("Product")
    .agg(Units_Sold=("Quantity", "sum"),
         Revenue=("Total_Sales", "sum"),
         Orders=("Product", "count"))
    .sort_values("Revenue", ascending=False)
)
best_by_revenue = product_summary["Revenue"].idxmax()
best_by_units = product_summary["Units_Sold"].idxmax()

# Metric 4: Revenue by region
region_summary = (
    df.groupby("Region")["Total_Sales"].sum().sort_values(ascending=False)
)

# Metric 5: Monthly revenue trend
monthly = df.groupby(df["Date"].dt.to_period("M"))["Total_Sales"].sum()

# Metric 6: Total units sold
total_units = df["Quantity"].sum()

# ---------------------------------------------------------------
# DAY 5: CREATE REPORT
# ---------------------------------------------------------------
def inr(value):
    """Format a number as Indian Rupees with commas."""
    return f"₹{value:,.2f}"


lines = []
lines.append("# Sales Data Analysis Report\n")
lines.append(f"**Period covered:** {df['Date'].min():%d %b %Y} to "
             f"{df['Date'].max():%d %b %Y}  ")
lines.append(f"**Records analysed:** {len(df)}\n")

lines.append("## 1. Key Metrics\n")
lines.append("| Metric | Value |")
lines.append("|---|---|")
lines.append(f"| Total Revenue | {inr(total_revenue)} |")
lines.append(f"| Total Units Sold | {total_units:,} |")
lines.append(f"| Average Sale Value | {inr(avg_sale)} |")
lines.append(f"| Highest Sale | {inr(max_sale)} ({max_row['Product']}, "
             f"{max_row['Region']}, {max_row['Date']:%d %b %Y}) |")
lines.append(f"| Lowest Sale | {inr(min_sale)} ({min_row['Product']}, "
             f"{min_row['Region']}, {min_row['Date']:%d %b %Y}) |")
lines.append(f"| Best-Selling Product (Revenue) | {best_by_revenue} |")
lines.append(f"| Best-Selling Product (Units) | {best_by_units} |\n")

lines.append("## 2. Product Performance\n")
lines.append("| Product | Orders | Units Sold | Revenue | Share |")
lines.append("|---|---|---|---|---|")
for product, r in product_summary.iterrows():
    share = r["Revenue"] / total_revenue * 100
    lines.append(f"| {product} | {int(r['Orders'])} | {int(r['Units_Sold'])} | "
                 f"{inr(r['Revenue'])} | {share:.1f}% |")
lines.append("")

lines.append("## 3. Regional Performance\n")
lines.append("| Region | Revenue | Share |")
lines.append("|---|---|---|")
for region, rev in region_summary.items():
    lines.append(f"| {region} | {inr(rev)} | {rev / total_revenue * 100:.1f}% |")
lines.append("")

lines.append("## 4. Monthly Revenue\n")
lines.append("| Month | Revenue |")
lines.append("|---|---|")
for period, rev in monthly.items():
    lines.append(f"| {period} | {inr(rev)} |")
lines.append("")

lines.append("## 5. Data Cleaning Summary\n")
lines.append(f"- Missing values found: {int(missing_before.sum())}")
lines.append(f"- Duplicate rows removed: {duplicates}")
lines.append(f"- Total_Sales mismatches corrected: {mismatches}\n")

top_region = region_summary.idxmax()
low_product = product_summary["Revenue"].idxmin()
lines.append("## 6. Insights\n")
lines.append(f"- **{best_by_revenue}** generates the most revenue "
             f"({product_summary.loc[best_by_revenue, 'Revenue'] / total_revenue * 100:.1f}% of total).")
lines.append(f"- **{top_region}** is the strongest region "
             f"({region_summary.max() / total_revenue * 100:.1f}% of total revenue).")
lines.append(f"- **{low_product}** is the weakest product by revenue, so it is a "
             "candidate for promotions or review.")
lines.append(f"- The best month was **{monthly.idxmax()}** "
             f"({inr(monthly.max())}) and the weakest was **{monthly.idxmin()}** "
             f"({inr(monthly.min())}).")
# Warn if the last month is incomplete (data ends before month-end)
last_date = df["Date"].max()
if last_date.day < last_date.days_in_month:
    lines.append(f"- Note: **{last_date:%Y-%m}** only has data up to "
                 f"{last_date:%d %b}, so its low total reflects a partial month.")

report = "\n".join(lines)

print("\n" + "=" * 60)
print("STEP 5: SALES REPORT")
print("=" * 60)
print(report)

# Save the report to a markdown file
with open("analysis_report.md", "w", encoding="utf-8") as f:
    f.write(report + "\n")
print("\nReport saved to analysis_report.md")
