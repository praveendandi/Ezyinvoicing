import threading
import requests
import glob
import os
from os import path
import time





def getfiles():
    try:
        print("start-------------------------")
        time.sleep(5)
        print("waiting for print")
        files = glob.glob("/home/caratred/Downloads/xmlfiles/*.xml")
        for file_path in files:
            data = {"company":"DIPL-01","host":"http://0.0.0.0:8000/api/method/","api":"version2_app.version2_app.doctype.xml_parse.extract_xml"}
            invoicefile = {'file': open(file_path, 'rb')}
            payload = {
                'is_private': 1,
                'folder': 'Home',
                'doctype': 'Invoice Reconciliations',
                'docname': data["company"]}
            file_response = requests.post(data['host']+"upload_file",files=invoicefile, data=payload, verify=False).json()
            invoicefile['file'].close()
            invoicefile['file'].close()
            xml_apidata = {"file_list":file_response['message']['file_url']}
            print(xml_apidata)
            xml_api = requests.post(data['host']+data['api'],data=xml_apidata)
            if path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        print(e,"am from exception")
        #invoicefile['file'].close()
        if path.exists(file_path):
            os.remove(file_path)
    getfiles()

getfiles()

