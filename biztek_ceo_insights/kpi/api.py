# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Whitelisted APIs for the CEO Insight Dashboard."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from biztek_ceo_insights.kpi.filters import parse_filters
from biztek_ceo_insights.kpi.insights_links import insights_detail_path, resolve_insights_dashboard
from biztek_ceo_insights.kpi.registry import (
	KPI_REGISTRY,
	get_kpi,
	list_kpi_ids,
	ordered_sections,
	section_label,
)


@frappe.whitelist()
def get_kpi_cards(
	company: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
	as_on: str | None = None,
) -> dict[str, Any]:
	"""Return all KPI card values grouped by section."""
	filters = parse_filters(company, from_date, to_date, as_on)
	sections: dict[str, dict] = {
		s: {"id": s, "label": _(section_label(s)), "cards": []} for s in ordered_sections()
	}

	for kpi in KPI_REGISTRY:
		card = _evaluate_card(kpi, filters)
		sections[kpi.section]["cards"].append(card)

	return {
		"filters": {
			"company": filters.company,
			"from_date": str(filters.from_date),
			"to_date": str(filters.to_date),
			"as_on": str(filters.as_on),
			"currency": filters.currency,
		},
		"sections": [sections[s] for s in ordered_sections()],
		"kpi_ids": list_kpi_ids(),
	}


@frappe.whitelist()
def get_kpi_detail(
	kpi_id: str,
	company: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
	as_on: str | None = None,
) -> dict[str, Any]:
	"""Return card value, formula, and supporting rows for a KPI detail view."""
	kpi = get_kpi(kpi_id)
	if not kpi:
		frappe.throw(_("Unknown KPI: {0}").format(kpi_id))

	filters = parse_filters(company, from_date, to_date, as_on)
	card = _evaluate_card(kpi, filters)
	detail = None
	if kpi.detail_fn:
		try:
			detail = kpi.detail_fn(filters)
		except frappe.PermissionError:
			raise
		except Exception:
			frappe.log_error(title=f"CEO KPI detail failed: {kpi_id}")
			detail = None

	insights = resolve_insights_dashboard(kpi.detail_dashboard_key)
	insights_path = insights_detail_path(kpi.detail_dashboard_key, filters)
	return {
		"kpi_id": kpi.id,
		"label": _(kpi.label) if isinstance(kpi.label, str) else kpi.label,
		"formula_doc": kpi.formula_doc,
		"detail_dashboard_key": kpi.detail_dashboard_key,
		"snapshot": kpi.snapshot,
		"filters": {
			"company": filters.company,
			"from_date": str(filters.from_date),
			"to_date": str(filters.to_date),
			"as_on": str(filters.as_on),
			"currency": filters.currency,
		},
		"card": card,
		"detail": detail,
		"insights_path": insights_path,
		"insights": insights,
	}


@frappe.whitelist()
def get_kpi_definitions() -> list[dict]:
	"""Return KPI metadata without calculating values (for tests / config UI)."""
	return [
		{
			"id": k.id,
			"section": k.section,
			"section_label": _(section_label(k.section)),
			"label": _(k.label) if isinstance(k.label, str) else k.label,
			"formula_doc": k.formula_doc,
			"detail_dashboard_key": k.detail_dashboard_key,
			"snapshot": k.snapshot,
		}
		for k in KPI_REGISTRY
	]


def _evaluate_card(kpi, filters) -> dict[str, Any]:
	try:
		result = kpi.value_fn(filters) or {}
	except frappe.PermissionError as e:
		result = {
			"available": False,
			"value": None,
			"secondary": None,
			"reason": str(e),
		}
	except Exception:
		frappe.log_error(title=f"CEO KPI failed: {kpi.id}")
		result = {
			"available": False,
			"value": None,
			"secondary": None,
			"reason": _("Calculation failed"),
		}

	display_label = result.get("label") or kpi.label
	return {
		"id": kpi.id,
		"section": kpi.section,
		"label": _(display_label) if isinstance(display_label, str) else display_label,
		"formula_doc": kpi.formula_doc,
		"detail_dashboard_key": kpi.detail_dashboard_key,
		"snapshot": kpi.snapshot,
		"available": result.get("available", True),
		"value": result.get("value"),
		"secondary": result.get("secondary"),
		"currency": result.get("currency") or filters.currency,
		"format": result.get("format") or "number",
		"reason": result.get("reason"),
		"insights_path": insights_detail_path(kpi.detail_dashboard_key, filters),
	}


@frappe.whitelist()
def get_insights_dashboard_map() -> dict[str, str]:
	"""Map template dashboard keys to imported Insights Dashboard v3 names."""
	from biztek_ceo_insights.kpi.insights_links import DETAIL_DASHBOARD_TITLES

	out = {}
	for key in DETAIL_DASHBOARD_TITLES:
		resolved = resolve_insights_dashboard(key)
		if resolved:
			out[key] = resolved["name"]
	return out
