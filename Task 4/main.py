"""
E-commerce Sales Analysis - Complete Data Analysis Project (Week 4)
===================================================================
Pipeline:  LOAD -> VALIDATE -> CLEAN -> ANALYZE -> VISUALIZE -> REPORT

Outputs
    visualizations/*.png        4 charts (bar, pie, line, stacked bar)
    report/analysis_report.md   written report with numbers, charts, insights
    report/analysis_report.pdf  same report as a PDF (needs reportlab)

Run:  python main.py
"""

from pathlib import Path
import sys

import pandas as pd
import matplotlib

matplotlib.use("Agg")  # draw charts to files; no window needed
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sales_data.csv"
VIS_DIR = BASE_DIR / "visualizations"
REPORT_DIR = BASE_DIR / "report"

REQUIRED_COLUMNS = ["Date", "Product", "Quantity", "Price",
                    "Customer_ID", "Region", "Total_Sales"]
NUMERIC_COLUMNS = ["Quantity", "Price", "Total_Sales"]
PALETTE = ["#2E5C8A", "#3F8F6B", "#D98E32", "#8E5BA8", "#C0504D"]


class DataError(Exception):
    """Raised when the input data is missing, empty or malformed."""


def inr(value):
    """Format a number as Indian Rupees, e.g. 1234.5 -> ₹1,234.50"""
    return f"₹{value:,.2f}"


# ---------------------------------------------------------------
# STEP 1: LOAD DATA (with error handling)
# ---------------------------------------------------------------
def load_data(path):
    """Read the CSV file and return a DataFrame."""
    path = Path(path)
    if not path.exists():
        raise DataError(f"Data file not found: {path}")
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise DataError("The CSV file is empty.")
    except pd.errors.ParserError as err:
        raise DataError(f"The CSV file could not be parsed: {err}")
    if df.empty:
        raise DataError("The CSV file has headers but no rows.")
    return df


