# 快速开发一个poi检索分析地图工具
# streamlit run hippo-map-tool.py --server.port 8051 --server.runOnSave True --server.maxUploadSize 1024  --runner.magicEnabled True
import json
import os
import time
from io import BytesIO

import dask.dataframe as dd
import pandas as pd
import streamlit as st
from dask.diagnostics import ProgressBar
from loguru import logger
from streamlit_folium import folium_static

from folium_utils import (add_circle, add_city, add_heat_map, add_plugins,
                          add_poi, add_pois, add_tiles, get_map, get_zoom_evel)
from gaode_api import gaode_poi_info
from poi import check_distance, get_poi_by_id, normalize_poi_info, parse_query

st.set_page_config(
    page_title="海马地图工具",
    page_icon="🌏",  # 🌐🌎🌍🌏
    layout="wide",
    initial_sidebar_state="expanded",
)
st.set_option('deprecation.showfileUploaderEncoding', False)

st.sidebar.header("海马地图工具")
height = st.sidebar.slider('高度', 0, 1080, 815, 5)
width = st.sidebar.slider('宽度', 0, 2196, 1475, 5)

context = {
    "map": None
}

page_list = ["检索", "热力图"]
page = st.sidebar.selectbox("选择功能", page_list)
if page in ["检索"]:
    env_list = ["百度", "高德"]
    envs = st.sidebar.multiselect("选择环境", env_list, ["高德"])
    context.update({
        "map_pois": {env: [] for env in envs},
        "plng": 0,
        "plat": 0,
        "max_radius": 0
    })

text_input = None
search = None
heat_file = None
if page == "检索":
    text_input = st.sidebar.text_area("支持ID查询，poi检索，坐标打点",
                                      '''B0FFF5QFGK 北京市 kfc 116.190306,39.295219 13900000000''')
    search = st.sidebar.button("search")


elif page == "热力图":
    heat_file = st.sidebar.file_uploader(
        "文件格式 lat lng heat [radius]",
        type=["json", "jsonl", "txt", "csv", "tsv"],
        encoding="utf-8")

if heat_file:
    f_type = heat_file.type
    if f_type.startswith("text"):
        df = pd.read_csv(heat_file,
                         names=["lat", "lng", "heat", "radius"],
                         sep={
                             "text/plain": " ",
                             "text/csv": ",",
                             "text/tab-separated-values": "\t"
                         }.get(f_type))
    elif f_type.startswith("application"):
        # application/json
        # application/octet-stream
        df = pd.read_json(heat_file,
                          lines=True if f_type == "application/octet-stream" else False)
    # adcode: "100000"
    # citycode: "total"
    # label: "全国"
    # name: "全国"
    # spell: ""
    # x: "116.3683244"
    # y: "39.915085"
    radius = st.sidebar.slider('radius', 0, 50, 5)
    blur = st.sidebar.slider('blur', 0, 50, 5)
    context["map"] = get_map([39.915085, 116.3683244])
    context["map"].options.update({"zoom": 4})
    heat_data = []
    # TODO city -> lng lat
    # 城市名模糊匹配
    for ix, row in df.iterrows():
        add_city(context["map"], row.to_dict())
        add_circle(context["map"], (row.lat, row.lng), row.radius*1000)
    add_heat_map(context["map"],
                 df[["lat", "lng", "heat"]].to_numpy(),
                 "热力图",
                 radius=radius,
                 blur=blur)


def check_loc(context, lng, lat):
    if not context["map"]:
        context["map"] = get_map([lat, lng])
        context["plat"], context["plng"] = lat, lng
        add_poi(context["map"], {
                "index": "@",
                "lng": lng,
                "lat": lat,
                "displayname": "定位点"
                })


def add_points(lng_lat_list):
    """
    坐标打点
    """
    pois = []
    for ix, lng_lat in enumerate(lng_lat_list):
        lng, lat = lng_lat.split(",")
        pois.append({
            "index": "@",
            "lng": lng,
            "lat": lat,
            "displayname": str(ix)
        })
    check_distance(lng, lat, pois)
    update_pois(context, "坐标打点", pois)


def update_pois(context, env, pois):
    for index, poi_info in enumerate(pois):
        if poi_info:
            check_loc(context, poi_info["lng"], poi_info["lat"])
            context["max_radius"] = max(
                context["max_radius"], poi_info["distance_meters"])
            context["map_pois"][env].append(poi_info)


if search:
    query = parse_query(text_input)
    logger.info(f"text_input: {text_input}")
    logger.info(f"query: {query}")
    if query["lng"]:
        check_loc(context, query["lng"], query["lat"])
        if len(query["lng_lat"]) > 1:
            context["map_pois"].update({
                "坐标打点": []
            })
            add_points(query["lng_lat"][1:])
        for env in envs:
            if env == "百度":
                pass
            elif env == "高德":
                uri, pois = gaode_poi_info(query["keyword"])
            st.sidebar.markdown(f"""
            [{env}]({uri})
            """)
            _ = [normalize_poi_info(poi) for poi in pois]
            check_distance(query["lng"], query["lat"], pois)
            update_pois(context, env, pois)

    if query["poi_ids"]:
        env = "didi_poi"
        context["map_pois"].update({
            env: []
        })
        pois = [get_poi_by_id(poi_id) for poi_id in query["poi_ids"]]
        pois = [poi for poi in pois if poi]
        if not context["map"]:
            lng, lat = pois[0]["lng"], pois[0]["lng"]
        else:
            lng, lat = context["plng"], context["plat"]
        check_distance(lng, lat, pois)
        update_pois(context, env, pois)

    sidebar_json = {}
    sidebar_json.update({
        "检索结果": context["map_pois"]
    })
    st.sidebar.json(sidebar_json)
    add_pois(context["map"], context["map_pois"])
    context["map"].options.update(
        {"zoom": get_zoom_evel(context["max_radius"])})
    add_circle(context["map"], [query["lat"], query["lng"]],
               context["max_radius"])

if context["map"]:
    add_tiles(context["map"])
    add_plugins(context["map"])
    # call to render Folium map in Streamlit
    folium_static(context["map"], width, height)
