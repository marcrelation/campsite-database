#!/usr/bin/env python

import time
import os
import pprint
import requests
from os.path import exists
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta

ARRIVAL_DATE=os.getenv('ARRIVAL_DATE', (datetime.now() + relativedelta(months=11)).strftime("%m-%d-%Y"))

def get_units(session,facility_id,dates):
    url='https://floridardr.usedirect.com/Floridardr/rdr/search/grid'

    params={
        "FacilityId":facility_id,
        "UnitTypeId":0,
        "StartDate": ARRIVAL_DATE,
        "MinDate": dates['min_date'],
        "MaxDate": dates['max_date'],
        "StartDate": dates['min_date'],
        "EndDate": dates['max_date'],
        "InSeasonOnly":False,
        "WebOnly":False,
        "IsADA":False,
        "SleepingUnitId":"0",
        "MinVehicleLength":0,
        "UnitCategoryId":"0"
    }
    resp = session.post(url, json=params) 
    resp_json = resp.json()
    units = resp_json['Facility'].get('Units')
    return units

def find_availability():
    SQL = """
    SELECT park_name, park_id, area_name, area_id, group_concat(site_number)
    FROM campsites
    WHERE
    vehicle_length>32 and 
    site_name like 'RV%'
    GROUP BY
    park_name,park_id,area_name,area_id
    """


    now = datetime.now() # current date and time
    min_date = now.strftime("%m/%d/%Y")
    mid_date = (now + relativedelta(months=5)).strftime("%m/%d/%Y")
    max_date = (now + relativedelta(months=11)).strftime("%m/%d/%Y")
    year_dates = [
        {'min_date':min_date,'max_date':mid_date},
        {'min_date':mid_date,'max_date':max_date}
    ]
    con = sqlite3.connect("campsites.db")
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS availability (
        park_id INTEGER, 
        area_id INTEGER,
        site_number TEXT, 
        date TEXT)
    ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS availability_ranges (
        park_id INTEGER, 
        area_id INTEGER,
        site_number TEXT, 
        start_date TEXT,
        available_days INTEGER)
    ''')

    cur = con.cursor()
    cur.execute("DELETE FROM availability")
    cur.execute("DELETE FROM availability_ranges")
    con.commit()
    park_name=''
    park_id=''
    facility_names=[]
    facility_ids=[]

    session = requests.Session()
    for row in cur.execute(SQL):
        park_name=row[0]
        park_id=row[1]
        facility_name=row[2]
        facility_id=row[3]
        sites_matching_criteria = row[4]
        for dates in year_dates:
            units = get_units(session,facility_id,dates)
            time.sleep(3)
            rows=[]
            if units is None:
                continue
            cur2 = con.cursor()
            for unitId,unit in units.items():
                if unit['ShortName'] in sites_matching_criteria:
                    for slice_date,slice in unit['Slices'].items():
                        if slice['IsFree']:
                            print(f"Park: {park_name} Area: {facility_name} Site: {unit['Name']} Date: {slice['Date']} is available.")
                            cur2.execute("INSERT INTO availability VALUES (?,?,?,?)",[park_id,facility_id,unit['ShortName'],slice['Date']])
                        #pprint.pprint(slice)
            con.commit()
    park_id=''
    area_id=''
    site_number=''
    date=''
    days=1
    for row in cur.execute("SELECT * FROM availability ORDER BY park_id,area_id,site_number,date"):
        if site_number=='':
            days=1
        elif park_id!=row[0] or area_id!=row[1] or site_number!=row[2] or (datetime.strptime(date, "%Y-%m-%d").toordinal()+1)!=datetime.strptime(row[3], "%Y-%m-%d").toordinal():
            cur2 = con.cursor()
            cur2.execute("INSERT INTO availability_ranges VALUES (?,?,?,?,?)",[park_id,area_id,site_number,date,days])
            con.commit()
            days=1
        else:
            days+=1
        park_id=row[0]
        area_id=row[1]
        site_number=row[2]
        date=row[3]
    con.close()
find_availability()