# ---------------------------------------------------------------
# STEP 2: VALIDATE STRUCTURE
# ---------------------------------------------------------------
def validate_columns(df):
    """Make sure every required column exists."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataError(f"Missing required column(s): {missing}")


# ---------------------------------------------------------------
# STEP 3: CLEAN DATA
# ---------------------------------------------------------------
def clean_data(df):
    """
    Clean the data and return (clean_df, log).
    The log is a dictionary counting every fix, used in the report.
    """
    df = df.copy()
    log = {"rows_start": len(df)}

    # Tidy text columns: remove extra spaces, consistent capitalisation
    for col in ["Product", "Region", "Customer_ID"]:
        df[col] = df[col].astype("string").str.strip()
    df["Product"] = df["Product"].str.title()
    df["Region"] = df["Region"].str.title()

    # Convert types; invalid values become NaN instead of crashing
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    log["missing_values"] = int(df.isnull().sum().sum())

    # Remove exact duplicate rows
    log["duplicates_removed"] = int(df.duplicated().sum())
    df = df.drop_duplicates()

    # Drop rows we cannot trust: no date/product/region or missing quantity/price
    before = len(df)
    df = df.dropna(subset=["Date", "Product", "Region", "Quantity", "Price"])
    log["rows_dropped_missing"] = before - len(df)

    # Drop impossible values (zero or negative quantity / price)
    before = len(df)
    df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]
    log["rows_dropped_invalid"] = before - len(df)

    # Total_Sales must equal Quantity x Price; recalculate any mismatch
    expected = df["Quantity"] * df["Price"]
    log["total_sales_fixed"] = int((expected != df["Total_Sales"]).sum())
    df["Total_Sales"] = expected

    if df.empty:
        raise DataError("No valid rows left after cleaning.")

    df = df.sort_values("Date").reset_index(drop=True)
    log["rows_end"] = len(df)
    return df, log


# ---------------------------------------------------------------
# STEP 4: ANALYZE
# ---------------------------------------------------------------
def analyze(df):
    """Calculate all metrics and return them in a dictionary."""
    r = {}
    r["total_revenue"] = df["Total_Sales"].sum()
    r["total_units"] = int(df["Quantity"].sum())
    r["orders"] = len(df)
    r["avg_order"] = df["Total_Sales"].mean()
    r["median_order"] = df["Total_Sales"].median()
    r["max_order"] = df.loc[df["Total_Sales"].idxmax()]
    r["min_order"] = df.loc[df["Total_Sales"].idxmin()]
    r["date_min"], r["date_max"] = df["Date"].min(), df["Date"].max()

    r["by_product"] = (
        df.groupby("Product")
        .agg(Orders=("Product", "count"), Units=("Quantity", "sum"),
             Revenue=("Total_Sales", "sum"), Avg_Price=("Price", "mean"))
        .sort_values("Revenue", ascending=False)
    )
    r["by_region"] = (
        df.groupby("Region")
        .agg(Orders=("Region", "count"), Revenue=("Total_Sales", "sum"))
        .sort_values("Revenue", ascending=False)
    )
    month = df["Date"].dt.to_period("M")
    r["monthly"] = df.groupby(month).agg(
        Revenue=("Total_Sales", "sum"),
        Avg_Order=("Total_Sales", "mean"),
        Days=("Date", lambda s: s.dt.normalize().nunique()),
    )
    r["region_product"] = df.pivot_table(
        index="Region", columns="Product", values="Total_Sales",
        aggfunc="sum", fill_value=0)
    return r


# ---------------------------------------------------------------
# STEP 5: VISUALIZE (4 chart types)
# ---------------------------------------------------------------
def _finish(fig, name):
    """Save a chart into the visualizations folder."""
    VIS_DIR.mkdir(parents=True, exist_ok=True)
    path = VIS_DIR / name
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def make_charts(r):
    """Create all charts and return a list of (file name, caption)."""
    charts = []
    prod, reg, mon = r["by_product"], r["by_region"], r["monthly"]

    # Chart 1 - BAR: revenue by product
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(prod.index, prod["Revenue"] / 1e6, color=PALETTE[0])
    ax.bar_label(bars, fmt="%.2f", fontsize=9, padding=2)
    ax.set_title("Revenue by Product", fontsize=13, fontweight="bold")
    ax.set_xlabel("Product")
    ax.set_ylabel("Revenue (₹ million)")
    ax.spines[["top", "right"]].set_visible(False)
    _finish(fig, "1_revenue_by_product_bar.png")
    charts.append(("1_revenue_by_product_bar.png",
                   "Bar chart: revenue by product"))

    # Chart 2 - PIE: share of revenue by region
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.pie(reg["Revenue"], labels=reg.index, autopct="%1.1f%%", startangle=90,
           colors=PALETTE[: len(reg)], wedgeprops={"edgecolor": "white"})
    ax.set_title("Share of Revenue by Region", fontsize=13, fontweight="bold")
    _finish(fig, "2_revenue_share_by_region_pie.png")
    charts.append(("2_revenue_share_by_region_pie.png",
                   "Pie chart: share of revenue by region"))

    # Chart 3 - LINE: monthly revenue trend
    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = [str(p) for p in mon.index]
    ax.plot(labels, mon["Revenue"] / 1e6, marker="o", color=PALETTE[1], lw=2)
    for x, y in zip(labels, mon["Revenue"] / 1e6):
        ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9)
    last_days = int(mon["Days"].iloc[-1])
    ax.set_title("Monthly Revenue Trend", fontsize=13, fontweight="bold")
    ax.set_xlabel(f"Month (last month has only {last_days} days of data)")
    ax.set_ylabel("Revenue (₹ million)")
    ax.set_ylim(0, (mon["Revenue"].max() / 1e6) * 1.2)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    _finish(fig, "3_monthly_revenue_line.png")
    charts.append(("3_monthly_revenue_line.png",
                   "Line chart: monthly revenue trend"))

    # Chart 4 - STACKED BAR: product mix inside each region
    rp = r["region_product"].loc[reg.index] / 1e6
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = pd.Series(0.0, index=rp.index)
    for i, product in enumerate(rp.columns):
        ax.bar(rp.index, rp[product], bottom=bottom, label=product,
               color=PALETTE[i % len(PALETTE)])
        bottom += rp[product]
    ax.set_title("Revenue by Region and Product", fontsize=13, fontweight="bold")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue (₹ million)")
    ax.legend(title="Product", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    _finish(fig, "4_region_product_stacked_bar.png")
    charts.append(("4_region_product_stacked_bar.png",
                   "Stacked bar chart: product mix inside each region"))
    return charts


# ---------------------------------------------------------------
# STEP 6: INSIGHTS (written automatically from the numbers)
# ---------------------------------------------------------------
def build_insights(r):
    """Return a list of plain-English insights."""
    total = r["total_revenue"]
    prod, reg, mon = r["by_product"], r["by_region"], r["monthly"]
    out = []

    top_p, low_p = prod.index[0], prod.index[-1]
    per_order = prod["Units"] / prod["Orders"]  # average units per order
    text = (f"**{top_p} is the top product.** It earns {inr(prod.loc[top_p, 'Revenue'])} "
            f"({prod.loc[top_p, 'Revenue'] / total:.1%} of revenue) from "
            f"{int(prod.loc[top_p, 'Orders'])} orders. ")
    if per_order.idxmax() == top_p:
        text += (f"Its lead comes from volume: customers buy {per_order[top_p]:.1f} units "
                 f"per order, the highest of any product, not from a higher price "
                 f"(average price {inr(prod.loc[top_p, 'Avg_Price'])}).")
    elif prod["Avg_Price"].idxmax() == top_p:
        text += (f"Its lead comes from price: its average price "
                 f"({inr(prod.loc[top_p, 'Avg_Price'])}) is the highest of any product.")
    else:
        text += (f"It sells {per_order[top_p]:.1f} units per order at an average price of "
                 f"{inr(prod.loc[top_p, 'Avg_Price'])}.")
    out.append(text)

    most_orders = prod["Orders"].idxmax()
    if most_orders != top_p:
        out.append(
            f"**{most_orders} gets the most orders** ({int(prod.loc[most_orders, 'Orders'])}) "
            f"but ranks #{list(prod.index).index(most_orders) + 1} by revenue, so order "
            f"count alone does not show which product earns the most.")

    out.append(
        f"**{low_p} is the weakest product** at {prod.loc[low_p, 'Revenue'] / total:.1%} "
        f"of revenue. It is the best candidate for a promotion or bundle offer.")

    top_r, low_r = reg.index[0], reg.index[-1]
    out.append(
        f"**{top_r} is the strongest region** ({reg.loc[top_r, 'Revenue'] / total:.1%}) "
        f"and **{low_r} is the weakest** ({reg.loc[low_r, 'Revenue'] / total:.1%}). "
        f"The gap is {inr(reg.loc[top_r, 'Revenue'] - reg.loc[low_r, 'Revenue'])}.")

    best_m = mon["Revenue"].idxmax()
    out.append(
        f"**{best_m} was the best month** with {inr(mon.loc[best_m, 'Revenue'])}.")

    last = mon.index[-1]
    if int(mon["Days"].iloc[-1]) < last.days_in_month:
        out.append(
            f"**{last} looks like a drop but is incomplete.** Data covers only "
            f"{int(mon['Days'].iloc[-1])} days of that month. Its average order value "
            f"({inr(mon.loc[last, 'Avg_Order'])}) is the fairer figure to compare.")

    spread = r["max_order"]["Total_Sales"] / r["min_order"]["Total_Sales"]
    out.append(
        f"**Order values vary a lot.** The largest order is about {spread:.0f}x the "
        f"smallest, and the average ({inr(r['avg_order'])}) is above the median "
        f"({inr(r['median_order'])}), so a few big orders pull the average up.")
    return out


# ---------------------------------------------------------------
# STEP 7: REPORT (Markdown + PDF)
# ---------------------------------------------------------------
def write_markdown_report(r, log, charts, insights, path):
    """Write the full report as a Markdown file."""
    L = []
    L.append("# E-commerce Sales Analysis Report\n")
    L.append(f"**Period:** {r['date_min']:%d %b %Y} to {r['date_max']:%d %b %Y}  ")
    L.append(f"**Orders analysed:** {r['orders']}\n")

    L.append("## 1. Key Metrics\n")
    L.append("| Metric | Value |\n|---|---|")
    L.append(f"| Total revenue | {inr(r['total_revenue'])} |")
    L.append(f"| Total units sold | {r['total_units']:,} |")
    L.append(f"| Average order value | {inr(r['avg_order'])} |")
    L.append(f"| Median order value | {inr(r['median_order'])} |")
    mx, mn = r["max_order"], r["min_order"]
    L.append(f"| Largest order | {inr(mx['Total_Sales'])} ({mx['Product']}, {mx['Region']}, {mx['Date']:%d %b %Y}) |")
    L.append(f"| Smallest order | {inr(mn['Total_Sales'])} ({mn['Product']}, {mn['Region']}, {mn['Date']:%d %b %Y}) |\n")

    L.append("## 2. Product Performance\n")
    L.append("| Product | Orders | Units | Revenue | Share |\n|---|---|---|---|---|")
    for p, row in r["by_product"].iterrows():
        L.append(f"| {p} | {int(row.Orders)} | {int(row.Units)} | {inr(row.Revenue)} | {row.Revenue / r['total_revenue']:.1%} |")
    L.append("")
    L.append("## 3. Regional Performance\n")
    L.append("| Region | Orders | Revenue | Share |\n|---|---|---|---|")
    for g, row in r["by_region"].iterrows():
        L.append(f"| {g} | {int(row.Orders)} | {inr(row.Revenue)} | {row.Revenue / r['total_revenue']:.1%} |")
    L.append("")
    L.append("## 4. Monthly Performance\n")
    L.append("| Month | Days with data | Revenue | Avg order value |\n|---|---|---|---|")
    for m, row in r["monthly"].iterrows():
        L.append(f"| {m} | {int(row.Days)} | {inr(row.Revenue)} | {inr(row.Avg_Order)} |")
    L.append("")

    L.append("## 5. Visualizations\n")
    for fname, caption in charts:
        L.append(f"![{caption}](../visualizations/{fname})\n")
        L.append(f"*{caption}*\n")

    L.append("## 6. Insights\n")
    for i, text in enumerate(insights, 1):
        L.append(f"{i}. {text}")
    L.append("")

    L.append("## 7. Recommendations\n")
    L.append(f"- Promote **{r['by_product'].index[-1]}** (bundles or discounts) to lift the weakest product line.")
    L.append(f"- Study what works in **{r['by_region'].index[0]}** and test it in **{r['by_region'].index[-1]}**.")
    L.append("- Track order value as well as order count when judging products.")
    L.append("- Collect a full month of data before comparing the latest month.\n")

    L.append("## 8. Data Quality Summary\n")
    L.append(f"- Rows loaded: {log['rows_start']}")
    L.append(f"- Missing values found: {log['missing_values']}")
    L.append(f"- Duplicate rows removed: {log['duplicates_removed']}")
    L.append(f"- Rows dropped (missing key fields): {log['rows_dropped_missing']}")
    L.append(f"- Rows dropped (zero/negative quantity or price): {log['rows_dropped_invalid']}")
    L.append(f"- Total_Sales values corrected: {log['total_sales_fixed']}")
    L.append(f"- Rows used in analysis: {log['rows_end']}\n")
    path.write_text("\n".join(L), encoding="utf-8")


def _strip_md(text):
    """Convert **bold** markers to ReportLab <b> tags."""
    parts = text.split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))


def write_pdf_report(r, log, charts, insights, path):
    """Write the report as a PDF. Skipped if reportlab is not installed."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, Image, KeepTogether)
    except ImportError:
        print("reportlab not installed - PDF report skipped.")
        return False

    # matplotlib ships DejaVu Sans, which can draw the rupee symbol
    font_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont("DV", str(font_dir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DV-B", str(font_dir / "DejaVuSans-Bold.ttf")))

    navy = colors.HexColor("#1F3A5F")
    H1 = ParagraphStyle("H1", fontName="DV-B", fontSize=20, leading=26, textColor=navy, spaceAfter=6)
    H2 = ParagraphStyle("H2", fontName="DV-B", fontSize=12.5, leading=16, textColor=navy, spaceBefore=14, spaceAfter=6,
                    keepWithNext=True)
    BODY = ParagraphStyle("B", fontName="DV", fontSize=9.5, leading=14, spaceAfter=4)
    SUB = ParagraphStyle("S", fontName="DV", fontSize=9.5, leading=13, textColor=colors.HexColor("#555555"), spaceAfter=8)
    CAP = ParagraphStyle("C", fontName="DV", fontSize=8.5, leading=11, textColor=colors.HexColor("#555555"), spaceAfter=8)
    CELL = ParagraphStyle("T", fontName="DV", fontSize=9, leading=12)

    def table(data, widths, right=()):
        t = Table(data, colWidths=widths, repeatRows=1)
        style = [("FONT", (0, 0), (-1, -1), "DV", 9), ("FONT", (0, 0), (-1, 0), "DV-B", 9),
                 ("BACKGROUND", (0, 0), (-1, 0), navy), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                 ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F9")]),
                 ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
                 ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]
        style += [("ALIGN", (c, 0), (c, -1), "RIGHT") for c in right]
        t.setStyle(TableStyle(style))
        return t

    tot = r["total_revenue"]
    mx, mn = r["max_order"], r["min_order"]
    s = [Paragraph("E-commerce Sales Analysis Report", H1),
         Paragraph(f"Period: {r['date_min']:%d %b %Y} to {r['date_max']:%d %b %Y} &nbsp;|&nbsp; "
                   f"Orders analysed: {r['orders']}", SUB)]

    s.append(Paragraph("1. Key Metrics", H2))
    s.append(table([
        ["Metric", "Value"],
        ["Total revenue", inr(tot)],
        ["Total units sold", f"{r['total_units']:,}"],
        ["Average order value", inr(r["avg_order"])],
        ["Median order value", inr(r["median_order"])],
        ["Largest order", Paragraph(f"{inr(mx['Total_Sales'])} ({mx['Product']}, {mx['Region']}, {mx['Date']:%d %b %Y})", CELL)],
        ["Smallest order", Paragraph(f"{inr(mn['Total_Sales'])} ({mn['Product']}, {mn['Region']}, {mn['Date']:%d %b %Y})", CELL)],
    ], [5*cm, 12*cm]))

    s.append(Paragraph("2. Product Performance", H2))
    rows = [["Product", "Orders", "Units", "Revenue", "Share"]]
    for p, row in r["by_product"].iterrows():
        rows.append([p, int(row.Orders), int(row.Units), inr(row.Revenue), f"{row.Revenue / tot:.1%}"])
    s.append(table(rows, [4*cm, 2.5*cm, 2.5*cm, 5*cm, 3*cm], right=(1, 2, 3, 4)))

    s.append(Paragraph("3. Regional Performance", H2))
    rows = [["Region", "Orders", "Revenue", "Share"]]
    for g, row in r["by_region"].iterrows():
        rows.append([g, int(row.Orders), inr(row.Revenue), f"{row.Revenue / tot:.1%}"])
    s.append(table(rows, [4*cm, 3*cm, 6*cm, 4*cm], right=(1, 2, 3)))

    s.append(Paragraph("4. Monthly Performance", H2))
    rows = [["Month", "Days", "Revenue", "Avg order value"]]
    for m, row in r["monthly"].iterrows():
        rows.append([str(m), int(row.Days), inr(row.Revenue), inr(row.Avg_Order)])
    s.append(table(rows, [3.5*cm, 2.5*cm, 5.5*cm, 5.5*cm], right=(1, 2, 3)))

    for n, (fname, caption) in enumerate(charts):
        img = Image(str(VIS_DIR / fname))
        ratio = img.imageHeight / img.imageWidth
        w = 12.5 * cm
        img.drawWidth, img.drawHeight = w, w * ratio
        block = [img, Paragraph(caption, CAP)]
        if n == 0:  # keep the section heading on the same page as the first chart
            block.insert(0, Paragraph("5. Visualizations", H2))
        s.append(KeepTogether(block))

    s.append(Paragraph("6. Insights", H2))
    for i, text in enumerate(insights, 1):
        s.append(Paragraph(f"{i}. {_strip_md(text)}", BODY))

    s.append(Paragraph("7. Recommendations", H2))
    for text in [f"Promote <b>{r['by_product'].index[-1]}</b> with bundles or discounts.",
                 f"Study what works in <b>{r['by_region'].index[0]}</b> and test it in <b>{r['by_region'].index[-1]}</b>.",
                 "Track order value as well as order count when judging products.",
                 "Collect a full month of data before comparing the latest month."]:
        s.append(Paragraph("• " + text, BODY))

    s.append(Paragraph("8. Data Quality Summary", H2))
    for text in [f"Rows loaded: {log['rows_start']}", f"Missing values found: {log['missing_values']}",
                 f"Duplicate rows removed: {log['duplicates_removed']}",
                 f"Rows dropped (missing key fields): {log['rows_dropped_missing']}",
                 f"Rows dropped (zero/negative quantity or price): {log['rows_dropped_invalid']}",
                 f"Total_Sales values corrected: {log['total_sales_fixed']}",
                 f"Rows used in analysis: {log['rows_end']}"]:
        s.append(Paragraph("• " + text, BODY))

    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                      topMargin=2*cm, bottomMargin=2*cm,
                      title="E-commerce Sales Analysis Report").build(s)
    return True


# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
def main():
    try:
        print("Step 1/6  Loading data ...")
        df = load_data(DATA_FILE)
        print(f"          {len(df)} rows, {len(df.columns)} columns loaded")

        print("Step 2/6  Validating structure ...")
        validate_columns(df)

        print("Step 3/6  Cleaning data ...")
        df, log = clean_data(df)
        print(f"          missing={log['missing_values']}, duplicates={log['duplicates_removed']}, "
              f"Total_Sales fixed={log['total_sales_fixed']}, rows kept={log['rows_end']}")

        print("Step 4/6  Analysing ...")
        results = analyze(df)
        print(f"          Total revenue : {inr(results['total_revenue'])}")
        print(f"          Top product   : {results['by_product'].index[0]}")
        print(f"          Top region    : {results['by_region'].index[0]}")

        print("Step 5/6  Creating charts ...")
        charts = make_charts(results)
        for fname, _ in charts:
            print(f"          saved visualizations/{fname}")

        print("Step 6/6  Writing report ...")
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        insights = build_insights(results)
        write_markdown_report(results, log, charts, insights, REPORT_DIR / "analysis_report.md")
        print("          saved report/analysis_report.md")
        if write_pdf_report(results, log, charts, insights, REPORT_DIR / "analysis_report.pdf"):
            print("          saved report/analysis_report.pdf")

        print("\nINSIGHTS")
        for i, text in enumerate(insights, 1):
            print(f"  {i}. {text.replace('**', '')}")
        print("\nDone.")
    except DataError as err:
        print(f"\nERROR: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
