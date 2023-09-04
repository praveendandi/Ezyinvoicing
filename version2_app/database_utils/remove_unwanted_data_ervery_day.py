import frappe,json
from datetime import date, datetime, timedelta



def remove_data_from_database_every_day():
    tables = ['Version','tabError Log','Scheduled Job Log','__global_search','tabArrival Activities','Email Queue']
    for table in tables:
        if table == 'tabError Log':
            frappe.log_error("Ezy-delete_error_logs", "test")
            days_before = (date.today() - timedelta(days=30)).isoformat()
            frappe.db.delete("Error Log", {"creation": ["<=", str(days_before)]})
            frappe.db.commit()
        elif table == 'tabArrival Activities':
            last_week = datetime.now() - timedelta(days=2)
            arrival_activity = frappe.db.get_all(
                "Arrival Activities",
                filters={"creation": ["<", last_week]},
                fields=["name", "file_path"],
            )
            frappe.db.sql(
                """DELETE FROM `tabArrival Activities` WHERE creation < %s""", last_week
            )
            frappe.db.commit()
            for each in arrival_activity:
                frappe.db.delete("File", {"file_url": each["file_path"]})
                frappe.db.commit()
        elif table == 'Email Queue':
            lastdate = date.today() - timedelta(days=1)
            emaildata = frappe.db.get_list(
                "Email Queue",
                filters={"creation": [">", lastdate], "status": "Sent"},
                fields=["name", "attachments"],
            )
            filelist = []
            if len(emaildata) > 0:
                for each in emaildata:
                    value = json.loads(each.attachments)
                    filelist.append(value[0]["fid"])
                    delete = frappe.delete_doc("File", value[0]["fid"])
                    print(delete)
            lastdate = date.today() - timedelta(days=6)
            frappe.db.sql("""DELETE FROM `tabDocument Bin` WHERE creation < %s""", lastdate)
            frappe.db.commit()
        elif table == 'Version':
            days_before = (date.today() - timedelta(days=60)).isoformat()
            frappe.db.delete("Version", {"creation": ["<=", str(days_before)]})
            frappe.db.commit()
        else:
            frappe.db.truncate(table)