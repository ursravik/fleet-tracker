from flask import Flask, render_template, request, redirect, send_file
import os
import csv
from datetime import datetime
from collections import defaultdict
import io
from flask import jsonify

app = Flask(__name__)
BASE_DIR = os.path.join(os.getcwd(), 'data')
CURRENT_YEAR = str(datetime.now().year)


def get_csv_path(filename):
    year_dir = os.path.join(BASE_DIR, CURRENT_YEAR)
    os.makedirs(year_dir, exist_ok=True)
    return os.path.join(year_dir, filename)


def append_to_csv(file_path, row, headers=None):
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists and headers:
            writer.writerow(headers)
        writer.writerow(row)

def load_vehicle_alerts():
    alerts = {}
    path = get_csv_path("vehicles.csv")
    if not os.path.exists(path):
        return alerts

    today = datetime.today()
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vehicle = row["Vehicle No"]
            alerts[vehicle] = {}

            for key, field in {
                "insurance": "Insurance Expiry",
                "fc": "FC Expiry",
                "tax": "Tax Expiry"
            }.items():
                try:
                    expiry_date = datetime.strptime(row[field], "%Y-%m-%d")
                    days_left = (expiry_date - today).days
                    if days_left <= 15:
                        alerts[vehicle][key] = "red"
                    elif days_left <= 30:
                        alerts[vehicle][key] = "amber"
                    else:
                        alerts[vehicle][key] = ""
                except:
                    alerts[vehicle][key] = ""
    return alerts

def load_vehicle_numbers():
    vehicles = []
    path = get_csv_path("vehicles.csv")
    if os.path.exists(path):
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            vehicles = [row["Vehicle No"] for row in reader]
    return vehicles

