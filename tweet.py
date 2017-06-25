#!/usr/bin/env python3
import argparse
import base64
import datetime
from get_tweepy import get_api
from io import BytesIO
import json
from PIL import Image
import requests
from selenium.webdriver import PhantomJS
from selenium.webdriver.common.action_chains import ActionChains
import time
import tweepy


def get_weekday(day):
    return '月火水木金土日'[day.weekday()]


def get_latest_data():
    url = 'https://skrm.ch/prettyrhythm/kinpri-box-office/api/v1/mimorin/daily.json'
    r = requests.get(url)
    j = json.loads(r.text)
    latest = j[-2]
    previous = j[-3]
    diff = latest[1] - previous[1]
    return {
        'date': latest[0],
        'sell': latest[1],
        'show': latest[2],
        'diff': diff,
    }

# prepare the args
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

# get tweepy api
if args.debug:
    api = get_api('sakuramochi_pre')
else:
    api = get_api('knpr_box_office')
    
# go to the site
url = 'https://skrm.ch/prettyrhythm/kinpri-box-office/'
br = PhantomJS()
br.maximize_window()
br.get(url)
time.sleep(3)

# move to the chart location
h3 = br.find_elements_by_css_selector('h3')[1]
ActionChains(br).move_to_element(h3).perform()
h3 = br.find_elements_by_css_selector('h3')[0]
ActionChains(br).move_to_element(h3).perform()

# hover on the latest day's bar
css = ('#daily-chart > div > div:nth-child(1) > div > svg > '
       'g:nth-child(4) > g:nth-child(2) > g:nth-child(2) > rect')
bar = br.find_elements_by_css_selector(css)[-2]
bar.click()
time.sleep(1)

# crop & save the chart area of the screenshot image
img = Image.open(BytesIO(br.get_screenshot_as_png()))
chart = br.find_element_by_css_selector('svg')
x, y = chart.location['x'], chart.location['y']
h, w = chart.size['height'], chart.size['width']
crop = img.crop((x + 100, y + 50, x + w - 100, y + h - 50))
crop.save('/tmp/knpr_box_office_daily_chart.png')

# tweet the chart image
data = get_latest_data()
yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
status = '''KING OF PRISM -PRIDE the HERO-
{date}の結果は、
上映回数{show}回
販売座席数{sell}席(前日{diff:+d})でした！

📈キンプラ 販売座席数グラフ📊
https://skrm.ch/prettyrhythm/kinpri-box-office/
#prettyrhythm #kinpri'''.format(
    date=data['date'],
    show=data['show'],
    sell=data['sell'],
    diff=data['diff'],
)
api.update_with_media('/tmp/knpr_box_office_daily_chart.png',
                      status=status)

br.quit()
