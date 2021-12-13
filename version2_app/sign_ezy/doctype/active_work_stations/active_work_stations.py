# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from version2_app.sign_ezy.doctype.tablet_config.tablet_config import disconnectTablet

class ActiveWorkStations(Document):
	pass

@frappe.whitelist(allow_guest=True)
def removeWorkstation(name=None):
    # delete tablet config
    print("remove workstation", name)
    frappe.db.delete('Tablet Config', {
        'work_station': name})
    # delete active tablet
    frappe.delete_doc('Active Work Stations', name)
    return True

@frappe.whitelist(allow_guest=True)
def resetWorkStations(name, doctype):
    try:
        type = ""
        if doctype == "Active Work Stations":
            type = "work_station"
        else:
            if doctype == "Active Tablets":
                type = "tablet"
        if frappe.db.exists({'doctype': 'Tablet Config',type: name,'mode': 'Active'}):
            tab_name = frappe.get_value('Tablet Config', {type: name,'mode': 'Active'})
            tab_doc = frappe.get_doc("Tablet Config",tab_name)
            tablet_disconnected = disconnectTablet(tab_name)
            if tablet_disconnected["success"] == False:
                return tablet_disconnected
            uuid = tab_doc.tablet
            tab_doc.uuid = uuid
            if type == "tablet":
                tab_doc = frappe.get_doc("Tablet Config",tab_name)
                tab_doc.delete()
                frappe.db.commit()
                tablet_doc = frappe.get_doc("Active Tablets",tab_doc.tablet)
                tablet_doc.delete()
                frappe.db.commit()
            frappe.publish_realtime("custom_socket", {'message': 'Reset WorkStation' if type == 'work_station' else 'Reset Tablet', 'data': tab_doc.__dict__})
            return {"success":True,"message":"Tablet mapped removed successfully"}
        else:
            return {"success":False,"message":"Work station not connected to any device" if type == 'work_station' else "Device not connected to any work station"}
    except Exception as e:
        return {"success":False,"message":str(e)}