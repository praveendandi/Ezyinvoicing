# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,sys,traceback,json
from frappe.model.document import Document

class TabletConfig(Document):
	pass


# @frappe.whitelist(allow_guest=True)
# def removeWorkstation(name=None):
#     # delete tablet config
#     # print(name, "name")
#     frappe.delete_doc('Tablet Config', name)
#     frappe.db.commit()
#     return True


# @frappe.whitelist(allow_guest=True)
# def pushToTab(name=None, confirmation_no=None):
#     tablet_config_exist = frappe.db.exists('Tablet Config', name)
#     print(tablet_config_exist, "test")
#     if tablet_config_exist is not None:
#         tablet_config = frappe.get_doc('Tablet Config', name)
#         # print(tablet_config.__dict__, confirmation_no)
#         information_folio_exist = frappe.db.exists(
#             'Information Folio', confirmation_no)
#         if information_folio_exist is not None:
#             information_folio = frappe.get_doc(
#                 'Information Folio', confirmation_no)
#             # print(information_folio.__dict__)
#             data = {
#                 'tablet_config': tablet_config.__dict__,
#                 'information_folio': information_folio.__dict__
#             }
#             frappe.publish_realtime(
#                 "custom_socket", {'message': 'Push To Tab', 'data': data})
#         else:
#             return {'success': False, 'message': "No Information Folio Found"}
#     else:
#         return {'success': False, 'message': "No Configuration Found"}
    
# @frappe.whitelist(allow_guest=True)
# def invoicePushToTab(name=None, invoice=None):
#     tablet_config_exist = frappe.db.exists('Tablet Config', name)
#     # print(tablet_config_exist, "test")
#     if tablet_config_exist is not None:
#         tablet_config = frappe.get_doc('Tablet Config', name)
#         invoice_exist = frappe.db.exists(
#             'Invoices', invoice)
#         if invoice_exist is not None:
#             invoice_folio = frappe.get_doc(
#                 'Invoices', invoice)
#             data = {
#                 'tablet_config': tablet_config.__dict__,
#                 'invoice': invoice_folio.__dict__
#             }
#             frappe.publish_realtime(
#                 "custom_socket", {'message': 'Push To Tab', 'data': data})
#         else:
#             return {'success': False, 'message': "No Invoice Found"}
#     else:
#         return {'success': False, 'message': "No Configuration Found"}


# @frappe.whitelist(allow_guest=True)
# def redgPushToTab(name=None, redg_name=None):
#     tablet_config_exist = frappe.db.exists('Tablet Config', name)
#     print(tablet_config_exist, "test")
#     if tablet_config_exist is not None:
#         tablet_config = frappe.get_doc('Tablet Config', name)
#         # print(tablet_config.__dict__, confirmation_no)
#         redg_exist = frappe.db.exists(
#             'Redg Card', redg_name)
#         if redg_exist is not None:
#             redg = frappe.get_doc(
#                 'Redg Card', redg_name)
#             # print(information_folio.__dict__)
#             data = {
#                 'tablet_config': tablet_config.__dict__,
#                 'redg_card': redg.__dict__
#             }
#             frappe.publish_realtime(
#                 "custom_socket", {'message': 'Push To Tab', 'data': data})
#         else:
#             return {'success': False, 'message': "No Redg Card Found"}
#     else:
#         return {'success': False, 'message': "No Configuration Found"}

