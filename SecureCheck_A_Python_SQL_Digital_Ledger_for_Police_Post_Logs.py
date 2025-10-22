import streamlit as st
import pandas as pd
import plotly.express as px
import pymysql
from pymysql.err import Error
import numpy as np

@st.cache_data
def load_data():
    df = pd.read_csv('C:/Users/vikiy/Downloads/traffic_stops - traffic_stops_with_vehicle_number (1).csv')
    
    df['search_type'] = df['search_type'].fillna('Unknown')
    
    df['stop_date'] = pd.to_datetime(df['stop_date']).dt.date
    df['stop_time'] = df['stop_time'].apply(lambda x: f"{x}:00:00" if len(str(x)) <= 2 else x)
    df['stop_time'] = pd.to_datetime(df['stop_time'], format='%H:%M:%S').dt.time  
    
    string_cols = ['country_name', 'driver_race', 'violation_raw', 'violation', 'stop_outcome', 'vehicle_number', 'search_type', 'driver_gender']
    for x in string_cols:
        df[x] = df[x].astype(str)
        df[x] = df[x].str.strip()
    
    df['driver_gender'] = df['driver_gender'].replace({'M': 1, "F": 0})
    bool_cols = ['search_conducted', 'is_arrested', 'drugs_related_stop']
    for col in bool_cols:
        df[col] = df[col].replace({True: 1, False: 0})
    duration_map = {'0-15 Min': 1, '16-30 Min': 2, '30+ Min': 3}
    df['stop_duration'] = df['stop_duration'].map(duration_map)
    return df

df = load_data()

# Simple MySQL connection
def get_db_connection():
    try:
        return pymysql.connect(
            host='localhost', database='police_logs', user='root', 
            password='admin', charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Error:
        st.error("Database connection failed")
        return None

def create_simple_table():
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traffic_stops (
                    stop_date DATE,
                    stop_time TIME,
                    country_name VARCHAR(100),
                    driver_gender TINYINT(1),
                    driver_age_raw INT,
                    driver_age INT,
                    driver_race VARCHAR(100),
                    violation_raw VARCHAR(100),
                    violation VARCHAR(100),
                    search_conducted TINYINT(1),
                    search_type VARCHAR(100),
                    stop_outcome VARCHAR(100),
                    is_arrested TINYINT(1),
                    stop_duration TINYINT(1),
                    drugs_related_stop TINYINT(1),
                    vehicle_number VARCHAR(50),
                    INDEX idx_vehicle (vehicle_number),
                    INDEX idx_date (stop_date),
                    INDEX idx_time (stop_time)
                )
            """)
            
            cursor.execute("TRUNCATE TABLE traffic_stops")
            
            # Insert data directly
            data = [tuple(row) for row in df[[
                'stop_date', 'stop_time', 'country_name', 'driver_gender', 
                'driver_age_raw', 'driver_age', 'driver_race', 'violation_raw',
                'violation', 'search_conducted', 'search_type', 'stop_outcome',
                'is_arrested', 'stop_duration', 'drugs_related_stop', 'vehicle_number'
            ]].values]
            
            insert_query = """
                INSERT INTO traffic_stops VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_query, data)
            conn.commit()
    except Error as e:
        st.error(f"Table creation/loading error: {e}")
    finally:
        conn.close()

create_simple_table()

def execute_query(sql):
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return pd.DataFrame(cursor.fetchall())
    except Error as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Define all queries in exact order
