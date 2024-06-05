from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Link engine to database & map tables to classes
engine = create_engine("sqlite:///data_files/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with = engine)
Base.classes.keys()
Station = Base.classes.station
Measurement = Base.classes.measurement

# Make flash object
app = Flask(__name__)

# Home page
@app.route('/')
def home():
    initial_start = '2010-01-01'
    initial_end = '2010-12-31'
    return (
        f'<div align="center"><h1>Hawaii Station API Index</h1></div><br>'
        f'<h2>Available endpoints:</h2><br>'
        f'<li><a href="/api/v1.0/precipitation">Precipitation</a></li>'
        f'<li><a href="/api/v1.0/stations">Station Info</a></li>'
        f'<li><a href="/api/v1.0/tobs">Temperatures Observed for Most Active Station</a></li>'
        f'<li><a href="/api/v1.0/{initial_start}">Temperatures Observed from start date {initial_start}</a></li>'
        f'<li><a href="/api/v1.0/{initial_start}/{initial_end}">Temperatures Observed from start date: {initial_start} to end date: {initial_end}.</a></li>'
        f'<br>'
        f'<br>'
        f'<h4><strong>Note:</strong> Start and end dates can be replace for custom filtering in the YYYY-M-D or YYYY-MM-DD formats directly in the URL.</h4>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    
    # Grabbing latest date from database to calculate data for last 12 months. 
    most_recent_date_str = session.query(Measurement).order_by(Measurement.date.desc()).first().date
    most_recent_date = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    one_year_ago = (most_recent_date - relativedelta(years=1)) - relativedelta(days=1)
    
    # Query last years precipitation data
    query_result = session.query(Measurement).filter(Measurement.date > one_year_ago).all()
    session.close()
    
    # Save results from database into a list of dictionaries & print to precipitation endpoint. 
    query_data = [{x.date: x.prcp} for x in query_result]
    return jsonify(query_data)
    
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    
    # Querying station name and number from station table in database
    stations = [(x.name, x.station) for x in session.query(Station).all()]
    session.close()
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    
    # Grabbing most active station
    most_act_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Grabbing latest reported date for most active station to calculate a 1 year look back date
    most_recent_date_for_act_station_str = session.query(Measurement).filter(Measurement.station == most_act_station).order_by(Measurement.date.desc()).first().date
    most_recent_date_for_act_station = datetime.strptime(most_recent_date_for_act_station_str, '%Y-%m-%d')
    one_year_ago_most_act = (most_recent_date_for_act_station - relativedelta(years=1)) - relativedelta(days=1)
    
    # Grabbing temperature observations for one year back for most active station
    tobs_result = session.query(Measurement).filter(Measurement.station == most_act_station).filter(Measurement.date > one_year_ago_most_act).all()
    session.close()
    
    # Saving results to list to print to temperature observed endpoint.
    temps_one_year_lookback = [result.tobs for result in tobs_result]
    return jsonify(temps_one_year_lookback)


@app.route('/api/v1.0/<start>')
def temp_details_from(start):
    # Ensuring proper date format from endpoint
    try:
        start_cleaned = datetime.strptime(start,'%Y-%m-%d')
    except ValueError:
        return f'Date must be formatted as "YYYY-M-D".'
    
    # Removing a day to ensure user inputted start date gets caputed
    date_to_start_at = start_cleaned - relativedelta(days=1)
    
    session = Session(engine)
    
    # Grabbing min, max, avg for dates from user input start date to end of observed data.
    
    result = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date > date_to_start_at).group_by(Measurement.date).all()
    result_list = [{row[0]: {'Min': row[1], 'Max': row[2], 'Avg': row[3]}} for row in result]
    session.close()
    
    # Printing result to end point
    return jsonify(result_list)

@app.route('/api/v1.0/<start>/<end>')
def temp_details_filter(start, end):
    # Ensuring proper date format from endpoint
    try:
        start_cleaned = datetime.strptime(start,'%Y-%m-%d')
        end_cleaned = datetime.strptime(end,'%Y-%m-%d')
    except ValueError:
        return f'Date must be formatted as "YYYY-M-D".'
    
    # Removing a day to ensure user inputted start date gets caputed
    date_to_start_at = start_cleaned - relativedelta(days=1)
    
    session = Session(engine)
    
    # Grabbing min, max, avg for dates from user input start date to user end of observed data.
    result = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date > date_to_start_at).filter(Measurement.date <= end_cleaned).group_by(Measurement.date).all()
    result_list = [{row[0]: {'Min': row[1], 'Max': row[2], 'Avg': row[3]}} for row in result]
    session.close()
    
    # Printing result to end point
    return jsonify(result_list)
    

# App object from flask only runs when the script is run directly from this file.
if __name__ == '__main__':
    app.run(debug=True)






