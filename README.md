### Biztek CEO Insights

BI Dashboards for Biztek

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/ajnaso10/biztek-ceo-insights --branch version-16
bench install-app biztek_ceo_insights
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/biztek_ceo_insights
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit

### Migration note

This repository was renamed from `biztek-insights` (`biztek_insights`, display title Biztek Insights). The GitHub repository itself is renamed separately to https://github.com/ajnaso10/biztek-ceo-insights; after that rename, update an existing clone with `git remote set-url origin https://github.com/ajnaso10/biztek-ceo-insights.git`.

A site that already has the app installed cannot switch names with `bench migrate` alone. Frappe identifies the app by the directory under `apps/`, the `sites/apps.txt` entry, the `installed_apps` global, and Module Def `Biztek Insights`. Pulling this change inside `apps/biztek_insights` leaves the wrong folder name, and `hooks.py` will no longer import as `biztek_insights`.

From the bench root, with workers stopped:

1. Uninstall only if you do it **before** replacing the code, and only if the Insights workspace and CEO Insight Dashboard page have no site-specific edits you need to keep. Uninstall deletes the workspace this app owns.

```bash
bench --site <site> uninstall-app biztek_insights
```

Then remove `apps/biztek_insights`, install the renamed app, and skip the database steps below:

```bash
bench get-app https://github.com/ajnaso10/biztek-ceo-insights --branch version-16
bench --site <site> install-app biztek_ceo_insights
bench build --app biztek_ceo_insights
bench restart
```

2. To keep the existing site records, rename the checkout instead of uninstalling. The app directory must match `app_name`:

```bash
mv apps/biztek_insights apps/biztek_ceo_insights
```

In `sites/apps.txt`, replace the `biztek_insights` line with `biztek_ceo_insights`. Reinstall the Python package and drop the old asset symlink:

```bash
./env/bin/pip uninstall -y biztek_insights
./env/bin/pip install -e apps/biztek_ceo_insights
rm -f sites/assets/biztek_insights
bench build --app biztek_ceo_insights
```

3. Point the site database at the new app before migrate. From `bench --site <site> console`:

```python
import json

apps = json.loads(frappe.db.get_global("installed_apps") or "[]")
frappe.db.set_global(
    "installed_apps",
    json.dumps(["biztek_ceo_insights" if a == "biztek_insights" else a for a in apps]),
)

if frappe.db.exists("DocType", "Installed Application"):
    old = frappe.db.get_value("Installed Application", {"app_name": "biztek_insights"}, "name")
    if old:
        frappe.rename_doc("Installed Application", old, "biztek_ceo_insights", force=True)

if frappe.db.exists("Module Def", "Biztek Insights"):
    frappe.rename_doc("Module Def", "Biztek Insights", "Biztek CEO Insights", force=True)
    frappe.db.set_value(
        "Module Def", "Biztek CEO Insights", "app_name", "biztek_ceo_insights", update_modified=False
    )

frappe.db.sql("update `tabWorkspace` set app=%s where app=%s", ("biztek_ceo_insights", "biztek_insights"))
frappe.db.commit()
```

`rename_doc` on Module Def rewrites Link fields such as Page, DocType, and Report. `after_migrate` also sets the Insights workspace `app` and `module`. Then:

```bash
bench --site <site> migrate
bench restart
```

Server Scripts, client scripts, and any external caller of `biztek_insights.*` (for example `biztek_insights.kpi.api.get_kpi_cards`) must use `biztek_ceo_insights.*`. Public asset URLs move from `/assets/biztek_insights/` to `/assets/biztek_ceo_insights/`. There are no patches under the old dotted path. The Frappe Insights app (`insights`) is unchanged.