def summarize_data(filter_vehicle=None, filter_month=None, from_date=None, to_date=None):
    trips_path = get_csv_path("trips.csv")
    expenses_path = get_csv_path("expenses.csv")
    fuel_path = get_csv_path("fuel.csv")

    summary = defaultdict(lambda: {"kms": 0, "revenue": 0, "expense": 0, "fuel": 0})

    def match_filters(row_date, row_vehicle):
        if filter_vehicle and filter_vehicle != row_vehicle:
            return False
        if filter_month:
            row_month = datetime.strptime(row_date, "%Y-%m-%d").month
            if row_month != int(filter_month):
                return False
        if from_date and datetime.strptime(row_date, "%Y-%m-%d") < datetime.strptime(from_date, "%Y-%m-%d"):
            return False
        if to_date and datetime.strptime(row_date, "%Y-%m-%d") > datetime.strptime(to_date, "%Y-%m-%d"):
            return False
        return True

    if os.path.exists(trips_path):
        with open(trips_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if match_filters(row["Date"], row["Vehicle No"]):
                    v = row["Vehicle No"]
                    summary[v]["kms"] += int(row["KMs Run"])
                    summary[v]["revenue"] += int(row["Revenue"])

    if os.path.exists(expenses_path):
        with open(expenses_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if match_filters(row["Date"], row["Vehicle No"]):
                    v = row["Vehicle No"]
                    summary[v]["expense"] += int(row["Amount"])

    if os.path.exists(fuel_path):
        with open(fuel_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if match_filters(row["Date"], row["Vehicle No"]):
                    v = row["Vehicle No"]
                    summary[v]["fuel"] += int(row["Amount"])

    return summary

def get_csv_path_by_year(filename, year):
    year_dir = os.path.join(BASE_DIR, year)
    os.makedirs(year_dir, exist_ok=True)
    return os.path.join(year_dir, filename)

def get_years():
    return sorted([d for d in os.listdir(BASE_DIR) if d.isdigit()], reverse=True)

@app.route('/')
@app.route('/')
def dashboard():
    vehicles = load_vehicle_numbers()
    return render_template("dashboard.html", vehicles=vehicles)

@app.route('/export')
def export_summary():
    summary = summarize_data()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["Vehicle No", "KMs Run", "Revenue", "Expenses", "Fuel Cost", "Net Profit"])
    for vehicle, data in summary.items():
        profit = data['revenue'] - data['expense'] - data['fuel']
        cw.writerow([vehicle, data['kms'], data['revenue'], data['expense'], data['fuel'], profit])
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='vehicle_summary.csv')


@app.route('/add/vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        data = [
            request.form['vehicle_no'],
            request.form['type'],
            request.form['insurance'],
            request.form['fc'],
            request.form['tax']
        ]
        append_to_csv(get_csv_path('vehicles.csv'), data,
                      headers=["Vehicle No", "Type", "Insurance Expiry", "FC Expiry", "Tax Expiry"])
        return redirect('/')
    return render_template('form_vehicles.html')


@app.route('/add/trip', methods=['GET', 'POST'])
def add_trip():
    if request.method == 'POST':
        data = [
            request.form['date'],
            request.form['vehicle_no'],
            request.form['kms'],
            request.form['revenue'],
            request.form['mode']
        ]
        append_to_csv(get_csv_path('trips.csv'), data,
                      headers=["Date", "Vehicle No", "KMs Run", "Revenue", "Mode"])
        return redirect('/')
    vehicle_list = load_vehicle_numbers()
    return render_template('form_trips.html', vehicle_list=vehicle_list)


@app.route('/add/expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        data = [
            request.form['date'],
            request.form['vehicle_no'],
            request.form['type'],
            request.form['amount'],
            request.form['details']
        ]
        append_to_csv(get_csv_path('expenses.csv'), data,
                      headers=["Date", "Vehicle No", "Type", "Amount", "Details"])
        return redirect('/')
    vehicle_list = load_vehicle_numbers()
    return render_template('form_expenses.html', vehicle_list=vehicle_list)


@app.route('/add/fuel', methods=['GET', 'POST'])
def add_fuel():
    if request.method == 'POST':
        data = [
            request.form['date'],
            request.form['vehicle_no'],
            request.form['litres'],
            request.form['amount']
        ]
        append_to_csv(get_csv_path('fuel.csv'), data,
                      headers=["Date", "Vehicle No", "Litres", "Amount"])
        return redirect('/')
    vehicle_list = load_vehicle_numbers()
    return render_template('form_fuel.html', vehicle_list=vehicle_list)


@app.route('/add/driver', methods=['GET', 'POST'])
def add_driver():
    if request.method == 'POST':
        data = [
            request.form['name'],
            request.form['vehicle_no'],
            request.form['salary'],
            request.form['advance'],
            request.form['remarks'],
            request.form['date']  # New field
        ]
        append_to_csv(get_csv_path('drivers.csv'), data,
                      headers=["Driver Name", "Vehicle No", "Monthly Salary", "Advance", "Remarks", "Date"])
        return redirect('/')
    vehicle_list = load_vehicle_numbers()
    return render_template('form_drivers.html', vehicle_list=vehicle_list)


@app.route('/dashboard/expiry')
def expiry_dashboard():
    year = request.args.get("year", CURRENT_YEAR)
    alerts = load_vehicle_alerts_by_year(year)
    return render_template("dashboard_expiry.html", alerts=alerts, year=year, years=get_years())

def load_vehicle_alerts_by_year(year):
    alerts = {}
    path = get_csv_path_by_year("vehicles.csv", year)
    if not os.path.exists(path):
        return alerts

    today = datetime.today()
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vehicle = row["Vehicle No"]
            alerts[vehicle] = {}
            for key, field in {
                "insurance": "Insurance Expiry",
                "fc": "FC Expiry",
                "tax": "Tax Expiry"
            }.items():
                try:
                    expiry_date = datetime.strptime(row[field], "%Y-%m-%d")
                    days_left = (expiry_date - today).days
                    if days_left <= 15:
                        alerts[vehicle][key] = "red"
                    elif days_left <= 30:
                        alerts[vehicle][key] = "amber"
                    else:
                        alerts[vehicle][key] = "ok"
                except:
                    alerts[vehicle][key] = "unknown"
    return alerts

@app.route('/dashboard/expenses')
def expenses_dashboard():
    year = request.args.get("year", CURRENT_YEAR)
    frequency = request.args.get("frequency", "monthly")
    vehicle = request.args.get("vehicle")
    summary = summarize_expenses_by_frequency(year, frequency, vehicle)
    return render_template(
        "dashboard_expenses.html",
        summary=summary,
        year=year,
        years=get_years(),
        frequency=frequency,
        selected_vehicle=vehicle,
        vehicles=load_vehicle_numbers()
    )

def summarize_expenses_by_frequency(year, frequency, filter_vehicle=None):
    trips_path = get_csv_path_by_year("trips.csv", year)
    expenses_path = get_csv_path_by_year("expenses.csv", year)
    fuel_path = get_csv_path_by_year("fuel.csv", year)
    drivers_path = get_csv_path_by_year("drivers.csv", year)

    freq_map = defaultdict(lambda: {
        "fuel": 0,
        "expense": 0,
        "salary": 0,
        "advance": 0,
        "revenue": 0
    })

    def get_period(date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if frequency == "daily":
            return date.strftime("%Y-%m-%d")
        elif frequency == "weekly":
            return f"Week {date.isocalendar()[1]}"
        elif frequency == "monthly":
            return date.strftime("%Y-%m")
        else:
            return date.strftime("%Y")

    if os.path.exists(trips_path):
        with open(trips_path, newline='') as f:
            for row in csv.DictReader(f):
                if filter_vehicle and row["Vehicle No"] != filter_vehicle:
                    continue
                period = get_period(row["Date"])
                freq_map[period]["revenue"] += int(row["Revenue"])

    if os.path.exists(expenses_path):
        with open(expenses_path, newline='') as f:
            for row in csv.DictReader(f):
                if filter_vehicle and row["Vehicle No"] != filter_vehicle:
                    continue
                period = get_period(row["Date"])
                freq_map[period]["expense"] += int(row["Amount"])

    if os.path.exists(fuel_path):
        with open(fuel_path, newline='') as f:
            for row in csv.DictReader(f):
                if filter_vehicle and row["Vehicle No"] != filter_vehicle:
                    continue
                period = get_period(row["Date"])
                freq_map[period]["fuel"] += int(row["Amount"])

    if os.path.exists(drivers_path):
        with open(drivers_path, newline='') as f:
            for row in csv.DictReader(f):
                if filter_vehicle and row["Vehicle No"] != filter_vehicle:
                    continue
                period = get_period(row["Date"])
                freq_map[period]["salary"] += int(row["Monthly Salary"])
                freq_map[period]["advance"] += int(row["Advance"])

    return freq_map

@app.route('/dashboard/vehicle/<vehicle_id>')
def vehicle_breakdown(vehicle_id):
    year = request.args.get("year", CURRENT_YEAR)
    frequency = request.args.get("frequency", "monthly")
    data = get_vehicle_details(vehicle_id, year, frequency)
    return render_template(
        "dashboard_vehicle.html",
        vehicle_id=vehicle_id,
        year=year,
        years=get_years(),
        data=data,
        frequency=frequency
    )

def get_vehicle_details(vehicle_id, year, frequency):
    from collections import defaultdict

    def get_period(date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if frequency == "daily":
            return date.strftime("%Y-%m-%d")
        elif frequency == "weekly":
            return f"Week {date.isocalendar()[1]}"
        elif frequency == "monthly":
            return date.strftime("%Y-%m")
        else:
            return date.strftime("%Y")

    details = defaultdict(lambda: {
        "fuel": 0, "expense": 0, "salary": 0, "advance": 0, "revenue": 0
    })

    paths = {
        "expenses": get_csv_path_by_year("expenses.csv", year),
        "fuel": get_csv_path_by_year("fuel.csv", year),
        "salary": get_csv_path_by_year("drivers.csv", year),
        "trips": get_csv_path_by_year("trips.csv", year)
    }

    if os.path.exists(paths["expenses"]):
        with open(paths["expenses"], newline='') as f:
            for row in csv.DictReader(f):
                if row["Vehicle No"] == vehicle_id:
                    p = get_period(row["Date"])
                    details[p]["expense"] += int(row["Amount"])

    if os.path.exists(paths["fuel"]):
        with open(paths["fuel"], newline='') as f:
            for row in csv.DictReader(f):
                if row["Vehicle No"] == vehicle_id:
                    p = get_period(row["Date"])
                    details[p]["fuel"] += int(row["Amount"])

    if os.path.exists(paths["salary"]):
        with open(paths["salary"], newline='') as f:
            for row in csv.DictReader(f):
                if row["Vehicle No"] == vehicle_id:
                    p = get_period(row["Date"])
                    details[p]["salary"] += int(row["Monthly Salary"])
                    details[p]["advance"] += int(row["Advance"])

    if os.path.exists(paths["trips"]):
        with open(paths["trips"], newline='') as f:
            for row in csv.DictReader(f):
                if row["Vehicle No"] == vehicle_id:
                    p = get_period(row["Date"])
                    details[p]["revenue"] += int(row["Revenue"])

    return dict(details)

@app.route('/export/expenses')
def export_expenses_csv():
    year = request.args.get("year", CURRENT_YEAR)
    frequency = request.args.get("frequency", "monthly")
    vehicle = request.args.get("vehicle")

    summary = summarize_expenses_by_frequency(year, frequency, vehicle)

    si = io.StringIO()
    writer = csv.writer(si)

    writer.writerow([
        "Period", "Revenue", "Fuel", "Expenses", "Salary", "Advance",
        "Operational Expense", "Net Profit/Loss"
    ])

    for period, row in summary.items():
        op = row["fuel"] + row["expense"] + row["salary"] + row["advance"]
        net = row["revenue"] - op
        writer.writerow([
            period, row["revenue"], row["fuel"], row["expense"],
            row["salary"], row["advance"], op, net
        ])

    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)

    filename = f"expense_report_{year}_{frequency}.csv"
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name=filename)

@app.route('/undo/<datatype>')
def undo_last_entry(datatype):
    valid_types = {
        "vehicle": "vehicles.csv",
        "trip": "trips.csv",
        "expense": "expenses.csv",
        "fuel": "fuel.csv",
        "driver": "drivers.csv"
    }

    if datatype not in valid_types:
        return f"Invalid type: {datatype}", 400

    year = CURRENT_YEAR
    filepath = get_csv_path_by_year(valid_types[datatype], year)

    if not os.path.exists(filepath):
        return "No data to undo", 404

    with open(filepath, "r") as f:
        lines = f.readlines()

    if len(lines) <= 1:
        return "No entries to undo", 400

    with open(filepath, "w") as f:
        f.writelines(lines[:-1])  # remove last line

    return redirect("/")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