def get_queries():
    return {
        "Vehicle-Based": {
            "Top 10 vehicle numbers involved in drug-related stops": """
                SELECT vehicle_number, COUNT(*) AS count 
                FROM traffic_stops 
                WHERE drugs_related_stop = 1 
                GROUP BY vehicle_number 
                LIMIT 10
            """,
            "Vehicles most frequently searched": """
                SELECT vehicle_number, COUNT(*) AS count 
                FROM traffic_stops 
                WHERE search_conducted = 1 
                GROUP BY vehicle_number 
                ORDER BY count DESC 
                LIMIT 10
            """
        },
        "Demographic-Based": {
            "Driver age group with highest arrest rate": """
                WITH age_groups AS (
                    SELECT 
                        CASE 
                            WHEN driver_age < 20 THEN 'Under 20'
                            WHEN driver_age BETWEEN 20 AND 29 THEN '20-29'
                            WHEN driver_age BETWEEN 30 AND 39 THEN '30-39'
                            WHEN driver_age BETWEEN 40 AND 49 THEN '40-49'
                            WHEN driver_age BETWEEN 50 AND 59 THEN '50-59'
                            WHEN driver_age BETWEEN 60 AND 69 THEN '60-69'
                            WHEN driver_age >= 70 THEN '70+'
                            ELSE 'Unknown'
                        END AS age_group,
                        is_arrested
                    FROM traffic_stops
                )
                SELECT age_group, 
                       ROUND(100.0 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate
                FROM age_groups
                GROUP BY age_group
                ORDER BY arrest_rate DESC
                LIMIT 1
            """,
            "Gender distribution of drivers stopped in each country": """
                SELECT 
                    country_name, 
                    CASE 
                        WHEN driver_gender = 0 THEN 'female' 
                        WHEN driver_gender = 1 THEN 'male' 
                        ELSE 'unknown' 
                    END AS driver_gender,
                    driver_race, 
                    ROUND(AVG(driver_age), 1) AS avg_age, 
                    COUNT(*) AS total_stops 
                FROM traffic_stops 
                GROUP BY country_name, driver_race, driver_gender 
                ORDER BY country_name, total_stops DESC;
            """,
            "Race and gender combination with highest search rate": """
                SELECT 
                    driver_race, 
                    CASE 
                        WHEN driver_gender = 0 THEN 'female' 
                        WHEN driver_gender = 1 THEN 'male' 
                        ELSE 'unknown' 
                    END AS driver_gender,
                    ROUND(100.0 * SUM(search_conducted) / COUNT(*), 2) AS search_rate 
                FROM traffic_stops 
                GROUP BY driver_race, driver_gender 
                ORDER BY search_rate DESC 
                LIMIT 1
            """
        },
        "Time & Duration Based": {
            "Time of day with most traffic stops": """
                SELECT HOUR(stop_time) AS hour, COUNT(*) AS count 
                FROM traffic_stops 
                GROUP BY hour 
                ORDER BY count DESC 
                LIMIT 1
            """,
            "Average stop duration for different violations": """
                WITH duration_map AS (
                    SELECT violation,
                           CASE 
                               WHEN stop_duration = 1 THEN 7.5
                               WHEN stop_duration = 2 THEN 23
                               WHEN stop_duration = 3 THEN 45
                               ELSE 0
                           END AS duration_min
                    FROM traffic_stops
                )
                SELECT violation, AVG(duration_min) AS avg_duration
                FROM duration_map
                GROUP BY violation
                ORDER BY avg_duration DESC
            """,
            "Stops more likely to lead to arrests": """
                WITH time_period AS (
                    SELECT 
                        CASE 
                            WHEN HOUR(stop_time) BETWEEN 20 AND 23 
                                 OR HOUR(stop_time) BETWEEN 0 AND 5 THEN 'Night'
                            ELSE 'Day'
                        END AS period,
                        is_arrested
                    FROM traffic_stops
                )
                SELECT period, 
                       ROUND(100.0 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate
                FROM time_period
                GROUP BY period
            """
        },
        "Violation-Based": {
            "Violations most associated with searches or arrests": """
                SELECT violation, 
                       ROUND(100.0 * SUM(search_conducted OR is_arrested) / COUNT(*), 2) AS association_rate 
                FROM traffic_stops 
                GROUP BY violation 
                ORDER BY association_rate DESC
            """,
            "Violations most common among younger drivers (<25)": """
                SELECT violation, COUNT(*) AS count 
                FROM traffic_stops 
                WHERE driver_age < 25 
                GROUP BY violation 
                ORDER BY count DESC
            """,
            "Violation that rarely results in search or arrest": """
                SELECT violation, 
                       ROUND(100.0 * SUM(search_conducted OR is_arrested) / COUNT(*), 2) AS rate 
                FROM traffic_stops 
                GROUP BY violation 
                ORDER BY rate ASC 
                LIMIT 1
            """
        },
        "Location-Based": {
            "Countries with highest rate of drug-related stops": """
                SELECT country_name, 
                       ROUND(100.0 * SUM(drugs_related_stop) / COUNT(*), 2) AS drug_rate 
                FROM traffic_stops 
                GROUP BY country_name 
                ORDER BY drug_rate DESC
            """,
            "Arrest rate by country and violation": """
                SELECT country_name, violation, 
                       ROUND(100.0 * SUM(is_arrested) / COUNT(*), 2) AS arrest_rate 
                FROM traffic_stops 
                GROUP BY country_name, violation 
                ORDER BY country_name, arrest_rate DESC
            """,
            "Country with most stops with search conducted": """
                SELECT country_name, SUM(search_conducted) AS search_count 
                FROM traffic_stops 
                GROUP BY country_name 
                ORDER BY search_count DESC 
                LIMIT 1
            """
        },
        "Complex": {
            "Yearly Breakdown of Stops and Arrests by Country": """
                SELECT 
                    country_name, 
                    year,
                    total_stops,
                    total_arrests,
                    arrest_rate,
                    RANK() OVER (PARTITION BY year ORDER BY total_stops DESC) AS rank_by_stops
                FROM (
                    SELECT 
                        country_name, 
                        EXTRACT(YEAR FROM stop_date) AS year, 
                        COUNT(*) AS total_stops, 
                        SUM(is_arrested) AS total_arrests,
                        ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate
                    FROM traffic_stops
                    GROUP BY country_name, year
                ) AS yearly_data
                ORDER BY year, total_stops DESC
            """,
            "Driver Violation Trends Based on Age and Race": """
                SELECT d.driver_race, d.driver_age_group, v.violation, v.total_cases
                FROM (
                    SELECT driver_race,
                           CASE 
                               WHEN driver_age < 25 THEN '<25'
                               WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
                               WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                               ELSE '>60'
                           END AS driver_age_group,
                           violation,
                           COUNT(*) AS total_cases
                    FROM traffic_stops
                    GROUP BY driver_race, driver_age_group, violation
                ) v
                JOIN (
                    SELECT DISTINCT driver_race,
                           CASE 
                               WHEN driver_age < 25 THEN '<25'
                               WHEN driver_age BETWEEN 25 AND 40 THEN '25-40'
                               WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                               ELSE '>60'
                           END AS driver_age_group
                    FROM traffic_stops
                ) d
                ON v.driver_race = d.driver_race AND v.driver_age_group = d.driver_age_group
                ORDER BY v.total_cases DESC
            """,
            "Time Period Analysis of Stops": """
                SELECT EXTRACT(YEAR FROM stop_date) AS year, 
                       EXTRACT(MONTH FROM stop_date) AS month, 
                       HOUR(stop_time) AS hour, 
                       COUNT(*) AS count 
                FROM traffic_stops 
                GROUP BY year, month, hour 
                ORDER BY year, month, hour
            """,
            "Violations with High Search and Arrest Rates": """
                SELECT violation,
                       ROUND(SUM(search_conducted)*100.0 / COUNT(*), 2) AS search_rate,
                       ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate,
                       RANK() OVER (ORDER BY SUM(is_arrested) DESC) AS rank_by_arrests
                FROM traffic_stops
                GROUP BY violation
                HAVING search_rate > 10 OR arrest_rate > 10
                ORDER BY rank_by_arrests
            """,
            "Driver Demographics by Country": """
                SELECT 
                    country_name, 
                    CASE 
                        WHEN driver_gender = 0 THEN 'female' 
                        WHEN driver_gender = 1 THEN 'male' 
                        ELSE 'unknown' 
                    END AS driver_gender, 
                    driver_race, 
                    ROUND(AVG(driver_age), 1) AS avg_age, 
                    COUNT(*) AS total_stops 
                FROM traffic_stops 
                GROUP BY country_name, driver_race, driver_gender 
                ORDER BY country_name, total_stops DESC
            """,
            "Top 5 Violations with Highest Arrest Rates": """
                SELECT violation, 
                       ROUND(SUM(is_arrested)*100.0 / COUNT(*), 2) AS arrest_rate 
                FROM traffic_stops 
                GROUP BY violation 
                ORDER BY arrest_rate DESC 
                LIMIT 5
            """
        }
    }

