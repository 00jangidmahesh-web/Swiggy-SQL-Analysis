# Swiggy Data Analysis – SQL + Streamlit Dashboard

So I built this little project to analyze food delivery data (inspired by Swiggy).  
It's a mix of SQL for digging into the numbers and a Streamlit dashboard to actually see what's going on.

 **Live demo here:** [Streamlit App](https://swiggy-sql-analysis-h2gpcpa4k67hayrzsfn9dp.streamlit.app/) (go click around)

---

##  Project Structure

```
Swiggy-SQL-Analysis/
├── datasets/          (CSV files)
├── DashBoard/
│   └── app.py
├── sql queries/
│   ├── schema.sql
│   └── queries.sql
├── requirements.txt
└── README.md

---

## Database Schema

```
users ──────────┐
                ↓
            orders ──── delivery_partner
                ↓
          order_details
                ↓
             food ←──── menu ←──── restaurants
```


| Table | Description |
|---|---|
| `users` | Customer profiles |
| `restaurants` | Restaurant master data |
| `food` | Food item catalogue (Veg / Non-Veg) |
| `menu` | Restaurant ↔ Food mapping with prices |
| `orders` | Order transactions with amounts & ratings |
| `order_details` | Line items per order |
| `delivery_partner` | Delivery agent profiles |

---

##  Dashboard Sections

| Section | What it shows |
|---|---|
| **KPI Metrics** | Total orders, revenue, avg order value, delivery time, rating |
| **Restaurant Performance** | Revenue, order share, ratings per restaurant |
| **Revenue Trends** | Monthly revenue line chart + MoM growth % |
| **Customer Insights** | RFM segmentation (High / Medium / Low Value), inactive users |
| **Food & Menu** | Top ordered dishes, avg price, Veg vs Non-Veg split |
| **Delivery Partners** | Avg delivery time, avg delivery rating per partner |
| **Raw Data Explorer** | Tabs for Orders, Restaurants, Menu, Users + CSV download |

---

##  SQL Queries Covered (`queries.sql`)

1. Customers who never ordered
2. Average price per dish
3. Top restaurant by month
4. Restaurants with sales > ₹500
5. Orders in a specific date range per customer
6. Restaurant with maximum repeat customers
7. Month-over-Month (MoM) revenue growth
8. Customer's favourite food (ranked)
9. RFM Analysis (Recency, Frequency, Monetary)
10. Top dishes by revenue (corrected to "Most ordered dishes")
11. Customer segmentation (High / Medium / Low Value)
12. Cohort Analysis (retention)
13. Delivery partner performance
14. Peak order time analysis (removed – not applicable to schema)

---

##  Tech Stack

| Layer | Tool |
|---|---|
| Data Storage | CSV (can be swapped with PostgreSQL/MySQL) |
| SQL Analysis | PostgreSQL / MySQL |
| Dashboard | Streamlit |
| Charts | Plotly Express |
| Language | Python 3.x |

---

##  Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/Swiggy-SQL-Analysis.git
cd Swiggy-SQL-Analysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the dashboard
```bash
streamlit run dashBoard/app.py
```

Open your browser at `http://localhost:8501`

---

##  Deploy on Streamlit Cloud

1. Push this repo to GitHub (must be **public**)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Fill in:
   - **Repository:** `00jangidmahesh-web/Swiggy-SQL-Analysis`
   - **Branch:** `main`
   - **Main file path:** `dashBoard/app.py`
4. Click **Deploy!**

---

##  requirements.txt

```
streamlit
pandas
plotly
```

---

##  Key Insights from the Dataset

- **KFC** has the highest average delivery time among partners.
- **Dominos** generates the highest revenue overall.
- Majority of orders are **Non-Veg** items like Chicken Wings.
- **Khushboo** is the highest-spending customer (High Value segment).
- MoM revenue shows a consistent upward trend from May → July 2022.

---

## Author

**Mahesh Kumar Jangid**  
 [00jangidmahesh@gmail.com]  
 [LinkedIn](www.linkedin.com/in/mahesh-kumar-jangid-22b375306)  
 [GitHub](https://github.com/00jangidmahesh-web)

---
