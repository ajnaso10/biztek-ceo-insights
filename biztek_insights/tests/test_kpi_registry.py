# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""KPI registry and formula smoke tests."""

from __future__ import annotations

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, flt, getdate, today

from biztek_insights.kpi.api import get_kpi_cards, get_kpi_definitions, get_kpi_detail
from biztek_insights.kpi.constants import PENDING_SO_STATUSES
from biztek_insights.kpi.filters import parse_filters
from biztek_insights.kpi.registry import KPI_REGISTRY, get_kpi, list_kpi_ids
from biztek_insights.kpi.sales import pending_sales_orders_value, total_sales_orders


class TestKPIRegistry(IntegrationTestCase):
	def test_twelve_kpis_registered(self):
		self.assertEqual(len(KPI_REGISTRY), 12)
		self.assertEqual(len(list_kpi_ids()), 12)

	def test_definitions_expose_detail_keys(self):
		defs = get_kpi_definitions()
		keys = {d["detail_dashboard_key"] for d in defs}
		expected = {
			"td-pending-so",
			"td-total-so",
			"td-total-stock",
			"td-total-ar",
			"td-total-ap",
			"td-pdc-payable",
			"td-cash-hand",
			"td-net-cash",
			"td-cash-bank",
			"td-headcount",
			"td-salary",
			"td-hr-kpi",
		}
		self.assertEqual(keys, expected)

	def test_get_kpi_cards_returns_sections(self):
		company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
			"Company", {}, "name"
		)
		if not company:
			self.skipTest("No company on site")
		result = get_kpi_cards(company=company, from_date=today(), to_date=today(), as_on=today())
		self.assertIn("sections", result)
		self.assertEqual(len(result["sections"]), 5)
		card_ids = [c["id"] for s in result["sections"] for c in s["cards"]]
		self.assertEqual(len(card_ids), 12)
		self.assertIn("pending_so_value", card_ids)

	def test_filter_propagation_on_detail(self):
		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company on site")
		from_date = add_days(today(), -30)
		to_date = today()
		detail = get_kpi_detail(
			"total_stock",
			company=company,
			from_date=from_date,
			to_date=to_date,
			as_on=to_date,
		)
		self.assertEqual(detail["filters"]["company"], company)
		self.assertEqual(detail["filters"]["from_date"], str(getdate(from_date)))
		self.assertIn("insights_path", detail)
		self.assertTrue(
			detail["insights_path"].startswith("/insights/dashboards"),
			detail["insights_path"],
		)
		from urllib.parse import unquote_plus

		self.assertIn(company, unquote_plus(detail["insights_path"]))

	def test_pending_so_formula_matches_statuses(self):
		company = frappe.db.get_value("Company", {}, "name")
		if not company or not frappe.db.exists("DocType", "Sales Order"):
			self.skipTest("Sales Order / Company unavailable")

		filters = parse_filters(company=company, from_date=today(), to_date=today(), as_on=today())
		result = pending_sales_orders_value(filters)
		self.assertTrue(result["available"])

		# Cross-check against direct SQL using the same status list
		placeholders = ", ".join(["%s"] * len(PENDING_SO_STATUSES))
		expected = frappe.db.sql(
			f"""
			SELECT COALESCE(SUM(base_grand_total - IFNULL(advance_paid, 0)), 0)
			FROM `tabSales Order`
			WHERE docstatus = 1 AND company = %s AND status IN ({placeholders})
			""",
			(company, *PENDING_SO_STATUSES),
		)[0][0]
		self.assertEqual(flt(result["value"]), flt(expected))

	def test_total_so_period_count(self):
		company = frappe.db.get_value("Company", {}, "name")
		if not company or not frappe.db.exists("DocType", "Sales Order"):
			self.skipTest("Sales Order / Company unavailable")
		filters = parse_filters(company=company, from_date=today(), to_date=today(), as_on=today())
		result = total_sales_orders(filters)
		self.assertTrue(result["available"])
		expected = frappe.db.count(
			"Sales Order",
			{
				"docstatus": 1,
				"company": company,
				"transaction_date": ["between", [filters.from_date, filters.to_date]],
			},
		)
		self.assertEqual(result["value"], expected)

	def test_net_cash_equals_hand_plus_bank(self):
		from biztek_insights.kpi.cash import cash_in_bank, cash_in_hand, net_cash

		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company")
		filters = parse_filters(company=company, as_on=today())
		hand = cash_in_hand(filters)
		bank = cash_in_bank(filters)
		net = net_cash(filters)
		if not hand["available"]:
			self.skipTest("Cash accounts unavailable")
		self.assertAlmostEqual(flt(net["value"]), flt(hand["value"]) + flt(bank["value"]), places=2)

	def test_unknown_kpi_throws(self):
		company = frappe.db.get_value("Company", {}, "name")
		with self.assertRaises(frappe.ValidationError):
			get_kpi_detail("not_a_real_kpi", company=company)

	def test_get_kpi_lookup(self):
		self.assertIsNotNone(get_kpi("pending_so_value"))
		self.assertIsNone(get_kpi("nope"))
