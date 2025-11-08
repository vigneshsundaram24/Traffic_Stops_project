# SecureCheck: A Python-SQL Digital Ledger for Police Post Logs

## Project Overview
**SecureCheck** is a Python and SQL-based application designed to streamline the logging, tracking, and analysis of vehicle movements at police check posts. By replacing manual logging with a centralized database and a real-time dashboard, it enhances law enforcement efficiency and public safety. The project leverages **Python**, **SQL**, and **Streamlit** to provide real-time insights, automated suspect vehicle identification, and data-driven decision-making for law enforcement agencies.

### Domain
- **Law Enforcement & Public Safety**
- **Real-time Monitoring Systems**

### Skills Gained
- **Python**: Data processing, scripting, and dashboard creation.
- **SQL**: Database design, querying, and optimization.
- **Streamlit**: Building interactive web-based dashboards.

## Problem Statement
Police check posts often rely on manual logging and inefficient databases, slowing down security processes. **SecureCheck** addresses this by creating an SQL-based database for police stop records, integrated with a Python-powered Streamlit dashboard for real-time insights, alerts, and analytics.

### Business Use Cases
- **Real-time Logging**: Track vehicles and personnel instantly.
- **Automated Suspect Identification**: Flag high-risk vehicles using SQL queries.
- **Efficiency Monitoring**: Analyze check post performance with data analytics.
- **Crime Pattern Analysis**: Identify trends in violations using Python scripts.
- **Centralized Database**: Manage data across multiple check post locations.

## Approach
The project follows a structured approach to build a robust system for police check post management:

1. **Data Collection & Storage**
   - Define an SQL schema for police stop records.
   - Store data in a relational database (MySQL/PostgreSQL/SQLite).
   - Use Python libraries (`pandas`, `sqlalchemy`) for data insertion and querying.

2. **Python for Data Processing**
   - Remove columns with only missing values.
   - Handle `NaN` values to ensure data quality.

3. **Database Design (SQL)**
   - Create a table (`traffic_stops`) to store stop records with fields like `stop_date`, `driver_gender`, and `vehicle_number`.
   - Insert cleaned data into the SQL table.

4. **Streamlit Dashboard**
   - Display vehicle logs, violations, and officer reports.
   - Implement SQL-based search filters for quick data lookups.
   - Generate analytics and trends (e.g., high-risk vehicles) using charts.

### Example
A 27-year-old male driver was stopped for **speeding** at **2:30 PM**. No search was conducted, and he received a **citation**. The stop lasted **6-15 minutes** and was **not drug-related**.

## Dataset
The project uses the `traffic_stops` dataset, which includes the following fields:
- `stop_date`: Date of the stop (e.g., 2023-01-01).
- `stop_time`: Time of the stop (e.g., 14:30:00).
- `country_name`: Country where the stop occurred.
- `driver_gender`: Gender of the driver (Male/Female).
- `driver_age_raw`: Raw recorded age of the driver.
- `driver_age`: Cleaned driver age.
- `driver_race`: Race/ethnicity of the driver.
- `violation_raw`: Original reason for the stop.
- `violation`: Cleaned violation type (e.g., Speeding, DUI).
- `search_conducted`: Whether a search was conducted (True/False).
- `search_type`: Type of search (e.g., Frisk, Vehicle Search).
- `stop_outcome`: Result of the stop (e.g., Warning, Citation, Arrest).
- `is_arrested`: Whether the driver was arrested (True/False).
- `stop_duration`: Duration of the stop (e.g., 0-15 Min).
- `drugs_related_stop`: Whether the stop was drug-related (True/False).
- `vehicle_number`: Vehicle identifier (e.g., license plate).

