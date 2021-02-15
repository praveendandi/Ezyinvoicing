import frappe

from version2_app.parsers import *
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
    

    # check if it's all there..
    # def bla(mod):
    #     print(dir(mod))
    # bla(module)



    # from p
    # print("Invoice Created",doc.name,"Hey am created *****************8")
    # doc.comapnay
    # from parsers import 



import json, os, shlex, time, re
from subprocess import Popen, PIPE, STDOUT

def emitsocket(doc,method=None):
    frappe.log_error("trigger socket bench update", " {'message':'bench  update started','type':'bench update'}")
    frappe.publish_realtime("custom_socket", {'message':'bench  update started','type':"bench update"})


def updateManager(doc, method=None):
    # print(
    #     "am logged here buddy",
    #     '****************************************************************************8'
    # )
    # frappe.log_error("log error", doc.__dict__)
    # d = run_command('pwd', doc.doctype, str(time.time()))
    # frappe.log_error("log error", d)
    # print(doc)
    if doc.status!="Ongoing":
        commands = ['git pull','service nginx reload','service nginx restart']
        console_dump = ''
        # cwd = '/home/caratred/Desktop/ezy-invoice-production'
        cwd = '/home/caratred/Documents/angular/ezy-invoice-production'
        key = str(time.time())
        for command in commands:
            terminal = Popen(shlex.split(command),
                            stdin=PIPE,
                            stdout=PIPE,
                            stderr=STDOUT,
                            cwd=cwd)
            # frappe.log_error("log error", terminal.stdout.read(1))
            for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
                frappe.publish_realtime(key, c, user=frappe.session.user)
                console_dump += c
        logged_command = " && ".join(commands)
        frappe.publish_realtime("custom_socket", {'message':'bench  update completed','type':"bench start",'data':doc.__dict__})
        frappe.log_error("Angular project pull", console_dump)
        frappe.log_error("Angular project pull data",doc.__dict__)

        # if terminal.wait():
        # 	_close_the_doc(start_time, key, console_dump, status='Failed', user=frappe.session.user)
        # else:
        # 	_close_the_doc(start_time, key, console_dump, status='Success', user=frappe.session.user
        # manager = frappe.get_doc({
        #     'doctype': 'Bench Manager Command',
        #     'key': key,
        #     'source': "tesing",
        #     'command': logged_command,
        #     'console': console_dump,
        #     'status': 'Ongoing'
        # })
        # manager.insert()
        # frappe.db.commit()


def safe_decode(string, encoding='utf-8'):
    try:
        string = string.decode(encoding)
    except Exception:
        pass
    return string

