import sqlite3

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

DB_FILE = "pharmeasy.db"
FLAG_THRESHOLD = 8  

MONTHS_IN_ORDER = ["2026-04", "2026-05", "2026-06"]
MONTH_LABELS = {"2026-04": "Apr 2026", "2026-05": "May 2026", "2026-06": "Jun 2026"}


BASE_COLOR ="#1F6FB2"
HIGHLIGHT_COLOR = "#E4572E"
BACKGROUND_COLOR = "#F5F7FA"
CARD_BORDER_COLOR = "#E1E6ED"
TEXT_DARK = "#1B2A41"
TEXT_MUTED = "#6B7684"




def format_inr_short(value):
    # turns something like 3265191.42 into ₹32.65L (lakh) or ₹1.29Cr (crore)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_00_00_000:
        return f"{sign}\u20b9{value / 1_00_00_000:.2f}Cr"
    if value >= 1_00_000:
        return f"{sign}\u20b9{value / 1_00_000:.2f}L"
    return f"{sign}\u20b9{value:,.2f}"


def format_inr_full(value):
    return f"\u20b9{value:,.2f}"


def format_count(value):
    return f"{value:,}"


def format_pct(value):
    return f"{value:+.2f}%"




def load_orders_and_regions():
    conn = sqlite3.connect(DB_FILE)
    orders = pd.read_sql("SELECT * FROM orders_clean", conn)
    regions = pd.read_sql("SELECT * FROM regions_master", conn)
    conn.close()

   
    orders["month"] = orders["order_date"].str.slice(0, 7)
    return orders, regions


def compute_percentage_change(current, previous):
    
    if previous == 0:
        return 0
    return (current - previous) / previous * 100


def get_kpis(orders):
    return {
        "total_orders": orders["order_id"].nunique(),  
        "total_sales": orders["sales_inr"].sum(),
        "total_profit": orders["profit_inr"].sum(),
    }


def get_flagged_changes(orders):
    monthly = orders.groupby(["region", "month"])["sales_inr"].sum().unstack(fill_value=0)
    flagged_rows = []

    for i in range(1, len(MONTHS_IN_ORDER)):
        prev_month = MONTHS_IN_ORDER[i - 1]
        cur_month = MONTHS_IN_ORDER[i]
        transition_label = f"{MONTH_LABELS[prev_month]} -> {MONTH_LABELS[cur_month]}"

        for region in monthly.index:
            previous = monthly.loc[region, prev_month]
            current = monthly.loc[region, cur_month]
            change = compute_percentage_change(current, previous)

            if abs(change) > FLAG_THRESHOLD:
                flagged_rows.append({
                    "region": region,
                    "transition": transition_label,
                    "previous_sales": previous,
                    "current_sales": current,
                    "pct_change": change,
                })

    return flagged_rows


def get_flagged_region_set(flagged_changes):
    return {row["region"] for row in flagged_changes}


def get_category_sales(orders):
    return orders.groupby("category")["sales_inr"].sum().sort_values(ascending=False)


def get_region_sales_with_zero_regions(orders, regions):
    region_totals = orders.groupby("region").agg(
        total_sales=("sales_inr", "sum"),
        total_orders=("order_id", "nunique"),
    ).reset_index()

    merged = regions[["region"]].merge(region_totals, on="region", how="left")
    merged["total_sales"] = merged["total_sales"].fillna(0)
    merged["total_orders"] = merged["total_orders"].fillna(0).astype(int)
    return merged.sort_values("total_sales", ascending=False)


def get_region_month_detail(orders, selected_region):
    detail = orders.groupby(["region", "month"]).agg(
        total_sales_inr=("sales_inr", "sum"),
        total_profit_inr=("profit_inr", "sum"),
        order_count=("order_id", "nunique"),
    ).reset_index()
    detail["month"] = detail["month"].map(MONTH_LABELS)

    if selected_region != "All Regions":
        detail = detail[detail["region"] == selected_region]

    return detail.sort_values(["region", "month"])



