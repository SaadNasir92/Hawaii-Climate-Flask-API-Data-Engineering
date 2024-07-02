# Hawaii Climate Analysis API

## Project Overview

This project involves the transformation and analysis of Hawaii climate data. Using CSV files, pandas, and matplotlib, an ORM is used to create a SQLite database file. The data is then served via a Flask API, allowing users to query various climate-related information.

## Tools and Technologies

- **Python**: The primary programming language used for data manipulation and API development.
- **Pandas**: For data cleaning, transformation, and analysis.
- **Matplotlib**: For data visualization.
- **SQLAlchemy**: For ORM to create and interact with the SQLite database.
- **SQLite**: The database used to store the processed data.
- **Flask**: For creating the API to serve the data.

## Methodology

1. **Data Preparation**:
    - **CSV Files**: The initial climate data is provided in CSV format.
    - **Pandas**: The CSV files are loaded into pandas DataFrames for cleaning and transformation.
    - **Matplotlib**: Used for visualizing the data to understand its distribution and trends.

2. **Database Creation**:
    - **SQLAlchemy ORM**: The cleaned data is used to create a SQLite database using SQLAlchemy ORM. This involves defining the database schema and populating it with data from the pandas DataFrames.

3. **API Development**:
    - **Flask**: A Flask application (`app.py`) is developed to serve the data from the SQLite database. Various endpoints are created to allow users to query different aspects of the climate data.
    - **Endpoints**:
        - `/`: Home page with links to available endpoints.
        - `/api/v1.0/precipitation`: Returns the last 12 months of precipitation data.
        - `/api/v1.0/stations`: Provides information about weather stations.
        - `/api/v1.0/tobs`: Returns temperature observations for the most active station over the last year.
        - `/api/v1.0/<start>`: Returns minimum, maximum, and average temperature for all dates from the given start date.
        - `/api/v1.0/<start>/<end>`: Returns minimum, maximum, and average temperature for dates between the given start and end date.

    Sample Code:
```python
@app.route('/api/v1.0/<start>/<end>')
def temp_details_filter(start, end):
# Ensuring proper date format from endpoint
try:
    start_cleaned = datetime.strptime(start,'%Y-%m-%d')
    end_cleaned = datetime.strptime(end,'%Y-%m-%d')
except ValueError:
    return f'Date must be formatted as "YYYY-M-D" or "YYYY-MM-DD".'

# Removing a day to ensure user inputted start date gets caputed
date_to_start_at = start_cleaned - relativedelta(days=1)

session = Session(engine)

# Grabbing min, max, avg for dates from user input start date to user end of observed data.
result = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date > date_to_start_at).filter(Measurement.date <= end_cleaned).group_by(Measurement.date).all()
result_list = [{row[0]: {'Min': row[1], 'Max': row[2], 'Avg': row[3]}} for row in result]
session.close()

if len(result_list) <= 0:
    return f'No results found between {datetime.strftime(start_cleaned, "%Y-%m-%d")} and {datetime.strftime(end_cleaned, "%Y-%m-%d")}, try a different start/end.'
else:
    # Printing result to end point
    return jsonify(result_list)

# App object from flask only runs when the script is run directly from this file.
if __name__ == '__main__':
    app.run(debug=True)
```

## Notebooks

### EDA Notebook (`eda.ipynb`)

- **DB Connection Setup**: Sets up the connection to the SQLite database using SQLAlchemy.
- **Data Analysis and Visualization**: Uses pandas and matplotlib to analyze and visualize the climate data. This includes examining temperature trends, precipitation patterns, and other climate-related metrics.

ORM QUERY SAMPLE:
```python
tobs_result = session.query(Measurement).filter(Measurement.station == most_act_station).filter(Measurement.date > one_year_ago_most_act).all()
data_for_df = [{'Date': result.date, 'tobs': result.tobs} for result in tobs_result]
temp_df = pd.DataFrame(data_for_df)
```

### Flask Application (`app.py`)

- **API Endpoints**: Defines the endpoints for the Flask API, allowing users to query different aspects of the climate data. Each endpoint performs specific queries on the SQLite database and returns the results in JSON format.

## Conclusion

This project demonstrates a complete workflow from data preparation and transformation to database creation and API development. By leveraging tools like pandas, matplotlib, SQLAlchemy, and Flask, it provides a cost_effective solution for serving climate data to end-users via an API.

Feel free to explore the notebooks and the Flask application to understand the data transformation process and how the API is constructed. This project showcases proficiency in data engineering, data analysis, and web development using Python and related libraries.

