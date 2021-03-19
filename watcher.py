import threading
import requests
import glob
import os
import frappe
from os import path
import time
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
company = frappe.get_last_doc("company")
print(company.__dict__)
print(company.watcher_folder_path,"////////")
files = glob.glob(company.watcher_folder_path)
def getfiles():
    try:
        time.sleep(5)
        
        for file_path in files:
            data = {"company":company.name,"host":"http://0.0.0.0:8000/api/method/"}
            print(data,"config data")
            invoicefile = {'file': open(file_path, 'rb')}
            payload = {
                'is_private': 1,
                'folder': 'Home',
                'doctype': 'invoices',
                'docname': data["company"],
                'fieldname': 'invoice'}
            #invoicefile['file'].close()
            file_response = requests.post(data['host']+"upload_file",files=invoicefile, data=payload, verify=False)
            invoicefile['file'].close()
            print(file_response)
            invoicefile['file'].close()
            #if file_response:
            if path.exists(file_path):
            #time.sleep(5)
                os.remove(file_path)
    except Exception as e:
        print(e,"am from exception")
        #invoicefile['file'].close()
        #if path.exists(file_path):
            #os.remove(file_path)
    getfiles()

getfiles()

