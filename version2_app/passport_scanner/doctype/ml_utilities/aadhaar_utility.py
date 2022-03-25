import frappe
import requests


@frappe.whitelist(allow_guest=True)
def fetch_aadhaar_details(image_1=None, image_2=None):
    try:
        company = frappe.get_last_doc("company")
        post_data = {
            "base": image_1 if image_1 is not None else image_2,
            "thresh": 0.5,
            "class": "aadhaar",
            "version": "v1",
        }
        image_response = requests.post(
            company.detection_api,
            json=post_data,
        )
        image_response = image_response.json()
        return {"success": True, "data": image_response}
    except Exception as e:
        frappe.log_error(str(e), "fetch_aadhaar_details")
        return {"success": False, "message": str(e)}
