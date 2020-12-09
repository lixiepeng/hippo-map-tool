# http://npm.taobao.org/mirrors/chromedriver/
# java
# !pip install selenium browsermob-proxy
# chmod +x browsermob-proxy
# export PATH=PATH:.
from selenium import webdriver
from browsermobproxy import Server
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/download/{file_name}")
async def download(file_name: str):
    return FileResponse(f"./download/{file_name}")

server = Server('browsermob-proxy')
server.start()
proxy = server.create_proxy()

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('headless')

browser = webdriver.Chrome(options=chrome_options)
proxy.new_har("gaode", options={'captureHeaders': True, 'captureContent': True})

@hug.get("search")
def gaode_search(query,city=110000,pagenum=1):
    browser.get(f'https://ditu.amap.com/search?query={query}&city={city}&pagenum={pagenum}')
    
def wait_ele_by_css(css,browser,timeout=5):
     WebDriverWait(browser,timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    
    
api_result = {
    "poiInfo":[],
    "poiTipslite":[],
    "whether":[],
    "regeo":[]
}
for ix,entry in enumerate(proxy.har['log']['entries']):
    for k,v in api_result.items():
        if k in entry['request']['url']:
            api_result[k].append({
                **entry
            })
            
server.stop()
driver.quit()