@frappe.whitelist(allow_guest=True)
def createTabConfig():
    try:
        data=json.loads(frappe.request.data)
        data = data["data"]
        if frappe.db.exists({"doctype":"Tablet Config","work_station":data["work_station"]}):
            tablet_config = frappe.db.get_value("Tablet Config",{"work_station":data["work_station"]},["name","tablet","work_station","work_station_socket_id","tablet_socket_id"], as_dict=1)
            tab_doc = frappe.get_doc("Active Tablets",tablet_config["tablet"])
            tab_doc.status = "Not Connected"
            tab_doc.save(ignore_permissions=True,ignore_version=True)
            tablet_config["uuid"] = tablet_config["tablet"]
            frappe.publish_realtime("custom_socket", {'message': 'Disconnect Tablet', 'data': tablet_config})
            frappe.db.delete("Tablet Config", {"work_station": data["work_station"]})
            frappe.db.commit()
        tablet = frappe.get_doc("Active Tablets",data["tablet"])
        work_station = frappe.get_doc("Active Work Stations",data["work_station"])
        if not frappe.db.exists({"doctype":"Tablet Config","work_station":data["work_station"],"mode":"Active"}):
            if not frappe.db.exists({"doctype":"Tablet Config","tablet":data["tablet"],"mode":"Active"}):
                data["work_station_socket_id"] = work_station.socket_id
                data["tablet_ip_address"] = tablet.ip_address
                data["tablet_socket_id"] = tablet.socket_id
                data["mode"] = "Active"
                data["doctype"] = "Tablet Config"
                insert_tabconfig = frappe.get_doc(data)
                insert_tabconfig.insert(ignore_permissions=True, ignore_links=True)
                tablet.status = "Connected"
                tablet.save(ignore_permissions=True,ignore_version=True)
                return {"success":True, "message":"Tablet connected"}
            else:
                return {"success":False,"message":"Already tablet connected to other work station"}
        else:
            return {"success":False,"message":"Already work station connected to other tablet"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing Create Tab Config","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, "attach qr code")

@frappe.whitelist(allow_guest=True)
def deleteTabConfig():
    try:
        data=json.loads(frappe.request.data)
        data = data["data"]
        if frappe.db.exists({"doctype":"Tablet Config","work_station":data["work_station"],"tablet":data["tablet"]}):
            # frappe.db.delete("Tablet Config", {"work_station": data["work_station"],"tablet":data["tablet"]})
            # frappe.db.commit()
            table_config_data = frappe.db.get_value("Tablet Config", {"work_station": data["work_station"],"tablet":data["tablet"]},["name","tablet","work_station","work_station_socket_id","tablet_socket_id"], as_dict=1)
            tab_doc = frappe.get_doc("Active Tablets",data["tablet"])
            tab_doc.status = "Not Connected"
            tab_doc.save(ignore_permissions=True,ignore_version=True)
            table_config_data.uuid = data["tablet"]
            frappe.publish_realtime("custom_socket", {'message': 'Disconnect Tablet', 'data': table_config_data})
            return {"success":True,"message":"Tablet mapped removed successfully"}
        else:
            return {"success":False,"message":"No records found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing Delete Tab Config","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, "attach qr code")

@frappe.whitelist(allow_guest=True)
def pushToTab(name=None, doc_name=None,doc_type=None):
    tablet_config_exist = frappe.db.exists('Tablet Config', name)
    # print(tablet_config_exist, "test")
    if tablet_config_exist is not None:
        tablet_config = frappe.get_doc('Tablet Config', name)
        doc_exist = frappe.db.exists(
            doc_type, doc_name)
        if doc_exist is not None:
            doc_data = frappe.get_doc(
                doc_type, doc_name)
            data = {
                'tablet_config': tablet_config.__dict__,
                'doc_data': doc_data.__dict__,
                'uuid':tablet_config.tablet
            }
            frappe.publish_realtime(
                "custom_socket", {'message': 'Push To Tab', 'data': data})
            return {"success":True, "data":data}
        else:
            return {'success': False, 'message': "No Doc Found"}
    else:
        return {'success': False, 'message': "No Configuration Found"}
    
@frappe.whitelist(allow_guest=True)
def removeAllDevices():
    frappe.db.delete('Tablet Config', {
        'docstatus': 0
    })
    frappe.db.delete('Active Tablets', {
        'docstatus': 0
    })
    frappe.db.delete('Active Work Stations', {
        'docstatus': 0
    })
    frappe.db.commit()
    print("**********************************")
    return True


