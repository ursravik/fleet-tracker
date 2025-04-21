import unittest
import os
import shutil
from datetime import datetime
from app import app

TEST_YEAR = str(datetime.now().year)
TEMP_DATA_PATH = f"tmp/test_data/{TEST_YEAR}"

class FleetAppTestCase(unittest.TestCase):
    def setUp(self):
        # Override BASE_DIR to temp directory
        app.config["TESTING"] = True
        app.config["BASE_DIR"] = "tmp/test_data"
        self.app = app.test_client()

        # Ensure the test data path exists
        os.makedirs(TEMP_DATA_PATH, exist_ok=True)

        # Patch the BASE_DIR globally in app (optional, depending on implementation)
        global BASE_DIR
        BASE_DIR = app.config["BASE_DIR"]

    def tearDown(self):
        # Clean up after each test run
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")

    def test_add_vehicle(self):
        data = {
            "vehicle_no": "TEST1234",
            "type": "Mini Truck",
            "insurance": "2025-12-31",
            "fc": "2026-12-31",
            "tax": "2025-11-30"
        }
        res = self.app.post("/add/vehicle", data=data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_add_driver(self):
        data = {
            "name": "Test Driver",
            "vehicle_no": "TEST1234",
            "salary": "18000",
            "advance": "2000",
            "remarks": "Test Salary",
            "date": datetime.today().strftime("%Y-%m-%d")
        }
        res = self.app.post("/add/driver", data=data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_add_trip(self):
        data = {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "vehicle_no": "TEST1234",
            "kms": "120",
            "revenue": "2400",
            "mode": "daily"
        }
        res = self.app.post("/add/trip", data=data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_add_expense(self):
        data = {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "vehicle_no": "TEST1234",
            "type": "maintenance",
            "amount": "1800",
            "details": "Test brake work"
        }
        res = self.app.post("/add/expense", data=data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_add_fuel(self):
        data = {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "vehicle_no": "TEST1234",
            "litres": "30",
            "amount": "3000"
        }
        res = self.app.post("/add/fuel", data=data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_expiry_dashboard(self):
        res = self.app.get("/dashboard/expiry")
        self.assertEqual(res.status_code, 200)

    def test_expense_dashboard(self):
        res = self.app.get("/dashboard/expenses")
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
