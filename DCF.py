import streamlit as st
import pandas as pd

st.title("Intrinsic Value Calculator")

# — Metric selection and input —
metric = st.selectbox(
    "Metric to use",
    ["EPS", "FCF per share"],
    help="Select which per-share metric you want to project and value."
)
metric_value = st.number_input(
    f"Current {metric}",
    value=2.50,
    format="%.2f",
    help=f"Enter the current {metric} per share."
)

# — Growth & discount inputs —
cagr_pct = st.number_input(
    "CAGR (%)",
    value=5.00,
    format="%.2f",
    help="Expected annual growth rate (in percent) for your projection horizon."
)
dr_pct = st.number_input(
    "Discount Rate (%)",
    value=10.00,
    format="%.2f",
    help="Annual discount rate (in percent) used to bring future value back to today."
)
years = st.number_input(
    "Horizon (years)",
    value=5,
    min_value=1,
    step=1,
    help="Number of years to project growth."
)

# — Price and multiples —
share_price = st.number_input(
    "Current Share Price",
    value=72.00,
    format="%.2f",
    help="The stock’s current market price per share, used to calculate upside."
)
mult_str = st.text_input(
    "Average P/E Multiples (comma-separated)",
    value="5,10,15,20,25,30,35,40,45,50",
    help="List the average P/E multiples observed over your projection period, separated by commas."
)

if st.button("Calculate"):
    try:
        # parse and convert
        cagr      = cagr_pct / 100
        dr        = dr_pct   / 100
        multiples = [int(m.strip()) for m in mult_str.split(",") if m.strip()]

        # project and discount the chosen metric
        future_value = metric_value * (1 + cagr) ** years
        pv_value     = future_value / (1 + dr) ** years

        # assemble results
        data = {
            "P/E Multiple":      [],
            f"Value per Share ({metric})": [],
            "Upside (%)":        []
        }
        for m in multiples:
            implied = pv_value * m
            upside  = (implied / share_price - 1) * 100
            data["P/E Multiple"].append(m)
            data[f"Value per Share ({metric})"].append(implied)
            data["Upside (%)"].append(upside)

        df = pd.DataFrame(data).set_index("P/E Multiple")
        df[f"Value per Share ({metric})"] = df[f"Value per Share ({metric})"].map("${:,.2f}".format)
        df["Upside (%)"]                  = df["Upside (%)"].map("{:+.1f}%".format)

        st.subheader("Implied Values vs. Current Price")
        st.table(df)

    except Exception as e:
        st.error(f"Input error: {e}")
