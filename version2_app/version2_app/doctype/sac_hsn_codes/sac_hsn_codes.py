# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import random, string

class SACHSNCODES(Document):

	def before_insert(self):
		# pass
		match = ''.join(random.choice(string.digits) for _ in range(6))
		self.sac_index = match