import threading
import requests
import glob
import os,random
from os import path
import time
import subprocess

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

cid_issue = True
def getfiles():
    try:
        time.sleep(5)
        print("waiting for print")
        files = glob.glob("/home/caratred/Desktop/projects/watcher/invoice_files/*.pdf")
        for file_path in files:
            random_nbr = str(random.randint(0, 9999))
            new_file_path = file_path.split(".pdf")[0]+random_nbr+'.pdf'
            if cid_issue == True:
                cmd = "gs -dPDFA -dBATCH -dNOPAUSE -dUseCIEColor -sProcessColorModel=DeviceCMYK -sDEVICE=pdfwrite -sPDFACompatibilityPolicy=1 -sOutputFile="+new_file_path+" "+file_path
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                    print(line),
                retval = p.wait()
                if path.exists(file_path):
                    # os.remove(file_path)
                    pass
                file_path = new_file_path


            data = {"company":"MJH-01","host":"http://0.0.0.0:8003/api/method/"} 
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
                pass
            #time.sleep(5)
                # os.remove(file_path)
    except Exception as e:
        print(e,"am from exception")
        #invoicefile['file'].close()
        #if path.exists(file_path):
            #os.remove(file_path)
    getfiles()

getfiles()


