# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Drop the Desk CEO KPI page; KPIs live in the Insights workbook only."""

from __future__ import annotations

import frappe


def execute():
	page = "ceo-insight-dashboard"
	if frappe.db.exists("Page", page):
		frappe.delete_doc("Page", page, force=True, ignore_permissions=True)
