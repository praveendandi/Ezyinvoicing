import base64
import datetime
import sys
import traceback

import babel.dates
import frappe
import pandas as pd
import pgeocode
import requests
from babel.core import UnknownLocaleError
from dateutil import parser
from dateutil.parser._parser import ParserError


def convert_base64_to_image(base, name, site_folder_path, company):
    try:
        file = site_folder_path + "/private/files/" + name + "face.png"
        # res = bytes(base, 'utf-8')
        with open(file, "wb") as fh:
            fh.write(base64.b64decode(base))
        files = {"file": open(file, "rb")}
        payload = {"is_private": 1, "folder": "Home"}
        site = company.host
        upload_qr_image = requests.post(
            site + "api/method/upload_file", files=files, data=payload
        )
        response = upload_qr_image.json()
        if "message" in response:
            return response
        else:
            return {"success": False, "message": "something went wrong"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Guest Details Opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def get_address_from_zipcode(postal_code):
    try:
        data = {}
        geo_country = pgeocode.Nominatim("IN")
        location = geo_country.query_postal_code(postal_code)
        # if not pd.isna(location.community_name):
        #     data["location"] = location.community_name
        if not pd.isna(location.county_name):
            data["guest_city"] = location.county_name
        if not pd.isna(location.state_name):
            data["guest_state"] = location.state_name
        if not pd.isna(location.country_code):
            if location.country_code == "IN":
                data["guest_country"] = "IND"
                data["guest_nationality"] = "IND"
        return {"success": True, "data": data}
    except Exception as e:
        frappe.log_error(
            "Scan-update_company",
            traceback.format_exc(),
        )
        return {"success": False, "message": str(e)}


# All method give below are date formatter taken from core module frappe

def format_date(string_date=None, format_string=None):
    """Converts the given string date to :data:`user_date_format`
    User format specified in defaults

    Examples:

    * dd-mm-yyyy
    * mm-dd-yyyy
    * dd/mm/yyyy
    """

    if not string_date:
        return ""

    date = getdate(string_date)
    if not format_string:
        format_string = get_user_date_format()
    format_string = format_string.replace("mm", "MM")
    try:
        formatted_date = babel.dates.format_date(
            date, format_string, locale=(frappe.local.lang or "").replace("-", "_")
        )
    except UnknownLocaleError:
        format_string = (
            format_string.replace("MM", "%m").replace("dd", "%d").replace("yyyy", "%Y")
        )
        formatted_date = date.strftime(format_string)
    return formatted_date


def getdate(string_date=None):
    """
    Converts string date (yyyy-mm-dd) to datetime.date object
    """

    if not string_date:
        return get_datetime().date()
    if isinstance(string_date, datetime.datetime):
        return string_date.date()

    elif isinstance(string_date, datetime.date):
        return string_date

    if is_invalid_date_string(string_date):
        return None
    try:
        return parser.parse(string_date).date()
    except ParserError:
        pass
        # frappe.throw(
        #     frappe._("{} is not a valid date string.").format(frappe.bold(string_date)),
        #     title=frappe._("Invalid Date"),
        # )


def is_invalid_date_string(date_string):
    # dateutil parser does not agree with dates like "0001-01-01" or "0000-00-00"
    return (not date_string) or (date_string or "").startswith(
        ("0001-01-01", "0000-00-00")
    )


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT


def get_datetime(datetime_str=None):
    if datetime_str is None:
        return now_datetime()

    if isinstance(datetime_str, (datetime.datetime, datetime.timedelta)):
        return datetime_str

    elif isinstance(datetime_str, (list, tuple)):
        return datetime.datetime(datetime_str)

    elif isinstance(datetime_str, datetime.date):
        return datetime.datetime.combine(datetime_str, datetime.time())

    if is_invalid_date_string(datetime_str):
        return None

    try:
        return datetime.datetime.strptime(datetime_str, DATETIME_FORMAT)
    except ValueError:
        pass
        # return parser.parse(datetime_str)


def now_datetime():
    dt = convert_utc_to_user_timezone(datetime.datetime.utcnow())
    return dt.replace(tzinfo=None)


def convert_utc_to_user_timezone(utc_timestamp):
    from pytz import UnknownTimeZoneError, timezone

    utcnow = timezone("UTC").localize(utc_timestamp)
    try:
        return utcnow.astimezone(timezone(get_time_zone()))
    except UnknownTimeZoneError:
        pass
        # return utcnow


def get_user_date_format():
    """Get the current user date format. The result will be cached."""
    if getattr(frappe.local, "user_date_format", None) is None:
        frappe.local.user_date_format = frappe.db.get_default("date_format")

    return frappe.local.user_date_format or "yyyy-mm-dd"


def get_time_zone():
    if frappe.local.flags.in_test:
        return _get_time_zone()


def _get_time_zone():
    return (
        frappe.db.get_system_setting("time_zone") or "Asia/Kolkata"
    )  # Default to India ?!

# till here are date formatter methods