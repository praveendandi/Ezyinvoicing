# Copyright (c) 2023, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RolesPermission(Document):
    pass

@frappe.whitelist()
def update_roles_routes(doc,method=None):
    roles_list= frappe.get_list('Role')
    get_list = frappe.db.get_list("Routes",fields=["name","route",'module'])
    if len(get_list)>0:
        for each in roles_list:
            if not frappe.db.exists("Roles Permission", each.name, cache=True):
                doc = frappe.get_doc({ 'doctype': 'Roles Permission','select_role':each.name})
                for route in get_list:
                    select_route = route.get('name')
                    route_link = route.get('route')
                    module= route.get('module')
                    doc.append('permission_list',{
                                'select_route':select_route,
                                'route_link':route_link,
                                'module':module
                    })
                doc.insert()
                doc.save()
                frappe.db.commit()


@frappe.whitelist()
def add_new_routes_to_existing(doc,method=None):
    try:
        get_value = frappe.db.get_list('Roles Permission')
        get_routes = frappe.db.get_list('Routes')
        for each in get_value:
            if not frappe.db.exists("Permission List", {"parent": each.name, "select_route": doc.name,"route_link": doc.route}, cache=True):
                child_doc = frappe.get_doc({"doctype": "Permission List","parentfield":"permission_list", "parent": each.name, "select_route": doc.name, "route_link": doc.route,"parenttype":"Roles Permission"})
                child_doc.insert(ignore_permissions=True,ignore_links=True)
                frappe.db.commit()
                
    except Exception as e:
        print(str(e))