# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import base64
import math
import os
import random
import re
import sys
# import time

# import xmltodict
# import traceback

# from PIL import Image
from collections import OrderedDict
from datetime import date, datetime
from difflib import get_close_matches

# from pyzbar.pyzbar import decode, ZBarSymbol
from os.path import expanduser

import cv2
import dateparser
import frappe
import numpy as np
import requests
from frappe.model.document import Document
from scipy import ndimage
from version2_app.passport_scanner.doctype.ml_utilities.common_utility import convert_base64_to_image

date = str(date.today())
home = expanduser("~")
abs_path = os.path.dirname(os.getcwd())
basedir = abs_path + "/sites/"



class Reservations(Document):
    pass


@frappe.whitelist(allow_guest=True)
def file_parsing():
    try:
        with open("/home/caratred/Downloads/new_ocr.txt") as file:
            data = file.readlines()
        for each in data:
            split_line = each.split("|")
            remove_data = [x.replace("\n", "") for x in split_line]
            if len(remove_data) == 26 and remove_data[-1] == "RESERVED":
                if not frappe.db.exists(
                    {"doctype": "Reservations", "reservation_number": remove_data[16]}
                ):
                    reservation_data = {
                        "doctype": "Reservations",
                        "guest_first_name": remove_data[2],
                        "guest_last_name": remove_data[1],
                        "email": remove_data[3],
                        "contact_phone_no": remove_data[5].replace("+", ""),
                        "no_of_nights": remove_data[9],
                        "confirmation_number": remove_data[12],
                        "reservation_number": remove_data[16],
                        "status": "Pending",
                        "booking_status": "Pending",
                        "no_of_adults": remove_data[7],
                        "no_of_children": remove_data[8],
                    }
                    reservation_data["checkin_date"] = datetime.strptime(
                        remove_data[17], "%d-%b-%y"
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    reservation_data["checkout_date"] = datetime.strptime(
                        remove_data[18], "%d-%b-%y"
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    doc = frappe.get_doc(reservation_data)
                    doc.insert(ignore_permissions=True, ignore_links=True)
                    frappe.db.commit()
                else:
                    if remove_data[-1] == "RESERVED":
                        name = frappe.db.get_value(
                            "Reservations",
                            filters={"reservation_number": remove_data[16]},
                        )
                        rev_doc = frappe.get_doc("Reservations", name)
                        if rev_doc.booking_status == "Pending":
                            rev_doc.guest_first_name = remove_data[2]
                            rev_doc.guest_last_name = remove_data[1]
                            rev_doc.email = remove_data[3]
                            rev_doc.contact_phone_no = remove_data[5]
                            rev_doc.no_of_nights = remove_data[9]
                            rev_doc.confirmation_number = remove_data[12]
                            rev_doc.reservation_number = remove_data[16]
                            rev_doc.no_of_adults = remove_data[7]
                            rev_doc.no_of_children = remove_data[8]
                            rev_doc.checkout_date = datetime.strptime(
                                remove_data[18], "%d-%b-%y"
                            ).strftime("%Y-%m-%d %H:%M:%S")
                            rev_doc.checkin_date = datetime.strptime(
                                remove_data[17], "%d-%b-%y"
                            ).strftime("%Y-%m-%d %H:%M:%S")
                            rev_doc.save(ignore_permissions=True, ignore_version=True)
                            frappe.db.commit()
        return {"success": True, "message": "Reservations successfully added"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy file_parsing",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


CASCADE = os.path.join(
    abs_path,
    "apps/version2_app/version2_app/passport_scanner/doctype/reservations/",
    "Har_cascade.xml",
)
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)
rand_int = random.randint(0, 10000)

# API to detect faces of a document


def detect_faces(image_path, number):
    try:
        company = frappe.get_last_doc("company")
        image = cv2.imread(image_path)
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_path = basedir + company.site_name + "/private/files/face.jpeg"

        faces = FACE_CASCADE.detectMultiScale(
            image_grey, scaleFactor=1.16, minNeighbors=5, minSize=(30, 50), flags=0
        )
        for x, y, w, h in faces:
            sub_img = image[y - 20 : y + h + 95, x - 10 : x + w + 35]
            cv2.imwrite(face_path, sub_img)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)
            break
        return {"success": True, "data": face_path}
    except IndexError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy detect_faces",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


def text_getter(image_file):
    try:
        company = frappe.get_last_doc("company")
        url = "https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAWvJ0ftbmjXxz8-nfgU1OYw9bbYCRQnq0"
        header = {"Content-Type": "application/json"}
        body = {
            "requests": [
                {
                    "image": {
                        "content": image_file,
                    },
                    "features": [
                        {
                            "type": "DOCUMENT_TEXT_DETECTION",
                            "maxResults": 100,
                        }
                    ],
                    "imageContext": {"languageHints": ["en-t-iO-handwrit"]},
                }
            ]
        }
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://", "@")
            proxies = {
                "https": "https://"
                + company.proxy_username
                + ":"
                + company.proxy_password
                + proxyhost
            }
            response = requests.post(
                url, headers=header, json=body, proxies=proxies
            ).json()
        else:
            response = requests.post(url, headers=header, json=body).json()
        text = (
            response["responses"][0]["textAnnotations"][0]["description"]
            if len(response["responses"][0]) > 0
            else ""
        )
        return {"success": True, "data": text}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy text_getter",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


def aadhar_detect_text(image_file, doc_type):
    try:
        remove = [
            "GOVERNMENT OF INDIA",
            "Government of India",
            "Government of India",
            "Year of Birth",
            "/ Male",
            "GOVERNMENT OF IND",
            "Nent of India",
            "GOVERMENTER",
        ]
        unlike = [
            "UNIQUE IDENTIFICATION AUTHORITY",
            "OF INDIA",
            "Identification",
            "Bengaluru-560001",
            "-500001",
            "500001",
            "Bengaluru-580001",
            "560001",
            " WWW",
            "WWW",
            "-560001",
            "-560101",
            "560101",
            "uidai",
            "Aam Admi ka",
            "VvV",
            "he",
            "uldai",
            "uldal",
            "govin",
            "www",
            "A Unique Identification",
            "Www",
            "in",
            "gov",
            "of India",
            "uidai",
            "INDIA",
            "India",
            "www",
            "I",
            "1B 1ST",
            "MERI PEHACHAN",
            "1E 1B",
            "MERA AADHAAR",
            "Unique Identification Authority",
            "of India",
            "UNQUE IDENTIFICATION AUTHORITY",
            "1800 180 1947",
            "1800180 1947",
            "Admi ka Adhikar",
            "w",
            "ww",
            "S",
            "s",
            "1800 180 17",
            "WWW",
            "dai",
            "uidai",
            "Address",
            "1809 180 1947",
            "help",
            "AADHAAR",
            "160 160 1947",
            "Aadhaar",
            "180 18167",
            "Aadhaar-Aam Admi ka Adhikar",
            "gov in",
            "1947",
            "MERA AADHAAR MERI PEHACHAN",
            "38059606 3964",
            "8587 1936 9174",
            "Unique Identification Authority of India",
        ]
        # req_start = time.time()
        text_data = text_getter(image_file)
        if not text_data["success"]:
            return text_data
        text = text_data["data"]
        block = str(text).split("\n")
        if doc_type == "front":
            abc = [str(x) for x in block]
            dob_in = re.compile(
                r"[0-9]{4}|[0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4}"
            )
            date = dob_in.findall(text)
            date_of_birth = date[0]
            for y in date:
                find_date = re.search(
                    r"([0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4})", y
                )
                if find_date:
                    date_of_birth = y
            gender_list = ["MALE", "FEMALE", "Male", "Female"]
            gender = ""
            for x in block:
                for y in gender_list:
                    if y in x:
                        gender = y
            da_find = re.compile(
                r"([0-9]{2,4} [0-9]{2,4} [0-9]{2,4}|[0-9]+ [0-9]+|[0-9]{12})"
            )
            number = da_find.findall(text)
            number = [x for x in number if len(x) > 6]
            uid = number[0]
            for x in number:
                find_uid = re.search(r"([0-9]+ [0-9]+ [0-9]+)", x)
                if find_uid:
                    uid = x
            uid_number = re.sub(" ", "", uid)
            if len(uid_number) != 12:
                uid = ""
            if date_of_birth in uid:
                date_of_birth = ""
            na_find = re.compile(
                r"([a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+)"
            )
            noun = na_find.findall(text)
            noun = [
                x
                for x in noun
                if x not in remove
                if "GOVERNMENT" not in x
                if "Government" not in x
                if "Govern" not in x
                if "GOVERN" not in x
                if "Gove" not in x
                if "GOVE" not in x
                if "ERNMENT" not in x
                if "ernment" not in x
            ]
            person_details = {
                "Date_of_birth": date_of_birth,
                "sex": gender,
                "uid": uid,
                "name": noun[0],
            }
            return {"success": True, "data": person_details}
        elif doc_type == "back":
            final_address = []
            for x in block:
                if "Address" in x:
                    abc = block.index(x)
            address = block[abc:]
            regex = re.compile(
                r"([^a-zA-Z0-9-,./ ]|Address|govin|ligovin|help|No|www|o  |uidai)"
            )
            cannot = [regex.sub("", i) for i in address]
            cannot = [x for x in cannot if x not in unlike]
            unique_list = list(OrderedDict((element, None) for element in cannot))
            for x in unique_list:
                abc = x.lstrip("  ")
                abc = x.lstrip(" -")
                abc = x.lstrip(" ")
                final_address.append(abc)
            ind = [
                final_address.index(x)
                for x in final_address
                if re.search("([0-9]{6})", x)
            ]
            final_address = final_address[: ind[len(ind) - 1] + 1]
            abc = " ".join(x for x in final_address)
            final = abc.split()
            final_address = list(OrderedDict((element, None) for element in final))
            person_address = " ".join(x for x in final_address)
            pin_code = re.findall("([0-9]{6})", person_address)
            [
                final_address.remove(x)
                for x in final_address
                if re.search("([0-9]{6})", x)
            ]
            final_address.append(pin_code[0])
            person_address = " ".join(x for x in final_address)
            # pin_get = re.findall(r"[0-9]{6}", person_address)
            postal_code = ""
            state = ""
            address1 = ""
            address2 = ""
            person_address = (
                person_address.replace("W|O", "")
                .replace("W/O", "")
                .replace("w/o", "")
                .replace("w|o", "")
                .replace("D/O", "")
                .replace("d/o", "")
                .replace("d|o", "")
                .replace("D|O", "")
                .replace("d/o", "")
                .replace("s/o", "")
                .replace("s/o", "")
                .replace("S/O", "")
                .replace("s/o", "")
                .replace("S|O", "")
                .replace("s/o", "")
                .replace("s|o", "")
            )
            split_address = person_address.split(" ")
            if len(split_address) > 2:
                if (
                    split_address[0] == "DIO"
                    or split_address[0] == "WIO"
                    or split_address[0] == "AND"
                    or split_address[0] == "SIO"
                ):
                    split_address.pop(0)
                if (
                    split_address[1] == "DIO"
                    or split_address[1] == "WIO"
                    or split_address[1] == "AND"
                    or split_address[1] == "SIO"
                    or split_address[1] == "WIO"
                    or split_address[1] == "BO"
                ):
                    split_address.pop(1)
                person_address = " ".join(split_address)
            if person_address != "":
                if re.search(r"\d{6}", person_address):
                    postal_code_data = re.match(
                        r"^.*(?P<zipcode>\d{6}).*$", person_address
                    ).groupdict()["zipcode"]
                    postal_code = postal_code_data if len(postal_code_data) == 6 else ""
                if "," in person_address:
                    split_address = person_address.split(",")
                    address1 = ",".join(split_address[: len(split_address) // 2])
                    address2 = ",".join(split_address[len(split_address) // 2 :])
                else:
                    split_address = person_address.split(" ")
                    address1 = " ".join(split_address[: len(split_address) // 2])
                    address2 = " ".join(split_address[len(split_address) // 2 :])
            return {
                "success": True,
                "data": {
                    "person_address": person_address,
                    "postal_code": postal_code,
                    "state": state,
                    "address1": address1,
                    "address2": address2,
                },
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy aadhar_detect_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


def imgdeskew(image):
    try:
        company = frappe.get_last_doc("company")
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=7)
        lines = cv2.HoughLinesP(
            img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5
        )
        angles = []
        for x1, y1, x2, y2 in lines[0]:
            # cv2.line(img_before, (x1, y1), (x2, y2), (255, 0, 0), 3)
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            angles.append(angle)
        median_angle = np.median(angles)
        if (median_angle > -5) and (median_angle < 5):
            img_rotated = ndimage.rotate(image, median_angle)
            # print("Angle is {}".format(median_angle))
            cv2.imwrite(
                basedir
                + company.site_name
                + "/private/files/aadhar_cropped_skewed_image.jpeg",
                img_rotated,
            )
            with open(
                basedir
                + company.site_name
                + "/private/files/aadhar_cropped_skewed_image.jpeg",
                "rb",
            ) as f:
                base64_string = base64.b64encode(f.read()).decode()
            os.remove(
                basedir
                + company.site_name
                + "/private/files/aadhar_cropped_skewed_image.jpeg"
            )
            return {"success": True, "data": base64_string}
        else:
            cv2.imwrite(
                basedir
                + company.site_name
                + "/private/files/aadhar_cropped_skewed_image.jpeg",
                image,
            )
            # print("angle is more than 5")
            with open(
                basedir
                + company.site_name
                + "/private/files/aadhar_cropped_skewed_image.jpeg",
                "rb",
            ) as f:
                base64_string = base64.b64encode(f.read()).decode()
            os.remove(
                basedir
                + company.site_name
                + "/private/files/aadhar_cropped_skewed_image.jpeg"
            )
            return {"success": True, "data": base64_string}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy imgdeskewu",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


def image_processing(image):
    try:
        im = cv2.imread(image)
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        mx = (0, 0, 0, 0)  # biggest bounding box so far
        mx_area = 0
        for cont in contours:
            x, y, w, h = cv2.boundingRect(cont)
            area = w * h
            if area > mx_area:
                mx = x, y, w, h
                mx_area = area

        x, y, w, h = mx
        roi = im[y : y + h, x : x + w]
        output_data = imgdeskew(roi)
        if output_data["success"] is False:
            return output_data
        output = output_data["data"]
        return {"success": True, "data": output}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy image_processing",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}


# API to scan aadhar card images


@frappe.whitelist(allow_guest=True)
def scan_aadhar():
    try:
        base = frappe.local.form_dict.get("aadhar_image")
        doc_type = frappe.local.form_dict.get("scanView")
        company = frappe.get_last_doc("company")
        # api_time = time.time()
        # base = data['aadhar_image']
        # doc_type = data['scanView']
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/aadhardoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)
        details = ""
        croppedaadhar = image_processing(filename)
        if croppedaadhar["success"] is False:
            return croppedaadhar
        cropped_aadhar = croppedaadhar["data"]
        aadhar_text = aadhar_detect_text(base, doc_type)
        if aadhar_text["success"] is False:
            return aadhar_text
        details = aadhar_text["data"]
        details["base64_string"] = cropped_aadhar
        image_string = " "
        rand_int = str(datetime.now())
        face_detect = detect_faces(filename, rand_int)
        if face_detect["success"] is False:
            return face_detect
        face = face_detect["data"]
        os.remove(filename)
        if doc_type == "front":
            if os.path.isfile(face) is True:
                with open(face, "rb") as image:
                    image_string = base64.b64encode(image.read()).decode()
                faceimage_size = (
                    "{:,.0f}".format(os.path.getsize(face) / float(1 << 10)) + " KB"
                )
                os.remove(face)
                details["face"] = image_string
                details["doc_type"] = "front"
            if "error" in details.keys():
                if len(details.keys()) == 1:
                    details["success"] = False
                    return details
                elif len(details.keys()) > 1:
                    details["success"] = False
                    return details
            elif "error" not in details.keys():
                details["success"] = True
                return details
        elif doc_type == "back":
            if "error" in details.keys():
                details["success"] = False
                return details
            elif "error" not in details.keys():
                details["success"] = True
                details["doc_type"] = "back"
                return details

    except IndexError as e:
        company = frappe.get_last_doc("company")
        # api_time = time.time()
        base = frappe.local.form_dict.get("aadhar_image")
        doc_type = frappe.local.form_dict.get("scanView")
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/aadhardoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)

        details = {"base64_string": cropped_aadhar}
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy scan_aadhar",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "error": str(e),
            "success": False,
            "aadhar_details": details,
            "message": "Unable to scan Aadhar",
        }
    except Exception as e:
        company = frappe.get_last_doc("company")
        base = frappe.local.form_dict.get("aadhar_image")
        doc_type = frappe.local.form_dict.get("scanView")
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/aadhardoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)

        croppedaadhar = image_processing(filename)
        if croppedaadhar["success"] is False:
            return croppedaadhar
        cropped_aadhar = croppedaadhar["data"]
        details = {"base64_string": cropped_aadhar}
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy scan_aadhar",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "error": str(e),
            "success": False,
            "aadhar_details": details,
            "message": "Unable to scan Aadhar",
        }


def license_detect_text(image_file):
    try:
        # req_time = time.time()
        text_data = text_getter(image_file)
        if not text_data["success"]:
            return text_data
        text = text_data["data"]
        # logger.info(
        #     f"time elapsed for vision request is{time.time()-req_time}")
        text = re.sub("_", " ", text)
        block = str(text).split("\n")
        block = [x for x in block if "Form 7" not in x]

        dates = re.findall(
            r"(\d{2}\/\d{2}\/\d{4}|\d{2}\-\d{2}\-\d{4}|[0-9]{1,2}\-[A-Za-z]{3}\-[0-9]{2,4}|[0-9]{1,2} [A-Z0-9]{1,3} [0-9]{4})",
            text,
        )

        abc = len(dates)
        Date_of_birth = ""
        if abc > 0:
            get_date = [dates[i][6:10] for i in range(abc)]

            min_year = min(get_date)
            max_year = max(get_date)
            for x in list(set(dates)):
                if max_year in x:
                    expiryDate = x

                elif min_year in x:
                    Date_of_birth = x

                else:
                    date_of_issue = x

        no = re.findall(
            r"([A-Z]{2,6} [0-9]{4}\-[0-9]{5,7}|[A-Z]{2,6}\-[0-9]{2,6}\-[0-9]{2,6}|[A-Z]{1,3}\-[0-9]{3,5}\/[0-9]{5,7}|[A-Z0-9]{2,6} [0-9]{5,13}|[A-Z0-9]{2,5}\/[0-9]{2,6}\/[0-9]{1,4}\/[0-9]{1,4}\/[0-9]{1,4}|[A-Z0-9]{14,18}|[A-Z0-9]{3,5} [0-9]{2,4} [0-9]{7}|[A-Z0-9]{3,5}\-[0-9]{2,4}\-[0-9]{7}|[A-Z]{2}\-[0-9]{2}\/[0-9]{3,5}\/[0-9]{7}|[0-9]{1,2}\/[0-9]{3,4}\/[0-9]{4}|[A-Z]{1,2}\/[A-Z]{1,2}\/[0-9]{1,4}\/[0-9]{5,7}\/[0-9]{4}|[A-Z]{2,6}\-[0-9]{9,15}|[A-Z- ]{2,6}[0-9]{4,15}|[A-Z]{2}[0-9]{2}\/[A-Z]{3}\/[0-9]{5}\-[0-9]{2}\/[0-9]{4}|[A-Z]{1,2}\/[A-Z]{2}\/[0-9]{10}\/[0-9]{4}|[A-Z]{2}\-[0-9]{2} [0-9]{11}|[0-9]{4}\/[0-9]{4}|[A-Z]{2} [0-9]{2}\/[A-Z]{3}\/[0-9]{2}\/[0-9]{5})",
            text,
        )
        uid = ""
        try:
            try:
                if len(no) > 0:
                    licence_no = [x for x in no if len(x) >= 10]

                    if re.search(r"\d", licence_no[0]) is not None:
                        uid = licence_no[0]

            except Exception as e:
                no = [x for x in no if re.search(r"[0-9]{4}\/[0-9]{4}", x)]

                uid = no[0]
        except Exception as e:
            uid = ""
        address = []
        for x in block:
            if (
                "Address" in x
                or "ADDRESS" in x
                or "Address :" in x
                or "Add " in x
                or "Addess" in x
                or "ADORESS" in x
            ):
                abc = block.index(x)

                address = block[abc:]
                break
        person_address = ""
        if len(address) > 0:
            for x in address:
                if re.search(
                    r"([0-9]{6}|[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}|[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}|Holder|Issuing|Sign|licenced|Signature)",
                    x,
                ):
                    ind = address.index(x)
                    final_address = address[: ind + 1]
                    person_address = " ".join(x for x in final_address)
                    person_address = re.sub("[^A-Za-z0-9-,/ ]", "", person_address)

                    break
        if person_address != "":
            final_address = person_address.split()
            for x in final_address:
                if re.search(
                    r"([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}|[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}|Holder|Issuing|Signature|licenced)",
                    x,
                ):
                    ind = final_address.index(x)
                    final_address = final_address[:ind]
                    person_address = " ".join(x for x in final_address)

                    break
        elif person_address == "":
            for x in block:
                if x.startswith("AP") or x.startswith("TS") or x.startswith("DLFAP"):
                    abc = block.index(x)

                    address = block[abc + 3 :]

            if len(address) > 0:
                for x in address:
                    if re.search(
                        r"([0-9]{6}|[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2,4}|[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}|Holder|Issued|Sign|Signature|licenced)",
                        x,
                    ):
                        ind = address.index(x)
                        final_address = address[: ind + 1]
                        person_address = " ".join(x for x in final_address)
                        person_address = re.sub(
                            r"[^A-Za-z0-9-,/ ]|[0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4}",
                            "",
                            person_address,
                        )
                        break
        name = ""
        for x in block:
            if "Name" in x or "NAME" in x or "Nam " in x:
                abc = block.index(x)
                noun = block[abc]
                name = re.sub("[^A-Za-z]|Name|NAME|Nam|ATH ", "", noun)
                if name == "":
                    name = re.sub("DOB|D.O.B|-|/", "", block[abc + 1])
                    if re.search(r"\d", name) is not None:
                        name = block[abc + 2]
                        break
                break
        if name != "":
            if re.search("Designation|Original|RTA|[0-9]+", name):
                name = ""
        if name == "":
            for x in block:
                if "S/D/W of" in x:
                    abc = block.index(x)
                    noun = block[abc - 1]
                    name = noun
        if name == "":
            for x in block:
                if x.startswith("AP") or x.startswith("TS") or x.startswith("DLFAP"):
                    abc = block.index(x)
                    noun = block[abc + 1]
                    name = noun
        if name != "":
            if re.search(r"Designation|Original|RTA|[0-9]+|Slo", name):
                name = ""
        if person_address != "":
            pin_get = re.findall(r"[0-9]{6}", person_address)
            person_address = re.sub("Permanent|Signature", "", person_address)
            person_address = re.sub(
                "/Address|/Addess|/Ad|/ Address|/ Addess|/ Ad|Add|/Add|Addess|Ad",
                "Address",
                person_address,
            )
            person_address = re.sub("PIN", "", person_address)
            final_address = person_address.split()
            final_address = list(
                OrderedDict((element, None) for element in final_address)
            )
            if len(pin_get) > 0:
                for x in final_address:
                    abc = re.search("([0-9]{6})", x)
                    if abc:
                        no_pin = final_address.index(x)
                        final_address = final_address[:no_pin]
                final_address.append(pin_get[0])
                person_address = " ".join(x for x in final_address)
        address1 = ""
        address2 = ""
        postal_code = ""
        state = ""
        if person_address != "":
            person_address = re.sub(
                r"Issued on|Issued|Date of First Issue|ssued|DoB|[0-9]{2}\/[0-9]{2}\/[0-9]{4}|Addressress|Address|ADDRESS|address",
                "",
                person_address,
            )
            if re.search(r"\d{6}", person_address):
                postal_code_data = re.match(
                    r"^.*(?P<zipcode>\d{6}).*$", person_address
                ).groupdict()["zipcode"]
                postal_code = postal_code_data if len(postal_code_data) == 6 else ""
            if "," in person_address:
                split_address = person_address.split(",")
                address1 = ",".join(split_address[: len(split_address) // 2])
                address2 = ",".join(split_address[len(split_address) // 2 :])
            else:
                split_address = person_address.split(" ")
                address1 = " ".join(split_address[: len(split_address) // 2])
                address2 = " ".join(split_address[len(split_address) // 2 :])
        details = {
            "uid": uid,
            "Date_of_birth": Date_of_birth,
            "name": name,
            "person_address": person_address,
            "state": state,
            "postal_code": postal_code,
            "address1": address1,
            "address2": address2,
        }
        # logger.info(f"time elapsed for parse text is{time.time()-req_time}")
        return {"success": True, "data": details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy license_detect_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


# API to scan driving license images


@frappe.whitelist(allow_guest=True)
def scan_driving_license():
    try:
        company = frappe.get_last_doc("company")
        # api_time = time.time()
        file_type = frappe.local.form_dict.get("scanView")
        base = frappe.local.form_dict.get("driving_image")
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/driverdoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)
        details = ""
        details_data = license_detect_text(base)
        if not details_data["success"]:
            return details_data
        details = details_data["data"]
        drivingcropped = image_processing(filename)
        if not drivingcropped["success"]:
            return drivingcropped
        driving_cropped = drivingcropped["data"]
        details["base64_string"] = driving_cropped
        image_string = ""
        rand_int = str(datetime.now())
        face_detect = detect_faces(filename, rand_int)
        if not face_detect["success"]:
            return face_detect
        face = face_detect["data"]
        os.remove(filename)
        if file_type == "back":
            details = {k: v for k, v in details.items() if v}
        if os.path.isfile(face) is True:
            with open(face, "rb") as image:
                image_string = base64.b64encode(image.read()).decode()
            faceimage_size = (
                "{:,.0f}".format(os.path.getsize(face) / float(1 << 10)) + " KB"
            )
            os.remove(face)
            details["face"] = image_string
            details["doc_type"] = "front"
        if "error" in details.keys():
            if len(details.keys()) == 1:
                details["success"] = False
                face_ex = {
                    key: value for key, value in details.items() if key != "face"
                }
                return details
            elif len(details.keys()) > 1:
                face_ex = {
                    key: value for key, value in details.items() if key != "face"
                }
                details["success"] = True
                return details
        elif "error" not in details.keys():
            face_ex = {key: value for key, value in details.items() if key != "face"}
            details["success"] = True
            return details

    except IndexError as e:
        company = frappe.get_last_doc("company")
        base = frappe.local.form_dict.get("driving_image")
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/driverdoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)
        drivingcropped = image_processing(filename)
        if not drivingcropped["success"]:
            return drivingcropped
        driving_cropped = drivingcropped["data"]
        details = {"base64_string": driving_cropped}
        os.remove(filename)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy scan_driving",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "error": str(e),
            "message": "Unable to scan your id",
            "success": False,
            "driving_details": details,
        }
    except Exception as e:
        company = frappe.get_last_doc("company")
        base = frappe.local.form_dict.get("driving_image")
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/driverdoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)
        drivingcropped = image_processing(filename)
        if not drivingcropped["success"]:
            return drivingcropped
        driving_cropped = drivingcropped["data"]
        details = {"base64_string": driving_cropped}
        os.remove(filename)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy scan_driving",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "error": str(e),
            "message": "Unable to scan your id",
            "success": False,
            "driving_details": details,
        }


def pan_detect_text(image_file):
    try:
        company = frappe.get_last_doc("company")
        unlike = [
            "OF INDIA",
            "INCOME TAX DEPARTMENT",
            "Permanent Account Number",
            "s Name",
            "INDIA",
            "OF INDIA",
            "Birth",
        ]
        with open(image_file, "rb") as image:
            base64_image = base64.b64encode(image.read()).decode()
        url = "https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAWvJ0ftbmjXxz8-nfgU1OYw9bbYCRQnq0"
        header = {"Content-Type": "application/json"}
        body = {
            "requests": [
                {
                    "image": {
                        "content": base64_image,
                    },
                    "features": [
                        {
                            "type": "DOCUMENT_TEXT_DETECTION",
                            "maxResults": 100,
                        }
                    ],
                }
            ]
        }

        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://", "@")
            proxies = {
                "https": "https://"
                + company.proxy_username
                + ":"
                + company.proxy_password
                + proxyhost
            }
            response = requests.post(
                url, headers=header, json=body, proxies=proxies, verify=False
            ).json()
        else:
            response = requests.post(url, headers=header, json=body).json()
        text = (
            response["responses"][0]["textAnnotations"][0]["description"]
            if len(response["responses"][0]) > 0
            else ""
        )
        block = str(text).split("\n")
        bca = re.findall(r"\s([a-zA-Z]{5}\d{4}[a-zA-Z0-9]{1})", text)
        noun = re.compile(
            "([a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+)"
        )
        names = noun.findall(text)
        DOB = re.findall(r"\s(\d{2}\/\d{2}\/\d{4})", text)
        names = [x for x in names if x not in unlike]
        face_detect = detect_faces(image_file, bca[0])
        if not face_detect["success"]:
            return face_detect
        face = face_detect["data"]
        image_string = ""
        if os.path.isfile(face) is True:
            with open(face, "rb") as image:
                image_string = base64.b64encode(image.read()).decode()
            os.remove(face)
        if len(names) > 1:
            name = names[0]
            father_name = names[1]
        elif len(names) == 1:
            name = names[0]
            father_name = ""
        else:
            name = ""
            father_name = ""
        parsed_birth = str(
            dateparser.parse(DOB[0], settings={"DATE_ORDER": "DMY"}).date()
        )
        details = {
            "name": name,
            "father_name": father_name,
            "pan_no": bca[0],
            "date_of_birth": parsed_birth,
            "pan_face": image_string,
        }
        return {"success": True, "data": details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy pan_dete981492ct_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


# API to scan pan card images


@frappe.whitelist(allow_guest=True)
def scan_pancard():
    try:
        base = frappe.local.form_dict.get("pancard")
        company = frappe.get_last_doc("company")
        imagedata = base64.b64decode(base)
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/pan_document.jpeg"
        with open(filename, "wb") as f:
            f.write(imagedata)
        pan_details = pan_detect_text(filename)
        if not pan_details["success"]:
            return pan_details
        details = pan_details["data"]
        # consolelog.info("details extracted")
        os.remove(filename)
        return {"success": True, "details": details}
    except IndexError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy scan_pancard",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"error": str(e), "success": False, "message": "Unable to scan your id"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy scan_pancard",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


# def image_processing(image):
#     im = cv2.imread(image)
#     imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
#     ret, thresh = cv2.threshold(imgray, 127, 255, 0)
#     contours, hierarchy = cv2.findContours(
#         thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     mx = (0, 0, 0, 0)      # biggest bounding box so far
#     mx_area = 0
#     for cont in contours:
#         x, y, w, h = cv2.boundingRect(cont)
#         area = w*h
#         if area > mx_area:
#             mx = x, y, w, h
#             mx_area = area

#     x, y, w, h = mx
#     roi = im[y:y+h, x:x+w]
#     output = imgdeskew(roi)
#     return output


# def imgdeskew(image):
#     img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=7)
#     lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0,
#                             100, minLineLength=100, maxLineGap=5)

#     angles = []

#     for x1, y1, x2, y2 in lines[0]:
#         # cv2.line(img_before, (x1, y1), (x2, y2), (255, 0, 0), 3)
#         angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
#         angles.append(angle)
#     median_angle = np.median(angles)
#     if (median_angle > -5) and (median_angle < 5):
#         img_rotated = ndimage.rotate(image, median_angle)
#         # print("Angle is {}".format(median_angle))
#         cv2.imwrite(basedir+"/aadhar_cropped_skewed_image.jpeg", img_rotated)
#         with open(basedir+"/aadhar_cropped_skewed_image.jpeg", 'rb') as f:
#             base64_string = base64.b64encode(f.read()).decode()
#         os.remove(basedir+"/aadhar_cropped_skewed_image.jpeg")
#         return base64_string
#     else:
#         cv2.imwrite(basedir+"/aadhar_cropped_skewed_image.jpeg", image)
#         # print("angle is more than 5")
#         with open(basedir+"/aadhar_cropped_skewed_image.jpeg", 'rb') as f:
#             base64_string = base64.b64encode(f.read()).decode()
#         os.remove(basedir+"/aadhar_cropped_skewed_image.jpeg")
#         return base64_string


def voter_detect_text(image_file, doc_type):
    try:
        gender_list = ["MALE", "FEMALE", "Male", "Female"]
        ignore_list = [
            "ELECTION ",
            "ELECTION COMMISSION OF",
            "S NAME",
            "EECTOR PHOTO IDENTITY",
            "ELECTOR",
            "IDENTITY CARD",
            "IDENTITY CAR",
            "Date of Birth",
            "s Name",
            "HI FAM",
            "OF INDIA",
            "INDIA ",
            "INDIA PD",
            "s Name",
            "Date of Birtta",
            "IDENTITY CARD",
        ]
        # req_time = time.time()
        text_data = text_getter(image_file)
        if not text_data["success"]:
            return text_data
        text = text_data["data"]
        # logger.info(f"time elapsed for vision request is {time.time()-req_time}")
        block = str(text).split("\n")
        if doc_type == "front":
            for y in block:
                removesymbol = re.search(r"([a-zA-Z0-9]+)", y)
                if removesymbol is None:
                    block.remove(y)

            for x in block:
                if x == "Name:":
                    block.remove(x)
            base = re.compile(
                r'([a-zA-Z]{3}[0-9]{7}|[a-zA-Z]{3}[0-9]+|[a-zA-Z]{2}\/[0-9]{2}\/[0-9]{3}\/[0-9]{1,6})')
            data = base.findall(text)

            data = [x for x in data if len(x) > 5]
            regex = re.compile("(Age as on|Photo|hoto 10|er a 6|on Pv6|Age as on )")
            data = [regex.sub("", i) for i in data]
            id = ""
            if len(data) >= 1:
                for x in data:
                    if len(x) >= 5:
                        if "XXXX" not in x:
                            id = x
                            break
            else:
                id = ""
            sex = ""
            for x in block:
                for y in gender_list:
                    if y in x:
                        sex = y
            if sex == "":
                for x in block:
                    if "sex:" in x and "/" in x:
                        sex = x.split("/")[-1]
            noun = re.compile(
                "([a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+)"
            )
            name = noun.findall(text)
            for x in ignore_list:
                r = re.compile(x)
                if list(filter(r.match, name)):
                    match = list(filter(r.match, name))
                    if match[0]:
                        listmatch = match[0]
                        pop_dob = name.index(listmatch)
                        name.pop(pop_dob)
            for y in name:
                if y in ignore_list:
                    pop_dob = name.index(y)
                    name.pop(pop_dob)
            likes = [
                ".*ELECTION.* ",
                ".*Election Commission of.*",
                ".*Duplicate.*",
                ".*IIII.*",
                ".* Photo.*",
                ".*COMMISSION .*",
                ".*EPIC.*",
                ".*XIZ.*",
                ".*care.*",
                ".*card.*",
                ".*water.*",
                ".*ELECTION COMMISSION OF.*",
                ".*S NAME.*",
                ".*Age.*",
                ".*Eeron.*",
                ".*EECTOR PHOTO IDENTITY.*",
                "ELECTOR",
                ".*IDENTITY CARD.*",
                ".*IDENTITY.*",
                ".*Date of Birth.*",
                ".*s Name.*",
                ".*HI FAM.*",
                ".*OF INDIA.*",
                ".*INDIA.* ",
                ".*INDIA PD.*",
                ".*s Name.*",
                ".*Date of Birtta.*",
                ".*IDENTITY CARD.*",
            ]
            dob_in = re.compile(
                r"[0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4}|[0-9]{2}\/[0-9]{2}\/[0-9]+|[a-zA-Z]{2}\/[a-zA-Z]{2}\/[0-9]+"
            )
            date = dob_in.findall(text)
            date_of_birth = ""
            if len(date) >= 1:
                date_of_birth = date[0]
            else:
                if len(data) == 1:
                    if "Date of Birth" in text and data[0] in text:
                        date_of_birth = data[0]
            for x in likes:
                r = re.compile(x)
                if list(filter(r.match, name)):
                    match = list(filter(r.match, name))
                    if match[0]:
                        listmatch = match[0]
                        pop_dob = name.index(listmatch)
                        name.pop(pop_dob)
            person_name = ""
            if len(name) >= 1:

                regex = re.compile(
                    r"([^a-zA-Z0-9-/ ]|\d+|\-|I L AJ|DATE OF BIRTH|HI FAM|SPIC EN|EPALLI|Mother|Name |Father|Duplicate|EPISO|SAREE|HANDMADE|LADESH PADA|ESH ANDR E SE|Name:|NAME|EPIC|SERIES|IDENTITY CARD|HUSBAND|S NAME|card|ELECTOR|Elector|s Name|Husband|Smt|FATHER|Election Commission of|PICES|DUPLATE)"
                )
                name = [regex.sub("", i) for i in name]
                name = [
                    x.lstrip(" ")
                    for x in name
                    if x != ""
                    if x != "  "
                    if x != "   "
                    if x != " "
                    if len(x) >= 4
                ]
                if len(name) >= 1:

                    person_name = name[0]
            if id != "":
                for x in block:
                    abc = re.search(str(id), x)
                    if abc:
                        index_match = block.index(x)
                after_removeid = block[index_match + 1 :]

                regex = re.compile(
                    r"([^a-zA-Z0-9-/ ]|\d+|\-|HI FAM|AMERIC|SPIC EN|pre E|TRENICS|OR RAJ|EPALLI|Mother|Name |ipornpapers|Father|Duplicate|EPISO|SAREE|HANDMADE|LADESH PADA|ESH ANDR E SE|Name:|NAME|EPIC|SERIES|IDENTITY CARD|HUSBAND|S NAME|card|ELECTOR|Elector|s Name|Husband|Smt|FATHER|Election Commission of|PICES|DUPLATE)"
                )
                after_removeid = [regex.sub("", i) for i in after_removeid]
                after_removeid = [
                    x.lstrip(" ")
                    for x in after_removeid
                    if x != ""
                    if x != "  "
                    if x != "   "
                    if x != " "
                    if x != "EE EN"
                    if len(x) >= 4
                ]
                after_removeid = [x.rstrip(" ") for x in after_removeid]
                after_removeid = [x for x in after_removeid if len(x) > 4]

                person_name = after_removeid[0]

            person_details = {
                "uid": id,
                "name": person_name,
                "sex": sex,
                "Date_of_birth": date_of_birth,
            }
            # logger.info(f"time elapsed for parse text is {time.time()-req_time}")
            return {"success": True, "data": person_details}
        elif doc_type == "back":
            abc = ""
            person_address = ""
            date_of_birth = ""
            postal_code = ""
            state = ""
            for x in block:
                if "ADDRESS" in x:
                    abc = block.index(x)
                elif "Address" in x:
                    abc = block.index(x)
                elif "Addres" in x:
                    abc = block.index(x)
                elif "Addre" in x:
                    abc = block.index(x)
            if abc != "":
                date_of_birth = ""
                for x in block[:abc]:
                    find_date = re.compile(r"([0-9]{2}\/[0-9]{2}\/[0-9]{4})")
                    date_find = find_date.findall(x)
                    if len(date_find) == 1:
                        date_of_birth = date_find[0]
                final = block[abc:]
                regex = re.compile("([^a-zA-Z0-9-/ ]|Address|Addres|Addre|ADDRESS)")
                final = [regex.sub("", i) for i in final]
                last = ""
                for x in final:

                    if "Date" in x:
                        last = final.index(x)
                if last != "":
                    final_address = final[:last]
                else:
                    add_length = (len(final)) // 2
                    final_address = final[: add_length + 5]
                final_address = [
                    x
                    for x in final_address
                    if x != ""
                    if "ELECT" not in x
                    if len(x) > 3
                ]
                date_index = ""
                if len(final_address) > 10:
                    for x in final_address:
                        abc = re.search(r"([0-9]{2}\/[0-9]{2}\/[0-9]{4})", x)
                        if abc:
                            date_index = final_address.index(x)

                if date_index != "":
                    final_address = final_address[:date_index]
                extra_index = ""
                if len(final_address) > 1:
                    for x in final_address:
                        abc = re.search(r"Electoral|Facsimile|Assembly", x)
                        if abc:
                            extra_index = final_address.index(x)
                if extra_index != "":
                    final_address = final_address[:extra_index]
                address = " ".join(x for x in final_address)

                address = re.sub(
                    r"[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}|[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}|[a-zA-Z]{3}[0-9]{7}|/Locality|Village|Pin|Code|Date|Scanned|Resten|lector|Registration|Officer|Facsimile",
                    "",
                    address,
                )
                final_address = address.split()
                pincode = re.findall(r"[0-9]{6}", address)

                if len(pincode) > 0:
                    for x in final_address:
                        pin = re.search("([0-9]{6})", x)
                        if pin:
                            final_address.remove(x)
                    final_address.append(pincode[0])

                final_address = [x.rstrip(" ") for x in final_address]

                final_address = [
                    x.lstrip(" ")
                    for x in final_address
                    if "Signature" not in x
                    if x != "Eal"
                    if x != "of"
                    if x != "/"
                ]
                person_address = " ".join(x for x in final_address)
                pin_get = re.findall("[0-9]{6}", person_address)
                postal_code = ""
                state = ""
            address1 = ""
            address2 = ""
            if person_address != "":
                if re.search(r"\d{6}", person_address):
                    postal_code_data = re.match(
                        "^.*(?P<zipcode>\d{6}).*$", person_address
                    ).groupdict()["zipcode"]
                    postal_code = postal_code_data if len(postal_code_data) == 6 else ""
                if "," in person_address:
                    split_address = person_address.split(",")
                    address1 = ",".join(split_address[: len(split_address) // 2])
                    address2 = ",".join(split_address[len(split_address) // 2 :])
                else:
                    split_address = person_address.split(" ")
                    address1 = " ".join(split_address[: len(split_address) // 2])
                    address2 = " ".join(split_address[len(split_address) // 2 :])
            # logger.info(f"time elapsed for parse text is {time.time()-req_time}")
            return {
                "success": True,
                "data": {
                    "person_address": person_address,
                    "Date_of_birth": date_of_birth,
                    "postal_code": postal_code,
                    "state": state,
                    "address1": address1,
                    "address2": address2,
                },
            }
    except IndexError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy voter_detect_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy voter_detect_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


# API to scan voter card images


@frappe.whitelist(allow_guest=True)
def scan_votercard():
    try:
        company = frappe.get_last_doc("company")
        # api_time = time.time()
        # logger.info("api call hits")
        base = frappe.local.form_dict.get("voter_image")
        doc_type = frappe.local.form_dict.get("scanView")
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/voterdoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)
        details = ""
        votercropped = image_processing(filename)
        if not votercropped["success"]:
            return votercropped
        voter_cropped = votercropped["data"]
        details = voter_detect_text(base, doc_type)
        if not details["success"]:
            return details
        details = details["data"]
        # logger.info(details)
        details["base64_string"] = voter_cropped
        image_string = " "
        rand_int = str(datetime.now())
        face_detect = detect_faces(filename, rand_int)
        if not face_detect["success"]:
            return face_detect
        face = face_detect["data"]
        os.remove(filename)
        if doc_type == "front":
            if os.path.isfile(face) is True:
                with open(face, "rb") as image:
                    image_string = base64.b64encode(image.read()).decode()
                faceimage_size = (
                    "{:,.0f}".format(os.path.getsize(face) / float(1 << 10)) + " KB"
                )
                os.remove(face)
                # logger.info("face extracted")
                details["face"] = image_string
                details["doc_type"] = "front"
            if "error" in details.keys():
                if len(details.keys()) == 1:
                    details["success"] = False
                    face_ex = {
                        key: value for key, value in details.items() if key != "face"
                    }
                    # logger.info(
                    #     f"time elapsed for api request is {time.time()-api_time}")

                    return details
                elif len(details.keys()) > 1:
                    details["success"] = True
                    face_ex = {
                        key: value for key, value in details.items() if key != "face"
                    }
                    # logger.info(
                    #     f"time elapsed for api request is {time.time()-api_time}")

                    return details
            elif "error" not in details.keys():
                details["success"] = True
                face_ex = {
                    key: value for key, value in details.items() if key != "face"
                }
                # logger.info(
                #     f"time elapsed for api request is {time.time()-api_time}")
                return details
        elif doc_type == "back":
            if "error" in details.keys():
                details["success"] = False
                # logger.info(
                #     f"time elapsed for api request is {time.time()-api_time}")
                return details
            elif "error" not in details.keys():
                details["success"] = True
                details["doc_type"] = "back"
                # logger.info(
                #     f"time elapsed for api request is {time.time()-api_time}")
                return details

    except IndexError as e:
        company = frappe.get_last_doc("company")
        base = frappe.local.form_dict.get("voter_image")
        doc_type = frappe.local.form_dict.get("scanView")
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/voterdoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)
        votercropped = image_processing(filename)
        if not votercropped["success"]:
            return votercropped
        voter_cropped = votercropped["data"]
        details = {"base64_string": voter_cropped}
        os.remove(filename)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy scan_votercard",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "error": str(e),
            "message": "Unable to scan your id",
            "success": False,
            "voter_details": details,
        }
    except Exception as e:
        company = frappe.get_last_doc("company")
        base = frappe.local.form_dict.get("voter_image")
        doc_type = frappe.local.form_dict.get("scanView")
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/voterdoc.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)
        votercropped = image_processing(filename)
        if not votercropped["success"]:
            return votercropped
        voter_cropped = votercropped["data"]
        details = {"base64_string": voter_cropped}
        os.remove(filename)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy scan_votercard",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "error": str(e),
            "message": "Unable to scan your id",
            "success": False,
            "voter_details": details,
        }


class customException(Exception):
    pass


class textAnnotations(customException):
    """Raised when the no text is detected in an image"""

    pass


class NoneType(customException):
    """Raised when the value is not assigned to the variable"""

    pass


class listindexoutofrange(customException):
    """Raised when the text is not detected properly"""

    pass


def pass_detect_text(image_file):
    try:
        loss = []
        exact_length = []
        two_lines_mrz = []
        # req_time = time.time()
        text_data = text_getter(image_file)
        if not text_data["success"]:
            return text_data
        text = text_data["data"]
        # logger.info(f"time elapsed for vision request is{time.time()-req_time}")
        full_text = str(text).split("\n")
        reverse_text = full_text[::-1]
        ca = re.sub(r"\s+", "", str(reverse_text[2]))
        loss.append(ca)
        a = re.sub(r"\s+", "", str(reverse_text[1]))

        loss.append(a)
        for x in reverse_text:
            if len(x) >= 25:
                exact_length.append(x)

        line_first = re.sub(r"\s+", "", str(exact_length[1]))
        two_lines_mrz.append(line_first)
        line_second = re.sub(r"\s+", "", str(exact_length[0]))
        two_lines_mrz.append(line_second)
        first = two_lines_mrz[0]
        second = two_lines_mrz[1]
        Date_of_issue = ''
        if first[0] == "P" or second[0] == "P":

            passport_type = "\n".join(tuple(loss))

            type = first[0]
            date_issue = re.findall(
                r"\s([0-9][0-9] [a-zA-Z]+ \d{4}|\d{2}/\d{2}/\d{4}|\d{2}.\d{2}.\d{4}|\d{2} \w+/\w+ \d{4}|\d{2} \d{2} \d{4}|\d{2}-d{2}-d{4}|\d{2} \w+ /\w+ \d{2}|\d{2} \w+ \d{2}|\d{2} \w+/\w+ \d{2}|\d{2} \w+ \w+ \d{2}|\d{2}-\w+-\d{4}|\d{2} \w+\/ \w+ \d{4}|\d{2} \d{2}\. \d{4})",
                text,
            )
            static = [" ", ".", "/", "-"]
            dates = []
            Date_of_issue = " "
            try:
                for x in date_issue:
                    for y in static:
                        if y in (x):
                            if len(x) > 7:
                                dates.append(x)

                res = []
                [res.append(x) for x in dates if x not in res]
                parsed_issue = dateparser.parse(res[1], settings={"DATE_ORDER": "DMY"})
                if parsed_issue is None:
                    Date_of_issue = " "
                else:
                    issue_join = str((parsed_issue).date())
                    Date_of_issue = issue_join
            except:
                Date_of_issue = " "

            country_code = re.sub(r"\ |\?|\.|\!|\/|\;|\:|\<", " ", first[2:5])

            name_with_symbols = first[5:45]

            fullname = name_with_symbols.strip("<")
            name_spliting = fullname.split("<<")
            surname = re.sub(r"\ |\?|\.|\!|\/|\;|\:|\<|\>", " ", name_spliting[0])

            if len(name_spliting) == 2:
                mrx = re.sub(r"\ |\?|\.|\!|\/|\;|\:|\<|\>", " ", name_spliting[1])
                givenname = re.sub("[^A-Za-z0-9]+", " ", mrx)
                # print("given name:",givenname)
            else:
                givenname = ""

            document_no = second[0:9]
            passport_no = re.sub(r"[^\w]", " ", document_no)

            nationality = re.sub(r"\ |\?|\.|\!|\/|\;|\:|\<", " ", second[10:13])

            birthdate = second[13:19]
            birth_joindate = "/".join([birthdate[:2], birthdate[2:4], birthdate[4:]])
            parsed_birth = dateparser.parse(
                birth_joindate, settings={"DATE_ORDER": "YMD"}
            )
            if parsed_birth is None:
                date_of_birth = ""
            else:
                date_of_birth = str((parsed_birth).date())
                year = date_of_birth[0:4]

                present_date = datetime.now()
                present_year = present_date.year
                if str(present_year) < year:
                    two = date_of_birth[0:2]
                    remain = date_of_birth[2:]
                    full = two.replace(str(20), str(19))
                    date_of_birth = full + remain

            sex = second[20]
            if "М" in sex:
                sex = "Male"
            expiry_date = second[21:27]
            expiry_joindate = "/".join(
                [expiry_date[:2], expiry_date[2:4], expiry_date[4:]]
            )
            parsed_expiry = dateparser.parse(
                expiry_joindate, settings={"DATE_ORDER": "YMD"}
            )
            if parsed_expiry is None:
                date_of_expiry = " "
            else:
                date_of_expiry = str((parsed_expiry).date())
            if Date_of_issue == date_of_expiry or Date_of_issue == date_of_birth:
                Date_of_issue = " "
            data = {
                "Document_Type": type,
                "country_code": country_code,
                "FamilyName": surname,
                "Given_Name": givenname,
                "Date_of_Issue": Date_of_issue,
                "Passport_Document_No": passport_no,
                "Nationality": nationality,
                "Date_of_Birth": date_of_birth,
                "Gender": sex,
                "Date_of_Expiry": date_of_expiry,
                "type": "PASSPORT"
            }
            # details = {"type": "PASSPORT", "data": data}
            if date_of_expiry != " ":
                expiry = datetime.strptime(date_of_expiry, "%Y-%m-%d").date()
                today_date = datetime.now().date()
                if expiry <= today_date:
                    data["expired"] = True
                    return {
                        "success": True,
                        "data": data,
                        "message": "Passport is expired",
                        "expired": True
                    }
            # logger.info(
            #     f"time elapsed for text parse is{time.time()-req_time}")
            data["expired"] = False
            return {"success": True, "data": data, "expired": False}
        elif first[0] == "V" or second[0] == "V":
            visa_type = "\n".join(tuple(loss))
            Date_of_issue = ""
            type_of_visa = ''
            type = first[0]
            issuingcountry = re.sub(r"\ |\?|\.|\!|\/|\;|\:|\<", " ", first[2:5])
            if first[1].isalpha():
                date_issue = re.findall(
                    r"\s([0-9][0-9] [a-zA-Z]+ \d{4}|\d{2}/\d{2}/\d{4}|\d{2}.\d{2}.\d{4}|\d{2} \w+/\w+ \d{4}|\d{2} \d{2} \d{4}|\d{2}-d{2}-d{4}|\d{2} \w+ /\w+ \d{2}|\d{2} \w+/\w+ \d{4} \w+|\d{2}-\w+-\d{4}|\d{2} \w+\d{4})",
                    text,
                )
                static = [" ", ".", "/", "-"]
                dates = []
                for x in date_issue:
                    for y in static:
                        if y in (x):
                            if len(x) > 7:
                                dates.append(x)

                issue_date = []
                [issue_date.append(x) for x in dates if x not in issue_date]
                type_of_visa = first[1]
                Date_of_issue = " "
                try:
                    min_year = issue_date[0][6:10]
                    if len(issue_date) > 1:
                        min_year = min(
                            issue_date[0][6:10], issue_date[1][6:10])

                    for x in issue_date:
                        if min_year in x:
                            Date = x
                            parsed_issue = dateparser.parse(
                                Date, settings={"DATE_ORDER": "DMY"}
                            )
                            if parsed_issue is None:
                                Date_of_issue = " "
                            else:
                                issue_join = str((parsed_issue).date())
                                Date_of_issue = issue_join
                except:
                    Date_of_issue = " "
            elif first[1] == "<":
                date_issue = re.findall(
                    r"\s([0-9][0-9] [a-zA-Z]+ \d{4}|\d{2}/\d{2}/\d{4}|\d{2}.\d{2}.\d{4}|\d{2} \w+/\w+ \d{4}|\d{2} \d{2} \d{4}|\d{2}-d{2}-d{4}|\d{2} \w+ /\w+ \d{2}|\d{2} \w+/\w+ \d{4} \w+|\d{2}-\w+-\d{4})",
                    text,
                )
                static = [" ", ".", "/", "-"]
                dates = []
                for x in date_issue:
                    for y in static:
                        if y in (x):
                            if len(x) > 7:
                                dates.append(x)

                issue_date = []
                type_of_visa = " "
                Date_of_issue = " "
                try:
                    [issue_date.append(x)
                     for x in dates if x not in issue_date]

                    if len(issue_date) == 2:

                        Date = issue_date[1]
                        parsed_issue = dateparser.parse(
                            Date, settings={"DATE_ORDER": "DMY"}
                        )
                        if parsed_issue is None:
                            Date_of_issue = " "
                        else:
                            issue_join = str((parsed_issue).date())
                            Date_of_issue = issue_join

                    else:
                        Date = issue_date[0]
                        parsed_issue = dateparser.parse(
                            Date, settings={"DATE_ORDER": "DMY"}
                        )
                        if parsed_issue is None:
                            Date_of_issue = " "
                        else:
                            issue_join = str((parsed_issue).date())
                            Date_of_issue = issue_join
                except:
                    Date_of_issue = " "

            entries = ["MULTIPLE", "SINGLE", "DOUBLE"]
            entry = " "
            for y in full_text[::-1]:
                result = "".join(i for i in y if not i.isdigit())
                matched_entries = get_close_matches(result, entries)

                if len(matched_entries) == 1:
                    entry = matched_entries[0]
            name_with_symbols = (first[5:]).strip("<")
            fullname = name_with_symbols.split("<<")
            surname = re.sub(r"\ |\?|\.|\!|\/|\;|\:|\<|\>", " ", fullname[0])
            if len(fullname) == 2:
                mrx = re.sub(r"\ |\?|\.|\!|\/|\;|\:|\<|\>", " ", fullname[1])
                givenname = re.sub(r"[^A-Za-z0-9]+", " ", mrx)
            else:
                givenname = ""
            visa_number = re.sub(r"[^\w]", " ", second[0:9])
            nationality = re.sub(r"\ |\?|\.|\!|\/|\;|\:|\<", " ", second[10:13])
            birthdate = second[13:19]
            birth_joindate = "/".join([birthdate[:2], birthdate[2:4], birthdate[4:]])
            parsed_birth = dateparser.parse(
                birth_joindate, settings={"DATE_ORDER": "YMD"}
            )
            if parsed_birth is None:
                date_of_birth = ""
            else:
                date_of_birth = str((parsed_birth).date())
                year = date_of_birth[0:4]

                present_date = datetime.now()
                present_year = present_date.year
                if str(present_year) < year:
                    two = date_of_birth[0:2]
                    remain = date_of_birth[2:]
                    full = two.replace(str(20), str(19))
                    date_of_birth = full + remain
            sex = second[20]
            expiry_date = second[21:27]
            expiry_joindate = "/".join(
                [expiry_date[:2], expiry_date[2:4], expiry_date[4:]]
            )
            parsed_expiry = dateparser.parse(
                expiry_joindate, settings={"DATE_ORDER": "YMD"}
            )
            if parsed_expiry:
                date_of_expiry = " "
            else:
                date_of_expiry = str((parsed_expiry).date())
            if Date_of_issue == date_of_expiry or Date_of_issue == date_of_birth:
                Date_of_issue = " "
            optional_data = second[28:]
            data = {
                "Document_Type": type,
                "visa_Type": type_of_visa,
                "Issued_country": issuingcountry,
                "Visa_No_Of_Enteries": entry,
                "FamilyName": surname,
                "Visa_Issue_Date": Date_of_issue,
                "Given_Name": givenname,
                "Visa_Number": visa_number,
                "Nationality": nationality,
                "Date_of_Birth": date_of_birth,
                "Gender": sex,
                "Visa_Expiry_Date": date_of_expiry,
                "type": "VISA"
            }
            if date_of_expiry != " ":
                expiry = datetime.strptime(date_of_expiry, "%Y-%m-%d").date()
                today_date = datetime.now().date()
                if expiry <= today_date:
                    data["expired"] = True
                    return {
                        "success": True,
                        "data": data,
                        "message": "Visa is expired",
                        "expired": True,
                    }
            # logger.info(
            #     f"time elapsed for text parse is{time.time()-req_time}")
            data["expired"] = False
            return {"success": True, "data": data, "expired": False}
            # else:
            #     details={"type":"partial data","message":"image not scaned properly"}
            #     return
        else:
            return {"success": False, "data": "unable to scan image"}
    except IndexError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy pass_detect_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "success": False,
            "type": "partial data",
            "message": "Unable to scan your id",
            "error": str(e),
            "expired": False,
        }
    # except NoneType as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     frappe.log_error("SignEzy pass_detect_text","line No:{}\n{}".format(exc_tb.tb_lineno,str(e)))
    #     return ({"success":False, "type":"partial data","message":str(e),"expired":False})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy pass_detect_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "success": False,
            "type": "partial data",
            "message": "Unable to scan your id",
            "error": str(e),
            "expired": False,
        }


def rotate(imagepath, number):
    img = cv2.imread(imagepath)
    # get image height, width
    (h, w) = img.shape[:2]
    # calculate the center of the image
    center = (w / 2, h / 2)
    angle180 = 180
    scale = 1.0
    M = cv2.getRotationMatrix2D(center, angle180, scale)
    rotated180 = cv2.warpAffine(img, M, (w, h))
    cv2.imwrite(home + "/" + "xxxx" + str(number) + "rotate.jpeg", rotated180)
    path = home + "/" + "xxxx" + str(number) + "rotate.jpeg"
    return path


# API to scan passport and visa images


@frappe.whitelist(allow_guest=True)
def passportvisadetails():
    pass_visa_image = ""
    try:
        company = frappe.get_last_doc("company")
        # api_time = time.time()
        # startlog.info("api call hits")
        # file = request.form
        base = frappe.local.form_dict.get("Passport_Image")
        imgdata = base64.b64decode(base)
        convert_image = convert_base64_to_image(base, "passport_visa", basedir + company.site_name, company)
        if "success" in convert_image:
            return convert_image
        pass_visa_image = convert_image["message"]["file_url"]
        header = frappe.local.form_dict.get("scan_type")
        pass_details = pass_detect_text(base)
        if pass_details is None:
            return {"success": False, "message": "unable to scan your ID", "file_url": pass_visa_image}
        if not pass_details["success"]:
            pass_details["file_url"] = pass_visa_image
            return pass_details
        details = pass_details["data"]
        # startlog.info(details)
        unique_no = str(datetime.now())
        if details["type"] == "PASSPORT":
            no = details["Passport_Document_No"]
            unique_no = no[5:]
        elif details["type"] == "VISA":
            no = details["Visa_Number"]
            unique_no = no[5:]
        convert_image = convert_base64_to_image(base, "passport_visa", basedir + company.site_name, company)
        if "success" in convert_image:
            return convert_image
        pass_visa_image = convert_image["message"]["file_url"]
        #  elif details['type']=='partial data':
        #      rand_int=random.randint(0,10000)
        #      unique_no = rand_int
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/document.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)

        if header == "mobile":
            crop = rotate(filename, unique_no)
            fullimage_size = (
                "{:,.0f}".format(os.path.getsize(filename) / float(1 << 10)) + " KB"
            )
            face_detect = detect_faces(crop, unique_no)
            if not face_detect["success"]:
                return face_detect
            face = face_detect["data"]
            os.remove(crop)
            os.remove(filename)
        elif header == "web":
            fullimage_size = (
                "{:,.0f}".format(os.path.getsize(filename) / float(1 << 10)) + " KB"
            )
            face_detect = detect_faces(filename, unique_no)
            if not face_detect["success"]:
                return face_detect
            face = face_detect["data"]
            os.remove(filename)

        image_string = ""
        faceimage_size = ""
        if os.path.isfile(face) is True:
            with open(face, "rb") as image:
                image_string = base64.b64encode(image.read()).decode()
            faceimage_size = (
                "{:,.0f}".format(os.path.getsize(face) / float(1 << 10)) + " KB"
            )
            os.remove(face)

        # logger.info("Data added successfully to passport")
        details["face"] = image_string
        details["fullimage_size"] = fullimage_size
        details["faceimage_size"] = faceimage_size
        details["base64_string"] = base
        details["file_url"] = pass_visa_image
        # logger.info(
        #     f"time elapsed for api request is{time.time()-api_time}")
        details["success"] = True
        return details
    except OSError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy passportvisadetails",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "message": "Unable to scan your id, please try again",
            "error": str(e),
            "success": False,
            "file_url": pass_visa_image
        }
    except IndexError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy passportvisadetails",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "message": "Unable to scan your id, please try again",
            "error": str(e),
            "success": False,
            "file_url": pass_visa_image
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy passportvisadetails",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "success": False,
            "error": str(e),
            "message": "Unable to scan your id, please try again",
            "file_url": pass_visa_image
        }


def passport_address_detect_text(image_file):
    try:
        # req_time = time.time()
        text_data = text_getter(image_file)
        if not text_data["success"]:
            return text_data
        text = text_data["data"]
        split_text = str(text).split("\n")
        modified_Text = ",".join(map(str, split_text))
        person_address = ""
        for x in split_text:
            if "Address" in x:
                abc = split_text.index(x)
                addr = split_text[abc + 1 :]
                addr_len = len(addr)
                person_address = ",".join(addr)
                if addr_len > 3:
                    addr = split_text[abc + 1 : abc + 4]
                    person_address = ",".join(addr)
                break

            elif "FLAT" in x or "PLOT" in x and person_address == "":
                abc = split_text.index(x)
                addr = split_text[abc + 1 :]
                addr_len = len(addr)
                person_address = ",".join(addr)
                if addr_len > 3:
                    addr = split_text[abc : abc + 3]
                    person_address = ",".join(addr)
                break
            elif re.search(r"\d+", x) and person_address == "":
                abc = split_text.index(x)
                if abc == 0:
                    continue
                addr = split_text[abc + 1 :]
                addr_len = len(addr)
                person_address = ",".join(addr)
                if addr_len > 3:
                    addr = split_text[abc : abc + 3]
                    person_address = ",".join(addr)
                break
        # logger.info(f"time elapsed for parse text is {time.time()-req_time}")
        address1 = ""
        address2 = ""
        postal_code = ""
        person_address = re.sub(r"[^a-zA-Z0-9:\s,-]|", "", person_address)
        if person_address != "":
            if re.search(r"\d{6}", person_address):
                postal_code_data = re.match(
                    r"^.*(?P<zipcode>\d{6}).*$", person_address
                ).groupdict()["zipcode"]
                postal_code = postal_code_data if len(postal_code_data) == 6 else ""
            if "," in person_address:
                split_address = person_address.split(",")
                address1 = ",".join(split_address[: len(split_address) // 2])
                address2 = ",".join(split_address[len(split_address) // 2 :])
            else:
                split_address = person_address.split(" ")
                address1 = " ".join(split_address[: len(split_address) // 2])
                address2 = " ".join(split_address[len(split_address) // 2 :])
        return {
            "success": True,
            "data": {
                "personaddress": person_address,
                "address1": address1,
                "address2": address2,
            },
        }
    except Exception as e:
        print(str(e),"..........................................")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy passport_address_detect_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


# API to passort address images


@frappe.whitelist(allow_guest=True)
def passport_address():
    file_url = ""
    try:
        company = frappe.get_last_doc("company")
        # api_time = time.time()
        # logger.info(f"request get from client")
        base = frappe.local.form_dict.get("Passport_Image")
        # imgdata = base64.b64decode(base)
        add_details = passport_address_detect_text(base)
        if not add_details["success"]:
            return add_details
        details = add_details["data"]
        convert_image = convert_base64_to_image(base, "passport_visa", basedir + company.site_name, company)
        if "success" in convert_image:
            return convert_image
        file_url = convert_image["message"]["file_url"]
        details["file_url"] = convert_image["message"]["file_url"]
        details["base64_string"] = base
        # logger.info(f"extracted address is {details}")
        # logger.info(
        #     f"time elapsed for api request is {time.time()-api_time}")
        details["success"] = True
        return details
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy passport_address",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {
            "success": False,
            "error": str(e),
            "message": "Unable to scan your id, please try again",
            "file_url": file_url
        }


# def qr_scan(img_path):
#     try:
#         data = decode(Image.open(img_path), symbols=[ZBarSymbol.QRCODE])
#         if len(data)>0:
#             qr_extracted_data = (data[0][0]).decode("utf-8")
#             d = (xmltodict.parse(qr_extracted_data, process_namespaces=True))
#             original = d['applicant']
#             person_data = dict(original)
#             print("......,:", d, person_data)
#             Visa_Number = person_data['visaNumber']
#             Given_Name = person_data['applname']
#             passportNumber = person_data['passportNumber']
#             details = {'Visa_Number': Visa_Number, "Given_Name": Given_Name, "passportNumber": passportNumber}
#         else:
#             details = {'Visa_Number':"","Given_Name": "", "passportNumber": ""}
#         return {"success":True,"data":details}
#     except Exception as e:
#         frappe.log_error("qr_scan",str(e))
#         return ({"success":False,"message": str(e)})


country_with_codes = {
    "MDG": "Madagascar",
    "AND": "Andorra",
    "LIE": "Liechtenstein",
    "SGS": "South Georgia and the South Sandwich Island",
    "GEO": "Georgia",
    "GAB": "Gabon",
    "GNQ": "Equatorial Guinea",
    "IND": "India",
    "NIU": "Niue",
    "IRN": "Iran, Islamic Republic of",
    "UZB": "Uzbekistan",
    "JAM": "Jamaica",
    "TGO": "Togo",
    "SYR": "Syrian Arab Republic",
    "STP": "Sao Tome and Principe",
    "BWA": "Botswana",
    "BHR": "Bahrain",
    "AZE": "Azerbaijan",
    "TCD": "Chad",
    "LVA": "Latvia",
    "MHL": "Marshall Islands",
    "GBD": "Dependent territories citizen",
    "MAR": "Morocco",
    "D": "Germany",
    "PLW": "Palau",
    "SHN": "Saint Helena",
    "SUR": "Suriname",
    "ANT": "Netherlands Antilles",
    "CYM": "Cayman Islands",
    "LUX": "Luxembourg",
    "NIC": "Nicaragua",
    "ESP": "Spain",
    "WLF": "Wallis and Futuna Islands",
    "COG": "Congo",
    "MUS": "Mauritius",
    "CXR": "Christmas Island",
    "RUS": "Russian Federation",
    "KAZ": "Kazakhstan",
    "SYC": "Seychelles",
    "TKM": "Turkmenistan",
    "CHN": "China",
    "IDN": "Indonesia",
    "CIV": "Côte d'Ivoire",
    "FLK": "Falkland Islands (Malvinas)",
    "ARM": "Armenia",
    "GRC": "Greece",
    "GIN": "Guinea",
    "COK": "Cook Islands",
    "BRN": "Brunei Darussalam",
    "ATA": "Antarctica",
    "YEM": "Yemen",
    "GBN": "National (overseas)",
    "AUT": "Austria",
    "EGY": "Egypt",
    "MOZ": "Mozambique",
    "VUT": "Vanuatu",
    "CAF": "Central African Republic",
    "KIR": "Kiribati",
    "CAN": "Canada",
    "SOM": "Somalia",
    "GUF": "French Guiana",
    "NTZ": "Neutral Zone",
    "PHL": "Philippines",
    "HTI": "Haiti",
    "BRB": "Barbados",
    "GUY": "Guyana",
    "AIA": "Anguilla",
    "TKL": "Tokelau",
    "NOR": "Norway",
    "MKD": "The former Yugoslav Republic of Macedonia",
    "SAU": "Saudi Arabia",
    "DOM": "Dominican Republic",
    "GIB": "Gibraltar",
    "PNG": "Papua New Guinea",
    "COL": "Colombia",
    "PAK": "Pakistan",
    "DJI": "Djibouti",
    "SGP": "Singapore",
    "TZA": "United Republic of Tanzania",
    "FIN": "Finland",
    "GMB": "Gambia",
    "ECU": "Ecuador",
    "ABW": "Aruba",
    "ERI": "Eritrea",
    "SMR": "San Marino",
    "PAN": "Panama",
    "NRU": "Nauru",
    "MSR": "Montserrat",
    "PRK": "Democratic People's Republic of Korea",
    "CHE": "Switzerland",
    "TON": "Tonga",
    "COM": "Comoros",
    "BTN": "Bhutan",
    "REU": "Réunion",
    "GBS": "Subject",
    "LCA": "Saint Lucia",
    "MEX": "Mexico",
    "ARG": "Argentina",
    "TUR": "Turkey",
    "HUN": "Hungary",
    "HND": "Honduras",
    "NFK": "Norfolk Island",
    "BRA": "Brazil",
    "LAO": "Lao People's Democratic Republic",
    "NZL": "New Zealand",
    "PRY": "Paraguay",
    "QAT": "Qatar",
    "GRD": "Grenada",
    "AGO": "Angola",
    "BLR": "Belarus",
    "BVT": "Bouvet Island",
    "GUM": "Guam",
    "MMR": "Myanmar",
    "POL": "Poland",
    "FSM": "Micronesia, Federated States of",
    "LBR": "Liberia",
    "HRV": "Croatia",
    "PCN": "Pitcairn",
    "GRL": "Greenland",
    "MNP": "Northern Mariana Islands",
    "SWZ": "Swaziland",
    "THA": "Thailand",
    "ASM": "American Samoa",
    "SLV": "El Salvador",
    "VNM": "Viet Nam",
    "PRI": "Puerto Rico",
    "LKA": "Sri Lanka",
    "CCK": "Cocos (Keeling) Islands",
    "GLP": "Guadeloupe",
    "DMA": "Dominica",
    "SWE": "Sweden",
    "CZE": "Czech Republic",
    "DZA": "Algeria",
    "TTO": "Trinidad and Tobago",
    "BHS": "Bahamas",
    "SLE": "Sierra Leone",
    "VIR": "Virgin Islands (United States)",
    "SVN": "Slovenia",
    "MTQ": "Martinique",
    "DNK": "Denmark",
    "ATG": "Antigua and Barbuda",
    "AFG": "Afghanistan",
    "MYT": "Mayotte",
    "UKR": "Ukraine",
    "KGZ": "Kyrgyzstan",
    "BIH": "Bosnia and Herzegovina",
    "LBN": "Lebanon",
    "COD": "Democratic Republic of the Congo",
    "MYS": "Malaysia",
    "GBP": "Protected Person",
    "PER": "Peru",
    "LBY": "Libyan Arab Jamahiriya",
    "ZAR": "Zaire",
    "FJI": "Fiji",
    "VEN": "Venezuela",
    "VCT": "Saint Vincent and the Grenadines",
    "MDA": "Republic of Moldova",
    "IOT": "British Indian Ocean Territory",
    "TUN": "Tunisia",
    "ARE": "United Arab Emirates",
    "HMD": "Heard and McDonald Islands",
    "SLB": "Solomon Islands",
    "GTM": "Guatemala",
    "PYF": "French Polynesia",
    "MRT": "Mauritania",
    "SEN": "Senegal",
    "MNG": "Mongolia",
    "BDI": "Burundi",
    "EST": "Estonia",
    "KNA": "Saint Kitts and Nevis",
    "JPN": "Japan",
    "BEN": "Benin",
    "GNB": "Guinea-Bissau",
    "KOR": "Republic of Korea",
    "NPL": "Nepal",
    "TUV": "Tuvalu",
    "TWN": "Taiwan Province of China",
    "MLT": "Malta",
    "BGD": "Bangladesh",
    "SPM": "Saint Pierre and Miquelon",
    "UGA": "Uganda",
    "BFA": "Burkina Faso",
    "TJK": "Tajikistan",
    "MWI": "Malawi",
    "TMP": "East Timor",
    "KWT": "Kuwait",
    "ESH": "Western Sahara",
    "BOL": "Bolivia",
    "OMN": "Oman",
    "CRI": "Costa Rica",
    "BLZ": "Belize",
    "NAM": "Namibia",
    "ZAF": "South Africa",
    "SVK": "Slovakia",
    "ZMB": "Zambia",
    "PRT": "Portugal",
    "LSO": "Lesotho",
    "URY": "Uruguay",
    "USA": "United States of America",
    "MDV": "Maldives",
    "UMI": "United States of America Minor Outlying Islands",
    "ISR": "Israel",
    "GBR": "United Kingdom of Great Britain and Northern Ireland",
    "GBO": "Overseas citizen",
    "NLD": "Netherlands, Kingdom of the",
    "SDN": "Sudan",
    "ISL": "Iceland",
    "VGB": "Virgin Islands (Great Britian)",
    "ALB": "Albania",
    "WSM": "Samoa",
    "ETH": "Ethiopia",
    "TCA": "Turks and Caicos Islands",
    "NCL": "New Caledonia",
    "BMU": "Bermuda",
    "JOR": "Jordan",
    "AUS": "Australia",
    "KHM": "Cambodia",
    "CHL": "Chile",
    "VAT": "Holy See (Vatican City State)",
    "SJM": "Svalbard and Jan Mayen Islands",
    "CUB": "Cuba",
    "FXX": "France, Metropolitan",
    "CMR": "Cameroon",
    "MCO": "Monaco",
    "GHA": "Ghana",
    "ITA": "Italy",
    "CPV": "Cape Verde",
    "BEL": "Belgium",
    "BGR": "Bulgaria",
    "HKG": "Hong Kong",
    "KEN": "Kenya",
    "FRA": "France",
    "MLI": "Mali",
    "ZWE": "Zimbabwe",
    "RWA": "Rwanda",
    "CYP": "Cyprus",
    "IRL": "Ireland",
    "NER": "Niger",
    "IRQ": "Iraq",
    "FRO": "Faeroe Islands",
    "LTU": "Lithuania",
    "ROM": "Romania",
    "NGA": "Nigeria",
}


def qr_detect_text(image_file):
    try:
        service = [
            "eTOURIST VISA",
            "eBUSSINESS VISA",
            "eMEDICAL VISA",
            "eCONFERENCE Visa",
            "eMEDICAL ATTENDANT VISA",
        ]
        text_data = text_getter(image_file)
        if not text_data["success"]:
            return text_data
        text = text_data["data"]
        text = re.sub("INDIAN E-VISA", "", text)
        block = str(text).split("\n")
        entries = ["MULTIPLE", "SINGLE", "DOUBLE", "Double", "Single", "Multiple"]
        entry = " "
        for y in block:
            for x in entries:
                if x in y:
                    print(f"matchedentry is {x}")
                    entry = x
                    break
            result = "".join(i for i in y if not i.isdigit())
            matched_entries = get_close_matches(result, entries)
            if len(matched_entries) == 1:
                entry = matched_entries[0]
                print("entry:", entry)
        details = {}

        get = country_with_codes.values()
        get = [x.upper() for x in list(get)]
        nation = []
        nationality = ""
        for x in block:
            if x in get:
                nationality = x
                print("country:", x)
        #     result = ''.join(i for i in x if not i.isdigit())
        #     matched_entries = get_close_matches(x, get)
        #     # print("matched_entries:",matched_entries)
        #     if len(matched_entries) >= 1:
        #         nation.append(matched_entries[0])
        # nationality = ''
        # if len(nation) > 0:
        #     nationality = nation[0]
        type_visa = []
        for x in block:
            result = "".join(i for i in x if not i.isdigit())
            matched_entries = get_close_matches(result, service)
            if len(matched_entries) >= 1:
                type_visa.append(matched_entries[0])

        visa_type = ""
        if len(type_visa) >= 1:
            visa_type = type_visa[0]
        details["visa_Type"] = visa_type
        details["Nationality"] = nationality
        details["Visa_No_Of_Enteries"] = entry
        details["Issued_country"] = "INDIA"
        details["Document_Type"] = "e-VISA"

        return {"success": True, "data": details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy qr_detect_text",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "error": str(e), "message": "Unable to scan your id"}


# API to scan QR-Visa and E-Visa images
# @frappe.whitelist(allow_guest=True)
# def qrvisa(data):
#     try:
#         company = frappe.get_last_doc('company')
#         # logger.info("api call hits")
#         # file = request.form
#         base = data['evisaqr']
#         doc_type = data['scanView']
#         imgdata = base64.b64decode(base)
#         unique_no = datetime.now()
#         filename = basedir + company.site_name + "/private/files/evisa.jpeg"
#         with open(filename, 'wb') as f:
#             f.write(imgdata)
#         if doc_type == 'qrscan':
#             qrdetails = qr_scan(filename)
#             if qrdetails["success"] == False:
#                 return qrdetails
#             qr_details = qrdetails["data"]
#             face_detect = detect_faces(filename, unique_no)
#             if face_detect["success"] == False:
#                 return {"success": False,"message": face_detect["message"]}
#             face = face_detect["data"]
#             face = ""
#             if os.path.exists(filename):
#                 image_string = ''
#                 if os.path.isfile(face) is True:
#                     with open(face, 'rb') as image:
#                         image_string = base64.b64encode(image.read()).decode()
#                     os.remove(face)
#             os.remove(filename)
#             # logger.info(qr_details)
#             return ({"success": True, "data": qr_details, "face": image_string})
#         if doc_type == 'textscan':
#             textdetails = qr_detect_text(base)
#             if textdetails["success"] == False:
#                 return textdetails
#             text_details = textdetails["data"]
#             face_detect = detect_faces(filename, unique_no)
#             if face_detect["success"] == False:
#                 return {"success": False,"message": face_detect["message"]}
#             face = face_detect["data"]
#             if os.path.exists(filename):
#                 image_string = ''
#                 if os.path.isfile(face) is True:
#                     with open(face, 'rb') as image:
#                         image_string = base64.b64encode(image.read()).decode()
#                     os.remove(face)
#             os.remove(filename)
#             # logger.info(text_details)
#             return ({"success": True, "data": text_details, "face": image_string})
#     except Exception as e:
#         frappe.log_error("qrVisa",str(e))
#         return ({"success": False, "message": "Unable to scan your id, please try again","error":str(e)})


# API to scan other images
@frappe.whitelist(allow_guest=True)
def other_images():
    try:
        company = frappe.get_last_doc("company")
        base = frappe.local.form_dict.get("image")
        # doc_type = file['scanView']
        imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # I assume you have a way of picking unique filenames
        filename = basedir + company.site_name + "/private/files/otherimage.jpeg"
        with open(filename, "wb") as f:
            f.write(imgdata)
        croppedother = image_processing(filename)
        if not croppedother["success"]:
            return croppedother
        cropped_other = croppedother["data"]
        details = {"base64_string": cropped_other}
        os.remove(filename)
        # logger.info("Image Cropped and Skewed successfully")
        return {"success": True, "otherimage_details": details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "SignEzy other_images",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"error": str(e), "message": "Unable to scan your id", "success": False}
