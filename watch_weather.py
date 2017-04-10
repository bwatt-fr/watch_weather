# coding: utf-8

import json
import smtplib
import sys
import os
import datetime

import requests

def send_mail(config, mail_to, message):
    server = smtplib.SMTP(config["server_mail"],
                          config["port_server_mail"])
    server.starttls()
    server.login(config["username"], config["password"])
    server.sendmail(config["email_from"], mail_to, message)
    server.quit()


def create_mail(config, mail_to, temp_min):

    temp_min = float(temp_min) - 273.15
    message = config["message"].replace("####", str(temp_min))
    mail = ("From: %s\nTo: %s\nSubject: %s\n\n\n%s" %
           (config["email_from"], mail_to, config["subject"], message))
    return mail


def get_tomorow_date(data):
    now = datetime.datetime.now()
    delta = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M:%S") - now
    if delta.days == 0:
        return True
    return False

# Location of the python file
dir_name = os.path.dirname(__file__)

# Load of the config
with open(os.path.join(dir_name, 'config.json')) as my_json:
    config = json.load(my_json)


# send_mail(config, message)
response = requests.get("{url}?q={city}&APPID={key}".format(
                            url=config["owm_url"], city=config["city"],
                            key=config["owm_api_key"]))
weather_json = response.json()

tomorow_data = [data for data in weather_json["list"]
                if get_tomorow_date(data["dt_txt"])]

tomorow_data_min = min(tomorow_data, key=lambda d: d["main"]["temp_min"])
temp_min = tomorow_data_min["main"]["temp_min"]

if float(temp_min) < float(config["temp_min"]):
    for mail_to in config["mail_to"]:
        mail = create_mail(config, mail_to, data["main"]["temp_min"])
        send_mail(config, mail_to, mail)
