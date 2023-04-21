import frappe
import pandas as pd

 
@frappe.whitelist(allow_guest=True)
def migrating_routes():
    folder_path = frappe.utils.get_bench_path()
    file_path = folder_path +"/apps/version2_app/version2_app/migrate_routes/EzyInvRoutes.xlsx"
    dataframe1 = pd.read_excel(file_path)
    data = dataframe1.to_dict("records")
    print(data)
    for i in data:
        if not frappe.db.exists("Routes",{"route_name":i['Route Name'],"route":i['Route']}):
            routes_data= frappe.get_doc({"doctype":"Routes","route_name":i['Route Name'],"route":i['Route']})
            routes_data.insert()



