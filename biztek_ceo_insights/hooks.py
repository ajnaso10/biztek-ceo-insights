app_name = "biztek_ceo_insights"
app_title = "Biztek CEO Insights"
app_publisher = "Savad Ibrahim"
app_description = "BI Dashboards for Biztek"
app_email = "savadibrahim@gmail.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["insights"]

# Insights v3/v4 workbook templates (CRM Pipeline, etc.)
insights_workbooks = "workbook_templates"

# Inject hide-script + top bar into Insights SPA (/insights, /insights_v2)
after_request = ["biztek_ceo_insights.branding.after_request"]

after_install = "biztek_ceo_insights.install.after_install"
after_migrate = "biztek_ceo_insights.install.after_migrate"
before_uninstall = "biztek_ceo_insights.uninstall.before_uninstall"
after_uninstall = "biztek_ceo_insights.uninstall.after_uninstall"

# Desk: URL workspace clicks (Insights → /insights/dashboards)
app_include_js = ["/assets/biztek_ceo_insights/js/desk_topbar_url.js?v=4"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "biztek_ceo_insights",
# 		"logo": "/assets/biztek_ceo_insights/logo.png",
# 		"title": "Biztek CEO Insights",
# 		"route": "/biztek_ceo_insights",
# 		"has_permission": "biztek_ceo_insights.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# KPI page CSS is loaded from the page JS (not global desk include)
# app_include_js = "/assets/biztek_ceo_insights/js/biztek_ceo_insights.js"

# include js, css files in header of web template
# web_include_css = "/assets/biztek_ceo_insights/css/biztek_ceo_insights.css"
# web_include_js = "/assets/biztek_ceo_insights/js/biztek_ceo_insights.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "biztek_ceo_insights/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "biztek_ceo_insights/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "biztek_ceo_insights.utils.jinja_methods",
# 	"filters": "biztek_ceo_insights.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "biztek_ceo_insights.install.before_install"
# after_install = "biztek_ceo_insights.install.after_install"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "biztek_ceo_insights.utils.before_app_install"
# after_app_install = "biztek_ceo_insights.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "biztek_ceo_insights.utils.before_app_uninstall"
# after_app_uninstall = "biztek_ceo_insights.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "biztek_ceo_insights.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "biztek_ceo_insights.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"biztek_ceo_insights.tasks.all"
# 	],
# 	"daily": [
# 		"biztek_ceo_insights.tasks.daily"
# 	],
# 	"hourly": [
# 		"biztek_ceo_insights.tasks.hourly"
# 	],
# 	"weekly": [
# 		"biztek_ceo_insights.tasks.weekly"
# 	],
# 	"monthly": [
# 		"biztek_ceo_insights.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "biztek_ceo_insights.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "biztek_ceo_insights.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "biztek_ceo_insights.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "biztek_ceo_insights.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["biztek_ceo_insights.utils.before_request"]
# after_request = ["biztek_ceo_insights.utils.after_request"]

# Job Events
# ----------
# before_job = ["biztek_ceo_insights.utils.before_job"]
# after_job = ["biztek_ceo_insights.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"biztek_ceo_insights.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

