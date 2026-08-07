"""
AI Relationship Manager
Streamlit Dashboard
"""

import requests
import streamlit as st
import plotly.graph_objects as go

# ==========================================
# Page Config
# ==========================================

st.set_page_config(
    page_title="AI Relationship Manager",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000/predict"

# ==========================================
# Color Theme
# ==========================================

COLORS = {
    "primary": "#2563EB",
    "danger": "#DC2626",
    "warning": "#F59E0B",
    "success": "#16A34A",
    "background": "#F8FAFC",
    "text": "#1E293B",
    "muted": "#64748B",
}

RISK_COLORS = {
    "Very Low": COLORS["success"],
    "Low": COLORS["success"],
    "Medium": COLORS["warning"],
    "High": COLORS["danger"],
    "Very High": COLORS["danger"],
}

# ==========================================
# Custom CSS
# ==========================================

st.markdown(f"""
<style>
    .stApp {{
        background-color: {COLORS['background']};
    }}

    .main-title {{
        font-size: 2.1rem;
        font-weight: 700;
        color: {COLORS['text']};
        margin-bottom: 0rem;
    }}

    .subtitle {{
        color: {COLORS['muted']};
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }}

    .card {{
        background-color: white;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }}

    .badge {{
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
        color: white;
    }}

    .section-header {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {COLORS['text']};
        margin-top: 0.5rem;
        margin-bottom: 0.8rem;
    }}

    .driver-item, .rec-item {{
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        background-color: #F1F5F9;
        margin-bottom: 0.4rem;
        font-size: 0.95rem;
    }}

    .exec-summary-card {{
        background: linear-gradient(135deg, #1E293B, #0F172A);
        color: white;
        border-radius: 16px;
        padding: 2rem;
    }}

    .exec-summary-card h3 {{
        color: white;
        margin-top: 0;
    }}

    .exec-summary-text {{
        font-size: 1.05rem;
        line-height: 1.6;
        opacity: 0.92;
    }}
</style>
""", unsafe_allow_html=True)


# ==========================================
# Session State
# ==========================================

if "result" not in st.session_state:
    st.session_state.result = None

if "error" not in st.session_state:
    st.session_state.error = None


# ==========================================
# Sidebar — Customer Details Form
# ==========================================

with st.sidebar:
    st.markdown("## 📡 AI Relationship Manager")
    st.markdown("Enter customer details to predict churn risk.")
    st.markdown("---")
    st.markdown("### Customer Details")

    with st.form("customer_form"):
        customer_id = st.text_input("Customer ID", value="CUST-1001")

        gender = st.selectbox("Gender", ["Male", "Female"])
        senior_citizen = st.selectbox("Senior Citizen", ["Yes", "No"])
        partner = st.selectbox("Partner", ["Yes", "No"])
        dependents = st.selectbox("Dependents", ["Yes", "No"])
        tenure_months = st.slider("Tenure (months)", 0, 72, 12)

        phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
        online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
        device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
        tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])

        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
        payment_method = st.selectbox(
            "Payment Method",
            ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
        )

        monthly_charges = st.number_input("Monthly Charges (₹)", min_value=0.0, value=700.0, step=10.0)
        total_charges = st.number_input("Total Charges (₹)", min_value=0.0, value=8400.0, step=50.0)

        submitted = st.form_submit_button("🔮 Predict Customer", use_container_width=True)

    if submitted:
        payload = {
            "CustomerID": customer_id,
            "Gender": gender,
            "Senior_Citizen": senior_citizen,
            "Partner": partner,
            "Dependents": dependents,
            "Tenure_Months": tenure_months,
            "Phone_Service": phone_service,
            "Multiple_Lines": multiple_lines,
            "Internet_Service": internet_service,
            "Online_Security": online_security,
            "Online_Backup": online_backup,
            "Device_Protection": device_protection,
            "Tech_Support": tech_support,
            "Streaming_TV": streaming_tv,
            "Streaming_Movies": streaming_movies,
            "Contract": contract,
            "Paperless_Billing": paperless_billing,
            "Payment_Method": payment_method,
            "Monthly_Charges": monthly_charges,
            "Total_Charges": total_charges,
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=15)
            response.raise_for_status()
            st.session_state.result = response.json()
            st.session_state.error = None
        except requests.exceptions.ConnectionError:
            st.session_state.result = None
            st.session_state.error = "Could not reach the API. Is FastAPI running on localhost:8000?"
        except requests.exceptions.HTTPError as e:
            st.session_state.result = None
            st.session_state.error = f"API returned an error: {e}"
        except Exception as e:
            st.session_state.result = None
            st.session_state.error = f"Unexpected error: {e}"


