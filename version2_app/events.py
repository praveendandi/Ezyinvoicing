import frappe

from version2_app.parsers import *
import os
import sys
import datetime
import importlib.util
import traceback
# from version2_app.version2_app.doctype.invoices import *

# modules = dir()
# command = sys.argv[1]
# try:
#     command_module = __import__("myapp.commands.%s" % command, fromlist=["myapp.commands"])
# except ImportError:
#     # Display error message

# command_module.run()


def invoiceCreated(doc, method=None):
    try:
        print("Invoice Created",doc.name)
        # frappe.publish_realtime("invoice_created", "message")
        frappe.publish_realtime("custom_socket", {'message':'Invoices Created','data':{"name":doc.name, "irn_generated":doc.irn_generated,"invoice_type":doc.invoice_type,"invoice_from":doc.invoice_from,"guest_name":doc.guest_name,"invoice_file":doc.invoice_file,"print_by":doc.print_by,"creation":doc.creation,"invoice_category":doc.invoice_category}})
        soc_doc = frappe.new_doc("Socket Notification")
        soc_doc.invoice_number = doc.name
        soc_doc.guest_name = doc.guest_name
        soc_doc.invoice_type = doc.invoice_type
        soc_doc.room_number = doc.room_number
        soc_doc.confirmation_number = doc.confirmation_number
        soc_doc.print_by = doc.print_by
        soc_doc.invoice_category = doc.invoice_category
        soc_doc.insert(ignore_permissions=True)
    except Exception as e:
        print(str(e), "Invoice Created Socket Method")
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}	


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
        bin_doc = frappe.new_doc("Document Bin")
        bin_doc.invoice_file = doc.file_url
        bin_doc.printed_at = datetime.datetime.now()
        bin_doc.insert(ignore_permissions=True)
        frappe.db.commit()
    else:
        print('Normal File')




