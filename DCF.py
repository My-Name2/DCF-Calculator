import streamlit as st
import pandas as pd

st.title("Intrinsic Value Calculator")

# — Inputs —
eps       = st.number_input("Current EPS", value=2.50, format="%.2f")
cagr_pct  = st.number_input("5-Year CAGR (%)", value=5.00, format="%.2f")
dr_pct    = st.number_input("Discount Rate (%)", value=10.00, format="%.2f")
years     = st.number_input("Horizon (years)", value=5, min_value=1, step=1)
mult_str  = st.text_input(
    "P/E Multiples (comma-separated)",
    value="5,10,15,20,25,30,35,40,45,50"
)

if st.button("Calculate"):
    try:
        # parse inputs
        cagr     = cagr_pct / 100
        dr       = dr_pct   / 100
        multiples = [int(m.strip()) for m in mult_str.split(",") if m.strip()]

        # project and discount
        eps_fut = eps * (1 + cagr) ** years
        pv_eps  = eps_fut / (1 + dr) ** years

        # build results
        data = {"P/E Multiple": [], "Value per Share": []}
        for m in multiples:
            data["P/E Multiple"].append(m)
            data["Value per Share"].append(pv_eps * m)

        df = pd.DataFrame(data).set_index("P/E Multiple")
        df["Value per Share"] = df["Value per Share"].map("${:,.2f}".format)

        st.subheader("Implied Values")
        st.table(df)

    except Exception as e:
        st.error(f"Input error: {e}")
