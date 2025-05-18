import streamlit as st
import pandas as pd

# — Guide / Instructions —
st.sidebar.header("📘 How to use")
st.sidebar.markdown("""
1. **Metric to use** – Choose between **EPS** (Earnings Per Share) or **FCF per share** (Free Cash Flow per share).
2. **Current Metric** – Enter today’s EPS or FCF/share value.
3. **CAGR (%)** – Expected annual growth rate for that metric, over your chosen horizon.
4. **Discount Rate (%)** – Annual rate used to discount future value back to the present.
5. **Horizon (years)** – Number of years to project growth.
6. **Current Share Price** – The stock’s market price today, for upside calculation.
7. **Average P/E Multiples** – Comma-separated list of P/E ratios (e.g., historical averages) you want to test.
8. Click **Calculate** – See implied per-share values at each multiple, plus % upside vs. today’s price.
""")

st.title("Intrinsic Value Calculator")

# — Metric selection and input —
metric = st.selectbox(
    "Metric to use",
    ["EPS", "FCF per share"],
    help="Choose which per-share figure you want to project and value."
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
    help="Annual rate used to discount future value back to today."
)
years = st.number_input(
    "Horizon (years)",
    value=5,
    min_value=1,
    step=1,
    help="Number of years over which to project growth."
)

# — Price and multiples —
share_price = st.number_input(
    "Current Share Price",
    value=72.00,
    format="%.2f",
    help="Stock’s current market price per share, for calculating upside."
)
mult_str = st.text_input(
    "Average P/E Multiples (comma-separated)",
    value="5,10,15,20,25,30,35,40,45,50",
    help="List the P/E ratios (e.g., historical averages) you want to test, separated by commas."
)

if st.button("Calculate"):
    try:
        # parse inputs
        cagr = cagr_pct / 100
        dr   = dr_pct   / 100
        multiples = [int(m.strip()) for m in mult_str.split(",") if m.strip()]

        # project & discount
        fv = metric_value * (1 + cagr) ** years
        pv = fv / (1 + dr) ** years

        # build results
        data = {
            "P/E Multiple":      [],
            f"Value per Share ({metric})": [],
            "Upside (%)":        []
        }
        for m in multiples:
            implied = pv * m
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

