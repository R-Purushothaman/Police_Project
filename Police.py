import streamlit as st
import pandas as pd
import mysql.connector

def create_connection():
    try:
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Police"
        )
        mycursor = mydb.cursor(buffered=True)
        return mydb
    except Exception as e:
        st.error(f"Database connection error:{e}")
        return None

def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
           cursor = connection.cursor(dictionary=True)
           cursor.execute(query)
           result = cursor.fetchall()
           df = pd.DataFrame(result)
           return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()

# Title
st.header("PROJECT TITLE")
st.header("SecureCheck: A Python-SQL Digital Ledger for Police Post Logs")
st.divider()

st.subheader("Security Log Queries")
df = pd.read_csv("traffic_stops.csv")
# Queries 
queries=st.selectbox("Select a Query to proceed",[
    "Top 10 vehicle_Number involved in drug-related stops",
    "Vehicles were most frequently searched",
    "Driver age group had the highest arrest rate",
    "Gender distribution of drivers stopped in each country",
    "Which race and gender combination has the highest search rate",
    "What time of day sees the most traffic stops",
    "What is the average stop duration for different violations",
    "Are stops during the night more likely to lead to arrests",
    "Which violations are most associated with searches or arrests",
    "Which violations are most common among younger drivers (<25)",
    "Is there a violation that rarely results in search or arrest",
    "Which countries report the highest rate of drug-related stops",
    "What is the arrest rate by country and violation",
    "Which country has the most stops with search conducted",
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops Number of Stops by Year,Month, Hour of the Day",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country",
    "Top 5 Violations with Highest Arrest Rates"
])

queries_map={
    "Top 10 vehicle_Number involved in drug-related stops":"""select vehicle_number, count(*) as total_stops from data where drugs_related_stop = 1 group by vehicle_number order by total_stops asc limit 10;""",
    "Vehicles were most frequently searched":"""select vehicle_number, count(*) as search_count from data where search_conducted = 1 group by vehicle_number order by search_count limit 10""",
    "Driver age group had the highest arrest rate":"""select 
                case 
                    when driver_age between 16 and 25 then '16-25'
                    when driver_age between 26 and 35 then '26-35'
                    when driver_age between 36 and 45 then '36-45'
                    when driver_age between 46 and 55 then '46-55'
                    when driver_age between 56 and 65 then '56-65'
                    else '65+'
                end as age_group,
                count(case when is_arrested = 1 then 1 end) as arrest_count,
                count(*) as total_stops,
                round(count(case when is_arrested = 1 then 1 end) / count(*) * 100, 2) as arrest_rate_percent
            from data
            group by age_group
            order by arrest_rate_percent desc;""",
    "Gender distribution of drivers stopped in each country":"""select country_name, driver_gender, count(*) as stop_count from data group by country_name, driver_gender order by country_name, driver_gender;""",
    "Which race and gender combination has the highest search rate":"""select driver_race, driver_gender, sum(search_conducted = 1) as search_count,
             round(sum(search_conducted = 1) / count(*) * 100, 2) as search_rate from data group by driver_race, driver_gender order by search_rate desc;""",
    "What time of day sees the most traffic stops":"""select hour(stop_time) AS hour, count(*) AS stop_count from data group by hour(stop_time) order by stop_count desc;""",
    "What is the average stop duration for different violations":"""select violation, avg(stop_duration) as avg_stop_duration from data group by violation order by avg_stop_duration desc;""",
    "Are stops during the night more likely to lead to arrests":"""select 
                case 
                    when hour(stop_time) between 6 and 17 then 'Day'
                    else 'Night'
                end as time_of_day,
                count(*) as total_stops, sum(is_arrested = 1) as arrest_count, round(sum(is_arrested = 1) / count(*) * 100, 2) as arrest_rate
                from data group by time_of_day;""",
    "Which violations are most associated with searches or arrests":"""select violation, count(*) as total_stops, sum(search_conducted = 1) as searches, sum(is_arrested =1) as arrests,
            round(sum(search_conducted = 1) / count(*) * 100, 2) as search_rate, round(sum(is_arrested = 1) / COUNT(*) * 100, 2) as arrest_rate from data
            group by violation order by searches desc, arrests desc;""",
    "Which violations are most common among younger drivers (<25)":"""select violation, count(*) as total_stops from data where driver_age < 25 group by violation order by total_stops desc""",
    "Is there a violation that rarely results in search or arrest":"""select violation, count(*) as total_stops, sum(search_conducted = 1) as searches, sum(is_arrested = 1) as arrests,
            round(sum(search_conducted = 1) / count(*) * 100, 2) as search_rate, round(sum(is_arrested = 1) / count(*) * 100, 2) as arrest_rate from data group by violation order by search_rate, arrest_rate asc limit 1;""",
    "Which countries report the highest rate of drug-related stops":"""select country_name, sum(drugs_related_stop = 1) as drug_related_stops, round(sum(drugs_related_stop=1) / COUNT(*) * 100, 2) as drug_stop_rate
            from data group by country_name order by drug_stop_rate desc;""",
    "What is the arrest rate by country and violation":"""select country_name, violation, sum(is_arrested=1) as arrests, round(sum(is_arrested = 1) / count(*) * 100, 2) as arrest_rate from data group by country_name, 
            violation order by arrest_rate desc;""",
    "Which country has the most stops with search conducted":"""select country_name, count(*) as total_stops, sum(search_conducted = 1) as search_conducted
            from data group by country_name order by search_conducted desc;""",
    "Yearly Breakdown of Stops and Arrests by Country":"""select country_name, year(stop_date) as year, total_stops, sum(total_stops) over (partition by country_name order by year(stop_date)) as cumulative_stops,
            sum(arrests) over (partition by country_name order by year(stop_date)) as cumulative_arrests from (SELECT country_name, stop_date,
            count(*) as total_stops, sum(is_arrested = 1) as arrests from data group by country_name, year(stop_date)) as yearly_data
            order by country_name, year;""",
    "Driver Violation Trends Based on Age and Race":"""select driver_race, age_group, violation, total_stops from (select driver_race, violation, count(*) as total_stops,
        case 
            when driver_age between 18 and 25 then '18-25'
            when driver_age between 26 and 35 then '26-35'
            when driver_age between 36 and 45 then '36-45'
            when driver_age between 46 and 60 then '46-60'
            else '60+'
        end as age_group
            from data group by driver_race, violation, age_group) as age_race_data order by driver_race, age_group, total_stops asc;""",
    "Time Period Analysis of Stops Number of Stops by Year,Month, Hour of the Day":"""select
            year(stop_date) AS year,
            month(stop_date) AS month,
            hour(stop_time) AS hour,
            count(*) as total_stops
            from data group by year(stop_date), month(stop_date), hour(stop_time) order by year, month, hour;""",
    "Violations with High Search and Arrest Rates":"""select violation, count(*) as total_stops, sum(search_conducted = 1) as total_searches, sum(is_arrested = 1) as total_arrests,
            round(sum(search_conducted = 1) * 100.0 / count(*), 2) as search_rate, round(sum(is_arrested = 1) * 100.0 / count(*), 2) as arrest_rate,  rank() over (order by sum(case when search_conducted = 1 then 1 else 0 end) * 1.0 / count(*) desc) as search_ranking,
            rank() over (order by sum(case when is_arrested = 1 then 1 else 0 end) * 1.0 / count(*) desc) as arrest_ranking from data group by violation order by search_rate desc, arrest_rate desc;""",
    "Driver Demographics by Country":"""select country_name, round(avg(driver_age), 1) as avg_driver_age,
            sum(case when driver_gender = 'M' then 1 else 0 end) as male_count,
            sum(case when driver_gender = 'F' then 1 else 0 end) as female_count,           
            sum(case when driver_race = 'White' then 1 else 0 end) as white_count,
            sum(case when driver_race = 'Black' then 1 else 0 end) as black_count,
            sum(case when driver_race = 'Hispanic' then 1 else 0 end) as hispanic_count,
            sum(case when driver_race = 'Asian' then 1 else 0 end) as asian_count
         from data group by country_name order by country_name;""",
    "Top 5 Violations with Highest Arrest Rates":"""select violation, count(*) as total_stops, sum(case when is_arrested = True then 1 else 0 end) as total_arrests,
          round(sum(case when is_arrested = True then 1 else 0 end) * 100.0 / count(*), 2) as arrest_rate from data group by violation order by arrest_rate desc limit 5;"""

}

