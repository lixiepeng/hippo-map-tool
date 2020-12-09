# coding=utf-8
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import doctest
import math
import re

import requests

from similarity import editdistance

EARTH_RADIUS = 6378137.0


def lng_lat_to_distance(lng1, lat1, lng2, lat2):
    """
    >>> lng_lat_to_distance(116.371728, 39.982907, 116.37736, 39.985336)
    491.69174111268757
    """
    lat1, lng1, lat2, lng2 = [float(x) for x in [lat1, lng1, lat2, lng2]]

    x1 = math.cos(lat1) * math.cos(lng1)
    y1 = math.cos(lat1) * math.sin(lng1)
    z1 = math.sin(lat1)
    x2 = math.cos(lat2) * math.cos(lng2)
    y2 = math.cos(lat2) * math.sin(lng2)
    z2 = math.sin(lat2)
    line_distance = math.sqrt((x1 - x2) * (x1 - x2) +
                              (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2))
    return EARTH_RADIUS * math.pi * 2 * math.asin(0.5 * line_distance) / 180


def check_distance(lng, lat, pois):
    for poi in pois:
        if not "distance_meters" in poi:
            distance_meters = lng_lat_to_distance(
                lng, lat, poi["lng"], poi["lat"])
            poi.update({
                "distance_meters": distance_meters,
                "distance": pretty_distance(distance_meters)
            })


def pretty_distance(meters, ndigits=3):
    if meters < 1000:
        return str(round(meters, ndigits))+"m"
    else:
        return str(round(meters/1000, ndigits))+"km"


def is_approx(a, b):
    dis = lng_lat_to_distance(a["lng"], a["lat"], b["lng"], b["lat"])
    _, name_ratio = editdistance(a["displayname"], b["displayname"])
    _, address_ratio = editdistance(a["address"], b["address"])
    if dis < 10 and name_ratio > 0.6 and address_ratio > 0.6:
        return True
    if dis < 100 and name_ratio > 0.8 and address_ratio > 0.8:
        return True
    if dis < 500 and name_ratio > 0.95 and address_ratio > 0.95:
        return True
    if dis < 1000 and name_ratio > 0.99 and address_ratio > 0.99:
        return True
    return False


def parse_addr(addr):
    return re.findall("(?P<province>.{,5}(?:省|自治区))?(?P<city>.{,5}?(?:市|自治州))(?P<district>.{,5}(?:区|市|县|自治县|镇))?(?P<road>.{,5}(?:街道|新村|大道|道|路|街|巷))?", addr)


def parse_url(url):
    url = url.strip()
    domain = re.findall("https?:\/\/([\d\.]+:\d+)", url)
    lng = re.findall("(?P<lng>lng=\d+\.\d+)", url)
    lat = re.findall("(?P<lat>lat=\d+\.\d+)", url)
    return {
        "domain": domain[0] if domain else None,
        "lng": lng[0].split("=")[1] if lng else None,
        "lat": lat[0].split("=")[1] if lat else None
    }


def parse_query(query):
    """
    >>> parse_query('''B0FFF5QFGK
    北京市 kfc 116.190306,39.295219 13900000000 
    http://127.0.0.1:8000/
    ''')
   {'poi_ids': ['B0FFF5QFGK'],
    'city': '北京市',
    'keyword': 'kfc',
    'lng': '116.190306',
    'lat': '39.295219',
    'lng_lat': ['116.190306,39.295219'],
    'phone': '13900000000',
    'url': 'http://127.0.0.1:8000/'}
    """
    url = re.findall(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", query)
    if url:
        url = url[0]
        query = re.sub(re.escape(url), "", query).strip()
    lng_lat = re.findall("(\d+\.+\d+,\d+\.+\d+)", query)
    for lng_lat_ in lng_lat:
        query = re.sub(lng_lat_, "", query).strip()
    phone = re.findall("1[0-9]{10}", query)
    if phone:
        phone = phone[0]
        query = re.sub(phone, "", query).strip()
    poi_ids = re.findall("([\d]{18,19}|[A-Z\d]{10})", query)
    for poi_id in poi_ids:
        query = re.sub(poi_id, "", query).strip()
        query = re.sub("^,", "", query).strip()
    city = re.findall(r"([\u4e00-\u9fa5]+[市|区|县|州|盟])", query)
    if city:
        city = city[0]
        query = re.sub(city, "", query).strip()

    keyword = re.findall(".+", query.strip())
    if keyword:
        keyword = keyword[0]

    return {
        "poi_ids": poi_ids,
        "city": city,
        "keyword": keyword,
        "lng": lng_lat[0].split(",")[0],
        "lat": lng_lat[0].split(",")[1],
        "lng_lat": lng_lat,
        "phone": phone,
        "url": url
    }


def get_poi_by_id(poi_id):
    return {}


def normalize_poi_info(poi_info):
    poi_info.update({
        "lng": poi_info["longitude"],
        "lat": poi_info["latitude"],
        "displayname": poi_info["disp_name"],
        "city": poi_info["cityname"]
    })
    

