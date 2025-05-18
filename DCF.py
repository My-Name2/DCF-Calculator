import streamlit as st
import pandas as pd

# — Guide / Instructions —
st.sidebar.header("📘 How to use & DCF Best Practices")
st.sidebar.markdown("""
**1. Metric to use**  
• Choose between **EPS** (Earnings Per Share) or **FCF per share** (Free Cash Flow per share).

**2. Current Metric (TTM)**  
• Enter the trailing-12-month EPS or FCF per share for a stable baseline.

**3. CAGR (%)**  
• Expected annual growth rate for your chosen metric over the projection horizon.

**4. Discount Rate (%)**  
• Use your WACC or a risk-adjusted rate to discount future cash flows.

**5. Horizon (years)**  
• Typical range is 5–10 years; adjust based on business maturity.

**6. Current Share Price**  
• Today’s market price, used to calculate implied upside.

**7. Average P/E Multiples**  
• Historical or peer-group average P/Es, comma-separated.

**8. Terminal Value (optional)**  
• Toggle on to include a perpetuity value at horizon:  
  – **Terminal Growth Rate**: long-term growth < discount rate.  
  – Uses **TV = (Metricₙ × (1 + g)) / (r – g)**, discounted back as a lump sum.

**DCF Best Practices**  
- Use TTM figures to smooth seasonality.  
- Run sensitivity on growth, discount, and multiples.  
- Cross-check implied values against peers.  
""")

st.title("Intrinsic Value + Terminal Value Calculator")

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
    help="Expected annual growth rate for your projection horizon."
)
dr_pct = st.number_input(
    "Discount Rate (%)",
    value=10.00,
    format="%.2f",
    help="Annual rate to discount future value back to present."
)
years = st.number_input(
    "Horizon (years)",
    value=5,
    min_value=1,
    step=1,
    help="Years to project growth."
)

# — Terminal value toggle & input —
include_tv = st.checkbox(
    "Include Terminal Value?",
    value=False,
    help="Toggle to add a perpetuity value at the end of your horizon."
)
if include_tv:
    term_growth_pct = st.number_input(
        "Terminal Growth Rate (%)",
        value=2.00,
        format="%.2f",
        help="Long-term perpetual growth rate (must be < discount rate)."
    )

# — Price and multiples —
share_price = st.number_input(
    "Current Share Price",
    value=72.00,
    format="%.2f",
    help="Today’s market price per share."
)
mult_str = st.text_input(
    "Average P/E Multiples (comma-separated)",
    value="5,10,15,20,25,30,35,40,45,50",
    help="Historical or peer P/E ratios to test."
)

if st.button("Calculate"):
    try:
        # parse inputs
        cagr      = cagr_pct / 100
        dr        = dr_pct   / 100
        multiples = [int(m.strip()) for m in mult_str.split(",") if m.strip()]

        # project metric to horizon and discount
        future_metric = metric_value * (1 + cagr) ** years
        pv_metric     = future_metric / (1 + dr) ** years

        # compute terminal value if requested
        if include_tv:
            g = term_growth_pct / 100
            if g >= dr:
                st.error("Terminal growth must be less than discount rate.")
                st.stop()
            tv     = future_metric * (1 + g) / (dr - g)
            pv_tv  = tv / (1 + dr) ** years
            pv_base = pv_metric
            pv_total = pv_base + pv_tv
            st.write(f"**PV of Horizon Metric**: ${pv_base:,.2f}  ")
            st.write(f"**PV of Terminal Value**: ${pv_tv:,.2f}  ")
            st.write(f"**Combined PV Factor**:  ${pv_total:,.2f}  ")
            pv_factor = pv_total
        else:
            pv_factor = pv_metric

        # build results table
        data = {
            "P/E Multiple":      [],
            f"Value per Share ({metric})": [],
            "Upside (%)":        []
        }
        for m in multiples:
            implied = pv_factor * m
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
