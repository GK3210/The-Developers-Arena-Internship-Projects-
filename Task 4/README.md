# E-commerce Sales Analysis (Week 4: Complete Data Analysis Project)

A complete Python data analysis pipeline that loads an e-commerce sales dataset, cleans and validates it, calculates business metrics, draws four charts, and produces a written report with insights.

**Project option chosen:** Option 4, E-commerce Sales Analysis

---

## 1. Project Overview

### Goals
- Build a full pipeline: **load → validate → clean → analyze → visualize → report**
- Answer practical business questions: which products and regions earn the most, how revenue changes over time, and where there is room to improve
- Use at least two chart types (this project uses four: bar, pie, line, stacked bar)
- Handle bad input safely and prove the code works with tests

### Dataset
`data/sales_data.csv` has 100 orders from 1 Jan 2024 to 9 Apr 2024.

| Column | Meaning |
|---|---|
| Date | Order date |
| Product | Laptop, Phone, Tablet, Headphones, Monitor |
| Quantity | Units in the order |
| Price | Price per unit (₹) |
| Customer_ID | Customer identifier |
| Region | North, South, East, West |
| Total_Sales | Order value (₹) = Quantity × Price |

---

## 2. Project Structure

```
week4_sales_analysis/
├── README.md                  Project documentation (this file)
├── main.py                    Complete analysis pipeline
├── requirements.txt           Python dependencies
├── data/
│   └── sales_data.csv         Input dataset
├── visualizations/            Charts created by main.py
│   ├── 1_revenue_by_product_bar.png
│   ├── 2_revenue_share_by_region_pie.png
│   ├── 3_monthly_revenue_line.png
│   └── 4_region_product_stacked_bar.png
├── report/
│   ├── analysis_report.md     Full report (numbers, charts, insights)
│   ├── analysis_report.pdf    Same report as PDF
│   ├── run_output.txt         Console output of one full run
│   └── test_results.txt       Output of the test suite
└── tests/
    └── test_main.py           18 automated test cases
```

---

## 3. Setup Instructions

**Requirements:** Python 3.9 or newer.

```bash
# 1. Go into the project folder
cd week4_sales_analysis

# 2. (Optional) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac / Linux

# 3. Install the libraries
pip install -r requirements.txt

# 4. Run the project
python main.py
```

Running `main.py` prints each step, then creates the 4 charts in `visualizations/` and the report in `report/`.

To run the tests:
```bash
python -m unittest discover -s tests -v
```

---

## 4. Code Structure

`main.py` is organised as one function per pipeline stage:

| Function | Stage | What it does |
|---|---|---|
| `load_data()` | Load | Reads the CSV; raises a clear error if the file is missing, empty or unreadable |
| `validate_columns()` | Validate | Confirms all 7 required columns exist |
| `clean_data()` | Clean | Tidies text, converts types, removes duplicates and invalid rows, recalculates Total_Sales |
| `analyze()` | Analyze | Calculates all metrics with pandas `groupby` and `pivot_table` |
| `make_charts()` | Visualize | Draws and saves the 4 matplotlib charts |
| `build_insights()` | Report | Writes the insights in plain English from the calculated numbers |
| `write_markdown_report()` / `write_pdf_report()` | Report | Produces the Markdown and PDF reports |
| `main()` | Control | Runs everything in order and handles errors |

---

## 5. Technical Details

**Data structures:** The data lives in a pandas `DataFrame`. Grouped results (by product, region, month) are also DataFrames, and the full set of metrics is passed between functions in a Python dictionary.

**Cleaning rules**
- Remove extra spaces and fix capitalisation in text columns
- Convert Date to a real date type and numeric columns to numbers; unreadable values become missing (`NaN`) instead of crashing
- Remove exact duplicate rows
- Drop rows with a missing date, product, region, quantity or price
- Drop rows with zero or negative quantity or price
- Recalculate `Total_Sales = Quantity × Price` so revenue figures are always consistent

**Error handling:** A custom `DataError` is raised for a missing file, an empty file, a missing column, or no valid rows left. `main()` catches it, prints a clear message and exits instead of showing a long traceback.

**Metrics calculated:** total revenue, total units, average and median order value, largest and smallest order, revenue / orders / units / average price per product, revenue and orders per region, monthly revenue and average order value, and revenue per region and product.

---

## 6. Results

| Metric | Value |
|---|---|
| Total revenue | ₹12,365,048.00 |
| Total units sold | 478 |
| Average order value | ₹123,650.48 |
| Median order value | ₹97,955.50 |
| Top product (revenue) | Laptop (31.5%) |
| Top region (revenue) | North (32.2%) |

### Visual Documentation

**Bar chart: revenue by product**

![Revenue by product](visualizations/1_revenue_by_product_bar.png)

**Pie chart: revenue share by region**

![Revenue share by region](visualizations/2_revenue_share_by_region_pie.png)

**Line chart: monthly revenue trend**

![Monthly revenue trend](visualizations/3_monthly_revenue_line.png)

**Stacked bar chart: product mix in each region**

![Region and product](visualizations/4_region_product_stacked_bar.png)

---

## 7. Key Insights

1. **Laptop is the top product.** It earns ₹3,889,210 (31.5% of revenue) from 24 orders. Its lead comes from volume: customers buy 5.7 units per order, the highest of any product, not from a higher price.
2. **Tablet gets the most orders** (26) but ranks #2 by revenue, so order count alone does not show which product earns the most.
3. **Monitor is the weakest product** at 10.9% of revenue, which makes it the best candidate for a promotion or bundle offer.
4. **North is the strongest region** (32.2%) and **West is the weakest** (17.2%), a gap of ₹1,859,713.
5. **March was the best month** with ₹4,485,006.
6. **April looks like a drop but is incomplete.** Data covers only 9 days of the month, so its average order value (₹122,608) is the fairer comparison.
7. **Order values vary a lot.** The largest order is about 57× the smallest, and the average is above the median, so a few big orders pull the average up.

### Recommendations
- Promote Monitor with bundles or discounts.
- Study what works in North and test it in West.
- Track order value as well as order count when judging products.
- Collect a full month of data before comparing the latest month.

---

## 8. Testing Evidence

The test suite (`tests/test_main.py`) has **18 test cases, all passing** (full output in `report/test_results.txt`).

| Area | Examples of what is tested |
|---|---|
| Loading | Missing file and empty file raise `DataError`; real dataset loads 100 rows |
| Validation | A missing column is detected; a valid table passes |
| Cleaning | Duplicates removed; missing quantity, negative quantity and bad date rows dropped; wrong `Total_Sales` corrected; text spacing and capitalisation fixed; all-invalid data raises an error |
| Analysis | On a small dataset with known answers: total revenue, units, average order, best product and region, monthly totals |
| Real data | Full pipeline returns ₹12,365,048 revenue, 478 units, Laptop and North as the top product and region |

Data quality result for the real dataset: 100 rows loaded, 0 missing values, 0 duplicates, 0 corrections needed, 100 rows used.

---

## 9. Limitations
- The dataset covers about 3 months, so seasonal patterns cannot be measured.
- Each customer appears only once, so customer-level analysis (repeat buyers, lifetime value) is not possible.
- April has only 9 days of data and should not be compared with full months.

---

## Author
Gautam Kurpatwar
