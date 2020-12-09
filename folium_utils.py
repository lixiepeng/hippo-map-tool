# pip install git+https://github.com/python-visualization/folium.git
import math

import branca.colormap as cm
import folium
from folium import plugins
from loguru import logger

logger.info(f"folium.__version__: {folium.__version__}")

folium.folium._default_js.append(
    ('jquery', 'http://libs.baidu.com/jquery/2.0.0/jquery.min.js'))

ATTR = "&copy 海马地图工具"

tiles_map = {
    "滴滴底图": folium.raster_layers.TileLayer(
        tiles="https://m{s}.map.gtimg.com/hwap?z={z}&x={x}&y={y}&styleid=5&scene=0&version=224",
        min_zoom=1,
        max_zoom=20,
        max_native_zoom=18,
        tile_size=128,
        attr=ATTR,
        name="滴滴底图",
        subdomains='0123',
        tms=True),
    "滴滴瓦片": folium.raster_layers.TileLayer(
        tiles="http://tile{s}.map.xiaojukeji.com/{z}/{x}/{y}.png",
        min_zoom=1,
        max_zoom=20,
        max_native_zoom=18,
        attr=ATTR,
        name="滴滴瓦片",
        subdomains='1234',
        tms=True),
    "腾讯底图": folium.raster_layers.TileLayer(
        tiles="https://m{s}.map.gtimg.com/hwap?z={z}&x={x}&y={y}&styleid=1000&scene=0&version=110",
        min_zoom=1,
        max_zoom=20,
        max_native_zoom=18,
        tile_size=128,
        attr=ATTR,
        name="腾讯底图",
        subdomains='0123',
        tms=True),
    "高德底图": folium.raster_layers.TileLayer(
        tiles="http://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}",
        min_zoom=1,
        max_zoom=20,
        max_native_zoom=18,
        attr=ATTR,
        name="高德底图",
        subdomains='1234'),
    "高德卫星图": folium.raster_layers.TileLayer(
        tiles="http://www.google.cn/maps/vt?lyrs=s@729&gl=cn&x={x}&y={y}&z={z}",
        min_zoom=1,
        max_zoom=20,
        max_native_zoom=18,
        attr=ATTR,
        name="高德卫星图"),
    "谷歌底图": folium.raster_layers.TileLayer(
        tiles="http://mt0.google.cn/vt/lyrs=m@160000000&hl=EN&gl=EN&src=app&y={y}&x={x}&z={z}&s=Ga",
        min_zoom=1,
        max_zoom=20,
        max_native_zoom=18,
        attr=ATTR,
        name="谷歌底图"),
    "谷歌底图(英)": folium.raster_layers.TileLayer(
        tiles="http://mt0.google.cn/vt/lyrs=m@160000000&hl=EN&gl=EN&src=app&y={y}&x={x}&z={z}&s=Ga",
        min_zoom=1,
        max_zoom=20,
        max_native_zoom=18,
        attr=ATTR,
        name="谷歌底图(英)"),
    "谷歌卫星图": folium.raster_layers.TileLayer(
        tiles="https://webst03.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
        min_zoom=1,
        max_zoom=20,
        max_native_zoom=18,
        attr=ATTR,
        name="谷歌卫星图"),
}


def add_tiles(m):
    for k, v in tiles_map.items():
        v.add_to(m)
    folium.LayerControl().add_to(m)


def add_plugins(m):
    plugins.MiniMap(tile_layer=tiles_map["滴滴瓦片"],
                    toggle_display=True,
                    position='topleft').add_to(m)
    plugins.MousePosition().add_to(m)
    m.add_child(plugins.MeasureControl())
    m.add_child(folium.LatLngPopup())
    m.add_child(folium.ClickForMarker())
    m.add_child(plugins.Fullscreen())
    # m.add_child(plugins.ScrollZoomToggler())
    m.add_child(plugins.LocateControl())


def add_heat_map(m, data, name, radius=25, blur=15):
    m.add_child(plugins.HeatMap(data,
                                name,
                                radius=radius,
                                blur=blur))


def get_map(lat_lng):
    m = folium.Map(location=lat_lng,
                   zoom_start=20,
                   tiles=None,
                   control_scale=True,
                   world_copy_jump=True,
                   no_wrap=False)
    return m


def add_circle(m, lat_lng, radius=250):
    # folium.CircleMarker
    folium.vector_layers.Circle(lat_lng,
                                radius=radius,
                                color='#3186cc',
                                fill_color='#3186cc').add_to(m)


color_map = {
    "red": cm.linear.Reds_08,
    "orange": cm.linear.Oranges_04,
    "green": cm.linear.Greens_07,
    "blue": cm.linear.Blues_09,
    "purples": cm.linear.Purples_09,
    "greys": cm.linear.Greys_06
}
colors = ['red', 'blue', 'green', 'purples', 'orange', 'greys']


def d_to_ul(d, keys=None):
    if not keys:
        keys = d.keys()
    return "<div><ul>"+"".join(["<li>"+str({k: v})+"</li>"
                                for k, v in d.items() if k in keys]) + "</ul></div>"


def get_div_icon(font_size="8", color="red", index="", displayname=""):
    return folium.features.DivIcon(icon_size=(100, 36),
                                   icon_anchor=(0, 0),
                                   html=f'<div style="font-size: {font_size}pt; color: {color};">'
                                   + index + " - "
                                   + displayname
                                   + '</div>',
                                   )


def add_city(m, item):
    marker = folium.Marker(location=[item["lat"], item["lng"]],
                           popup=d_to_ul(item),
                           tooltip=d_to_ul(item),
                           icon=folium.features.DivIcon())
    # plugins.BeautifyIcon("location-arrow",
    #                      background_color="transparent",
    #                      border_width=0).add_to(marker)
    marker.add_to(m)


def add_poi(m, item):
    folium.Marker(location=[item["lat"], item["lng"]],
                  popup=d_to_ul(item),
                  tooltip=d_to_ul(
                      item, ["id", "lng", "lat", "distance",  "address", "displayname", "category"]),
                  icon=get_div_icon("1",
                                    "darkblue",
                                    item["index"],
                                    item.get("displayname", ""))).add_to(m)


def add_pois(m, pois):
    fg = {}
    for k, v in pois.items():
        num = len(v)
        for ix, item in enumerate(v):
            if not k in fg:
                color = colors.pop(0)
                fg.update({
                    k: folium.FeatureGroup(name=k)
                })
                colors.append(color)
                color_range = color_map[color].to_step(num*2)
            ix = item.get("index", ix)
            folium.Marker(location=[item["lat"], item["lng"]],
                          popup=d_to_ul(item),
                          tooltip=d_to_ul(item, [
                                          "id", "lng", "lat", "distance",  "address", "displayname", "category"]),
                          icon=get_div_icon("1",
                                            color,
                                            # color_range((num-int(ix))/num),
                                            str(ix),
                                            item.get("displayname", ""))).add_to(fg[k])
    for k, v in fg.items():
        v.add_to(m)
    return m


def get_zoom_evel(radius):
    radius = max(radius, 10)
    return max(min(20 - math.log2(radius/1000/0.0234375), 20), 1)
