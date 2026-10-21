# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Inventory KPI calculations."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

from biztek_insights.kpi.filters import ensure_permission, ok_result, unavailable


def total_stock(filters) -> dict:
	"""Live inventory value from Bin.stock_value (configured valuation)."""
	if not frappe.db.exists("DocType", "Bin"):
		return unavailable(_("Bin is not available"))
	ensure_permission("Bin")

	bin = frappe.qb.DocType("Bin")
	row = (
		frappe.qb.from_(bin)
		.select(
			frappe.query_builder.functions.Sum(bin.stock_value).as_("stock_value"),
			frappe.query_builder.functions.Sum(bin.actual_qty).as_("actual_qty"),
		)
		.where(bin.company == filters.company)
	).run(as_dict=True)

	stock_value = flt(row[0].stock_value) if row else 0.0
	actual_qty = flt(row[0].actual_qty) if row else 0.0
	return ok_result(
		stock_value,
		secondary={"label": _("Total Qty"), "value": actual_qty, "format": "float"},
		currency=filters.currency,
		format="currency",
	)


def stock_by_warehouse(filters) -> list[dict]:
	"""Stock value and qty grouped by warehouse."""
	ensure_permission("Bin")
	return frappe.db.sql(
		"""
		SELECT warehouse,
			COALESCE(SUM(stock_value), 0) AS stock_value,
			COALESCE(SUM(actual_qty), 0) AS actual_qty
		FROM `tabBin`
		WHERE company = %s
		GROUP BY warehouse
		ORDER BY stock_value DESC
		""",
		(filters.company,),
		as_dict=True,
	)
