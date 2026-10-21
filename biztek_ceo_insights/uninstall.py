"""Clean uninstall for Biztek CEO Insights overlay."""

from __future__ import annotations

import frappe

INSIGHTS_WORKSPACE = "Insights"


def before_uninstall():
	try:
		frappe.clear_cache()
		if frappe.db.exists("Workspace", INSIGHTS_WORKSPACE):
			app = frappe.db.get_value("Workspace", INSIGHTS_WORKSPACE, "app")
			# Only remove the URL workspace we own
			if app == "biztek_ceo_insights":
				frappe.delete_doc("Workspace", INSIGHTS_WORKSPACE, force=True, ignore_permissions=True)
		frappe.clear_cache()
	except Exception:
		frappe.log_error(title="Biztek CEO Insights before_uninstall failed")


def after_uninstall():
	try:
		frappe.clear_cache()
	except Exception:
		frappe.log_error(title="Biztek CEO Insights after_uninstall failed")
