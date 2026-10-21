"""Clean uninstall for Biztek Insights overlay."""

from __future__ import annotations

import frappe

INSIGHTS_WORKSPACE = "Insights"


def before_uninstall():
	try:
		frappe.clear_cache()
		if frappe.db.exists("Workspace", INSIGHTS_WORKSPACE):
			app = frappe.db.get_value("Workspace", INSIGHTS_WORKSPACE, "app")
			# Only remove the URL workspace we own
			if app == "biztek_insights":
				frappe.delete_doc("Workspace", INSIGHTS_WORKSPACE, force=True, ignore_permissions=True)
		frappe.clear_cache()
	except Exception:
		frappe.log_error(title="Biztek Insights before_uninstall failed")


def after_uninstall():
	try:
		frappe.clear_cache()
	except Exception:
		frappe.log_error(title="Biztek Insights after_uninstall failed")
