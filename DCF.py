import streamlit as st
import pandas as pd

# — Guide / Instructions —
st.sidebar.header("📘 How to use & DCF Best Practices")
st.sidebar.markdown("""
**1. Metric to use**  
• Choose between **EPS** (Earnings Per Share) or **FCF per share** (Free Cash Flow per share).

**2. Current Metric**  
• Enter today’s TTM (trailing twelve months) EPS or FCF per share rather than a single quarterly value for stability.

**3. CAGR (%)**  
• Expected annual growth rate for your chosen metric over the projection horizon.  
• Base this on historical performance, analyst forecasts, or industry outlook.

**4. Discount Rate (%)**  
• Use your company’s WACC or a risk-adjusted rate to discount future cash flows.

**5. Horizon (years)**  
• 5 years is common, but longer horizons (7–10 years) can capture mature cash flows for stable businesses.

**6. Current Share Price**  
• The stock’s market price today, used to calculate implied upside scenarios.

**7. Average P/E Multiples**  
• Use historical average P/E or peer multiples. Test a range to see sensitivity.

**DCF Best Practices**  
- **Use TTM figures**: smooths out seasonality and one-offs.  
- **Conservatism**: err on the side of cautious growth and higher discount rates.  
- **Sensitivity Analysis**: vary growth, discount rate, and multiples to understand valuation drivers.  
- **Terminal Value**: if extending beyond your horizon, model a conservative long-term growth rate.  
- **Reconcile with comparables**: cross-check implied values against peer valuations.
""")

st.title("Intrinsic Value Calculator")

# — Metric selection and input —
metric = st.selectbox(
    "Metric to use",
    ["EPS", "FCF per share"],
    help="Choose which per-share figure you want to project and value."
)
metric_value = st.number_input(
    f"Current {metric} (TTM)",
    value=2.50,
    format="%.2f",
    help=f"Enter the trailing-12-month {metric} per share."
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
    help="List the P/E ratios (e.g., historical averages or peer multiples) you want to test, separated by commas."
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
