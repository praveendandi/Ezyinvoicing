# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

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
def resetWorkStations(ws):
    try:
        if frappe.db.exists({'doctype': 'Tablet Config','work_station': ws,'mode': 'Active'}):
            if frappe.db.exists('Active Work Stations', ws):
                tab_name = frappe.get_value('Tablet Config', {'work_station': ws,'mode': 'Active'})
                tab_doc = frappe.get_doc("Tablet Config",tab_name)
                tab_doc.mode = 'Sleep'
                tab_doc.save(ignore_permissions=True, ignore_version=True)
                frappe.db.commit()
                ws_doc = frappe.get_doc("Active Work Stations", ws)
                ws_doc.status = "In Active"
                ws_doc.mode = "Not Connected"
                ws_doc.save(ignore_permissions=True, ignore_version=True)
                frappe.db.commit()
                tab_doc.uuid = tab_doc.name
                frappe.publish_realtime("custom_socket", {'message': 'Reset WorkStation', 'data': tab_doc.__dict__})
                return {"success":True,"message":"Tablet mapped removed successfully"}
            else:
                return {"success":False,"message":"No work station found"}
        else:
            return {"success":False,"message":"Work station not connected to any device"}
    except Exception as e:
        return {"success":False,"message":str(e)}