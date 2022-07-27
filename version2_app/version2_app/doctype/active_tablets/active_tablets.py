# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests,os,sys,traceback

class ActiveTablets(Document):
    pass


@frappe.whitelist(allow_guest=True)
def validateConnection(property_code=None, ip_address=None, type=None):
    # return True
    company = frappe.get_doc('company', property_code)
    if company is not None:
        return True
    else:
        return False


# @frappe.whitelist(allow_guest=True)
# def removeTab(name=None):
#     # delete tablet config
#     frappe.db.delete('Tablet Config', {
#         'Tablet': name})
#     # delete active tablet
#     frappe.delete_doc('Active Tablets', name)
#     return True

@frappe.whitelist(allow_guest=True)
def updateTab(name=None,status=None):
    #update Tab status
    doc = frappe.get_doc('Active Tablets',name)
    doc.status = status
    doc.save()
    return True


@frappe.whitelist(allow_guest=True)
def createTab(data):
    try:
        company = frappe.get_last_doc('company')
        print(data)
        if frappe.db.exists("Active Tablets",data["uuid"]):
            doc = frappe.get_doc("Active Tablets",data["uuid"])
            doc.socket_id = data["socket_id"]
            doc.save(ignore_permissions=True,ignore_version=True)
            tablet_config = frappe.db.get_value("Tablet Config", {"work_station":data["work_station"],"tablet":data["uuid"]},["name"])
            tablet_doc = frappe.get_doc("Tablet Config", tablet_config)
            tablet_doc.tablet_socket_id = data["socket_id"]
            tablet_doc.save(ignore_permissions=True,ignore_version=True)
        else:
            data["doctype"] = "Active Tablets"
            doc = frappe.get_doc(data)
            doc.insert(ignore_permissions=True)
            tablet_doc = frappe.get_doc("Active Work Stations",data["work_station"])
            tablet_doc.mode = "Connected"
            tablet_doc.save(ignore_permissions=True,ignore_version=True)
            config_data = {"work_station":tablet_doc.work_station,"tablet":data["uuid"],"tablet_ip_address":data["ip_address"],"work_station_ip_address":tablet_doc.ip_address,"doctype":"Tablet Config","work_station_socket_id":tablet_doc.socket_id,"tablet_socket_id":data["socket_id"]}
            config_tab = frappe.get_doc(config_data)
            config_tab.insert(ignore_permissions=True)
            frappe.publish_realtime("custom_socket", {'message':'Tablet Configuration','type':"document_bin_insert","tablet_config":config_data,"company":company.name})
            return {"success": True,"tablet_config":config_data,"company":company.name}
    except Exception as e:
        print(str(e))



@frappe.whitelist(allow_guest=True)
def CheckConnection(data):
    try:
        station = ""
        if "work_station" in data:
            workstation = frappe.db.get_value("Active Work Stations",{"work_station":data["work_station"]},["ip_address"])
            response = os.system("ping -c 1 " + workstation)
            station="Work Stations"
        else:
            tab = frappe.db.get_value("Active Tablets",{"uuid":data["uuid"]},["ip_address"])
            response = os.system("ping -c 1 " + tab)
            station="Active Tablet"
        if response == 0:
            return {"status":True,"station":station}
        else:
            return {"status":False,"station":station}
    except Exception as e:
        print(str(e), "      CheckInternet")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("CheckConnection","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return False

@frappe.whitelist(allow_guest=True)
def resetworkstation_tablet(data):
    try:
        if frappe.db.exists("Tablet Config",data["name"]):
            doc = frappe.get_doc("Tablet Config",data["name"])
            doc.mode = "Sleep"
            doc.save(ignore_permissions=True,ignore_version=True)
            work_doc = frappe.get_doc("Active Work Stations",doc.work_station)
            work_doc.status = "In Active"
            work_doc.mode = "Not Connected"
            work_doc.save(ignore_permissions=True,ignore_version=True)
            data["uuid"] = doc.tablet
            frappe.publish_realtime("custom_socket", {'message':'Reset Workstation Tablet','type':"document_bin_insert","data":data})
            return {"success":True}
        else:
            return {"success":False}
    except Exception as e:
        print(str(e), "      CheckInternet")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("restetablet","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return False