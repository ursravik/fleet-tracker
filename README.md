# 🚛 Fleet Tracker

**Fleet Tracker** is a lightweight Python Flask-based web application designed to help businesses efficiently manage and monitor cold storage vehicles and their operational expenses — all with local, CSV-based storage and a clean web UI.

---

## 🧰 Features

- 🧾 Vehicle tracking with insurance, FC, and tax expiry alerts
- 🗓️ Dashboards for:
  - Expiry alerts
  - Operational expenses (daily, weekly, monthly, yearly)
  - Per-vehicle detailed breakdown
- 💸 Tracks:
  - Trips (KMs run + revenue)
  - Maintenance and fuel expenses
  - Driver salary and advance payouts
- 📊 Financial reports: net profit/loss per vehicle and frequency
- 💾 CSV-based storage by year (`/data/YYYY/`)
- ✅ Designed for offline-first + cloud-sync-ready backup
- 🔍 Easily testable with isolated test data
- 🔒 Admin-only data entry, view-only support for others

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/ursravik/fleet-tracker.git
cd fleet-tracker
```

### 2. Create Virtual Environment

```bash
make install
```

> This creates `.venv/` and installs dependencies from `requirements.txt`.

### 3. Run the App

```bash
make run
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 🧪 Run Tests

```bash
make test
```

- Tests run in a sandbox using `tmp/test_data/YYYY` — your actual data is never modified.

---

## 🗂️ Folder Structure

```
fleet-tracker/
├── app.py                # Main Flask app
├── data/                 # CSV storage (organized by year)
├── templates/            # HTML templates
├── tests/                # Unit tests (isolated)
├── Makefile              # Setup, run, test automation
├── requirements.txt
└── README.md
```

---

## 📅 Sample Dashboards

- `/dashboard/expiry` – insurance, FC, tax alerts
- `/dashboard/expenses` – operational summary by frequency
- `/dashboard/vehicle/<vehicle_no>` – full breakdown per vehicle

---

## 📌 Data Entry Pages

- `/add/vehicle`
- `/add/trip`
- `/add/fuel`
- `/add/expense`
- `/add/driver`

---

## 📦 Backup Strategy

Just backup your `/data/` folder (year-wise).  
You can sync it with:
- Google Drive
- Dropbox
- External USB

If your laptop crashes, just point the app to the backup path.

---

## 🙋‍♂️ Author

Built with ❤️ by [@ursravik](https://github.com/ursravik)

---

## 📜 License

MIT License – free to use, modify, and improve!