import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Swiggy Analysis Dashboard",
    page_icon="🍔",
    layout="wide"
)

# ─────────────────────────────────────────────
# Custom Styling
# ─────────────────────────────────────────────
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #e6e9ef;
    }
    [data-testid="stMetricLabel"] { color: #555555 !important; }
    [data-testid="stMetricValue"] { color: #111111 !important; }

    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #fc5a03;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Load Data  (works locally AND on Streamlit Cloud)
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "datasets")

@st.cache_data
def load_data():
    orders       = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"),         parse_dates=["date"])
    users        = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
    restaurants  = pd.read_csv(os.path.join(DATA_DIR, "restaurants.csv"))
    food         = pd.read_csv(os.path.join(DATA_DIR, "food.csv"))
    menu         = pd.read_csv(os.path.join(DATA_DIR, "menu.csv"))
    order_details= pd.read_csv(os.path.join(DATA_DIR, "order_details.csv"))
    delivery     = pd.read_csv(os.path.join(DATA_DIR, "delivery_partner.csv"))
    return orders, users, restaurants, food, menu, order_details, delivery

orders, users, restaurants, food, menu, order_details, delivery = load_data()

# ─────────────────────────────────────────────
# Pre-process / Merge
# ─────────────────────────────────────────────
orders["month"]      = orders["date"].dt.to_period("M").astype(str)
orders["month_num"]  = orders["date"].dt.month
orders["month_name"] = orders["date"].dt.strftime("%b")

# Full orders enriched
orders_full = (
    orders
    .merge(users[["user_id", "name"]], on="user_id", how="left")
    .merge(restaurants, on="r_id", how="left")
    .merge(delivery, on="partner_id", how="left")
)

# Order items enriched
items_full = (
    order_details
    .merge(orders[["order_id", "user_id", "r_id", "date", "month"]], on="order_id", how="left")
    .merge(food, on="f_id", how="left")
    .merge(restaurants[["r_id", "r_name"]], on="r_id", how="left")
)

# ─────────────────────────────────────────────
# Sidebar Filters
# ─────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/en/1/12/Swiggy_logo.svg",
    width=160
)
st.sidebar.header("🔎 Filters")

all_restaurants = sorted(restaurants["r_name"].unique())
sel_rest = st.sidebar.multiselect(
    "Restaurant", all_restaurants, default=all_restaurants
)

all_months = sorted(orders["month"].unique())
sel_months = st.sidebar.multiselect(
    "Month", all_months, default=all_months
)

all_users = sorted(users["name"].unique())
sel_users = st.sidebar.multiselect(
    "Customer", all_users, default=all_users
)

# Apply filters
r_ids   = restaurants[restaurants["r_name"].isin(sel_rest)]["r_id"].tolist()
u_ids   = users[users["name"].isin(sel_users)]["user_id"].tolist()
f_orders = orders_full[
    orders_full["r_id"].isin(r_ids) &
    orders_full["month"].isin(sel_months) &
    orders_full["user_id"].isin(u_ids)
]

# ─────────────────────────────────────────────
# Title & Empty Data Handling
# ─────────────────────────────────────────────
st.title("🍔 Swiggy Data Analysis Dashboard")
st.markdown("**Real-time insights** from SQL-backed Swiggy dataset — orders, restaurants, customers & delivery partners.")
st.divider()

if f_orders.empty:
    st.warning("⚠️ No orders match the selected filters. Please adjust your restaurant, month, or customer selection.")
    st.stop()

# ─────────────────────────────────────────────
# Section 1 — KPI Metrics
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Key Metrics</p>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Total Orders", len(f_orders))
with k2:
    st.metric("Total Revenue (₹)", f"₹{f_orders['amount'].sum():,}")
with k3:
    avg_order = f_orders['amount'].mean()
    st.metric("Avg Order Value", f"₹{avg_order:.0f}" if not pd.isna(avg_order) else "—")
