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
        company_doc = frappe.get_doc("company",doc.attached_to_name)
        new_parsers = company_doc.new_parsers
        if new_parsers == 0:
            file_path = abs_path + '/apps/version2_app/version2_app/parsers/'+doc.attached_to_name+'/invoice_parser.py'
        else:
            file_path = abs_path + '/apps/version2_app/version2_app/parsers_invoices/invoice_parsers/'+doc.attached_to_name+'/invoice_parser.py'
        module_name = 'file_parsing'
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.file_parsing(doc.file_url)
    else:
        print('Normal File')
    
