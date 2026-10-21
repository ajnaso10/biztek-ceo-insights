// Copyright (c) 2026, Savad Ibrahim and Contributors
// License: MIT

frappe.pages["ceo-insight-dashboard"].on_page_load = function (wrapper) {
	if (!document.getElementById("ceo-kpi-css")) {
		const link = document.createElement("link");
		link.id = "ceo-kpi-css";
		link.rel = "stylesheet";
		link.href = "/assets/biztek_insights/css/ceo_kpi.css?v=5";
		document.head.appendChild(link);
	}

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("CEO Insight Dashboard"),
		single_column: true,
	});
	frappe.ceo_insight_dashboard = new CeoInsightDashboard(page, wrapper);
};

frappe.pages["ceo-insight-dashboard"].on_page_show = function () {
	if (frappe.ceo_insight_dashboard) {
		frappe.ceo_insight_dashboard.apply_route_options();
		frappe.ceo_insight_dashboard.refresh();
	}
};

class CeoInsightDashboard {
	constructor(page, wrapper) {
		this.page = page;
		this.wrapper = wrapper;
		this.data = null;
		this.detail_kpi = null;
		this.fields = {};

		this.$root = $(`<div class="ceo-kpi-page"></div>`).appendTo(page.main);
		this.$toolbar = $(`<div class="ceo-kpi-toolbar"></div>`).appendTo(this.$root);
		this.$content = $(`<div class="ceo-kpi-content"></div>`).appendTo(this.$root);

		this.make_filters();
		this.make_actions();
		this.apply_route_options();
		this.refresh();
	}

	make_filters() {
		const today = frappe.datetime.get_today();
		const month_start = frappe.datetime.month_start(today);

		this.fields.company = this.add_filter_field({
			label: __("Company"),
			fieldtype: "Link",
			fieldname: "company",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
			css_class: "ceo-kpi-filter--company",
		});

		this.fields.from_date = this.add_filter_field({
			label: __("From Date"),
			fieldtype: "Date",
			fieldname: "from_date",
			default: month_start,
			reqd: 1,
		});

		this.fields.to_date = this.add_filter_field({
			label: __("To Date"),
			fieldtype: "Date",
			fieldname: "to_date",
			default: today,
			reqd: 1,
		});

		this.fields.as_on = this.add_filter_field({
			label: __("As On"),
			fieldtype: "Date",
			fieldname: "as_on",
			default: today,
			reqd: 1,
		});
	}

	add_filter_field(df) {
		const $wrap = $(`
			<div class="ceo-kpi-filter ${df.css_class || ""}">
				<label class="ceo-kpi-filter-label">${frappe.utils.escape_html(df.label)}</label>
				<div class="ceo-kpi-filter-control"></div>
			</div>
		`).appendTo(this.$toolbar);

		const field = frappe.ui.form.make_control({
			df: {
				...df,
				label: df.label,
				placeholder: df.label,
			},
			parent: $wrap.find(".ceo-kpi-filter-control"),
			render_input: true,
			only_input: true,
		});
		field.refresh();
		if (df.default) {
			field.set_input(df.default);
		}
		field.$input?.on("change", () => this.refresh());
		if (df.fieldtype === "Link") {
			field.$input?.on("awesomplete-selectcomplete", () => this.refresh());
		}
		return field;
	}

	make_actions() {
		this.page.set_primary_action(__("Refresh"), () => this.refresh());
	}

	apply_route_options() {
		const opts = frappe.route_options || {};
		["company", "from_date", "to_date", "as_on"].forEach((key) => {
			if (opts[key] && this.fields[key]) {
				this.fields[key].set_value(opts[key]);
			}
		});
		if (opts.kpi) {
			this.detail_kpi = opts.kpi;
		}
		frappe.route_options = null;
	}

	get_filter_args() {
		return {
			company: this.fields.company.get_value(),
			from_date: this.fields.from_date.get_value(),
			to_date: this.fields.to_date.get_value(),
			as_on: this.fields.as_on.get_value(),
		};
	}

	set_page_title(title) {
		this.page.set_title(title || __("CEO Insight Dashboard"));
	}

	async refresh() {
		const args = this.get_filter_args();
		if (!args.company) {
			this.$content.html(
				`<div class="text-muted p-3">${__("Select a Company to load KPIs.")}</div>`
			);
			return;
		}

		this.$content.html(`<div class="text-muted p-3">${__("Loading…")}</div>`);

		try {
			if (this.detail_kpi) {
				const detail = await frappe.xcall("biztek_insights.kpi.api.get_kpi_detail", {
					kpi_id: this.detail_kpi,
					...args,
				});
				this.render_detail(detail);
			} else {
				this.data = await frappe.xcall("biztek_insights.kpi.api.get_kpi_cards", args);
				this.render_cards();
			}
		} catch (e) {
			this.$content.html(
				`<div class="text-danger p-3">${__("Failed to load KPIs.")}</div>`
			);
			console.error(e);
		}
	}

