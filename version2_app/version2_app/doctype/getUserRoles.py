import frappe
import json
import requests
@frappe.whitelist(allow_guest=True)
def getUserRoles():
    if frappe.local.request.method=="GET":
        doc = frappe.get_roles(frappe.session.user)
        return {"success":True,"data":doc}
    else:
        return {"success":False, "message":"User doesn't exists! please Register"}




    
