import json
import threading
import requests
import glob
import os
import frappe
from os import path
import time
from version2_app.arrivals.doctype.arrival_information.arrival_information import arrivalActivity
# def printit():
# 	threading.Timer(5.0, printit).start()
# 	files = glob.glob("/home/caratred/test/*.pdf")
# 	print(files)
# 	for file_path in files:
# 		data = {"company":"EHNDNP-01",
# 							"host":"http://0.0.0.0:8000/api/method/",}
# 		invoicefile = {'file': open(file_path, 'rb')}
# 		payload = {
# 				'is_private': 1,
# 				'folder': 'Home',
# 				'doctype': 'invoices',
# 				'docname': data["company"],
# 				'fieldname': 'invoice'}
# 		file_response = requests.post(data['host']+"upload_file",files=invoicefile, data=payload, verify=False).json()
# 		print(file_response)
# 		if file_response:
# 			if path.exists(file_path):
# 				os.remove(file_path)
# printit()
def getprearrivals_file():
    try:
        time.sleep(5)
        print("waiting for print")
        files = glob.glob("/home/caratred/Desktop/files/*.txt")
        company = frappe.get_last_doc('company')
        for file_path in files:
            # data = {"company":"RAH-01","host":"http://0.0.0.0:8000/api/method/"}
            # print(data,"config data")
            invoicefile = {'file': open(file_path, 'rb')}
            payload = {
                'is_private': 1,
                'folder': 'Home',
                'doctype': 'invoices',
                'docname': company.name,
                'fieldname': 'invoice'}
            file_response = requests.post(company.host+"upload_file",files=invoicefile, data=payload, verify=False)
            if file_response.status_code==200:
                file_data = file_response.json()
                file_response_arr = requests.post(company.host+"version2_app.arrivals.doctype.arrival_information.arrival_information.arrivalActivity",params={"company":company.name,"file_url":file_data["message"]["file_url"]})
            invoicefile['file'].close()
            if path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        print(e,"am from exception")
    getprearrivals_file()
getprearrivals_file()

