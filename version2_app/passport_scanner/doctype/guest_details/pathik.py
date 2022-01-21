import time
from urllib.request import urlretrieve

import frappe
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options

pathik_url = 'https://pathik.guru/'
add_guest_url = 'https://pathik.guru/dashboard/add'

# userId = 'marriott.com'
# password = '1234@fourpoints'
driver = {}

global_delay = 30
folder_path = frappe.utils.get_bench_path()

guest_details = {
    "first_name": "sumanth",
    "middle_name": "kumar",
    "last_name": "reddy",
    "company_name": "caratred",
    "house_flat_no": "flat no 301",
    "address": "grc residency",
    "locality": "madhapur",
    "city": "hyderabad",
    "district": "hyderabad",
    "zip_code": "500081",
    "country": "India",
    "state": "Andhra Pradesh",
    "dob": "08-01-2022",
    "mobile_no": "8374141183",
    "phone_no": "8374141183",
    "email": "sumanth@cartared.com",
    "coming_from": "hyderabad",
    "going_to": "Goa",
    "doc_type": "Aadhar",
    "doc_no": "1234568",
    "room_no": "200",
    "checkin_date": "08-01-2022",
    "checkin_time": "02:15",
    "checkout_date": "08-01-2022",
    "checkout_time": "02:15",
    "child": "02",
    "adult": "01",
    "vehicle_type": "Bike",
    "vehicle_registration_no": "AP0423236",
    # 'customFile'



}

total_guest_details = []

def add_guest(driver):
    try:
        # data = guest_details
        driver.get(add_guest_url)
        for each in total_guest_details:
            if frappe.db.exists('Guest Details',each):
                data = frappe.db.get_value("Guest Details",each,["given_name as first_name","middle_name","given_name as last_name","guest_company_name as company_name","address","address2 as house_flat_no",
                                                                 "pathik_locality as locality", "city","pathik_district as district","pathik_country as country","postal_code as zip_code","pathik_state as state","date_of_birth as dob","permanent_mobile_no as mobile_no",
                                                                 "permanent_phone_no as phone_no","email","arrival_from_city as coming_from","next_destination_place as going_to","id_type as doc_type","passport_number","local_id_number","room_number as room_no",
                                                                 "checkin_date","checkin_time","checkout_date","checkout_time","no_of_children as child","no_of_adults as adult","vehicle_type","vehicle_number as vehicle_registration_no","confirmation_number"], as_dict=1) 
                data = { k: ('' if v is None else v) for k, v in data.items() }
                if data["doc_type"] == "Foreigner" or data["doc_type"] == "indianPassport":
                    data["doc_no"] = data["passport_number"]
                else:
                    data["doc_no"] = data["local_id_number"]
                if data["doc_type"] == "Foreigner" or data["doc_type"] == "indianPassport" or data["doc_type"] == "other":
                    data["doc_type"] = "Others"
                elif data["doc_type"] == "aadhaar":
                    data["doc_type"] = "Aadhar"
                elif data["doc_type"] == "driving":
                    data["doc_type"] = "Driving Licence"
                elif data["doc_type"] == "voterId":
                    data["doc_type"] = "Voter_ID"
                else:
                    pass
                data["checkin_date"] = data["checkin_date"].strftime("%b-%m-%Y")
                data["checkout_date"] = data["checkout_date"].strftime("%b-%m-%Y")
                data["checkin_time"] = str(data["checkin_time"])
                data["checkout_time"] = str(data["checkout_time"])
        
                first_name = driver.find_elements_by_name("first_name")
                first_name[0].send_keys(data['first_name'])

                middle_name = driver.find_elements_by_name("middle_name")
                middle_name[0].send_keys(data['middle_name'])

                last_name = driver.find_elements_by_name("last_name")
                last_name[0].send_keys(data['last_name'])

                company_name = driver.find_elements_by_name("company_name")
                company_name[0].send_keys(data['company_name'])

                house_flat_no = driver.find_elements_by_name("house_flat_no")
                house_flat_no[0].send_keys(data['house_flat_no'])

                address = driver.find_elements_by_name("address")
                address[0].send_keys(data['address'])

                locality = driver.find_elements_by_name("locality")
                locality[0].send_keys(data['locality'])

                city = driver.find_elements_by_name("city")
                city[0].send_keys(data['city'])

                district = driver.find_elements_by_name("district")
                district[0].send_keys(data['district'])

                zip_code = driver.find_elements_by_name("zip_code")
                zip_code[0].send_keys(data['zip_code'])

                country = driver.find_elements_by_name("country")
                select = Select(country[0])
                select.select_by_visible_text(data['country'])

                time.sleep(2)
                state = driver.find_elements_by_name("state")
                select_state = Select(state[0])
                select_state.select_by_visible_text(data['state'])

                # dob = driver.find_elements_by_name("dob")
                driver.execute_script(
                    f"document.getElementsByName('dob')[0].value  = '{data['dob']}'")

                mobile_no = driver.find_elements_by_name("mobile_no")
                mobile_no[0].send_keys(data['mobile_no'])

                phone_no = driver.find_elements_by_name("phone_no")
                phone_no[0].send_keys(data['phone_no'])

                email = driver.find_elements_by_name("email")
                email[0].send_keys(data['email'])

                coming_from = driver.find_elements_by_name("coming_from")
                coming_from[0].send_keys(data['coming_from'])

                going_to = driver.find_elements_by_name("going_to")
                going_to[0].send_keys(data['going_to'])

                doc_type = driver.find_elements_by_name("doc_type")
                select_doc_type = Select(doc_type[0])
                select_doc_type.select_by_visible_text(data['doc_type'])

                doc_no = driver.find_elements_by_name("doc_no")
                doc_no[0].send_keys(data['doc_no'])

                company = frappe.get_last_doc("company")
                documents = frappe.db.get_list("Guest Details",{"confirmation_number":data["confirmation_number"]},["id_image1"])
                multi_file = driver.find_element_by_id("customFile")
                for images in documents:
                    if "private" in images["id_image1"]:
                        multi_file.send_keys(folder_path+"/sites/"+company.site_name+images["id_image1"])
                    else:
                        multi_file.send_keys(folder_path+"/sites/"+company.site_name+"/public"+images["id_image1"])
                    
                room_no = driver.find_elements_by_name("room_no")
                room_no[0].send_keys(data['room_no'])

                # checkin_date = driver.find_elements_by_name("checkin_date")
                driver.execute_script(
                    f"document.getElementsByName('checkin_date')[0].value  = '{data['checkin_date']}'")

                # checkin_time = driver.find_elements_by_name("checkin_time")
                driver.execute_script(
                    f"document.getElementsByName('checkin_time')[0].value  = '{data['checkin_time']}'")

                # checkout_date = driver.find_elements_by_name("checkout_date")
                driver.execute_script(
                    f"document.getElementsByName('checkout_date')[0].value  = '{data['checkout_date']}'")

                # checkout_time = driver.find_elements_by_name("checkout_time")
                driver.execute_script(
                    f"document.getElementsByName('checkout_time')[0].value  = '{data['checkout_time']}'")

                # checkout_time[0].send_keys(data['checkout_time'])

                child = driver.find_elements_by_name("child")
                child[0].send_keys(data['child'])

                adult = driver.find_elements_by_name("adult")
                adult[0].send_keys(data['adult'])

                vehicle_type = driver.find_elements_by_name("vehicle_type")
                select_vehicle_type = Select(vehicle_type[0])
                select_vehicle_type.select_by_visible_text(data['vehicle_type'])
                # vehicle_type[0].send_keys(data['vehicle_type'])

                vehicle_registration_no = driver.find_elements_by_name(
                    "vehicle_registration_no")
                vehicle_registration_no[0].send_keys(data['vehicle_registration_no'])
                guest_doc = frappe.get_doc("Guest Details",each)
                guest_doc.pathik_status = "In House"
                guest_doc.pending_pathik = 1
                guest_doc.save(ignore_permissions=True,ignore_version=True)
                frappe.db.commit()
                frappe.publish_realtime("custom_socket", {'message': 'Pathik Upload', 'data': each})
        return {"success":True,"message":"Data uploaded successfully"}
    except Exception as e:
        frappe.log_error("CForm-intiate_pathik",str(e))
        return {"success":False,"message":str(e)}


