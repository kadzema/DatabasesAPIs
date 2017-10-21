from flask import Flask, jsonify
import json
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, desc, extract
from dateutil.relativedelta import relativedelta

engine = create_engine("sqlite:///hawaii2.sqlite", echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)
print(Base.classes.keys())
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

class Temp():
    def __init__(self, minimum, average, maximum):
        self.minimum = minimum
        self.average = average
        self.maximum = maximum
        

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    p="<p>Click <a href='/api/v1.0/precipitation'>Here</a> for the Precipitation API</p>"
    s = "<p>Click <a href='/api/v1.0/stations'>Here</a> for the Stations API</p>"
    t = "<p>Click <a href='/api/v1.0/tobs'>Here</a> for the Temperature Observations API</p>"
    d = "<p>Click <a href='/api/v1.0/'>Here</a> and enter a start date at the end of the url for the Daily Normals API from that date to the present date<br>Enter start date followed by a slash and then an end date to get the Daily Normals between those two dates</p>"
    return p+s+t+d

@app.route("/api/v1.0/")
def dailyNorms():
    return "<p>Enter a start date at the end of the url for the Daily Normals API from that date to the present date<br>Enter start date followed by a slash and then an end date to get the Daily Normals between those two dates</p>"

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year.
        Convert the query results to a Dictionary using date as the key and tobs as the value.
        Return the json representation of your dictionary"""
    precipList = []
    precip = session.query(Station.name, Measurement.date, Measurement.prcp).filter(Measurement.station==Station.station).filter(Measurement.date>='2016-08-23').order_by(Measurement.date).all()
    for p in precip:
        # print({"date":p[0],"tobs":p[1]})
        precipList.append({"station":p[0],"date":p[1],"prcp":p[2]})

    return jsonify(precipList)


@app.route("/api/v1.0/stations")
def stations():
    # Return a json list of stations from the dataset.
    stations = session.query(Station.station, Station.name).distinct().order_by(Station.station).all()
    stationList = []
    for s in stations:
        stationList.append({"station":s[0],"name":s[1]})

    return jsonify(stationList)

@app.route("/api/v1.0/tobs")
def tobs():
    # Return a json list of Temperature Observations (tobs) for the previous year
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    yearAgo = lastDate[0]- relativedelta(years=1)
    tobs = session.query(Station.name,Measurement.date, Measurement.tobs).filter(Measurement.station==Station.station).filter(Measurement.date>=yearAgo).order_by(Measurement.date).all()
    tobsList = []
    for t in tobs:
        tobsList.append({"station":t[0],"date":t[1],"temperature observation":t[2]})
    
    return jsonify(tobsList)

@app.route("/api/v1.0/<start>")
def start(start):
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    # Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    minimum = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).scalar()
#     print(f"Minimum temp: {minimum}")
    average = session.query(func.round(func.avg(Measurement.tobs))).filter(Measurement.date >= start).scalar()
#     print(f"Average temp: {average}")
    maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).scalar()
#     print(f"Maximum temp: {maximum}")
    
    result = [{"Minimum":minimum},{"Maximum":maximum},{"Average":average}]
    return jsonify(result)

@app.route("/api/v1.0/<sd>/<ed>")
def startEnd(sd,ed):
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    # Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

    minimum = session.query(func.min(Measurement.tobs)).filter(Measurement.date.between(sd,ed)).scalar()
    # print(f"Minimum temp: {minimum}")
    average = session.query(func.round(func.avg(Measurement.tobs))).filter(Measurement.date.between(sd,ed)).scalar()
    # print(f"Average temp: {average}")
    maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date.between(sd,ed)).scalar()
    # print(f"Maximum temp: {maximum}")
    
    result = [{"Minimum":minimum},{"Maximum":maximum},{"Average":average}]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