def setup_page():
    st.set_page_config(page_title="PharmEasy Regional Pulse", layout="wide")

    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {BACKGROUND_COLOR}; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .dashboard-card {{
            background-color: #FFFFFF;
            border: 1px solid {CARD_BORDER_COLOR};
            border-radius: 10px;
            padding: 20px 22px;
            box-shadow: 0 1px 4px rgba(20, 30, 50, 0.05);
            margin-bottom: 18px;
        }}
        .kpi-title {{ font-size: 14px; font-weight: 500; color: {TEXT_MUTED}; margin-bottom: 6px; }}
        .kpi-value {{ font-size: 30px; font-weight: 700; color: {TEXT_DARK}; line-height: 1.1; }}
        .kpi-caption {{ font-size: 12px; color: {TEXT_MUTED}; margin-top: 6px; }}
        .section-title {{ font-size: 18px; font-weight: 600; color: {TEXT_DARK}; margin-bottom: 4px; }}
        .insight-card {{
            background-color: #FFFFFF;
            border: 1px solid {CARD_BORDER_COLOR};
            border-left: 5px solid {BASE_COLOR};
            border-radius: 10px;
            padding: 20px 22px;
            margin-top: 10px;
            margin-bottom: 10px;
            color: {TEXT_DARK};
            font-size: 15px;
            line-height: 1.6;
        }}
        .app-title {{ font-size: 30px; font-weight: 700; color: {TEXT_DARK}; margin-bottom: 0px; }}
        .app-subtitle {{ font-size: 15px; color: {TEXT_MUTED}; margin-top: 2px; margin-bottom: 18px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown('<div class="app-title">PharmEasy Regional Pulse</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Regional Sales Intelligence — April to June 2026</div>',
        unsafe_allow_html=True,
    )




def render_kpi_card(title, value, caption=""):
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_section(orders):
    kpis = get_kpis(orders)
    active_region_count = orders["region"].nunique()  

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Orders", format_count(kpis["total_orders"]), "Distinct orders, Apr-Jun 2026")
    with col2:
        render_kpi_card("Total Sales", format_inr_short(kpis["total_sales"]), format_inr_full(kpis["total_sales"]))
    with col3:
        render_kpi_card("Total Profit", format_inr_short(kpis["total_profit"]), format_inr_full(kpis["total_profit"]))
    with col4:
        render_kpi_card("Active Regions", format_count(active_region_count), "Regions with at least one order")


def render_executive_summary(orders, flagged_changes):
    kpis = get_kpis(orders)
    top_category = get_category_sales(orders).idxmax()
    flagged_region_count = len(get_flagged_region_set(flagged_changes))

    st.markdown(
        f"""
        <div class="insight-card">
        Between April and June 2026, tracked regions generated
        <b>{format_inr_short(kpis['total_sales'])}</b> in sales and
        <b>{format_inr_short(kpis['total_profit'])}</b> in profit across
        <b>{format_count(kpis['total_orders'])}</b> distinct orders.
        Sales moved unevenly month to month, with <b>{flagged_region_count} of 9</b>
        active regions crossing the 8% Month-on-Month alert threshold in at least
        one transition. <b>{top_category}</b> is the leading category by sales.
        Guntur's April-to-May swing is the largest single move in the data and is
        flagged for review below, not treated as a confirmed trend. Use the
        region filter to explore any region's monthly detail.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_region_filter(orders):
    region_options = ["All Regions"] + sorted(orders["region"].unique())
    return st.selectbox("Region", region_options)




def render_trend_chart(orders, selected_region, flagged_region_set):
    monthly = orders.groupby(["region", "month"])["sales_inr"].sum().reset_index()
    monthly["month_label"] = monthly["month"].map(MONTH_LABELS)

    if selected_region != "All Regions":
        regions_to_plot = [selected_region]
    else:
        regions_to_plot = sorted(monthly["region"].unique())

    fig = go.Figure()
    for region in regions_to_plot:
        region_data = monthly[monthly["region"] == region].sort_values("month")
        is_flagged = region in flagged_region_set

        
        fig.add_trace(go.Scatter(
            x=region_data["month_label"],
            y=region_data["sales_inr"],
            mode="lines+markers",
            name=region,
            line=dict(
                color=HIGHLIGHT_COLOR if is_flagged else BASE_COLOR,
                width=3 if is_flagged else 1.5,
            ),
            text=[format_inr_full(v) for v in region_data["sales_inr"]],
            hovertemplate="%{x}<br>Sales: %{text}<extra></extra>",
        ))

    fig.update_layout(
        title="Monthly Sales Trend",
        xaxis_title="Month",
        yaxis_title="Sales (INR)",
        yaxis=dict(rangemode="tozero"),
        showlegend=(selected_region == "All Regions"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(t=50, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_sales_by_region_chart(orders, regions, selected_region, flagged_region_set):
    region_totals = get_region_sales_with_zero_regions(orders, regions)

    bar_colors = []
    for r in region_totals["region"]:
        if r in flagged_region_set or r == selected_region:
            bar_colors.append(HIGHLIGHT_COLOR)
        else:
            bar_colors.append(BASE_COLOR)

    fig = go.Figure(go.Bar(
        x=region_totals["region"],
        y=region_totals["total_sales"],
        marker_color=bar_colors,
        text=[format_inr_full(v) for v in region_totals["total_sales"]],
        hovertemplate="%{x}<br>Sales: %{text}<extra></extra>",
    ))
    fig.update_layout(
        title="Sales by Region",
        xaxis_title="Region",
        yaxis_title="Sales (INR)",
        yaxis=dict(rangemode="tozero"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(t=50, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_category_donut(filtered_orders):
    category_sales = get_category_sales(filtered_orders).reset_index()
    category_sales.columns = ["category", "sales_inr"]

    fig = px.pie(
        category_sales,
        names="category",
        values="sales_inr",
        hole=0.45,
        title="Sales by Category",
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", margin=dict(t=50, b=30))
    st.plotly_chart(fig, use_container_width=True)


def render_order_volume_chart(orders, regions, selected_region):
    region_totals = get_region_sales_with_zero_regions(orders, regions)
    bar_colors = [HIGHLIGHT_COLOR if r == selected_region else BASE_COLOR for r in region_totals["region"]]

    fig = go.Figure(go.Bar(
        x=region_totals["region"],
        y=region_totals["total_orders"],
        marker_color=bar_colors,
    ))
    fig.update_layout(
        title="Regional Performance — Order Volume",
        xaxis_title="Region",
        yaxis_title="Number of Orders",
        yaxis=dict(rangemode="tozero"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(t=50, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)



def render_flagged_table(flagged_changes):
    if not flagged_changes:
        st.info("No regions crossed the alert threshold this period.")
        return

    table_rows = []
    for row in flagged_changes:
        table_rows.append({
            "Region": row["region"],
            "Transition": row["transition"],
            "Previous Sales": format_inr_full(row["previous_sales"]),
            "Current Sales": format_inr_full(row["current_sales"]),
            "Month-on-Month Change": format_pct(row["pct_change"]),
        })

    st.dataframe(table_rows, use_container_width=True, hide_index=True)


def render_detail_table(orders, selected_region):
    detail = get_region_month_detail(orders, selected_region)
    detail = detail.rename(columns={
        "region": "Region",
        "month": "Month",
        "total_sales_inr": "Total Sales (INR)",
        "total_profit_inr": "Total Profit (INR)",
        "order_count": "Orders",
    })
    detail["Total Sales (INR)"] = detail["Total Sales (INR)"].apply(format_inr_full)
    detail["Total Profit (INR)"] = detail["Total Profit (INR)"].apply(format_inr_full)
    st.dataframe(detail, use_container_width=True, hide_index=True)


def render_executive_insight():
    st.markdown(
        """
        <div class="insight-card">
        <b>Executive Insight — Guntur Region</b><br><br>
        Guntur sales increased from &#8377;62,442.27 in April to
        &#8377;138,738.93 in May, a +122.19% Month-on-Month increase — the
        largest single move in this dataset and well past the 8% alert
        threshold. In June, Guntur sales declined to &#8377;99,745.18, a
        -28.11% change from May. Because the following month reversed
        direction, May is treated as an <b>unconfirmed spike</b>, not a
        confirmed demand trend. No external cause is claimed here; the data
        does not contain the information needed to explain why the swing
        occurred.
        </div>
        """,
        unsafe_allow_html=True,
    )



def main():
    setup_page()
    render_header()

    orders, regions = load_orders_and_regions()
    flagged_changes = get_flagged_changes(orders)
    flagged_region_set = get_flagged_region_set(flagged_changes)

    render_executive_summary(orders, flagged_changes)

    st.markdown('<div class="section-title">Executive Overview</div>', unsafe_allow_html=True)
    render_kpi_section(orders)

    selected_region = render_region_filter(orders)
    if selected_region == "All Regions":
        filtered_orders = orders
    else:
        filtered_orders = orders[orders["region"] == selected_region]

    st.markdown('<div class="section-title">Regional Performance</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        render_trend_chart(orders, selected_region, flagged_region_set)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        render_sales_by_region_chart(orders, regions, selected_region, flagged_region_set)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Business Detail</div>', unsafe_allow_html=True)
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        render_category_donut(filtered_orders)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_d:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        render_order_volume_chart(orders, regions, selected_region)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Regional Attention — Significant Changes</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    render_flagged_table(flagged_changes)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Selected Region Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    render_detail_table(orders, selected_region)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Executive Insight</div>', unsafe_allow_html=True)
    render_executive_insight()


if __name__ == "__main__":
    main()