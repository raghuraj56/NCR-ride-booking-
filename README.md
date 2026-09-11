# NCR Ride Bookings — Data Analysis & Business Intelligence Dashboard

## Overview

End-to-end data analysis pipeline for NCR (National Capital Region) ride bookings using **Python, Pandas, NumPy and Matplotlib**. It transforms raw ride data into actionable business insights through **data cleaning, feature engineering, KPI analysis and dashboard visualization**, simulating a real-world BI use case for ride-hailing platforms like Uber/Ola.

## Objectives

* Analyze ride booking trends and performance
* Identify revenue and profit patterns
* Understand vehicle-wise contribution
* Measure operational efficiency (cancellations & incomplete rides)
* Provide actionable business recommendations

## Project Structure

```
├── analysis_script.py            # Main analysis pipeline (run this)
├── NCR ride booking0.ipynb       # Notebook wrapper for Colab
├── ncr_ride_bookings.csv         # Dataset (NOT committed — see below)
├── outputs/
│   └── ncr_dashboard.png         # Generated dashboard (created on run)
├── .github/                      # Issue & PR templates
├── requirements.txt
├── LICENSE
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

### Dataset

The dataset is **not committed** to this repo. The pipeline expects a CSV named `ncr_ride_bookings.csv` with at least these columns:

| Column | Description |
|---|---|
| `Booking ID` | Unique booking identifier |
| `Customer ID` | Unique customer identifier |
| `Date` | Booking date (day-first or month-first is auto-detected) |
| `Booking Status` | e.g. Completed, Cancelled by Customer/Driver, No Driver Found, Incomplete |
| `Vehicle Type` | e.g. Auto, Bike, Go Mini, Go Sedan, Premier Sedan, Uber XL, eBike |
| `Booking Value` | Ride fare (₹) |

Place the file next to `analysis_script.py`, or pass `--data PATH`.

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the pipeline (uses ./ncr_ride_bookings.csv by default)
python analysis_script.py

# Or with custom paths
python analysis_script.py --data /path/to/ncr_ride_bookings.csv --output outputs/ncr_dashboard.png
```

**In Colab:** upload `ncr_ride_bookings.csv` and `analysis_script.py` to `/content`, then open the notebook and run its single cell.

## Methodology

### Data Cleaning
* Date parsing with **auto-detection of day-first vs month-first format** (avoids silently dropping `dd/mm/yyyy` dates with day > 12)
* Standardized booking statuses (all cancellation reasons collapse to "Cancelled")
* Numeric coercion of `Booking Value`; rows with unparseable dates or fares dropped
* Warning printed for unrecognized statuses

### Feature Engineering
* Year, Month, Month name, and a unique `YYYY-MM` period key per month
* Revenue = Booking Value; Cost = 65% of revenue (assumption); Profit = Revenue − Cost

### KPI Definitions (documented, consistent)
* **Revenue / Profit / Avg revenue** — **completed rides only**, since cancelled and incomplete bookings never realise a fare
* **Cancellation rate** = cancelled ÷ (completed + cancelled), ×100. Incomplete rides are excluded from the denominator: a booking that started but never finished is neither a completed sale nor a cancellation
* **Potential revenue gain** = cancelled × 50% × avg completed revenue — an explicit, documented assumption (half of cancelled bookings would have converted)

## Dashboard

Generated at `outputs/ncr_dashboard.png`:

1. **KPI header cards** — total rides, completed, cancellation rate, revenue, profit, avg revenue per ride
2. **Monthly Revenue & Profit** — grouped bars over `YYYY-MM` periods (grouped, not stacked, because profit is a *subset* of revenue)
3. **Vehicle Type analysis** — ride volume per vehicle with profit annotation
4. **Profit contribution donut** — share of profit by vehicle type
5. **Booking status pie** — completed / cancelled / incomplete distribution

## Key Insights (from the full dataset run)

* Strong revenue generation with stable monthly trends
* Certain vehicle types dominate both volume and profitability
* A high cancellation rate materially impacts potential revenue
* Incomplete rides indicate operational inefficiencies

## Business Recommendations

1. **Reduce cancellations** — incentivize drivers for low cancellation rates; improve driver allocation
2. **Upsell premium vehicles** — target high-volume users with upgrade offers to raise revenue per ride
3. **Improve operational efficiency** — analyze root causes of incomplete rides; invest in fleet maintenance

## Future Improvements

* Interactive dashboard (Streamlit / Power BI)
* Customer segmentation analysis
* Predictive modeling (cancellation prediction)
* Real-time data pipeline integration

## Contributing

Issues and pull requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and guidelines. By participating, you agree to our [Code of Conduct](CODE_OF_CONDUCT.md). Security reports go to [SECURITY.md](SECURITY.md) — please don't open a public issue for them.

## License

MIT — see [LICENSE](LICENSE).

## Author

**Raghuraj Pratap Singh** — Data Analyst portfolio project.

⭐ If you like this project, give it a star and feel free to fork or contribute!