	render_cards() {
		this.set_page_title(__("CEO Insight Dashboard"));
		this.page.clear_secondary_action();

		const sections = (this.data && this.data.sections) || [];
		const $html = $(`<div class="ceo-kpi-inner"><div class="ceo-kpi-sections"></div></div>`);
		const $sections = $html.find(".ceo-kpi-sections");

		sections.forEach((section) => {
			const $sec = $(`
				<section class="ceo-kpi-section">
					<h3 class="ceo-kpi-section-title">${frappe.utils.escape_html(section.label)}</h3>
					<div class="ceo-kpi-grid"></div>
				</section>
			`);
			const $grid = $sec.find(".ceo-kpi-grid");
			(section.cards || []).forEach((card) => {
				$grid.append(this.card_html(card));
			});
			$sections.append($sec);
		});

		this.$content.empty().append($html);
		this.$content.find(".ceo-kpi-card").on("click", (e) => {
			const id = $(e.currentTarget).data("kpi-id");
			this.open_detail(id);
		});
	}

	card_html(card) {
		const unavailable = !card.available;
		let value_html;
		if (unavailable) {
			value_html = `<div class="ceo-kpi-value">${__("Unavailable")}</div>
				<div class="ceo-kpi-reason">${frappe.utils.escape_html(card.reason || "")}</div>`;
		} else {
			value_html = `<div class="ceo-kpi-value" title="${frappe.utils.escape_html(
				this.format_value_full(card)
			)}">${this.format_value(card)}</div>`;
			if (card.secondary) {
				value_html += `<div class="ceo-kpi-secondary">${frappe.utils.escape_html(
					card.secondary.label || ""
				)}: ${frappe.utils.escape_html(this.format_secondary(card.secondary))}</div>`;
			}
		}

		return $(`
			<div class="ceo-kpi-card ${unavailable ? "ceo-kpi-card--unavailable" : ""}"
				data-kpi-id="${frappe.utils.escape_html(card.id)}"
				role="button" tabindex="0">
				<span class="ceo-kpi-card-label">${frappe.utils.escape_html(card.label)}</span>
				${value_html}
			</div>
		`);
	}

	format_value(card) {
		const v = card.value;
		if (v === null || v === undefined) {
			return "—";
		}
		if (card.format === "currency") {
			return this.format_compact_currency(v, card.currency);
		}
		if (card.format === "float") {
			return this.format_compact_number(v, 1);
		}
		return this.format_compact_number(v, 0);
	}

	format_value_full(card) {
		const v = card.value;
		if (v === null || v === undefined) {
			return "";
		}
		if (card.format === "currency") {
			return format_currency(v, card.currency);
		}
		if (card.format === "float") {
			return format_number(v);
		}
		return format_number(v, null, 0);
	}

	format_compact_number(value, precision) {
		const n = Number(value);
		if (Number.isNaN(n)) {
			return String(value);
		}
		if (Math.abs(n) < 1000) {
			return format_number(n, null, precision || 0);
		}
		try {
			return new Intl.NumberFormat(frappe.boot.lang || undefined, {
				notation: "compact",
				maximumFractionDigits: precision ?? 1,
			}).format(n);
		} catch (e) {
			return format_number(n, null, precision || 0);
		}
	}

	format_compact_currency(value, currency) {
		const n = Number(value);
		if (Number.isNaN(n)) {
			return String(value);
		}
		const code = currency || frappe.boot.sysdefaults?.currency || "AED";
		if (Math.abs(n) < 1000) {
			return format_currency(n, code);
		}
		try {
			return new Intl.NumberFormat(frappe.boot.lang || undefined, {
				style: "currency",
				currency: code,
				notation: "compact",
				maximumFractionDigits: 1,
			}).format(n);
		} catch (e) {
			return format_currency(n, code);
		}
	}

	format_secondary(secondary) {
		if (!secondary) {
			return "";
		}
		if (secondary.format === "number" && typeof secondary.value === "number") {
			return this.format_compact_number(secondary.value, 0);
		}
		if (secondary.format === "float" && typeof secondary.value === "number") {
			return this.format_compact_number(secondary.value, 1);
		}
		return String(secondary.value ?? "");
	}

	open_detail(kpi_id) {
		this.detail_kpi = kpi_id;
		this.refresh();
	}

	back_to_cards() {
		this.detail_kpi = null;
		this.refresh();
	}

