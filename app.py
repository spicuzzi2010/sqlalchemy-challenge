import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():

    return (
        f"Welcome to the Hawaii Climate Analysis API! <br/>"
        f"Available routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    session = Session(engine)
    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    most_recent_date
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    one_year_ago.date()
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago.date()).all()
    # Dict with date as the key and prcp as the value
    last_year_precipitation = []
    for result in results:
        precipitation_dict = {}
        precipitation_dict[result.date] = result.prcp
        last_year_precipitation.append(precipitation_dict)

    return jsonify(last_year_precipitation)

    session.close()
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""

    session = Session(engine)
    results = session.query(Station.name).all()
    # Unravel results into a 1D array and convert to a list
    station_count_list = list(np.ravel(results))

    return jsonify(station_count_list)

    session.close()
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""

    session = Session(engine)
    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    most_recent_date
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    one_year_ago.date()

    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    station_count = session.query(Measurement.station, Station.name, func.count(Measurement.id)).\
    filter(Measurement.station == Station.station).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.id).desc()).all()

    station_activity = [{"station_id": result[0], "station_name": result[1],"station_count": result[2]} for result in station_count]
    most_active = station_activity[0]['station_id']

    results = session.query(Measurement.station,Station.name, Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= one_year_ago.date()).\
    filter(Measurement.station == Station.station).\
    filter(Measurement.station == most_active).all()

    tobs = list(np.ravel(results))

    return jsonify(tobs)

    session.close()

def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    session = Session(engine)

    sel = [Measurement.station, 
       func.min(Measurement.tobs).label("min_temp"), 
       func.max(Measurement.tobs).label("max_temp"), 
       func.round(func.avg(Measurement.tobs),2).label("avg_temp")]
    
    if end = None:
        results = session.query(*sel).\
        filter(Measurement.date >= start).all()
    else:
        results = session.query(*sel).\
        filter(Measurement.date.between(start,end))
    
    stats_list = list(np.ravel(results))

    return jsonify(stats_list)

    session.close()
if __name__ == '__main__':
    app.run()