# ==========================================
# Header
# ==========================================

st.markdown('<div class="main-title">AI Relationship Manager</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Predict churn risk, understand why, and act before the customer leaves.</div>',
    unsafe_allow_html=True
)

if st.session_state.error:
    st.error(st.session_state.error)

result = st.session_state.result

if result is None:
    st.info("Fill in the customer details in the sidebar and click **Predict Customer** to see the report.")
    st.stop()


# ==========================================
# Helper: Gauge Chart Builder
# ==========================================

def make_gauge(value, title, max_value=100, color=COLORS["primary"], suffix=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix, "font": {"size": 32}},
        title={"text": title, "font": {"size": 15}},
        gauge={
            "axis": {"range": [0, max_value]},
            "bar": {"color": color, "thickness": 0.35},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, max_value * 0.4], "color": "#DCFCE7"},
                {"range": [max_value * 0.4, max_value * 0.7], "color": "#FEF3C7"},
                {"range": [max_value * 0.7, max_value], "color": "#FEE2E2"},
            ],
        }
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
    return fig


# ==========================================
# 2. KPI Cards
# ==========================================

prediction_label = result.get("prediction", "N/A")
probability = result.get("churn_probability", 0)
health_score = result.get("health_score", 0)
revenue_risk = result.get("annual_revenue_at_risk", 0)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("Prediction", prediction_label)
    st.markdown('</div>', unsafe_allow_html=True)

with kpi2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("Churn Probability", f"{probability * 100:.2f}%")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("Health Score", f"{health_score}/100")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("Annual Revenue at Risk", f"₹{revenue_risk:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 3. Customer Insights (Left: details, Right: gauges)
# ==========================================

st.markdown('<div class="section-header">Customer Insights</div>', unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1.2])

risk_level = result.get("risk_level", "N/A")
priority = result.get("customer_priority", "N/A")
summary_text = result.get("executive_summary", "")
badge_color = RISK_COLORS.get(risk_level, COLORS["muted"])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"**Customer ID:** {result.get('customer_id', 'N/A')}")
    st.markdown(f"**Prediction:** {prediction_label}")
    st.markdown(
        f"**Risk Level:** "
        f'<span class="badge" style="background-color:{badge_color};">{risk_level}</span>',
        unsafe_allow_html=True
    )
    st.markdown(f"**Priority:** {priority}")
    st.markdown("**Executive Summary:**")
    st.markdown(summary_text)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    gauge_col1, gauge_col2 = st.columns(2)
    with gauge_col1:
        st.plotly_chart(
            make_gauge(probability * 100, "Churn Probability", color=COLORS["danger"], suffix="%"),
            use_container_width=True
        )
    with gauge_col2:
        st.plotly_chart(
            make_gauge(health_score, "Health Score", color=COLORS["success"]),
            use_container_width=True
        )


# ==========================================
# 4. Explainability — Top Drivers + Recommendations
# ==========================================

st.markdown('<div class="section-header">Explainability</div>', unsafe_allow_html=True)

driver_col, rec_col = st.columns(2)

with driver_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Top Drivers**")
    top_drivers = result.get("top_drivers", [])
    if top_drivers:
        for driver in top_drivers:
            st.markdown(f'<div class="driver-item">✓ {driver}</div>', unsafe_allow_html=True)
    else:
        st.markdown("_No driver data available for this prediction._")
    st.markdown('</div>', unsafe_allow_html=True)

with rec_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Recommended Actions**")
    recommendations = result.get("recommendations", [])
    if recommendations:
        for rec in recommendations:
            st.markdown(f'<div class="rec-item">✓ {rec}</div>', unsafe_allow_html=True)
    else:
        st.markdown("_No recommendations available._")
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 5. Executive Summary (large card)
# ==========================================

st.markdown('<div class="section-header">Executive Summary</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="exec-summary-card">
    <h3>Summary Report — {result.get('customer_id', 'N/A')}</h3>
    <p class="exec-summary-text">{summary_text}</p>
    <p class="exec-summary-text"><b>Revenue at risk:</b> ₹{revenue_risk:,.2f} / year</p>
    <p class="exec-summary-text"><b>Recommended action:</b></p>
    <ul class="exec-summary-text">
        {''.join(f"<li>{rec}</li>" for rec in recommendations) if recommendations else "<li>No action needed</li>"}
    </ul>
</div>
""", unsafe_allow_html=True)

