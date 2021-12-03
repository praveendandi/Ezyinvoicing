from os import initgroups
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from urllib.request import urlretrieve
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

import time,json
import datetime
import frappe
import sys,traceback
import base64


driver = ''

'''
page delay 
'''
global_delay = 3


'''
intiate 
'''
data = {
    # "surname": "Ankireddypalli",
    # "given_name": "sumanth",
    # "gender": "M",
    # "date_of_birth": "29/07/1992",
    # "applicantSplCategory": "3",
    # "nationality": "EGY",
    # "address": "madhapur",
    # "city": "Hyderabad",
    # "country": "EGY",
    # "hotelAddress": "need to concat",
    # "hote_state": "ANDHRA PRADESH",
    # "hotel_city": "YSR DISTRICT KADAPA",
    # "hotel_pincode": "500081",
    # "passport_number": "1234848445",
    # "passport_place_of_issued_city": "hyderabad",
    # "passport_place_of_issued_country": "ALBANIA",
    # "passport_date_of_issue": "29072010",
    # "passport_valid_till": "29072025",
    # "visa_number": "1234567",
    # "visa_place_of_issued_city": "hyderabad",
    # "visa_place_of_issued_country": "ALBANIA",
    # "visa_date_of_issue": "29072000",
    # "visa_valid_till": "29072000",
    # "visa_type": "BUSINESS VISA",
    # "visa_sub_type": "",
    # "arrival_from_country": "ALBANIA",
    # "arrival_from_city": "Hyderabad",
    # "arrival_place": "Hyderabad",
    # "date_of_arrival_in_india": "24/10/2021",
    # "checkin_date": "24/10/2021",
    # "checkin_time": "12:00",
    # "no_of_nights": "2",
    # "whether_employed_in_india": "",
    # "purpose_of_visit": "Accompanying Parents",
    # "next_destination": "O",
    # "next_destination_place": "banglore",
    # "next_destination_state": "ANDHRA PRADESH",
    # "next_destination_city": "YSR DISTRICT KADAPA",
    # "next_destination_country": "EGY",
    # "contact_phone_no": "85452459",
    # "contact_mobile_no": "7145626839896",
    # "permanent_phone_no": "4754986245",
    # "permanent_mobile_no": "45456545585",
    # "remarks": "jge uer uer duyfuerb"
}

folder_path = frappe.utils.get_bench_path()
def intiate():
    try:
        # print(data)
        global driver
        company = frappe.get_last_doc('company')
        options = Options()
        options.add_argument("--headless")
        # options.headless = True if company.cform_chrome_headless == 1 else False
        driver = webdriver.Chrome(
            folder_path+'/apps/version2_app/version2_app/passport_scanner/doctype/guest_details/chromedriver',chrome_options=options)
        driver.get("https://indianfrro.gov.in/frro/FormC")
        myElem = WebDriverWait(driver, global_delay).until(
            EC.presence_of_element_located((By.ID, 'capt')))
        print(driver.title)
        download = download_captcha()
        if download["success"] == False:
            return download
        return {"success": True,"message": "CForm initiated successfully"}
    except TimeoutException:
        print("time exceed")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("intiate","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":"timeout"}

'''download captcha image form screen'''

