import urllib

import requests


def parse_params(url):
    parse = urllib.parse.urlparse(urllib.parse.unquote(url))
    return {line.split("=")[0]: line.split("=")[1] for line in parse.query.split("&")}


def parse_headers(headers):
    return {line.split(": ")[0]: line.split(": ")[1] for line in headers.strip().split("\n") if not line.startswith(":")}


headers = {'accept': 'application/json, text/javascript, */*; q=0.01',
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,zh-TW;q=0.6',
           'amapuuid': 'f4823af7-1e39-4577-bc89-b4c2cc74bfa7',
           'cookie': 'guid=a95f-9e2f-e4e0-a889; UM_distinctid=175f572c0fd9ae-081e7291a9ad22-10201b0b-1fa400-175f572c0fec82; CNZZDATA1255626299=2107773997-1606140038-https%253A%252F%252Fcn.bing.com%252F%7C1606140038; cna=M+cOGJTCnicCAXL51pvtAF8L; xlly_s=1; _uab_collina=160614074084534092068046; tfstk=cLDfB22Mlk4zKKON3mtz0uPT-u21Z9sQfIamcjEIKLyCpVnfiZBURa-osNB89u1..; l=eBxsV77uOlDVAU6FBOfZlurza77t9IRbmuPzaNbMiOCP9g5p5741WZ7gWIL9CnGVH6-y-35ivhU0BqYp5zsMNOU54WXXH1Nr3dC..; isg=BDc32ONRJLUWTaA5ulDV_zIKxiKB_AteE3dIsonkZYZtOFZ6k8xXrupeGphm1OPW',
           'dnt': '1',
           'referer': 'https://ditu.amap.com/',
           'sec-fetch-dest': 'empty',
           'sec-fetch-mode': 'cors',
           'sec-fetch-site': 'same-origin',
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
           'x-csrf-token': 'null',
           'x-requested-with': 'XMLHttpRequest'}


def poi_tips_lite():
    params = {
        "city": "",
        "geoobj": "",
        "words": ""
    }
    url = "https://ditu.amap.com/service/poiTipslite?" + \
        urllib.parse.quote(params)
    return requests.get(url).json()


def gaode_poi_info(keywords):
    params = {'query_type': 'TQUERY',
              'pagesize': '1',
              'pagenum': '1',
              'qii': 'true',
              'cluster_state': '5',
              'need_utd': 'true',
              'utd_sceneid': '1000',
              'div': 'PC1000',
              'addr_poi_merge': 'true',
              'is_classify': 'true',
              'zoom': '12',
              'city': '110000',
              'geoobj': '116.594072|40.024313|116.758867|40.226188',
              'keywords': keywords}
    url = "https://ditu.amap.com/service/poiInfo?" + \
        urllib.parse.urlencode(params)
    return url,requests.get(url, headers=headers).json()["data"]["poi_list"]