st.sidebar.title("🚦 Traffic Stops Analytics")

# Page navigation buttons
if st.sidebar.button("📊 Overview", use_container_width=True):
    st.session_state.page = "Overview"
if st.sidebar.button("🔍 Queries", use_container_width=True):
    st.session_state.page = "Queries" 
if st.sidebar.button("🎯 Prediction", use_container_width=True):
    st.session_state.page = "Prediction"

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Overview"

# Overview Page
if st.session_state.page == "Overview":
    st.title("Traffic Stops Overview")

    # Data Table Preview
    st.header("Data Preview")
    st.write("Sample of the traffic stops dataset (first 10 rows):")
    preview_cols = ['stop_date', 'stop_time', 'country_name', 'driver_gender', 'driver_age', 'driver_race', 'violation', 'stop_outcome']
    preview_df = df[preview_cols].head(10)
    preview_df['driver_gender'] = preview_df['driver_gender'].replace({1: 'Male', 0: 'Female'})
    st.dataframe(preview_df, use_container_width=True)

    # Key Metrics Dashboard
    st.header("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_stops = df.shape[0]
        st.metric("Total Stops", total_stops)
    with col2:
        arrest_rate = round(100 * df['is_arrested'].mean(), 2)
        st.metric("Arrest Rate (%)", arrest_rate)
    with col3:
        search_rate = round(100 * df['search_conducted'].mean(), 2)
        st.metric("Search Rate (%)", search_rate)
    with col4:
        avg_age = round(df['driver_age'].mean(), 1)
        st.metric("Average Driver Age", avg_age)

    # Visual Insights
    st.header("Visual Insights")
    tab1, tab2, tab3 = st.tabs(["Geographical Distribution", "Violation Breakdown", "Demographic Insights"])

    with tab1:
        if not df.empty and 'country_name' in df.columns:
            country_data = df['country_name'].value_counts().reset_index()
            country_data.columns = ['Country', 'Count']
            fig = px.bar(country_data, x='Country', y='Count', title="Stops by Country", color="Country", text='Count')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for Country chart.")

    with tab2:
        if not df.empty and 'violation' in df.columns:
            violation_data = df['violation'].value_counts().reset_index()
            violation_data.columns = ['Violation', 'Count']
            fig = px.pie(violation_data, names='Violation', values='Count', title="Violation Breakdown")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for Violation chart.")

    with tab3:
        if not df.empty and 'driver_gender' in df.columns and 'driver_race' in df.columns:
            demo_data = df.groupby(['driver_gender', 'driver_race']).size().reset_index(name='Count')
            demo_data['driver_gender'] = demo_data['driver_gender'].replace({1: 'Male', 0: 'Female'})
            fig = px.bar(demo_data, x='driver_race', y='Count', color='driver_gender', barmode='group',
                         title="Stops by Gender and Race", text='Count')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for Demographic chart.")

# Queries Page
elif st.session_state.page == "Queries":
    st.title("🔍 Detailed Analytics")
    
    queries = get_queries()
    categories = list(queries.keys())
    
    # Category selection
    selected_category = st.selectbox("Select Category", categories)
    
    # Query selection within category
    queries_in_category = queries[selected_category]
    selected_query = st.selectbox("Select Query", list(queries_in_category.keys()))

    # Query execution block
    if st.button("Execute Query"):
        sql = queries_in_category[selected_query]
        st.subheader(selected_query)
    
        with st.spinner("Running query..."):
            result_df = execute_query(sql)
        
            if not result_df.empty:
                st.dataframe(result_df, use_container_width=True)
            else:
                st.warning("No results returned from query")

# Prediction Page
elif st.session_state.page == "Prediction":
    st.header("🔎 Custom Natural Language Filter")

    st.markdown("Fill in the details below to get a natural language prediction of the stop outcome based on existing data.")

    st.header("Add New Police Log & Predict Outcome and Violation")

    # Input form for all fields (excluding outputs)
    with st.form("new_log_form"):
        stop_date = st.date_input("Stop Date")
        stop_time = st.time_input("Stop Time")
        county_name = st.text_input("County Name")
        driver_gender = st.selectbox("Driver Gender", ["male", "female"])
        driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
        driver_race = st.text_input("Driver Race")
        search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
        search_type = st.text_input("Search Type")
        drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
        stop_duration = st.selectbox("Stop Duration", df['stop_duration'].dropna().unique())
        vehicle_number = st.text_input("Vehicle Number")
        timestamp = pd.Timestamp.now()

        submitted = st.form_submit_button("Predict Stop Outcome & Violation")

        if submitted:
            # Filter data for prediction
            filtered_data = df[
                (df['driver_gender'] == driver_gender) &
                (df['driver_age'] == driver_age) &
                (df['search_conducted'] == int(search_conducted)) &
                (df['stop_duration'] == stop_duration) &
                (df['drugs_related_stop'] == int(drugs_related_stop))
            ]

            # Predict stop outcome
            if not filtered_data.empty:
                predicted_outcome = filtered_data['stop_outcome'].mode()[0]
                predicted_violation = filtered_data['violation'].mode()[0]
            else:
                predicted_outcome = "warning"  # Default fallback
                predicted_violation = "speeding"  # Default fallback

            # Natural Language summary
            search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
            drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

            st.markdown(f"""
                ## Prediction Summary

                **Predicted Violation:** {predicted_violation}

                **Predicted Stop Outcome:** {predicted_outcome}

                A {driver_age}-year-old {driver_gender} driver in {county_name} was stopped at 
                {stop_time.strftime('%I:%M %p')} on {stop_date}
                {search_text}, and the stop {drug_text}.
                Stop duration: **{stop_duration}**.
                Vehicle Number: **{vehicle_number}**.
                """)