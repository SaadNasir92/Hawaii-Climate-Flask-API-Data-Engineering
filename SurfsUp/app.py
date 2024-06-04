from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime
from dateutil.relativedelta import relativedelta

engine = create_engine("sqlite:///data_files/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with = engine)
Base.classes.keys()
Station = Base.classes.station
Measurement = Base.classes.measurement

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    most_recent_date_str = session.query(Measurement).order_by(Measurement.date.desc()).first().date
    most_recent_date = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    one_year_ago = (most_recent_date - relativedelta(years=1)) - relativedelta(days=1)
    query_result = session.query(Measurement).filter(Measurement.date > one_year_ago).all()
    session.close()
    query_data = [{x.date: x.prcp} for x in query_result]
    return jsonify(query_data)
    
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    stations = [x.station for x in session.query(Station.station).all()]
    session.close()
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    most_act_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    most_recent_date_for_act_station_str = session.query(Measurement).filter(Measurement.station == most_act_station).order_by(Measurement.date.desc()).first().date
    most_recent_date_for_act_station = datetime.strptime(most_recent_date_for_act_station_str, '%Y-%m-%d')
    one_year_ago_most_act = (most_recent_date_for_act_station - relativedelta(years=1)) - relativedelta(days=1)
    tobs_result = session.query(Measurement).filter(Measurement.station == most_act_station).filter(Measurement.date > one_year_ago_most_act).all()
    temps_one_year_lookback = [result.tobs for result in tobs_result]
    return jsonify(temps_one_year_lookback)


@app.route('/api/v1.0/<start>')
def temp_details_from(start):
    try:
        start_cleaned = datetime.strptime(start,'%Y-%m-%d')
    except ValueError:
        return f'Date must be formatted as "YYYY-M-D".'
    
    session = Session(engine)
    result = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date > start_cleaned).group_by(Measurement.date).all()
    result_list = [{row[0]: {'Min': row[1], 'Max': row[2], 'Avg': row[3]}} for row in result]
    return jsonify(result_list)

# @app.route('/api/v1.0/<start>/<end>')



if __name__ == '__main__':
    app.run(debug=True)






