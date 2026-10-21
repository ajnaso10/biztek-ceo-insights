"""Install / migrate sync for Biztek CEO Insights workspace overlay."""

from __future__ import annotations

import os

import frappe

INSIGHTS_WORKSPACE = "Insights"
INSIGHTS_URL = "/insights/dashboards"
WORKSPACE_JSON = "workspace/insights/insights.json"


def after_install():
	sync_insights_workspace()
	_update_desktop_icon_link()
	frappe.clear_cache()


def after_migrate():
	sync_insights_workspace()
	_update_desktop_icon_link()
	frappe.clear_cache()


def sync_insights_workspace():
	"""Ensure Insights URL workspace exists (not public) and points at /insights/dashboards."""
	try:
		app_path = frappe.get_app_path("biztek_ceo_insights")
		path = os.path.join(app_path, WORKSPACE_JSON)
		if not os.path.exists(path):
			return

		if frappe.db.exists("Workspace", INSIGHTS_WORKSPACE):
			doc = frappe.get_doc("Workspace", INSIGHTS_WORKSPACE)
			changed = False
			if doc.type != "URL":
				doc.type = "URL"
				changed = True
			if doc.external_link != INSIGHTS_URL:
				doc.external_link = INSIGHTS_URL
				changed = True
			if doc.public:
				doc.public = 0
				changed = True
			if doc.is_hidden:
				doc.is_hidden = 0
				changed = True
			if (doc.module or "") != "Biztek CEO Insights":
				doc.module = "Biztek CEO Insights"
				changed = True
			if (doc.app or "") != "biztek_ceo_insights":
				doc.app = "biztek_ceo_insights"
				changed = True
			if float(doc.sequence_id or 0) != 5.5:
				doc.sequence_id = 5.5
				changed = True
			if changed:
				doc.save(ignore_permissions=True)
			_ensure_workspace_roles(doc)
			# public is read_only on Workspace form — set via db
			if frappe.db.get_value("Workspace", INSIGHTS_WORKSPACE, "public"):
				frappe.db.set_value("Workspace", INSIGHTS_WORKSPACE, "public", 0, update_modified=False)
		else:
			from frappe.modules.import_file import import_file_by_path

			import_file_by_path(path, force=True, ignore_version=True)
			if frappe.db.exists("Workspace", INSIGHTS_WORKSPACE):
				_ensure_workspace_roles(frappe.get_doc("Workspace", INSIGHTS_WORKSPACE))
				frappe.db.set_value("Workspace", INSIGHTS_WORKSPACE, "public", 0, update_modified=False)

		frappe.db.commit()
	except Exception:
		frappe.log_error(title="Biztek CEO Insights sync_insights_workspace failed")


def _ensure_workspace_roles(doc):
	wanted = {"System Manager", "Insights Admin", "Insights User"}
	existing = {row.role for row in (doc.roles or [])}
	missing = wanted - existing
	if not missing:
		return
	for role in sorted(missing):
		if frappe.db.exists("Role", role):
			doc.append("roles", {"role": role})
	doc.save(ignore_permissions=True)


def _update_desktop_icon_link():
	"""Point Insights desktop / apps icon at dashboards route when present."""
	try:
		if not frappe.db.exists("Desktop Icon", "Insights"):
			return
		current = frappe.db.get_value("Desktop Icon", "Insights", "link")
		if current != INSIGHTS_URL:
			frappe.db.set_value("Desktop Icon", "Insights", "link", INSIGHTS_URL, update_modified=False)
	except Exception:
		frappe.log_error(title="Biztek CEO Insights desktop icon link update failed")
