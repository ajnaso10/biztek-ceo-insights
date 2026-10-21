# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Resolve Insights SPA URLs for KPI detail dashboards."""

from __future__ import annotations

from urllib.parse import urlencode

import frappe

# Template dashboard keys → titles shipped in workbook_templates/ceo
DETAIL_DASHBOARD_TITLES = {
	"td-pending-so": "Pending Sales Orders",
	"td-total-so": "Total Sales Orders",
	"td-total-stock": "Total Stock",
	"td-total-ar": "Total A/R",
	"td-total-ap": "Total A/P",
	"td-pdc-payable": "PDC Pending Payable",
	"td-cash-hand": "Cash in Hand",
	"td-net-cash": "Net Cash",
	"td-cash-bank": "Cash in Bank",
	"td-headcount": "Total Head Count",
	"td-salary": "Salary Total",
	"td-hr-kpi": "HR KPI",
}

CEO_FALLBACK_TITLE = "CEO Command Center"


def resolve_insights_dashboard(dashboard_key: str) -> dict:
	"""Return live Insights dashboard name/title/workbook for a template key.

	Falls back to the imported CEO Command Center dashboard when the dedicated
	detail dashboard has not been imported yet (template update pending).
	"""
	if not frappe.db.exists("DocType", "Insights Dashboard v3"):
		return {}

	wanted_title = DETAIL_DASHBOARD_TITLES.get(dashboard_key)
	rows = frappe.get_all(
		"Insights Dashboard v3",
		fields=["name", "title", "workbook"],
		limit_page_length=500,
	)
	by_title = {r.title: r for r in rows}
	by_name = {r.name: r for r in rows}

	# Exact template key as document name (rare, after some imports)
	if dashboard_key in by_name:
		row = by_name[dashboard_key]
	elif wanted_title and wanted_title in by_title:
		row = by_title[wanted_title]
	elif CEO_FALLBACK_TITLE in by_title:
		row = by_title[CEO_FALLBACK_TITLE]
	elif rows:
		row = rows[0]
	else:
		return {}

	return {
		"name": row.name,
		"title": row.title,
		"workbook": row.workbook,
		"is_fallback": row.title != wanted_title,
	}


def insights_detail_path(dashboard_key: str, filters) -> str:
	"""Canonical Insights URL: /insights/dashboards/<name>?filters."""
	resolved = resolve_insights_dashboard(dashboard_key)
	if not resolved:
		return "/insights/dashboards"

	params = urlencode(
		{
			"company": filters.company,
			"from_date": str(filters.from_date),
			"to_date": str(filters.to_date),
			"as_on": str(filters.as_on),
		}
	)
	# Prefer public dashboard route; workbook route as alternate
	return f"/insights/dashboards/{resolved['name']}?{params}"
