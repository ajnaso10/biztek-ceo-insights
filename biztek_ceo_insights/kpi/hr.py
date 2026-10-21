# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""HR and payroll KPI calculations."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

from biztek_ceo_insights.kpi.filters import doctype_exists, ensure_permission, ok_result, unavailable


def total_head_count(filters) -> dict:
	"""Active employee count (snapshot)."""
	if not doctype_exists("Employee"):
		return unavailable(_("Employee is not available"))
	ensure_permission("Employee")

	count = frappe.db.count(
		"Employee",
		{"status": "Active", "company": filters.company},
	)
	# Some sites leave company blank on Employee — fall back to all Active if zero and company filter empty match
	if count == 0:
		# Prefer company-scoped; if Employee has no company field match, try without company
		meta = frappe.get_meta("Employee")
		if meta.has_field("company"):
			pass
		else:
			count = frappe.db.count("Employee", {"status": "Active"})
	return ok_result(count, format="number")


def salary_total(filters) -> dict:
	"""Payroll cost (gross) from submitted Salary Slips in the period.

	Uses base_gross_pay only — does not sum salary Journal Entries (avoids double-count).
	"""
	if not doctype_exists("Salary Slip"):
		return unavailable(_("Salary Slip is not available (HRMS)"))
	ensure_permission("Salary Slip")

	ss = frappe.qb.DocType("Salary Slip")
	row = (
		frappe.qb.from_(ss)
		.select(frappe.query_builder.functions.Sum(ss.base_gross_pay).as_("total"))
		.where(
			(ss.docstatus == 1)
			& (ss.company == filters.company)
			& (ss.end_date >= filters.from_date)
			& (ss.end_date <= filters.to_date)
		)
	).run(as_dict=True)
	total = flt(row[0].total) if row else 0.0
	return ok_result(
		total,
		currency=filters.currency,
		format="currency",
		label=_("Payroll Cost (Gross)"),
	)


def hr_kpi_summary(filters) -> dict:
	"""HR summary mosaic: active headcount primary; new hires and exits supporting.

	No weighted HR score — components are shown separately.
	Attrition for the period is documented as exits / average active headcount
	and returned on the detail context, not as a single card score.
	"""
	if not doctype_exists("Employee"):
		return unavailable(_("Employee is not available"))
	ensure_permission("Employee")

	headcount = frappe.db.count("Employee", {"status": "Active", "company": filters.company})
	hires = _count_hires(filters)
	exits = _count_exits(filters)
	return ok_result(
		headcount,
		secondary={
			"label": _("Hires / Exits"),
			"value": f"{hires} / {exits}",
			"format": "text",
			"hires": hires,
			"exits": exits,
		},
		format="number",
		label=_("HR Summary (Active Headcount)"),
	)


def hr_detail_metrics(filters) -> dict:
	"""Detail metrics for the HR KPI dashboard."""
	ensure_permission("Employee")
	headcount = frappe.db.count("Employee", {"status": "Active", "company": filters.company})
	hires = _count_hires(filters)
	exits = _count_exits(filters)
	# Average headcount approximation: active now (snapshot). Documented limitation.
	attrition = flt(exits) / flt(headcount) * 100.0 if headcount else None
	by_department = frappe.db.sql(
		"""
		SELECT department, COUNT(name) AS count
		FROM `tabEmployee`
		WHERE status = 'Active' AND company = %s
		GROUP BY department
		ORDER BY count DESC
		""",
		(filters.company,),
		as_dict=True,
	)
	return {
		"headcount": headcount,
		"hires": hires,
		"exits": exits,
		"attrition_pct": attrition,
		"attrition_formula": "exits in period / active headcount as of as_on × 100",
		"by_department": by_department,
		"attendance_available": doctype_exists("Attendance"),
		"leave_available": doctype_exists("Leave Application"),
	}


def _count_hires(filters) -> int:
	return frappe.db.count(
		"Employee",
		{
			"company": filters.company,
			"date_of_joining": ["between", [filters.from_date, filters.to_date]],
		},
	)


def _count_exits(filters) -> int:
	return frappe.db.count(
		"Employee",
		{
			"company": filters.company,
			"relieving_date": ["between", [filters.from_date, filters.to_date]],
		},
	)


def headcount_by_dimension(filters, field: str) -> list[dict]:
	ensure_permission("Employee")
	if not frappe.get_meta("Employee").has_field(field):
		return []
	# field is from a fixed allow-list of callers (department, designation, branch)
	allowed = {"department", "designation", "branch", "status"}
	if field not in allowed:
		return []
	return frappe.db.sql(
		f"""
		SELECT `{field}` AS dimension, COUNT(name) AS count
		FROM `tabEmployee`
		WHERE status = 'Active' AND company = %s
		GROUP BY `{field}`
		ORDER BY count DESC
		""",
		(filters.company,),
		as_dict=True,
	)