def login(data, driver):
    try:
        print(total_guest_details)
        print(data)
        userId = driver.find_elements_by_name("email")
        userId[0].send_keys(data['userId'])
        password = driver.find_elements_by_name("password")
        password[0].send_keys(data['password'])
        login_button = driver.find_element_by_id("kt_login_signin_submit")
        login_button.click()
        myElem = WebDriverWait(driver, global_delay).until(
            EC.presence_of_element_located((By.ID, 'kt_header_menu')))
        add_guest_status = add_guest(driver)
        return add_guest_status
    except TimeoutException:
        return {"success":False,"message":"Unable to login"}
    except Exception as e:
        frappe.log_error("CForm-intiate_pathik",str(e))
        return {"success":False,"message":str(e)}


def intiate_pathik(obj,pathik_guest_details):
    try:
        folder_path = frappe.utils.get_bench_path()
        # print(data)
        global driver
        global data
        global total_guest_details
        total_guest_details = pathik_guest_details
        options = Options()
        options.add_argument("--headless")
        frappe.log_error("CForm-intiate_pathik",folder_path+'/apps/version2_app/version2_app/passport_scanner/doctype/guest_details/chromedriver')
        driver = webdriver.Chrome(folder_path+'/apps/version2_app/version2_app/passport_scanner/doctype/guest_details/chromedriver',chrome_options=options)
        driver.get(pathik_url)
        myElem = WebDriverWait(driver, global_delay).until(
            EC.presence_of_element_located((By.ID, 'kt_login_signin_submit')))
        print(driver.title)
        login_status = login(obj, driver)
        return login_status
    except TimeoutException:
        return {"success":False,"message":"Time exceed"}
    except Exception as e:
        frappe.log_error("CForm-intiate_pathik",str(e))
        return {"success":False,"message":str(e)}


# intiate({"userId": userId, "password": password})
