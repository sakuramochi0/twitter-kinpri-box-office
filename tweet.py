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
    latest = j[-3]
    previous_day = j[-4]
    last_week = j[-10]
    daily_show_diff = latest[2] - previous_day[2]
    daily_sell_diff = latest[1] - previous_day[1]
    weekly_show_diff = latest[2] - last_week[2]
    weekly_sell_diff = latest[1] - last_week[1]
    weekly_show_percent = int((latest[2] / last_week[2]) * 100)
    weekly_sell_percent = int((latest[1] / last_week[1]) * 100)
    return {
        'date': latest[0],
        'sell': latest[1],
        'show': latest[2],
        'daily_show_diff': daily_show_diff,
        'daily_sell_diff': daily_sell_diff,
        'weekly_show_diff': weekly_show_diff,
        'weekly_sell_diff': weekly_sell_diff,
        'weekly_show_percent': weekly_show_percent,
        'weekly_sell_percent': weekly_sell_percent,
    }


def kinpri2_daily():
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
    # css = ('#daily-chart > div > div:nth-child(1) > div > svg > '
    #        'g:nth-child(4) > g:nth-child(2) > g:nth-child(2) > rect')
    # bar = br.find_elements_by_css_selector(css)[-3]
    # bar.click()
    # time.sleep(1)

    # crop & save the chart area of the screenshot image
    img = Image.open(BytesIO(br.get_screenshot_as_png()))
    chart = br.find_elements_by_css_selector('svg')[0]
    x, y = chart.location['x'], chart.location['y']
    h, w = chart.size['height'], chart.size['width']
    crop = img.crop((x + 100, y + 50, x + w - 100, y + h - 50))
    crop.save('/tmp/knpr_box_office_chart.png')

    # tweet the chart image
    data = get_latest_data()
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    status = '''{date}の結果は、
上映回数 {show} 回 (先週{weekly_show_diff:+d}回 / {weekly_show_percent}%)
販売座席数 {sell} 席 (先週{weekly_sell_diff:+d}席 / {weekly_sell_percent}%)
でした！ #kinpri #prettyrhythm

📈キンプラ 販売座席数グラフ📊
https://skrm.ch/prettyrhythm/kinpri-box-office/'''.format(
    date=data['date'],
    show=data['show'],
    sell=data['sell'],
    daily_show_diff=data['daily_show_diff'],
    daily_sell_diff=data['daily_sell_diff'],
    weekly_show_diff=data['weekly_show_diff'],
    weekly_sell_diff=data['weekly_sell_diff'],
    weekly_show_percent=data['weekly_show_percent'],
    weekly_sell_percent=data['weekly_sell_percent'],
)
    api.update_with_media('/tmp/knpr_box_office_chart.png',
                          status=status)

    br.quit()


def kinpri2_weekly():
    # go to the site
    url = 'https://skrm.ch/prettyrhythm/kinpri-box-office/'
    br = PhantomJS()
    br.maximize_window()
    br.get(url)
    time.sleep(3)

    # move to the chart location
    h3 = br.find_elements_by_css_selector('h3')[3]
    ActionChains(br).move_to_element(h3).perform()
    h3 = br.find_elements_by_css_selector('h3')[1]
    ActionChains(br).move_to_element(h3).perform()

    # hover on the latest day's bar
    # css = ('#daily-chart > div > div:nth-child(1) > div > svg > '
    #        'g:nth-child(4) > g:nth-child(2) > g:nth-child(2) > rect')
    # bar = br.find_elements_by_css_selector(css)[-3]
    # bar.click()
    # time.sleep(1)

    # crop & save the chart area of the screenshot image
    img = Image.open(BytesIO(br.get_screenshot_as_png()))
    chart = br.find_elements_by_css_selector('svg')[1]
    x, y = chart.location['x'], chart.location['y']
    h, w = chart.size['height'], chart.size['width']
    crop = img.crop((x + 100, y + 50, x + w - 100, y + h - 50))
    crop.save('/tmp/knpr_box_office_chart.png')

    # tweet the chart image
    data = get_latest_data()
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    status = '''{date}の結果は、
上映回数 {show} 回 (先週{weekly_show_diff:+d}回 / {weekly_show_percent}%)
販売座席数 {sell} 席 (先週{weekly_sell_diff:+d}席 / {weekly_sell_percent}%)
でした！ #kinpri #prettyrhythm

📈キンプラ 販売座席数グラフ📊
https://skrm.ch/prettyrhythm/kinpri-box-office/'''.format(
    date=data['date'],
    show=data['show'],
    sell=data['sell'],
    daily_show_diff=data['daily_show_diff'],
    daily_sell_diff=data['daily_sell_diff'],
    weekly_show_diff=data['weekly_show_diff'],
    weekly_sell_diff=data['weekly_sell_diff'],
    weekly_show_percent=data['weekly_show_percent'],
    weekly_sell_percent=data['weekly_sell_percent'],
)
    api.update_with_media('/tmp/knpr_box_office_chart.png',
                          status=status)

    br.quit()


if __name__ == '__main__':
    # prepare the args
    parser = argparse.ArgumentParser()
    parser.add_argument('type')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    # get tweepy api
    if args.debug:
        api = get_api('sakuramochi_pre')
    else:
        api = get_api('knpr_box_office')

    # tweet according to the type
    if args.type == 'kinpri2_daily':
        kinpri2_daily()
    elif args.type == 'kinpri2_weekly':
        kinpri2_weekly()
    else:
        raise ArgumentError('invalid argument')
    
