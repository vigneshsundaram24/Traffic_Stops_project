import streamlit as st
import pandas as pd

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Traffic Stops Dashboard", layout="wide")

# ---- TITLE ----
st.title("🚓 Traffic Stops Data Dashboard")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    return pd.read_csv("C:/Users/vikiy/Downloads/traffic_stops - traffic_stops_with_vehicle_number (1).csv", low_memory=False)

df = load_data()

st.sidebar.header("🔍 Filters")

# ---- SIDEBAR FILTERS ----
countries = st.sidebar.multiselect("Select Country", df["country_name"].dropna().unique())
genders = st.sidebar.multiselect("Select Gender", df["driver_gender"].dropna().unique())
violations = st.sidebar.multiselect("Select Violation", df["violation"].dropna().unique())

filtered_df = df.copy()

if countries:
    filtered_df = filtered_df[filtered_df["country_name"].isin(countries)]
if genders:
    filtered_df = filtered_df[filtered_df["driver_gender"].isin(genders)]
if violations:
    filtered_df = filtered_df[filtered_df["violation"].isin(violations)]

# ---- METRICS ----
col1, col2, col3 = st.columns(3)
col1.metric("Total Stops", f"{len(filtered_df):,}")
col2.metric("Total Arrests", f"{filtered_df['is_arrested'].sum():,}")
col3.metric("Drug-Related Stops", f"{filtered_df['drugs_related_stop'].sum():,}")

# ---- DATA PREVIEW ----
st.write("### 🧾 Filtered Data Preview")
st.dataframe(filtered_df.head(20), use_container_width=True)

# ---- CHARTS ----
st.write("### 📊 Arrests by Gender")
if "driver_gender" in filtered_df.columns:
    st.bar_chart(filtered_df.groupby("driver_gender")["is_arrested"].sum())

st.write("### ⏰ Stops by Violation Type")
if "violation" in filtered_df.columns:
    st.bar_chart(filtered_df["violation"].value_counts())

st.write("### 🚗 Average Driver Age by Gender")
if "driver_age" in filtered_df.columns:
    st.bar_chart(filtered_df.groupby("driver_gender")["driver_age"].mean())

st.caption("Built with ❤️ using Streamlit")
