import json
import threading
import requests
import glob
import os
import frappe
from os import path
import time,json

config_json_path="/home/caratred/Desktop/greenpark/apps/version2_app/config.json"
headers = {'Content-Type': 'application/json'}
with open(config_json_path) as f:
   config_json = json.load(f)
def getprearrivals_file():
    try:
        time.sleep(5)
        files = glob.glob(config_json["file_path"])
        for file_path in files:
            invoicefile = {'file': open(file_path, 'rb')}
            payload = {
                'is_private': 1,
                'folder': 'Home',
                'doctype': 'invoices',
                'docname': config_json["name"],
                'fieldname': 'invoice'}
            if config_json["proxy"] == 1:
                proxyhost = config_json["proxy_url"]
                proxyhost = proxyhost.replace("http://","@")
                proxies = {'http':'http://'+config_json["proxy_username"]+":"+config_json["proxy_password"]+proxyhost,
                                'https':'https://'+config_json["proxy_username"]+":"+config_json["proxy_password"]+proxyhost}
                file_response = requests.get(config_json["host"]+"api/method/upload_file",headers=headers,proxies=proxies,verify=False)
            else:
                if config_json["skip_ssl_verify"] == 1:
                    file_response = requests.post(config_json["host"]+"api/method/upload_file",files=invoicefile, data=payload, verify=False)
                else:
                    file_response = requests.post(config_json["host"]+"api/method/upload_file",files=invoicefile, data=payload, verify=False)
            if file_response.status_code==200:
                file_data = file_response.json()
                if config_json["proxy"] == 1:
                    proxyhost = config_json["proxy_url"]
                    proxyhost = proxyhost.replace("http://","@")
                    proxies = {'http':'http://'+config_json["proxy_username"]+":"+config_json["proxy_password"]+proxyhost,
                                    'https':'https://'+config_json["proxy_username"]+":"+config_json["proxy_password"]+proxyhost}
                    file_response_arr = requests.get(config_json["host"]+"api/method/version2_app.arrivals.doctype.arrival_information.arrival_information.arrivalActivity",params={"company":file_data["message"]["attached_to_name"],"file_url":file_data["message"]["file_url"],"source":"Manual"})
                else:
                    if config_json["skip_ssl_verify"] == 1:
                        file_response_arr = requests.post(config_json["host"]+"api/method/version2_app.arrivals.doctype.arrival_information.arrival_information.arrivalActivity",params={"company":file_data["message"]["attached_to_name"],"file_url":file_data["message"]["file_url"],"source":"Manual"})
                    else:
                        file_response_arr = requests.post(config_json["host"]+"api/method/version2_app.arrivals.doctype.arrival_information.arrival_information.arrivalActivity",params={"company":file_data["message"]["attached_to_name"],"file_url":file_data["message"]["file_url"],"source":"Manual"})
            invoicefile['file'].close()
            if path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        print(e,"am from exception")
    getprearrivals_file()
getprearrivals_file()