import frappe

from version2_app.parsers import *
import json, shlex, time, re
from subprocess import Popen, PIPE, STDOUT
import os
import sys
import importlib.util
# from version2_app.version2_app.doctype.invoices import *

# modules = dir()
# command = sys.argv[1]
# try:
#     command_module = __import__("myapp.commands.%s" % command, fromlist=["myapp.commands"])
# except ImportError:
#     # Display error message

# command_module.run()

#sample

#sample

#sample
#sample
#sample


def invoiceCreated(doc, method=None):
    print("Invoice Created",doc.name,"")
    # frappe.publish_realtime("invoice_created", "message")
    # frappe.subscriber.on("invoice_created", function (channel, message) {  etc, etc })

def fileCreated(doc, method=None):
    # print(doc.attached_to_name)
    # # print(folder_path)
    # print(modules)
    # # from version2_app.parsers import doc.attached_to_name
    # imp.load_source(name, version2_app.parsers)
    if 'job-' in doc.file_name:
        abs_path = os.path.dirname(os.getcwd())
        file_path = abs_path + '/apps/version2_app/version2_app/parsers/'+doc.attached_to_name+'/invoice_parser.py'
        module_name = 'file_parsing'
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.file_parsing(doc.file_url)
    else:
        print('Normal File')
    






def emitsocket(doc,method=None):
    frappe.log_error("trigger socket bench update", " {'message':'bench  update started','type':'bench update'}")
    frappe.publish_realtime("custom_socket", {'message':'bench  update started','type':"bench update"})




def updateManager(doc, method=None):
  
    if doc.status!="Ongoing":
        commands = ['git pull','service nginx reload','service nginx restart']
        console_dump = ''
        # cwd = '/home/caratred/Desktop/ezy-invoice-production'
        company = frappe.get_last_doc('company')
        cwd = company.angular_project_production_path
        # cwd = '/home/caratred/Documents/angular/ezy-invoice-production'
        key = str(time.time())
        # count = 0
        for command in commands:
            terminal = Popen(shlex.split(command),
                            stdin=PIPE,
                            stdout=PIPE,
                            stderr=STDOUT,
                            cwd=cwd)
            # frappe.log_error("log error", terminal.stdout.read(1))
            for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
                console_dump += c
        logged_command = " && ".join(commands)
        frappe.publish_realtime("custom_socket", {'message':'bench update completed','type':"bench completed"})
        # frappe.log_error("Angular project pull", console_dump)
        frappe.log_error("Angular project pull data","sample")

        

def safe_decode(string, encoding='utf-8'):
    try:
        string = string.decode(encoding)
    except Exception:
        pass
    return string

