#import the dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#set up our database engine 
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect the databse into our classes
Base = automap_base()
Base.prepare(engine, reflect=True)

#save our references to each table - variables
Measurement = Base.classes.measurement
Station = Base.classes.station

#create a session link from Python to our database 
session = Session(engine)

#set up flask
app = Flask(__name__)
#define the welcome route
@app.route("/")
#add the routing information for each of the other routes using a function, return statement, and f-strings
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!<br/>
    Available Routes:<br/>
    /api/v1.0/precipitation<br/>
    /api/v1.0/stations<br/>
    /api/v1.0/tobs<br/>
    /api/v1.0/temp/start/end<br/>
    ''')

#mod 9.5.3 precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #calculate the date one year ago from the most recent date in the db
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #write a query to get the date and precipitation for the previous year
    #the ".\" signifies we want our query to continue on the next line.
    precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
    #create a dictionary with the date as the key and the precipitation as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


#9.5.4 station route
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


#9.5.5 Monthly Temperature Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#9.5.6 statistics route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)