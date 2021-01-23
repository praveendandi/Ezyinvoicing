from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
from version2_app.version2_app.doctype.invoices.credit_generate_irn import CreditgenerateIrn
from version2_app.version2_app.doctype.invoices.invoice_helpers import TotalMismatchError
from version2_app.version2_app.doctype.invoices.invoice_helpers import CheckRatePercentages
from version2_app.version2_app.doctype.invoices.invoices import *
import pandas as pd
import json
import os, os.path
import random, string
from random import randint
# from datetime import da
import datetime
import random
import math
from frappe.utils import get_site_name
from frappe.utils import logger
import time
import os