	render_detail(detail) {
		const card = detail.card || {};
		const label = detail.label || card.label || __("Detail");
		const insights_path = detail.insights_path || card.insights_path || "/insights/dashboards";
		const insights_fallback = detail.insights && detail.insights.is_fallback;
		this.set_page_title(label);

		this.page.set_secondary_action(__("Back"), () => this.back_to_cards());

		const value_line =
			card.available === false
				? __("Unavailable")
				: `${this.format_value_full(card)}${
						card.secondary
							? ` · ${card.secondary.label}: ${this.format_secondary(card.secondary)}`
							: ""
				  }`;

		const $html = $(`
			<div class="ceo-kpi-detail">
				<div class="ceo-kpi-nav">
					<button type="button" class="ceo-kpi-back-btn">
						<span aria-hidden="true">←</span> ${__("Back to KPIs")}
					</button>
					<div class="ceo-kpi-breadcrumb">
						<a href="#" class="ceo-kpi-back">${__("CEO Insight Dashboard")}</a>
						<span>/</span>
						<span class="ceo-kpi-breadcrumb__current">${frappe.utils.escape_html(label)}</span>
					</div>
				</div>
				<div class="ceo-kpi-detail-header">
					<div>
						<h2 class="ceo-kpi-detail-title">${frappe.utils.escape_html(label)}</h2>
						<p class="ceo-kpi-detail-value">${frappe.utils.escape_html(value_line)}</p>
						<p class="ceo-kpi-detail-formula">${frappe.utils.escape_html(detail.formula_doc || "")}</p>
						${
							insights_fallback
								? `<p class="ceo-kpi-detail-note">${__(
										"Charts open the CEO Command Center until the CEO workbook template is updated in Insights."
								  )}</p>`
								: ""
						}
					</div>
					<button type="button" class="btn btn-default btn-sm ceo-kpi-open-insights">
						${__("Open in Insights")}
					</button>
				</div>
				<div class="ceo-kpi-detail-body"></div>
			</div>
		`);

		$html.find(".ceo-kpi-detail-body").append(this.render_detail_table(detail));

		this.$content.empty().append($html);

		const go_back = (e) => {
			e.preventDefault();
			this.back_to_cards();
		};
		this.$content.find(".ceo-kpi-back-btn, .ceo-kpi-back").on("click", go_back);
		this.$content.find(".ceo-kpi-open-insights").on("click", () => {
			window.open(insights_path, "_blank");
		});
	}

	render_detail_table(detail) {
		const data = detail.detail;
		if (!data) {
			return $(`<div class="text-muted p-2">${__("No supporting rows.")}</div>`);
		}

		if (detail.kpi_id === "hr_kpi" && !Array.isArray(data)) {
			return $(`
				<div class="ceo-kpi-hr-metrics">
					<div class="ceo-kpi-hr-metric">
						<span class="ceo-kpi-hr-metric__label">${__("Active Headcount")}</span>
						<div class="ceo-kpi-hr-metric__value">${data.headcount ?? "—"}</div>
					</div>
					<div class="ceo-kpi-hr-metric">
						<span class="ceo-kpi-hr-metric__label">${__("New Hires")}</span>
						<div class="ceo-kpi-hr-metric__value">${data.hires ?? "—"}</div>
					</div>
					<div class="ceo-kpi-hr-metric">
						<span class="ceo-kpi-hr-metric__label">${__("Exits")}</span>
						<div class="ceo-kpi-hr-metric__value">${data.exits ?? "—"}</div>
					</div>
					<div class="ceo-kpi-hr-metric">
						<span class="ceo-kpi-hr-metric__label">${__("Attrition %")}</span>
						<div class="ceo-kpi-hr-metric__value">${
							data.attrition_pct != null ? format_number(data.attrition_pct) : "—"
						}</div>
						<div class="ceo-kpi-secondary">${frappe.utils.escape_html(
							data.attrition_formula || ""
						)}</div>
					</div>
				</div>
			`);
		}

		if (!Array.isArray(data) || !data.length) {
			return $(`<div class="text-muted p-2">${__("No supporting rows.")}</div>`);
		}

		const keys = Object.keys(data[0]).filter((k) => !k.startsWith("_"));
		const thead = keys
			.map((k) => `<th>${frappe.utils.escape_html(frappe.model.unscrub(k))}</th>`)
			.join("");
		const rows = data
			.slice(0, 200)
			.map((row) => {
				const cells = keys
					.map((k) => `<td>${frappe.utils.escape_html(String(row[k] ?? ""))}</td>`)
					.join("");
				return `<tr>${cells}</tr>`;
			})
			.join("");

		return $(`
			<div class="table-responsive">
				<table class="table table-bordered table-sm">
					<thead><tr>${thead}</tr></thead>
					<tbody>${rows}</tbody>
				</table>
			</div>
		`);
	}
}
