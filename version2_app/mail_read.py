import os
from traceback import print_tb
from webbrowser import get
from xmlrpc.client import TRANSPORT_ERROR
import frappe
from frappe.utils import cstr, get_site_name, logger, random_string
import sys,imaplib,base64,os,pdfkit,email,mailparser,re,requests,json
import email_listener
from datetime import datetime
logger = frappe.logger("api", allow_site=True, file_count=50)
import base64
import email
import glob
import json 


@frappe.whitelist(allow_guest=True)
def mailreader():
    try:
        imap_server = "imap-mail.outlook.com"
        mail = imaplib.IMAP4_SSL(imap_server)
        cwd = os.getcwd() 
        site_name = cstr(frappe.local.site)
        site = cwd+"/"+site_name
        mail_data = frappe.db.get_list('Email Credentials',fields=["username","password","subject"])
        print(mail_data,"/////////")
        mail.login(mail_data[0]["username"], mail_data[0]["password"])
        mail.select()
        cwd = os.getcwd()
        type, data = mail.search(None, '(UNSEEN)')
        mail_ids = data[0]
        id_list = mail_ids.split()
        filename = datetime.now().strftime("%Y%m%d-%H%M%S")
        for num in data[0].split():
            typ, data = mail.fetch(num, '(RFC822)' )
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)
            mail_parse = mailparser.parse_from_bytes(raw_email)
            get_sub = mail_parse.subject
            if mail_data[0]['subject'] == get_sub:
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    fileName = part.get_filename()
                    if bool(fileName) and ('.pdf' in fileName or ".PDF" in fileName):
                        cwd = os.getcwd()
                        site_name = cstr(frappe.local.site)
                        filepath = cwd + "/" + site_name + "/public/files/job-" + fileName
                        if not os.path.isfile(filepath) :
                            fp = open(filepath, 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()
                        print(filepath)
                        headers = {'Content-Type': 'application/form-data'}
                        files_new = {"file": open(filepath, 'rb')}
                        company = frappe.get_last_doc("company")
                        payload = {
                                    'is_private': 1,
                                    'folder': 'Home',
                                    'doctype': 'invoices',
                                    'docname': company.name,
                                    'fieldname': 'invoice'
                                  }
                        file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                                    data=payload, verify=False)                            
                        print(file_response.json())
    except Exception as e:
        print(str(e))
        frappe.log_error(str(e),"mailread")
        return str(e)