with k4:
    avg_del = f_orders['delivery_time'].mean()
    st.metric("Avg Delivery Time", f"{avg_del:.1f} min" if not pd.isna(avg_del) else "—")
with k5:
    avg_rat = f_orders['restaurant_rating'].mean()
    st.metric("Avg Restaurant Rating", f"{avg_rat:.2f} ⭐" if not pd.isna(avg_rat) else "—")

st.divider()

# ─────────────────────────────────────────────
# Section 2 — Revenue & Orders by Restaurant
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">🏪 Restaurant Performance</p>', unsafe_allow_html=True)

rest_grp = (
    f_orders.groupby("r_name")
    .agg(total_orders=("order_id","count"), total_revenue=("amount","sum"), avg_rating=("restaurant_rating","mean"))
    .reset_index()
    .sort_values("total_revenue", ascending=False)
)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Revenue by Restaurant")
    fig = px.bar(
        rest_grp, x="r_name", y="total_revenue",
        color="total_revenue", color_continuous_scale="Oranges",
        text_auto=True, labels={"r_name": "Restaurant", "total_revenue": "Revenue (₹)"}
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Order Share by Restaurant")
    fig2 = px.pie(
        rest_grp, values="total_orders", names="r_name",
        hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe
    )
    st.plotly_chart(fig2, use_container_width=True)

# Restaurant ratings bar
st.subheader("Average Restaurant Rating")
rest_grp_clean = rest_grp.dropna(subset=["avg_rating"])
if not rest_grp_clean.empty:
    fig_rat = px.bar(
        rest_grp_clean,
        x="r_name", y="avg_rating", color="avg_rating",
        color_continuous_scale="RdYlGn", range_color=[1,5],
        text=rest_grp_clean["avg_rating"].round(2),
        labels={"r_name": "Restaurant", "avg_rating": "Avg Rating"}
    )
    fig_rat.update_layout(coloraxis_showscale=False, yaxis_range=[0, 5])
    st.plotly_chart(fig_rat, use_container_width=True)
else:
    st.info("No restaurant rating data available for selected filters.")

st.divider()

# ─────────────────────────────────────────────
# Section 3 — Monthly Revenue Trend & MoM Growth
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">📈 Revenue Trends</p>', unsafe_allow_html=True)

# Ensure monthly data is sorted by date (convert month string to datetime for sorting)
monthly = (
    f_orders.groupby("month")
    .agg(revenue=("amount","sum"), orders=("order_id","count"))
    .reset_index()
)
# Convert month to datetime for correct chronological order
monthly["month_dt"] = pd.to_datetime(monthly["month"])
monthly = monthly.sort_values("month_dt").reset_index(drop=True)
monthly["prev_revenue"] = monthly["revenue"].shift(1)
monthly["mom_growth"]   = ((monthly["revenue"] - monthly["prev_revenue"]) / monthly["prev_revenue"] * 100).round(2)

c3, c4 = st.columns(2)
with c3:
    st.subheader("Monthly Revenue (₹)")
    fig_m = px.line(
        monthly, x="month", y="revenue",
        markers=True, text="revenue",
        labels={"month": "Month", "revenue": "Revenue (₹)"},
        color_discrete_sequence=["#fc5a03"]
    )
    fig_m.update_traces(textposition="top center")
    st.plotly_chart(fig_m, use_container_width=True)

with c4:
    st.subheader("Month-over-Month Growth (%)")
    mom = monthly.dropna(subset=["mom_growth"])
    if not mom.empty:
        fig_mom = px.bar(
            mom, x="month", y="mom_growth",
            color="mom_growth", color_continuous_scale="RdYlGn",
            text=mom["mom_growth"].apply(lambda x: f"{x:+.1f}%"),
            labels={"month": "Month", "mom_growth": "MoM Growth (%)"}
        )
        fig_mom.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_mom, use_container_width=True)
    else:
        st.info("Not enough data to calculate month‑over‑month growth.")

