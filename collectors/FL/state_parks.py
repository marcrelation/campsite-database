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

# FOR SOME REASON THIS MISSES THE LAST ONE ALPHA (Wekiva)
def get_parks_no_worky(session):
    url='https://floridardr.usedirect.com/Floridardr/rdr/search/place'
    params={
        "PlaceId":0,
        "Latitude":"28.6289",
        "Longitude":"-81.3573",
        "HighlightedPlaceId":0,
        "StartDate":ARRIVAL_DATE,
        "Nights":"1",
        "CountNearby":True,
        "NearbyLimit":1000,
        "NearbyOnlyAvailable":False,
        "NearbyCountLimit":1000,
        "Sort":"PlaceId",
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

def get_parks(session):
    return [
        {"Name":"Alafia River State Park", "PlaceId":1},
        {"Name":"Anastasia State Park", "PlaceId":2},
        {"Name":"Bahia Honda State Park", "PlaceId":4},
        {"Name":"Big Lagoon State Park", "PlaceId":6},
        {"Name":"Blackwater River State Park", "PlaceId":8},
        {"Name":"Blue Spring State Park", "PlaceId":9},
        {"Name":"Caladesi Island State Park", "PlaceId":10},
        {"Name":"Cayo Costa State Park", "PlaceId":12},
        {"Name":"Collier-Seminole State Park", "PlaceId":13},
        {"Name":"Colt Creek State Park", "PlaceId":14},
        {"Name":"Curry Hammock State Park", "PlaceId":15},
        {"Name":"Dr. Julian G. Bruce St. George Island State Park", "PlaceId":16},
        {"Name":"Falling Waters State Park", "PlaceId":17},
        {"Name":"Fanning Springs State Park", "PlaceId":18},
        {"Name":"Faver-Dykes State Park", "PlaceId":19},
        {"Name":"Florida Caverns State Park", "PlaceId":20},
        {"Name":"Fort Clinch State Park", "PlaceId":21},
        {"Name":"Fred Gannon Rocky Bayou State Park", "PlaceId":23},
        {"Name":"Gamble Rogers Memorial State Recreation Area at Flagler Beach", "PlaceId":24},
        {"Name":"Grayton Beach State Park", "PlaceId":25},
        {"Name":"Henderson Beach State Park", "PlaceId":26},
        {"Name":"Highlands Hammock State Park", "PlaceId":27},
        {"Name":"Hillsborough River State Park", "PlaceId":28},
        {"Name":"Hontoon Island State Park", "PlaceId":29},
        {"Name":"John Pennekamp Coral Reef State Park", "PlaceId":31},
        {"Name":"Jonathan Dickinson State Park", "PlaceId":32},
        {"Name":"Kissimmee Prairie Preserve State Park", "PlaceId":34},
        {"Name":"Koreshan State Park", "PlaceId":35},
        {"Name":"Lafayette Blue Springs State Park", "PlaceId":36},
        {"Name":"Lake Griffin State Park", "PlaceId":37},
        {"Name":"Lake Kissimmee State Park", "PlaceId":38},
        {"Name":"Lake Louisa State Park", "PlaceId":39},
        {"Name":"Lake Manatee State Park", "PlaceId":40},
        {"Name":"Little Manatee River State Park", "PlaceId":41},
        {"Name":"Little Talbot Island State Park", "PlaceId":42},
        {"Name":"Long Key State Park", "PlaceId":43},
        {"Name":"Manatee Springs State Park", "PlaceId":45},
        {"Name":"Mike Roess Gold Head Branch State Park", "PlaceId":46},
        {"Name":"Myakka River State Park", "PlaceId":47},
        {"Name":"Ochlockonee River State Park", "PlaceId":48},
        {"Name":"O'Leno State Park", "PlaceId":49},
        {"Name":"Oleta River State Park", "PlaceId":50},
        {"Name":"Oscar Scherer State Park", "PlaceId":51},
        {"Name":"Paynes Prairie Preserve State Park", "PlaceId":53},
        {"Name":"Rainbow Springs State Park", "PlaceId":54},
        {"Name":"Rodman Campground", "PlaceId":57},
        {"Name":"Ross Prairie Trailhead and Campground", "PlaceId":58},
        {"Name":"Ruth B. Kirby Gilchrist Blue Springs State Park", "PlaceId":59},
        {"Name":"Santos Trailhead and Campground", "PlaceId":60},
        {"Name":"Sebastian Inlet State Park", "PlaceId":61},
        {"Name":"Shangri-La Trailhead and Campground", "PlaceId":62},
        {"Name":"Silver Springs State Park", "PlaceId":63},
        {"Name":"St. Andrews State Park", "PlaceId":64},
        {"Name":"T.H. Stone Memorial St. Joseph Peninsula State Park", "PlaceId":65},
        {"Name":"Stephen Foster Folk Culture Center State Park", "PlaceId":69},
        {"Name":"Suwannee River State Park", "PlaceId":70},
        {"Name":"Three Rivers State Park", "PlaceId":71},
        {"Name":"Tomoka State Park", "PlaceId":72},
        {"Name":"Topsail Hill Preserve State Park", "PlaceId":73},
        {"Name":"Torreya State Park", "PlaceId":74},
        {"Name":"Wekiwa Springs State Park", "PlaceId":75},
        {"Name":"Suwannee River Wilderness Trail", "PlaceId":166}
    ]

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
                row.append(unit.get("IsAda"))
                row.append(unit.get("AllowWebBooking"))
                row.append(unit.get("IsWebViewable"))
                rows.append(row)
            cur = con.cursor()
            cur.executemany("INSERT INTO campsites VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
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
    view TEXT,
    is_ada TEXT,
    allow_web_booking TEXT,
    is_web_viewable TEXT
    )''')
fetch_amenities(con)
con.close()