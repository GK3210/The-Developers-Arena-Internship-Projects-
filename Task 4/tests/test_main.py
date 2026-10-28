"""
Test cases for main.py  -  run from the project folder with:
    python -m unittest discover -s tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import main  # noqa: E402


def sample_df():
    """A tiny dataset with known answers."""
    return pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-02", "2024-02-01", "2024-02-02"],
        "Product": ["Laptop", "Phone", "Laptop", "Phone"],
        "Quantity": [2, 1, 3, 1],
        "Price": [100, 50, 100, 50],
        "Customer_ID": ["C1", "C2", "C3", "C4"],
        "Region": ["North", "South", "North", "South"],
        "Total_Sales": [200, 50, 300, 50],
    })


class TestLoading(unittest.TestCase):
    def test_missing_file_raises_data_error(self):
        with self.assertRaises(main.DataError):
            main.load_data("does_not_exist.csv")

    def test_empty_file_raises_data_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "empty.csv"
            f.write_text("")
            with self.assertRaises(main.DataError):
                main.load_data(f)

    def test_real_dataset_loads(self):
        df = main.load_data(main.DATA_FILE)
        self.assertEqual(len(df), 100)


class TestValidation(unittest.TestCase):
    def test_missing_column_detected(self):
        with self.assertRaises(main.DataError):
            main.validate_columns(sample_df().drop(columns=["Region"]))

    def test_valid_columns_pass(self):
        main.validate_columns(sample_df())  # should not raise


class TestCleaning(unittest.TestCase):
    def test_duplicates_removed(self):
        df = pd.concat([sample_df(), sample_df().iloc[[0]]], ignore_index=True)
        clean, log = main.clean_data(df)
        self.assertEqual(log["duplicates_removed"], 1)
        self.assertEqual(len(clean), 4)

    def test_missing_quantity_row_dropped(self):
        df = sample_df()
        df.loc[0, "Quantity"] = None
        clean, log = main.clean_data(df)
        self.assertEqual(log["rows_dropped_missing"], 1)
        self.assertEqual(len(clean), 3)

    def test_negative_quantity_row_dropped(self):
        df = sample_df()
        df.loc[1, "Quantity"] = -5
        clean, log = main.clean_data(df)
        self.assertEqual(log["rows_dropped_invalid"], 1)

    def test_wrong_total_sales_is_corrected(self):
        df = sample_df()
        df.loc[0, "Total_Sales"] = 999
        clean, log = main.clean_data(df)
        self.assertEqual(log["total_sales_fixed"], 1)
        self.assertTrue((clean["Quantity"] * clean["Price"] == clean["Total_Sales"]).all())

    def test_bad_date_row_dropped(self):
        df = sample_df()
        df.loc[2, "Date"] = "not a date"
        clean, log = main.clean_data(df)
        self.assertEqual(len(clean), 3)

    def test_text_is_tidied(self):
        df = sample_df()
        df.loc[0, "Product"] = "  laptop "
        clean, _ = main.clean_data(df)
        self.assertIn("Laptop", set(clean["Product"]))
        self.assertEqual(clean["Product"].nunique(), 2)

    def test_all_rows_invalid_raises(self):
        df = sample_df()
        df["Quantity"] = -1
        with self.assertRaises(main.DataError):
            main.clean_data(df)


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        clean, _ = main.clean_data(sample_df())
        self.r = main.analyze(clean)

    def test_total_revenue(self):
        self.assertEqual(self.r["total_revenue"], 600)

    def test_total_units(self):
        self.assertEqual(self.r["total_units"], 7)

    def test_average_order(self):
        self.assertEqual(self.r["avg_order"], 150)

    def test_best_product_and_region(self):
        self.assertEqual(self.r["by_product"].index[0], "Laptop")
        self.assertEqual(self.r["by_region"].index[0], "North")

    def test_monthly_revenue(self):
        self.assertEqual(list(self.r["monthly"]["Revenue"]), [250, 350])


class TestRealDataset(unittest.TestCase):
    """Check the full pipeline on the real file against known values."""
    def test_known_totals(self):
        df, _ = main.clean_data(main.load_data(main.DATA_FILE))
        r = main.analyze(df)
        self.assertEqual(r["total_revenue"], 12365048)
        self.assertEqual(r["total_units"], 478)
        self.assertEqual(r["by_product"].index[0], "Laptop")
        self.assertEqual(r["by_region"].index[0], "North")


if __name__ == "__main__":
    unittest.main()