st.divider()

# ─────────────────────────────────────────────
# Section 4 — Customer Analysis
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">👤 Customer Insights</p>', unsafe_allow_html=True)

# Inactive customers
active_users = f_orders["user_id"].unique()
inactive = users[~users["user_id"].isin(active_users)][["name","email"]]

# RFM
rfm = (
    f_orders.groupby(["user_id","name"])
    .agg(
        last_order=("date","max"),
        frequency=("order_id","count"),
        monetary=("amount","sum")
    )
    .reset_index()
)
rfm["segment"] = rfm["monetary"].apply(
    lambda x: "🥇 High Value" if x > 1000 else ("🥈 Medium Value" if x > 500 else "🥉 Low Value")
)

c5, c6 = st.columns(2)
with c5:
    st.subheader("Customer Spend (₹)")
    fig_cust = px.bar(
        rfm.sort_values("monetary", ascending=False),
        x="name", y="monetary", color="segment",
        text_auto=True,
        labels={"name":"Customer","monetary":"Total Spend (₹)"},
        color_discrete_map={
            "🥇 High Value": "#2ecc71",
            "🥈 Medium Value": "#f39c12",
            "🥉 Low Value": "#e74c3c"
        }
    )
    st.plotly_chart(fig_cust, use_container_width=True)

with c6:
    st.subheader("Customer Segmentation (RFM)")
    seg_count = rfm["segment"].value_counts().reset_index()
    seg_count.columns = ["segment","count"]
    fig_seg = px.pie(
        seg_count, values="count", names="segment",
        hole=0.4,
        color_discrete_map={
            "🥇 High Value": "#2ecc71",
            "🥈 Medium Value": "#f39c12",
            "🥉 Low Value": "#e74c3c"
        }
    )
    st.plotly_chart(fig_seg, use_container_width=True)

# RFM Table
st.subheader("RFM Detail Table")
st.dataframe(
    rfm[["name","last_order","frequency","monetary","segment"]]
    .rename(columns={"name":"Customer","last_order":"Last Order","frequency":"Orders","monetary":"Total Spend (₹)","segment":"Segment"})
    .sort_values("Total Spend (₹)", ascending=False),
    use_container_width=True, hide_index=True
)

# Inactive customers
if len(inactive) > 0:
    st.subheader("🚨 Customers Who Never Ordered (Inactive)")
    st.dataframe(inactive.rename(columns={"name":"Name","email":"Email"}), use_container_width=True, hide_index=True)
else:
    st.success("✅ All customers have placed at least one order!")

st.divider()

# ─────────────────────────────────────────────
# Section 5 — Food & Menu Analysis
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">🍕 Food & Menu Insights</p>', unsafe_allow_html=True)

# Top ordered dishes
top_dishes = (
    items_full.groupby(["f_name","type"])
    .agg(order_count=("order_id","count"))
    .reset_index()
    .sort_values("order_count", ascending=False)
)

# Average price per dish
avg_price = (
    menu.merge(food, on="f_id")
    .groupby("f_name")["price"]
    .mean()
    .reset_index()
    .rename(columns={"price":"avg_price"})
    .sort_values("avg_price", ascending=False)
)

c7, c8 = st.columns(2)
with c7:
    st.subheader("Top Ordered Dishes")
    fig_dish = px.bar(
        top_dishes, x="order_count", y="f_name",
        orientation="h", color="type",
        color_discrete_map={"Veg":"#27ae60","Non-veg":"#e74c3c"},
        text_auto=True,
        labels={"f_name":"Dish","order_count":"Times Ordered","type":"Type"}
    )
    fig_dish.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_dish, use_container_width=True)

with c8:
    st.subheader("Average Price per Dish (₹)")
    fig_price = px.bar(
        avg_price, x="avg_price", y="f_name",
        orientation="h", color="avg_price",
        color_continuous_scale="Blues", text_auto=True,
        labels={"f_name":"Dish","avg_price":"Avg Price (₹)"}
    )
    fig_price.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_price, use_container_width=True)