def convert_image_to_base64(image):
    try:
        with open(image, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        encoded_str = encoded_string.decode("utf-8")
        # print(encoded_str)
        return {"success":True, "data":encoded_str}
    except Exception as e:
        print(str(e),"====================")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("CForm-convert image to base64","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def download_captcha():
    try:
        company = frappe.get_last_doc("company")
        driver.find_element_by_id('capt').screenshot(folder_path+'/apps/version2_app/version2_app/passport_scanner/doctype/guest_details/captcha/test.png')
        convert_base = convert_image_to_base64(folder_path+'/apps/version2_app/version2_app/passport_scanner/doctype/guest_details/captcha/test.png')
        if convert_base["success"] == False:
            return convert_base
        frappe.publish_realtime("custom_socket", {'message': 'Captcha Image', 'data': convert_base["data"]})
        return {"success": True}
        # username = company.cform_user_name
        # password = company.cform_password
        # captcha_text = input('Enter captcha: ')
        # login_cform(username, password, captcha_text)
    except Exception as e:
        print(str(e),"====================")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("CForm-download captcha","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}



'''refresh captcha'''

@frappe.whitelist(allow_guest=True)
def refresh_captcha():
    try:
        refresh_butoon = driver.find_element_by_xpath(
            '//*[@title="Refresh Image"]')
        refresh_butoon.click()
        download = download_captcha()
        if download["success"] == False:
            return download
        return {"success": True,"message": "CForm initiated successfully"}
    except Exception as e:
        print(str(e),"===================================")
        return {"success": False,"message": str(e)}


'''
enter userid password and captcha image
'''

@frappe.whitelist(allow_guest=True)
def login_cform():
    try:
        global data
        cform_data=json.loads(frappe.request.data)
        login_details = cform_data["data"]
        company = frappe.get_last_doc('company')
        if len(login_details["data"])>0:
            company_doc = frappe.get_doc('company',company.name)
            company_doc.cform_session = 1
            company_doc.save(ignore_permissions=True,ignore_version=True)
            for index, each in enumerate(login_details["data"]):
                each_data = frappe.db.get_value("Guest Details",each,["surname","given_name","gender","date_of_birth","select_category",
                "nationality","address","city","country","passport_number","passport_place_of_issued_city",
                "passport_place_of_issued_country","passport_date_of_issue","passport_valid_till","visa_number","visa_place_of_issued_city","visa_place_of_issued_country",
                "visa_date_of_issue","visa_valid_till","visa_type","visa_sub_type","arrival_from_country","arrival_from_city","arrival_place",
                "date_of_arrival_in_india","checkin_date","checkin_time","no_of_nights","whether_employed_in_india","purpose_of_visit","next_destination","next_destination_place",
                "next_destination_state","next_destination_city","next_destination_country","contact_phone_no","contact_mobile_no","permanent_phone_no","permanent_mobile_no","remarks","face_image","name"], as_dict=1)
                each_data["hotelAddress"] = company.address_1+" ,"+company.address_2
                each_data["hote_state"] = company.state
                each_data["hotel_city"] = company.city
                each_data["hotel_pincode"] = company.pincode
                if each_data["date_of_birth"]:
                    each_data["date_of_birth"] = each_data["date_of_birth"].strftime("%d/%m/%Y")
                if each_data["passport_date_of_issue"]:
                    each_data["passport_date_of_issue"] = each_data["passport_date_of_issue"].strftime("%d%m%Y")
                if each_data["passport_valid_till"]:
                    each_data["passport_valid_till"] = each_data["passport_valid_till"].strftime("%d%m%Y")
                if each_data["visa_date_of_issue"]:
                    each_data["visa_date_of_issue"] = datetime.datetime.strptime(each_data["visa_date_of_issue"], '%Y-%m-%d').strftime("%d%m%Y")
                if each_data["visa_valid_till"]:
                    each_data["visa_valid_till"] = datetime.datetime.strptime(each_data["visa_valid_till"], '%Y-%m-%d').strftime("%d%m%Y")
                if each_data["date_of_arrival_in_india"]:
                    each_data["date_of_arrival_in_india"] = each_data["date_of_arrival_in_india"].strftime("%d/%m/%Y")
                if each_data["checkin_date"]:
                    each_data["checkin_date"] = each_data["checkin_date"].strftime("%d/%m/%Y")
                if each_data["checkin_time"]:
                    each_data["checkin_time"] = str(each_data["checkin_time"])
                each_data = {k: "" if not v else v for k, v in each_data.items()}
                data = each_data
                if index == 0:
                    user_id = login_details["user_id"]
                    password = login_details["password"]
                    captcha = login_details["captcha"]
                    username = driver.find_element_by_name('uid')
                    username.clear()
                    username.send_keys(user_id)

                    passcode = driver.find_element_by_name('pwd')
                    passcode.clear()
                    passcode.send_keys(password)

                    captcha_text = driver.find_element_by_name('captchaval')
                    captcha_text.clear()
                    captcha_text.send_keys(captcha)

                    login = driver.find_elements_by_class_name("loginButton")
                    if len(login) > 0:
                        login[0].click()

                    WebDriverWait(driver, 3).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                    login = login_success()
                    if login["success"] == False: 
                        get_count = frappe.get_doc("Guest Details",each)
                        if get_count.frro_failure_count:
                            get_count.frro_failure_count = str(int(get_count.frro_failure_count)+1)
                        else:
                            get_count.frro_failure_count = str(0+1)
                        get_count.save(ignore_permissions=True, ignore_version=True)
                        frappe.db.commit()
                        return login
                elif index > 0:
                    mulcform = multiple_cforms(each_data)
                    if mulcform["success"]==False:
                        get_count = frappe.get_doc("Guest Details",each)
                        if get_count.frro_failure_count:
                            get_count.frro_failure_count = str(int(get_count.frro_failure_count)+1)
                        else:
                            get_count.frro_failure_count = str(0+1)
                        get_count.save(ignore_permissions=True, ignore_version=True)
                        frappe.db.commit()
                        return mulcform
            company_doc.cform_session = 0
            company_doc.save(ignore_permissions=True,ignore_version=True)
            return {"success":True,"message":"Guest uploaded to cform"}
    except TimeoutException:
        print("no alert")
        login = login_success()
        if login["success"] == False:
            return login

        # driver.find_element_by_name("Loginform").submit()

    except Exception as e:
        print(str(e),"-----------------------")
        company = frappe.get_last_doc('company')
        company_doc = frappe.get_doc('company',company.name)
        company_doc.cform_session = 0
        company_doc.save(ignore_permissions=True,ignore_version=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_obj, exc_tb,exc_tb.tb_lineno)
        frappe.log_error("login cform","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


''' check login is success or not'''


def login_success():
    try:
        element = driver.find_element_by_partial_link_text("Logout")
        checkin = intiate_checkin_process()
        if checkin["success"] == False:
            return checkin
        return {"success": True}
    except NoSuchElementException:
        print("login unsuccess")
        # intiate_checkin_process()
        check_invalid = check_invalid_details()
        if check_invalid["success"] == False:
            return check_invalid
        return {"success": True}
    except Exception as e:
        print(str(e),"+++++++++++++++++")
        company = frappe.get_last_doc('company')
        company_doc = frappe.get_doc('company',company.name)
        company_doc.cform_session = 0
        company_doc.save(ignore_permissions=True,ignore_version=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_obj, exc_tb,exc_tb.tb_lineno)
        frappe.log_error("login success","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


def check_invalid_details():
    try:
        wait = WebDriverWait(driver, global_delay)
        wait.until(EC.visibility_of_element_located((By.ID, 'err0')))
        error_message = driver.find_element_by_id('err0')
        print(error_message.text)
        if error_message.text == 'Wrong Userid Or Password':
            print("invalid username")
            return {"success":False,"message":"Wrong Userid Or Password"}
        else:
            print("invalid captcha")
            refresh_cap = refresh_captcha()
            if refresh_cap["success"] == False:
                return refresh_captcha
            return {"success":True}
    except NoSuchElementException:
        print("not invalid captcha issue")
        return {"success": False, "message": "not invalid captcha"}
    except Exception as e:
        print(str(e),"/////////////////////////")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_obj, exc_tb,exc_tb.tb_lineno)
        frappe.log_error("check invalid details","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


'''route to checkin page'''


def intiate_checkin_process():
    try:
        lnks = driver.find_elements_by_tag_name("a")
        for lnk in lnks:
            # get_attribute() to get all href
            # print(lnk.get_attribute('href'))
            if 'formc.jsp' in lnk.get_attribute('href'):
                # driver.find_element_by_partial_link_text(lnk.get_attribute('href')).click()
                lnk.click()
                check = checkin_cform()
                if check["success"] == False:
                    return check
                return {"success":True}
        pass
    except Exception as e:
        print(str(e),"..........................")
        company = frappe.get_last_doc('company')
        company_doc = frappe.get_doc('company',company.name)
        company_doc.cform_session = 0
        company_doc.save(ignore_permissions=True,ignore_version=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_obj, exc_tb,exc_tb.tb_lineno)
        frappe.log_error("intiate checkin process","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


'''start checkin'''


def checkin_cform():
    try:
        '''wait until page settle'''
        myElem = WebDriverWait(driver, global_delay).until(
            EC.presence_of_element_located((By.ID, 'Filerfno')))
        '''uplaod face image'''
        company = frappe.get_last_doc("company")
        if "private" in data["face_image"]:
            driver.find_element_by_id("file1").send_keys(folder_path+"/sites/"+company.site_name+data["face_image"])
        else:
            driver.find_element_by_id("file1").send_keys(folder_path+"/sites/"+company.site_name+"/public"+data["face_image"])
        driver.find_element_by_xpath(
            "//input[@value='Upload File'][@type='button']").click()
        '''accept success alert'''
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()

        '''enter form deatils'''

        applicant_surname = driver.find_element_by_id('applicant_surname')
        applicant_surname.send_keys(data['surname'])

        applicant_givenname = driver.find_element_by_id('applicant_givenname')
        applicant_givenname.send_keys(data['given_name'])

        applicant_sex = Select(driver.find_element_by_id('applicant_sex'))
        applicant_sex.select_by_value(data['gender'])

        dobformat = Select(driver.find_element_by_name('dobformat'))
        dobformat.select_by_value('DY')

        applicant_dob = driver.find_element_by_id('applicant_dob')
        applicant_dob.send_keys(data['date_of_birth'])

        applicant_special_category = Select(
            driver.find_element_by_id('applicant_special_category'))
        applicant_special_category.select_by_value(
            data['select_category'])

        applicant_nationality = Select(
            driver.find_element_by_id('applicant_nationality'))
        applicant_nationality.select_by_value(data['nationality'])

        applicant_permaddr = driver.find_element_by_id('applicant_permaddr')
        applicant_permaddr.send_keys(data['address'])

        applicant_permcity = driver.find_element_by_id('applicant_permcity')
        applicant_permcity.send_keys(data['city'])

        applicant_permcountry = Select(
            driver.find_element_by_id('applicant_permcountry'))
        applicant_permcountry.select_by_value(data['country'])

        applicant_refaddr = driver.find_element_by_id('applicant_refaddr')
        applicant_refaddr.send_keys(data['hotelAddress'])

        applicant_refstate = Select(
            driver.find_element_by_id('applicant_refstate'))
        applicant_refstate.select_by_visible_text(data['hote_state'].upper())
        time.sleep(1)

        applicant_refstatedistr = Select(
            driver.find_element_by_id('applicant_refstatedistr'))
        applicant_refstatedistr.select_by_visible_text(
            data['hotel_city'].upper())

        applicant_refpincode = driver.find_element_by_id(
            'applicant_refpincode')
        applicant_refpincode.send_keys(data['hotel_pincode'])

        applicant_passpno = driver.find_element_by_id('applicant_passpno')
        applicant_passpno.send_keys(data['passport_number'])

        applicant_passplcofissue = driver.find_element_by_id(
            'applicant_passplcofissue')
        applicant_passplcofissue.send_keys(
            data['passport_place_of_issued_city'])

        passport_issue_country = Select(driver.find_element_by_id(
            'passport_issue_country'))
        passport_issue_country.select_by_value(
            data['passport_place_of_issued_country'])

        applicant_passpdoissue = driver.find_element_by_id(
            'applicant_passpdoissue')
        applicant_passpdoissue.click()
        applicant_passpdoissue.send_keys(data["passport_date_of_issue"])

        applicant_passpvalidtill = driver.find_element_by_id(
            'applicant_passpvalidtill')
        applicant_passpvalidtill.click()
        applicant_passpvalidtill.send_keys(data["passport_valid_till"])

        applicant_visano = driver.find_element_by_id('applicant_visano')
        applicant_visano.send_keys(data['visa_number'])

        applicant_visaplcoissue = driver.find_element_by_id(
            'applicant_visaplcoissue')
        applicant_visaplcoissue.send_keys(data['visa_place_of_issued_city'])

        visa_issue_country = Select(driver.find_element_by_id(
            'visa_issue_country'))
        visa_issue_country.select_by_value(
            data['visa_place_of_issued_country'])

        applicant_visadoissue = driver.find_element_by_id(
            'applicant_visadoissue')
        applicant_visadoissue.click()
        applicant_visadoissue.send_keys(data["visa_date_of_issue"])

        applicant_visavalidtill = driver.find_element_by_id(
            'applicant_visavalidtill')
        applicant_visavalidtill.click()
        applicant_visavalidtill.send_keys(data["visa_valid_till"])

        applicant_visatype = Select(driver.find_element_by_id(
            'applicant_visatype'))
        applicant_visatype.select_by_value(data['visa_type'])

        applicant_arrivedfromcountry = Select(driver.find_element_by_id(
            'applicant_arrivedfromcountry'))
        applicant_arrivedfromcountry.select_by_value(
            data['arrival_from_country'])

        applicant_arrivedfromcity = driver.find_element_by_id(
            'applicant_arrivedfromcity')
        applicant_arrivedfromcity.send_keys(data['arrival_from_city'])

        applicant_arrivedfromplace = driver.find_element_by_id(
            'applicant_arrivedfromplace')
        applicant_arrivedfromplace.send_keys(data['arrival_place'])

        driver.execute_script(
            'document.getElementById("applicant_doarrivalindia").value ="'+data['date_of_arrival_in_india']+'"')

        driver.execute_script(
            'document.getElementById("applicant_doarrivalhotel").value ="'+data['checkin_date']+'"')

        applicant_timeoarrivalhotel = driver.find_element_by_id(
            'applicant_timeoarrivalhotel')
        applicant_timeoarrivalhotel.send_keys(data['checkin_time'])

        applicant_intnddurhotel = driver.find_element_by_id(
            'applicant_intnddurhotel')
        applicant_intnddurhotel.send_keys(data['no_of_nights'])

        # # employed
        applicant_purpovisit = Select(driver.find_element_by_id(
            'applicant_purpovisit'))
        applicant_purpovisit.select_by_value(data['purpose_of_visit'])

        if(data['next_destination'] == 'I'):
            driver.find_element_by_css_selector('input[value="I"').click()

            applicant_next_destination_state_IN = Select(
                driver.find_element_by_id('applicant_next_destination_state_IN'))
            applicant_next_destination_state_IN.select_by_value(
                data['next_destination_state'])
            time.sleep(1)

            applicant_next_destination_city_district_IN = Select(
                driver.find_element_by_id('applicant_next_destination_city_district_IN'))
            applicant_next_destination_city_district_IN.select_by_value(
                data['next_destination_city'])

            applicant_next_destination_place_IN = driver.find_element_by_id(
                'applicant_next_destination_place_IN')
            applicant_next_destination_place_IN.send_keys(
                data['next_destination_place'])

        else:
            driver.find_element_by_css_selector('input[value="O"').click()

            applicant_next_destination_country_OUT = Select(
                driver.find_element_by_id('applicant_next_destination_country_OUT'))
            applicant_next_destination_country_OUT.select_by_value(
                data['next_destination_country'])

            applicant_next_destination_city_OUT = driver.find_element_by_id(
                'applicant_next_destination_city_OUT')
            applicant_next_destination_city_OUT.send_keys(
                data['next_destination_city'])

            applicant_next_destination_place_OUT = driver.find_element_by_id(
                'applicant_next_destination_place_OUT')
            applicant_next_destination_place_OUT.send_keys(
                data['next_destination_place'])

        applicant_contactnoinindia = driver.find_element_by_id(
            'applicant_contactnoinindia')
        applicant_contactnoinindia.send_keys(
            data['contact_phone_no'])

        applicant_mcontactnoinindia = driver.find_element_by_id(
            'applicant_mcontactnoinindia')
        applicant_mcontactnoinindia.send_keys(
            data['contact_mobile_no'])

        applicant_contactnoperm = driver.find_element_by_id(
            'applicant_contactnoperm')
        applicant_contactnoperm.send_keys(
            data['permanent_phone_no'])

        applicant_mcontactnoperm = driver.find_element_by_id(
            'applicant_mcontactnoperm')
        applicant_mcontactnoperm.send_keys(
            data['permanent_mobile_no'])

        applicant_remark = driver.find_element_by_id(
            'applicant_remark')
        applicant_remark.send_keys(
            data['remarks'])

        tmpsbmt = driver.find_element_by_id(
            'tmpsbmt')
        tmpsbmt.click()
        save = save_temp_success()
        if save["success"] == False:
            return save
        return {"success": True}
    except TimeoutException:
        print(",.,.,.,.,")
        print("error in checkin")
    except Exception as e:
        print(str(e),"====================")
        company = frappe.get_last_doc('company')
        company_doc = frappe.get_doc('company',company.name)
        company_doc.cform_session = 0
        company_doc.save(ignore_permissions=True,ignore_version=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("save temp success","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


multiple = False

def save_temp_success():
    try:
        '''wait until page settle'''
        myElem = WebDriverWait(driver, global_delay).until(
            EC.presence_of_element_located((By.ID, 'GetFileno')))
        '''extract cform number'''
        cform_id_html = driver.find_elements_by_tag_name("h1")[0]
        cform_id = cform_id_html.get_attribute('innerHTML')
        guest_doc = frappe.get_doc("Guest Details",data["name"])
        guest_doc.frro_id = cform_id.strip()
        guest_doc.uploaded_to_frro = 1
        guest_doc.status = "In House"
        guest_doc.frro_failure_count = 0
        guest_doc.save(ignore_permissions=True, ignore_version=True)
        frappe.publish_realtime("custom_socket", {'message': 'Cform Success', 'data': data["name"]})
        '''only devmode else comment'''
        if multiple:
            multiple_cforms()
        return {"success":True}
    except TimeoutException:
        print("error in temp success")
    except Exception as e:
        print(str(e),"*****************")
        company = frappe.get_last_doc('company')
        company_doc = frappe.get_doc('company',company.name)
        company_doc.cform_session = 0
        company_doc.save(ignore_permissions=True,ignore_version=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("save temp success","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


def multiple_cforms(checkin_deatils):
    # checkin_cform()
    try:
        global data
        data = checkin_deatils
        menu_header = driver.find_elements_by_tag_name("a")
        menu_header[0].click()
        intiate = intiate_checkin_process()
        if intiate == False:
            return intiate
        return {"success":True}
    except Exception as e:
        print(str(e),"@@@@@@@@")
        company = frappe.get_last_doc('company')
        company_doc = frappe.get_doc('company',company.name)
        company_doc.cform_session = 0
        company_doc.save(ignore_permissions=True,ignore_version=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("multiple cforms","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}