#!/usr/bin/env python

import time
import os
import requests
from os.path import exists
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta

# DEFAULT ARRIVAL DATE TO TODAY + 11 MONTHS
ARRIVAL_DATE=os.getenv('ARRIVAL_DATE', (datetime.now() + relativedelta(months=11)).strftime("%m-%d-%Y"))

def get_parks(session):
    url='https://floridardr.usedirect.com/Floridardr/rdr/search/place'
    params={
        "PlaceId":0,
        "Latitude":"28.6289",
        "Longitude":"-81.3573",
        "HighlightedPlaceId":0,
        "StartDate":"01-14-2023",
        "Nights":"1",
        "CountNearby":True,
        "NearbyLimit":1000,
        "NearbyOnlyAvailable":False,
        "NearbyCountLimit":10,
        "Sort":"Name",
        "CustomerId":"0",
        "RefreshFavourites":True,
        "IsADA":False,
        "UnitCategoryId":"0",
        "SleepingUnitId":"0",
        "MinVehicleLength":"0",
        "UnitTypesGroupIds":[],
        "Highlights":[],
        "AmenityIds":[]
    }
    resp = session.post(url, json=params) 
    return resp.json()['NearbyPlaces']

def get_facilities(session,park):
    park_id = park['PlaceId']
    params = {
        "PlaceId":park_id,
        "Latitude":0,
        "Longitude":0,
        "HighlightedPlaceId":0,
        "StartDate":"01-15-2023",
        "Nights":"1",
        "CountNearby":True,
        "NearbyLimit":1000,
        "NearbyOnlyAvailable":False,
        "NearbyCountLimit":10,
        "Sort":"Distance",
        "CustomerId":"0",
        "RefreshFavourites":True,
        "IsADA":False,
        "UnitCategoryId":0,
        "SleepingUnitId":0,
        "MinVehicleLength":0,
        "UnitTypesGroupIds":[],
        "Highlights":[],
        "AmenityIds":[]
    }
    resp = session.post('https://floridardr.usedirect.com/Floridardr/rdr/search/place',json=params)
    json = resp.json()
    return json['SelectedPlace']['Facilities']

def get_units(session,facility):
    facility_name = facility['Name']
    facility_id = facility['FacilityId']

    url='https://floridardr.usedirect.com/Floridardr/rdr/search/grid'
    now = datetime.now() # current date and time
    min_date = now.strftime("%m/%d/%Y")
    max_date = (now + relativedelta(months=11)).strftime("%m/%d/%Y")

    params={
        "FacilityId":facility_id,
        "UnitTypeId":0,
        "StartDate": ARRIVAL_DATE,
        "MinDate": min_date,
        "MaxDate": max_date,
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

def fetch_amenities(con):
    session = requests.Session()
    try:
        parks = get_parks(session)
    except:
        time.sleep(30)
        parks = get_parks(session)
    time.sleep(1)
    for park in parks:
        park_name = park['Name']
        park_id = park['PlaceId']
        try:
            facilities = get_facilities(session,park)
        except:
            time.sleep(30)
            facilities = get_facilities(session,park)
        time.sleep(1)
        for facilityId,facility in facilities.items():
            area_name = facility['Name']
            area_id = facility['FacilityId']
            try:
                units = get_units(session,facility)
            except:
                time.sleep(30)
                units = get_units(session,facility)
            time.sleep(5)
            rows=[]
            if units is None:
                continue
            for unitId,unit in units.items():
                details_resp = session.get(f"https://floridardr.usedirect.com/Floridardr/rdr/search/details/{unit['UnitId']}/startdate/{ARRIVAL_DATE}")
                details_json = details_resp.json()
                amenities = details_json['Amenities']
                if amenities is None:
                    amenities = {}
                vehicle_length = unit['VehicleLength']
                if vehicle_length==0:
                    vehicle_length = int(amenities.get('0.Max Vehicle Length',{'Value':'0'}).get('Value'))
                water = amenities.get('0.Water Hookup',{'Value':'no'}).get('Value').lower()
                electric = amenities.get('0.Electric Hookup',{'Value':'no'}).get('Value').lower()
                sewer = amenities.get('0.Sewer Hookup',{'Value':'no'}).get('Value').lower()
                shade = amenities.get('0.Shade',{'Value':'N/A'}).get('Value')
                view = amenities.get('0.Proximity to Water',{'Value':'N/A'}).get('Value')
                print(park['Name']+' -  '+area_name+' - '+unit['Name'])
                row=[]
                row.append('FL')
                row.append(park_name)
                row.append(park_id)
                row.append(area_name)
                row.append(area_id)
                row.append(unit.get('Name'))
                row.append(unit.get('ShortName'))
                row.append(vehicle_length)
                row.append(electric)
                row.append(water=="yes")
                row.append(sewer=="yes")
                row.append(shade)
                row.append(view)
                rows.append(row)
            cur = con.cursor()
            cur.executemany("INSERT INTO Campsites VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
            con.commit()
            # THIS IS IMPORTANT... IF YOU HIT THE SITE TO FAST YOU WILL BE BLOCKED...

output_file = "campsites.db"
if exists(output_file):
    os.remove(output_file)
con = sqlite3.connect(output_file)
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS campsites (
    park_state TEXT,
    park_name TEXT, 
    park_id INTEGER, 
    area_name TEXT,
    area_id INTEGER,
    site_name TEXT, 
    site_number TEXT,
    vehicle_length INTEGER,
    electric TEXT,
    water INTEGER,
    sewer INTEGER,
    shade TEXT,
    view text
    )''')
fetch_amenities(con)
