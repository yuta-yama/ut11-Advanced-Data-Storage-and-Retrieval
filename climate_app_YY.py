# Dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import and_, or_
import datetime as dt
import numpy as np
import pandas as pd

#################################################
# Database Setup
#################################################

# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True)

# assign classes to respective tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# create session
session = Session(engine)

# setup Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"<b>Available Routes:</b><br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Please enter start date in the API below in the format YYYY-MM-DD:<br/><br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"Please enter start and end dates in the API below in the format YYYY-MM-DD/YYYY-MM-DD:<br/><br/>"
        f"/api/v1.0/"
    )

#################################################
# Last Year from Last Date
#################################################

last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#################################################
# Route 01 - PRECIPITATION ROUTE
# Query for the dates and temp observations from last year.
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():

    precip = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= last_year).\
    order_by(Measurement.date).all()

    precip_list = []

    for p in precip:
        precip_dict = {}
        precip_dict["date"] = p.date
        precip_dict["prcp"] = p.prcp
        precip_list.append(precip_dict)

    return jsonify(precip_list)

#################################################
# Route 02 - STATIONS ROUTE
# Return a JSON list of Stations.
#################################################

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.name).all()
    stations_flat = list(np.ravel(stations))

    return jsonify(stations_flat)

#################################################
# Route 03 - TEMP OBSERVATIONS ROUTE
# Return a JSON list Temperature Observations.
#################################################

@app.route("/api/v1.0/tobs")
def tobs():   
    tobs = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= last_year).\
    order_by(Measurement.date).all()
    
    tobs_list = []

    for t in tobs:
        tobs_dict = {}
        tobs_dict["date"] = t.date
        tobs_dict["tobs"] = t.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

#################################################
# Route 04 - START ROUTE
# JSON list when only start is given
#################################################

@app.route("/api/v1.0/<start>")
def start(start):
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_date = dt.date(2017, 8, 23)

    sel = [
        func.avg(Measurement.tobs),
        func.min(Measurement.tobs),
        func.max(Measurement.tobs)
    ]

    start_results = session.query(*sel).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= last_date).all()
    
    start_results = list(np.ravel(start_results))

    start_list = []
    
    start_dict = {}
    start_dict["start date"] = start_date
    start_dict["avg temp"] = start_results[0]
    start_dict["min temp"] = start_results[1]
    start_dict["max temp"] = start_results[2]
    start_list.append(start_dict)

    return jsonify(start_list)

#################################################
# Route 05 - START END ROUTE
# JSON list with start and end date
#################################################

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    sel = [
        func.avg(Measurement.tobs),
        func.min(Measurement.tobs),
        func.max(Measurement.tobs)
    ]

    sEnd_results = session.query(*sel).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).all()
    
    sEnd_results = list(np.ravel(sEnd_results))

    sEnd_list = []
    
    sEnd_dict = {}
    sEnd_dict["start date"] = start_date
    sEnd_dict["end date"] = end_date
    sEnd_dict["avg temp"] = sEnd_results[0]
    sEnd_dict["min temp"] = sEnd_results[1]
    sEnd_dict["max temp"] = sEnd_results[2]
    sEnd_list.append(sEnd_dict)

    return jsonify(sEnd_list)

if __name__ == '__main__':
    app.run(debug=True)