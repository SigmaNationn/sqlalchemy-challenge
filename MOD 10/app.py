# Import the dependencies.
from flask import Flask, json, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
default = automap_base()
# reflect the tables
default.prepare(engine)
# Save references to each table
Station = default.classes.station
Measurement = default.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Home section")
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<br/>"
        f"/api/v1.0/start/end/"
    )

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value. Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation/')
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()
    precip_dict = dict(results)
    print(f"Results for Precipitation - {precip_dict}")
    return jsonify(precip_dict) 

# Return a JSON list of temperature observations for the previous year.
@app.route('/api/v1.0/stations/')
def stations():
    print()
    stations = session.query(Station.station).order_by(Station.station).all() 
    stations_list = []
    print("Station List:")   
    for i in stations:
        print (i[0])
        stations_list.append(i[0])
    return jsonify(stations_list)

# Return a JSON list of temperature observations for the previous year.
@app.route('/api/v1.0/tobs/')
def tobs():
    print("In TOBS section.")
    print()
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    active_stations = most_active_stations[0][0]
    temperature_observations = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year).order_by(Measurement.date).filter(Measurement.station==active_stations).all()
    print("Temperature Results for All Stations")
    results = {}
    for row in temperature_observations:
        results[row.date] = row.tobs if row.tobs is not None else "null"
    return jsonify(results)

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route('/api/v1.0/<start_date>/')
def calc_temps_start(start_date):
    print("In start date section.")
    print()
    print(start_date)
    temperatures = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    result_temperature = session.query(*temperatures).filter(Measurement.date >= start_date).all()
    results = []
    min_temp, max_temp, avg_temp = result_temperature[0]
    results.append({
        "min_temperature": min_temp if min_temp is not None else "null",
        "max_temperature": max_temp if max_temp is not None else "null",
        "avg_temperature": avg_temp if avg_temp is not None else "null"
    })
    return jsonify(results)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route('/api/v1.0/<start_date>/<end_date>/')
def calc_temps_start_end(start_date, end_date):
    print("In start & end date section.")
    print()
    temperatures = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    result_temperature = session.query(*temperatures).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    results = []
    min_temp, max_temp, avg_temp = result_temperature[0]
    results.append({
        "min_temperature": min_temp if min_temp is not None else "null",
        "max_temperature": max_temp if max_temp is not None else "null",
        "avg_temperature": avg_temp if avg_temp is not None else "null"
    })
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)