**Dataset Link**: [traffic_stops](#) (Note: Replace with actual dataset link if available.)

## SQL Queries
The project includes a set of SQL queries to analyze traffic stop data, categorized as follows:

### Medium-Level Queries
- **Vehicle-Based**
  1. **Top 10 vehicle numbers involved in drug-related stops**: Identifies the top 10 vehicles linked to drug-related stops.
  2. **Vehicles most frequently searched**: Finds vehicles with the highest search frequency.
- **Demographic-Based**
  3. **Driver age group with highest arrest rate**: Determines which age group has the highest arrest rate.
  4. **Gender distribution of drivers stopped in each country**: Shows the number of male/female drivers per country.
  5. **Race and gender combination with highest search rate**: Identifies the race-gender combo with the most searches.
- **Time & Duration Based**
  6. **Time of day with most traffic stops**: Finds the hour with the most stops.
  7. **Average stop duration for different violations**: Calculates average stop duration per violation.
  8. **Stops more likely to lead to arrests**: Compares arrest rates for day vs. night stops.
- **Violation-Based**
  9. **Violations most associated with searches or arrests**: Identifies violations linked to searches or arrests.
  10. **Violations most common among younger drivers (<25)**: Finds common violations for drivers under 25.
  11. **Violation that rarely results in search or arrest**: Identifies the violation least likely to lead to searches or arrests.
- **Location-Based**
  12. **Countries with highest rate of drug-related stops**: Shows countries with the highest drug-related stop rates.
  13. **Arrest rate by country and violation**: Calculates arrest rates for each violation by country.
  14. **Country with most stops with search conducted**: Identifies the country with the most searches.

### Complex Queries
1. **Yearly Breakdown of Stops and Arrests by Country**: Uses subqueries and window functions to rank countries by stops per year.
2. **Driver Violation Trends Based on Age and Race**: Joins subqueries to analyze violations by age and race.
3. **Time Period Analysis of Stops**: Counts stops by year, month, and hour using date functions.
4. **Violations with High Search and Arrest Rates**: Uses window functions to rank violations with high search/arrest rates.
5. **Driver Demographics by Country**: Analyzes age, gender, and race distribution by country.
6. **Top 5 Violations with Highest Arrest Rates**: Identifies the top 5 violations with the highest arrest rates.

## Project Deliverables
- **SQL Database Schema**: A MySQL/PostgreSQL schema for storing traffic stop data.
- **Python Scripts**: Code for data preprocessing and database interaction using `pandas` and `pymysql`.
- **Streamlit Dashboard**: An interactive web interface for viewing logs, running queries, and predicting outcomes.
- **Automated SQL Reports**: Predefined queries for real-time analytics and logs.
- **Documentation**: User guide and code comments for system usage.

## Results
- **Faster Operations**: SQL queries enable quick data lookups.
- **Automated Alerts**: Flagged vehicles are identified instantly.
- **Real-time Reporting**: Immediate updates on security violations.
- **Data-Driven Decisions**: Insights support law enforcement strategies.

## Project Evaluation Metrics
- **Query Execution Time**: Optimized SQL queries for fast performance.
- **Data Accuracy**: Accurate log entries and flagged reports.
- **System Uptime**: Real-time updates with minimal lag.
- **User Engagement**: Officer interaction with the dashboard.
- **Violation Detection Rate**: Percentage of flagged vehicles identified.

## Technical Tags
- Python
- Data Preprocessing
- MySQL / PostgreSQL / SQLite
- Streamlit
- SQL Queries
- Data Analytics

## Setup Instructions
1. **Prerequisites**:
   - Install Python 3.8+.
   - Install required libraries: `pip install streamlit pandas plotly pymysql numpy`.
   - Install MySQL and create a database named `police_logs`.

2. **Database Setup**:
   - Configure MySQL with user `root` and password `admin`.
   - Run the `create_simple_table()` function to create the `traffic_stops` table and load data.

3. **Running the Application**:
   - Save the dataset (`traffic_stops.csv`) in the specified path (e.g., `C:/Users/vikiy/Downloads/`).
   - Run the Streamlit app: `streamlit run app.py`.
   - Access the dashboard at `http://localhost:8501`.

## Usage
- **Overview Page**: View a data preview, key metrics (total stops, arrest rate, etc.), and charts (geographical, violation, demographic).
- **Queries Page**: Select a category and query to run SQL-based analytics (e.g., top vehicles in drug stops).
- **Prediction Page**: Enter stop details to predict outcomes (e.g., citation or warning) based on historical data.

## Example Code Snippet
```python
import streamlit as st
import pandas as pd
import pymysql

@st.cache_data
def load_data():
    df = pd.read_csv('traffic_stops.csv')
    df['search_type'] = df['search_type'].fillna('Unknown')
    df['stop_date'] = pd.to_datetime(df['stop_date']).dt.date
    return df

st.title("Traffic Stops Analytics")
df = load_data()
st.dataframe(df.head())
```

## Future Enhancements
- Add real-time API integration for live vehicle data.
- Implement machine learning for advanced violation prediction.
- Enhance dashboard with interactive maps for stop locations.
- Support multi-user access with role-based authentication.

## Contributors
- [Vigneshwaran Sundaram] (Developer and Maintainer)

## License
This project is licensed under the MIT License.