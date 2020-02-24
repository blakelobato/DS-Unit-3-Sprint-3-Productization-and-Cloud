"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask, render_template
import openaq
import requests 
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)
api = openaq.OpenAQ()

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'ID: {id}, Date: {self.datetime}, Value: {self.value}'

def openaq_call(city, param_val):
    status, body = api.measurements(city=city, parameter=param_val)
    aq_results = []
    for entry in body['results']:
        data = ((entry['date']['utc'], entry['value']))
        aq_results.append(data)
        #aq_results.append((entry['date']['utc'], entry['value']))
        db_result = Record(datetime=str(data[0]), value=data[1])
        DB.session.add(db_result)
        DB.session.commit()
    return aq_results

@APP.route('/')
def root():
    """Base view."""
    returned_list = openaq_call("Los Angeles", "pm25")
    list_as_string = str(returned_list)
    filtered_records = Record.query.filter(Record.value >= 10).all()
    return render_template('base.html', filtered_records=filtered_records)




    # entry_list = []
    # for filtered_record in filtered_records:
    #     entry_dict = {"ID": filtered_record.id, "DateTime": (filtered_record.datetime, '%Y-%m-%dT%H:%M:%S.%fZ'), "Value": filtered_record.value}
    # #     entry_list.append(entry_dict)
        



@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    api_results = openaq_call("Los Angeles", "pm25")
    for api_result in api_results:
        time, value = api_result
        record_entry = Record(datetime=time, value=value)
        DB.session.add(record_entry)
    DB.session.commit()
    return 'Data refreshed!'


@APP.route('/about')
def about():
    """about page for the application"""
    return "Our application is going to be a dashboard that displays air quality data from the [Open AQ API](https://docs.openaq.org)."