# Veg vs Non-Veg split
veg_split = top_dishes.groupby("type")["order_count"].sum().reset_index()
st.subheader("Veg 🥦 vs Non-Veg 🍗 Order Split")
fig_veg = px.pie(
    veg_split, values="order_count", names="type",
    color="type", hole=0.4,
    color_discrete_map={"Veg":"#27ae60","Non-veg":"#e74c3c"}
)
st.plotly_chart(fig_veg, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# Section 6 — Delivery Partner Performance
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">🚴 Delivery Partner Performance</p>', unsafe_allow_html=True)

dp_perf = (
    f_orders.groupby("partner_name")
    .agg(
        total_deliveries=("order_id","count"),
        avg_delivery_time=("delivery_time","mean"),
        avg_delivery_rating=("delivery_rating","mean")
    )
    .reset_index()
    .round(2)
)

if not dp_perf.empty:
    c9, c10 = st.columns(2)
    with c9:
        st.subheader("Avg Delivery Time (min)")
        fig_dp1 = px.bar(
            dp_perf.sort_values("avg_delivery_time"),
            x="partner_name", y="avg_delivery_time",
            color="avg_delivery_time", color_continuous_scale="RdYlGn_r",
            text_auto=True,
            labels={"partner_name":"Partner","avg_delivery_time":"Avg Time (min)"}
        )
        fig_dp1.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_dp1, use_container_width=True)

    with c10:
        st.subheader("Avg Delivery Rating ⭐")
        fig_dp2 = px.bar(
            dp_perf.sort_values("avg_delivery_rating", ascending=False),
            x="partner_name", y="avg_delivery_rating",
            color="avg_delivery_rating", color_continuous_scale="RdYlGn",
            text_auto=True,
            range_y=[0, 5],  # Fixed y-axis range for ratings
            labels={"partner_name":"Partner","avg_delivery_rating":"Avg Rating"}
        )
        fig_dp2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_dp2, use_container_width=True)

    st.subheader("Delivery Partner Summary Table")
    st.dataframe(
        dp_perf.rename(columns={
            "partner_name":"Partner",
            "total_deliveries":"Total Deliveries",
            "avg_delivery_time":"Avg Delivery Time (min)",
            "avg_delivery_rating":"Avg Delivery Rating"
        }),
        use_container_width=True, hide_index=True
    )
else:
    st.info("No delivery partner data available for selected filters.")

st.divider()

# ─────────────────────────────────────────────
# Section 7 — Raw Data & Download
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">🗃️ Raw Data Explorer</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Orders", "Restaurants", "Menu", "Users"])

with tab1:
    st.dataframe(
        f_orders[["order_id","name","r_name","amount","date","partner_name","delivery_time","delivery_rating","restaurant_rating"]]
        .rename(columns={"name":"Customer","r_name":"Restaurant","partner_name":"Delivery Partner"}),
        use_container_width=True, hide_index=True
    )

with tab2:
    st.dataframe(restaurants, use_container_width=True, hide_index=True)

with tab3:
    menu_view = menu.merge(food, on="f_id").merge(restaurants[["r_id","r_name"]], on="r_id")
    st.dataframe(
        menu_view[["r_name","f_name","type","price"]].rename(columns={"r_name":"Restaurant","f_name":"Dish","type":"Type","price":"Price (₹)"}),
        use_container_width=True, hide_index=True
    )

with tab4:
    st.dataframe(users[["user_id","name","email"]], use_container_width=True, hide_index=True)

# Download
st.subheader("⬇️ Download Filtered Orders")
csv_data = f_orders.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download as CSV",
    data=csv_data,
    file_name="swiggy_filtered_orders.csv",
    mime="text/csv"
)

st.success("Dashboard loaded successfully! 🚀")