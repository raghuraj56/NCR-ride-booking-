# 🚗 NCR Ride Bookings — Data Analysis & Business Intelligence Dashboard

## 📌 Overview

This project presents an **end-to-end data analysis pipeline** for NCR ride bookings using **Python, Pandas, and Matplotlib**.
It transforms raw ride data into actionable business insights through **data cleaning, feature engineering, KPI analysis, and dashboard visualization**.

The goal is to simulate a **real-world business intelligence use case** for ride-hailing platforms like Uber/Ola.

---

## 🎯 Objectives

* Analyze ride booking trends and performance
* Identify revenue and profit patterns
* Understand vehicle-wise contribution
* Measure operational efficiency (cancellations & incomplete rides)
* Provide actionable business recommendations

---

## 🛠️ Tech Stack

* **Python**
* **Pandas** – Data manipulation
* **NumPy** – Numerical operations
* **Matplotlib** – Data visualization
* **OS / Warnings** – System handling

---

## 📂 Project Structure

```
├── ncr_ride_bookings.csv     # Dataset
├── analysis_script.py        # Main Python script
├── outputs/
│   └── ncr_dashboard.png     # Generated dashboard
└── README.md                 # Project documentation
```

---

## ⚙️ Features Implemented

### 🔹 1. Data Cleaning

* Date parsing & validation
* Standardized booking statuses
* Removed invalid/missing records
* Cleaned ID fields

### 🔹 2. Feature Engineering

* Extracted **Year, Month, Month Name**
* Derived:

  * Revenue
  * Cost (assumed 65%)
  * Profit (35% margin)

---

### 🔹 3. KPI Metrics

* Total Rides
* Completed / Cancelled / Incomplete Rides
* Cancellation Rate
* Total Revenue & Profit
* Average Revenue per Ride

---

## 📊 Dashboard Visualizations

### 📈 1. Monthly Revenue & Profit (Stacked Bar)

* Shows revenue distribution over time
* Highlights profit contribution

### 🚗 2. Vehicle Type Analysis (Bar Chart)

* Number of rides per vehicle
* Profit per vehicle (annotated)

### 🍩 3. Profit Contribution (Donut Chart)

* Percentage share of profit by vehicle type

### 🥧 4. Booking Status Distribution (Pie Chart)

* Completed vs Cancelled vs Incomplete rides

---

## 💡 Key Insights

* Strong revenue generation with stable monthly trends
* Certain vehicle types dominate both **volume and profitability**
* Cancellation rate significantly impacts potential revenue
* Incomplete rides indicate operational inefficiencies

---

## 📈 Business Recommendations

### 1. Reduce Cancellations

* Incentivize drivers for low cancellation rates
* Improve driver allocation algorithms

### 2. Upsell Premium Vehicles

* Target high-volume users with upgrade offers
* Increase revenue per ride

### 3. Improve Operational Efficiency

* Analyze root causes of incomplete rides
* Implement fleet maintenance strategies

---

## 🚀 How to Run

```bash
# Install dependencies
pip install pandas numpy matplotlib

# Run script
python analysis_script.py
```

---

## 📸 Output

The script generates a professional dashboard:

```
outputs/ncr_dashboard.png
```

---

## 🌟 Project Highlights

* End-to-end **data analysis pipeline**
* Strong **business storytelling**
* Clean and modular code structure
* Real-world **BI dashboard simulation**

---

## 📌 Future Improvements

* Interactive dashboard (Streamlit / Power BI)
* Customer segmentation analysis
* Predictive modeling (cancellation prediction)
* Real-time data pipeline integration

---

## 👨‍💻 Author

**Senior Data Analyst Project (Portfolio Ready)**

---

## ⭐ If you like this project

Give it a ⭐ on GitHub and feel free to fork or contribute!
