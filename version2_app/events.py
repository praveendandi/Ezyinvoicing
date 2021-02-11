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
    print("Invoice Created",doc.name)
    # frappe.publish_realtime("invoice_created", "message")
    frappe.publish_realtime("custom_socket", "{'message':'Invoices Created','data':'doc.name'}")


    # frappe.subscriber.on("invoice_created", function (channel, message) {  etc, etc })

def fileCreated(doc, method=None):
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