if st.button("Run Query"):
    result = fetch_data(queries_map[queries])
    if not result.empty:
        st.write(result)
    else:
        st.error("No results found")

st.divider()

st.header("📋 Display the Predict outcome and Violation")

# Input form for all fields
with st.form("new_log_form"):
    stop_date = st.date_input("stop Date")
    stop_time = st.time_input("stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ['Male','Female'])
    driver_age = st.number_input("Driver Age", min_value= 16, max_value= 90, value= 27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a Search Conducted?", ["0","1"])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it Drugs Related", ["0","1"])
    stop_duration = st.selectbox("Stop Duration", df['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button(" Predict Stop Outcome and Violation")

# Filter data for prediction
    if submitted:
        filter_data = df[
            (df['driver_gender'] == driver_gender) &
            (df['driver_age'] == driver_age) &
            (df['search_conducted'] == search_conducted) &
            (df['stop_duration'] == stop_duration) &
            (df['drugs_related_stop'] == int(drugs_related_stop))
        ]

        # Predict stop outcome
        if not filter_data.empty:
            predicted_outcome = filter_data['stop_outcome'].mode()[0]
            predicted_violation = filter_data['violation'].mode()[0]
        else:
            predicted_outcome = "Warning" 
            predicted_violation = "Speeding"

        # Natural Language Summary
        Search_text = "A Search was Conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "was drug_related" if int(drugs_related_stop) else "was not  drug_related"

        st.markdown(f"""
                    **Prediction Summary**
                    - **Predicted Violation:** {predicted_violation}
                    - **Predicted Stop Outcome:** {predicted_outcome}
                    
                     A  **{driver_age}**-year-old  **{driver_gender}** driver in  **{ country_name}** was stopped at **{stop_time.strftime('%I:%M%p')}** on **{stop_date}**. 
                    {Search_text}, and the stop {drug_text}.
                    stop duration: **{stop_duration}**.
                    Vehicle Number: **{vehicle_number}**.

                    """)



