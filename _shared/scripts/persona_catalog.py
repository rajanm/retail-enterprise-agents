#!/usr/bin/env python3
"""
persona_catalog.py — Retail Enterprise Persona Archetypes & Transformation Engine

Provides curated definitions for 10 Retail Persona Archetypes, their 4-stage
"Day in the Life: Without vs. With Gemini Enterprise Agents" chronological workflows,
and resilient extraction/synthesis of persona and transformation metadata across
all 100 retail enterprise agents.
"""

import re
from typing import Any

PERSONA_ORDER: list[str] = [
    "exec_leadership",
    "merchandising_buyers",
    "inventory_planners",
    "supply_chain_logistics",
    "store_field_ops",
    "ecommerce_digital",
    "marketing_loyalty",
    "finance_fpa",
    "customer_care_cx",
    "hr_esg_compliance",
]

PERSONA_ARCHETYPES: list[dict[str, Any]] = [
    {
        "id": "exec_leadership",
        "icon": "👔",
        "title": "C-Suite & VP Leadership",
        "subtitle": "Cross-Functional Strategic Governance & P&L Oversight",
        "roles_summary": "Chief Executive Officer, Chief Financial Officer, Chief Marketing Officer, CHRO, CSO, and VPs of Operations, Digital, and Merchandising.",
        "hours_saved": "Cycle Time: Weeks → Hours",
        "decision_speed": "Effort: Days → Minutes",
        "automated_pct": 60,
        "augmented_pct": 40,
        "automated_label": "Automated: Multi-Domain KPIs, Anomaly Alerts & Readouts",
        "augmented_label": "Augmented: Capital Allocation & Enterprise Strategy",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Enterprise Morning Pulse & P&L Anomaly Triage",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Sifting through fragmented executive PDF decks, cross-referencing disparate revenue reports, and emailing BI directors for clarification on margin erosion.",
                "with_agents": "Reviewing an automated Gemini Enterprise executive briefing highlighting gross margin variances, district labor anomalies, and cash flow projections instantly.",
                "automated_what": "Multi-domain KPI aggregation across BigQuery financial and operations tables with automated outlier flags.",
                "augmented_what": "Evaluating strategic capital allocation priorities and deciding which regional VPs require executive check-ins.",
                "featured_agents": ["gross_margin_profitability", "store_pnl_operating_costs", "working_capital_cashflow", "inventory_valuation_provisions", "gift_card_breakage_liability", "store_associate_turnover_retention"],
            },
            {
                "time": "Stage 2",
                "stage": "Multi-Source Root-Cause & Capital Allocation Review",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Hours",
                "without_agents": "Convening cross-functional crisis meetings with merchandising and supply chain leads to untangle root causes of regional quarterly earnings misses.",
                "with_agents": "Querying root agents in plain English with multi-turn reasoning to isolate whether margin drag stems from freight surcharges, promotions, or store labor drift.",
                "automated_what": "Conversational contribution analysis, multi-table variance attribution, and variance trend modeling.",
                "augmented_what": "Deciding executive mitigation policies, vendor rebate dispute escalation, and seasonal budget reallocations.",
                "featured_agents": ["corporate_budget_variance_fpna", "vendor_negotiation_rebates", "vendor_recovery_audit_compliance", "store_real_estate_lease_mgmt", "customer_acquisition_cost_cac", "campaign_performance_roi"],
            },
            {
                "time": "Stage 3",
                "stage": "Market Intelligence & Competitor Positioning",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Minutes",
                "without_agents": "Waiting days for consulting briefs or manual investor relations research summarizing macroeconomic shifts, tariff updates, and competitor discount waves.",
                "with_agents": "Engaging Google Search grounded sub-agents to benchmark company performance against published quarterly retail earnings, tariff policies, and competitor actions.",
                "automated_what": "Real-time Google Search synthesis of retail competitor earnings, inflation benchmarks, and tariff rulings.",
                "augmented_what": "Formulating long-term enterprise pricing defense and strategic hedging strategies for upcoming quarters.",
                "featured_agents": ["marketplace_seller_performance", "b2b_wholesale_portal_analytics", "omnichannel_customer_cdp_insights", "voice_of_customer_sentiment_nlp", "ethical_sourcing_labor_audits", "dei_supplier_diversity_spend"],
            },
            {
                "time": "Stage 4",
                "stage": "Board & Executive Readout Synthesis",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Directing administrative chiefs and analysts through stressful late-night slide deck revisions, copy-pasting charts into static presentation slides.",
                "with_agents": "Directing the agent to generate interactive 4-slide executive review Canvas summaries with embedded Matplotlib margin curves and action items.",
                "automated_what": "Automated Matplotlib visual chart generation, trend visualization, and structured executive briefing summaries.",
                "augmented_what": "Refining executive narrative, board messaging, and shareholder talking points ahead of quarterly committee meetings.",
                "featured_agents": ["carbon_footprint_scope_emissions", "energy_renewable_grid_transition", "product_safety_recall_readiness", "labor_union_compliance_cba", "training_onboarding_compliance"],
            },
        ],
    },
    {
        "id": "merchandising_buyers",
        "icon": "🛍️",
        "title": "Category & Merchandising Managers",
        "subtitle": "Assortment Breadth, Pricing Elasticity & SKU Rationalization",
        "roles_summary": "Category Managers, Senior Buyers, Merchandising Directors, Pricing Strategists, and Planogram Assortment Planners.",
        "hours_saved": "Cycle Time: Weeks → Hours",
        "decision_speed": "Effort: Days → Minutes",
        "automated_pct": 65,
        "augmented_pct": 35,
        "automated_label": "Automated: SKU Velocity, Elasticity & Space Analytics",
        "augmented_label": "Augmented: Assortment Mix & Vendor Negotiations",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Category SKU Health & Velocity Screening",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Manually downloading weekly point-of-sale spreadsheets, VLOOKUP-ing vendor catalogues, and manually calculating SKU sell-through rates across regions.",
                "with_agents": "Reviewing an automated Category Velocity Briefing ranking underperforming SKUs, stockout risks, and margin dilutive products across all store clusters.",
                "automated_what": "Point-of-sale data aggregation across BigQuery tables, velocity scoring, and automated markdown trigger flags.",
                "augmented_what": "Determining whether bottom-decile SKUs should receive markdown promotions, vendor returns, or delisting.",
                "featured_agents": ["assortment_planning", "markdown_clearance_optimization", "item_lifecycle_rationalization", "category_growth_strategy", "seasonal_transition_planning", "returns_reverse_logistics"],
            },
            {
                "time": "Stage 2",
                "stage": "Promotional Price Elasticity & Cannibalization Modeling",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Hours",
                "without_agents": "Building complex regression spreadsheets to guess whether a 20% discount on premium coffee will generate incremental gross margin lift or cannibalize house brands.",
                "with_agents": "Prompting the Pricing & Promotions agent to run Conversational Analytics elasticity models and forecast baseline lift vs cannibalization rates.",
                "automated_what": "Time-series forecasting, historical elasticity curve calculations, and baseline promotional lift isolation.",
                "augmented_what": "Finalizing promotional calendar depth, promotional co-op vendor funding, and feature circular ad placement.",
                "featured_agents": ["pricing_promotions", "trade_spend_effectiveness", "private_brand_development", "size_pack_optimization", "voice_of_customer_sentiment_nlp"],
            },
            {
                "time": "Stage 3",
                "stage": "Competitor Price Scraping & Market Grounding",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Minutes",
                "without_agents": "Visiting competitor websites manually, checking pricing discrepancies, and debating vendor cost concessions without verified market intelligence.",
                "with_agents": "Using Google Search grounding to scan real-time competitor promotions, MAP policy violations, and market-wide commodity raw material price trends.",
                "automated_what": "Web search extraction of omnichannel competitor pricing, manufacturer promotions, and retail category press.",
                "augmented_what": "Negotiating cost concessions and clawback allowances with suppliers during quarterly vendor reviews.",
                "featured_agents": ["price_matching_competitor_intel", "vendor_negotiation_rebates", "vendor_performance", "customs_import_tariff_compliance", "inbound_freight_optimization", "ethical_sourcing_labor_audits"],
            },
            {
                "time": "Stage 4",
                "stage": "Assortment Rationalization & Planogram Reset Memo",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Drafting multi-page line review documents and manually pasting floor planogram screenshots into presentations for retail field merchandisers.",
                "with_agents": "Commanding the agent to generate an Assortment Rationalization Memo with Matplotlib sales-per-square-foot charts and space reallocation recs.",
                "automated_what": "Space productivity calculation ($/sq.ft), chart rendering, and automated planogram reset action summaries.",
                "augmented_what": "Approving final seasonal space reallocations between national brands and high-margin private label lines.",
                "featured_agents": ["space_planning_micro_merch", "localized_curation_clustering", "visual_merchandising_compliance", "chemical_restricted_substances_rsl", "dei_supplier_diversity_spend", "sustainable_packaging_circularity"],
            },
        ],
    },
    {
        "id": "inventory_planners",
        "icon": "📦",
        "title": "Demand & Inventory Planners",
        "subtitle": "Multi-Echelon Replenishment, Safety Stock & DC Flow-Through",
        "roles_summary": "Demand Planners, Inventory Controllers, Allocation Analysts, Replenishment Managers, and Safety Stock Specialists.",
        "hours_saved": "Cycle Time: Days → Minutes",
        "decision_speed": "Effort: Hours → Minutes",
        "automated_pct": 75,
        "augmented_pct": 25,
        "automated_label": "Automated: Multi-Echelon Replenishment & Stockout Alerts",
        "augmented_label": "Augmented: Safety Stock Policies & Disruption Triage",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Out-of-Stock Risk & Lead Time Drift Alerting",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Manually reviewing thousands of ERP exception lines, cross-checking supplier lead times against open purchase orders, and flagging stockout risks.",
                "with_agents": "Receiving prioritized alerts of DC and store SKU inventory dips below dynamic safety stock thresholds with predicted stockout dates.",
                "automated_what": "Automated BigQuery joins across DC inventory, store pipeline, and vendor transit lead-time drift models.",
                "augmented_what": "Selecting expedited freight routes or emergency transfer orders for top revenue-generating SKUs.",
                "featured_agents": ["inventory_planning", "sell_through_inventory_health", "vendor_performance", "item_lifecycle_rationalization"],
            },
            {
                "time": "Stage 2",
                "stage": "Multi-Echelon Safety Stock Parameter Optimization",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Hours",
                "without_agents": "Recalculating static safety stock formulas in spreadsheet workbooks with stale standard deviations of demand and supplier variability.",
                "with_agents": "Simulating optimal multi-echelon safety stock levels across central distribution centers and forward regional fulfillment hubs using conversational forecasting.",
                "automated_what": "Stochastic demand variance modeling, service level probability calculations, and safety stock recalculations.",
                "augmented_what": "Balancing inventory carrying cost budgets against corporate 98.5% on-shelf availability targets.",
                "featured_agents": ["multi_echelon_safety_stock", "seasonal_transition_planning", "size_pack_optimization", "inventory_valuation_provisions"],
            },
            {
                "time": "Stage 3",
                "stage": "Supply Disruptions & Weather Impact Grounding",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Hearing about port congestion or severe weather delays via freight carrier email chains hours after replenishment orders were dispatched.",
                "with_agents": "Querying real-time port logistics delays, maritime weather disruptions, and regional severe storm forecasts via Google Search grounding.",
                "automated_what": "Correlating live weather and port congestion news with affected inbound PO containers and destination DCs.",
                "augmented_what": "Authorizing dynamic rerouting of container shipments to secondary regional cross-dock facilities.",
                "featured_agents": ["supplier_risk_resilience", "inbound_freight_optimization", "cold_chain_temperature_compliance", "customs_import_tariff_compliance"],
            },
            {
                "time": "Stage 4",
                "stage": "Automated PO Allocation & Reorder Scheduling",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Keying purchase order quantities line-by-line into legacy ERP ordering systems with risk of typographical errors.",
                "with_agents": "Validating agent-generated optimal order quantity (EOQ) proposals and bulk-submitting approved replenishment schedules to suppliers.",
                "automated_what": "Economic order quantity calculation, minimum order quantity constraints, and structured PO payload generation.",
                "augmented_what": "Conducting final human-in-the-loop review on million-dollar high-velocity seasonal inventory commitments.",
                "featured_agents": ["cross_dock_flow_through", "warehouse_dc_operations", "localized_curation_clustering", "returns_reverse_logistics"],
            },
        ],
    },
    {
        "id": "supply_chain_logistics",
        "icon": "🚚",
        "title": "Supply Chain & DC Leaders",
        "subtitle": "Vendor OTIF SLAs, Fleet Dispatch & Cold-Chain Compliance",
        "roles_summary": "Supply Chain VPs, Inbound Logistics Directors, Distribution Center General Managers, Fleet Dispatchers, and Customs Officers.",
        "hours_saved": "Cycle Time: Days → Minutes",
        "decision_speed": "Effort: Hours → Minutes",
        "automated_pct": 70,
        "augmented_pct": 30,
        "automated_label": "Automated: Yard Flow, OTIF Scorecards & Route Dispatch",
        "augmented_label": "Augmented: Carrier Allocation & Exception Resolution",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Inbound Yard & Dock Flow Exception Monitoring",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Radioing gatehouse guards and yard spotters to manually locate late trailers, creating dock door scheduling bottlenecks.",
                "with_agents": "Viewing an automated DC Flow Board showing inbound trailers, dock appointment compliance, and detention demurrage risk flags.",
                "automated_what": "Real-time WMS telemetry queries, trailer turnaround tracking, and automated carrier detention risk scoring.",
                "augmented_what": "Prioritizing perishable cold-chain and promotional freight dock doors over general merchandise.",
                "featured_agents": ["warehouse_dc_operations", "cold_chain_temperature_compliance", "cross_dock_flow_through", "dc_automation_robotics_kpis", "inventory_planning", "multi_echelon_safety_stock"],
            },
            {
                "time": "Stage 2",
                "stage": "Supplier OTIF Scorecard & Penalty Dispute Review",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Hours",
                "without_agents": "Arguing with vendor logistics reps over missing PO lines and spreadsheet timestamps to substantiate OTIF chargebacks.",
                "with_agents": "Executing Conversational Analytics queries against BigQuery vendor delivery tables to produce audit-ready OTIF scorecards with breakdown of carrier vs supplier fault.",
                "automated_what": "On-Time In-Full calculation, root-cause attribution, and automated chargeback penalty calculation.",
                "augmented_what": "Conducting quarterly vendor compliance renegotiations and waiving disputed penalties for strategic partners.",
                "featured_agents": ["vendor_performance", "supplier_risk_resilience", "vendor_recovery_audit_compliance", "damaged_goods_claims_resolution", "product_warranty_claims_repair", "returns_reverse_logistics"],
            },
            {
                "time": "Stage 3",
                "stage": "Diesel Fuel, Tariff & Freight Rate Grounding",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Subscribing to expensive static freight indices and manually checking national diesel fuel surcharge tables for spot market quotes.",
                "with_agents": "Grounding spot freight negotiations with real-time DAT freight rate indices, national diesel averages, and tariff updates via Google Search.",
                "automated_what": "Live retrieval and synthesis of national carrier spot rates, fuel surcharges, and customs tariff rulings.",
                "augmented_what": "Locking in contracted dedicated fleet commitments vs spot brokerage carrier allocations.",
                "featured_agents": ["inbound_freight_optimization", "customs_import_tariff_compliance", "carbon_footprint_scope_emissions", "extended_producer_responsibility_epr", "sustainable_packaging_circularity"],
            },
            {
                "time": "Stage 4",
                "stage": "Last-Mile Delivery Dispatch & Route Optimization",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Manually rebalancing delivery route sheets when final customer fulfillment parcels miss consolidation cutoffs.",
                "with_agents": "Reviewing agent-optimized last-mile dispatch recommendations factoring in driver hours of service, package cube, and delivery time windows.",
                "automated_what": "Vehicle routing optimization, parcel density calculations, and delivery ETA risk forecasting.",
                "augmented_what": "Resolving customer exception escalations and high-priority VIP same-day delivery dispatch reroutes.",
                "featured_agents": ["last_mile_delivery_dispatch", "logistics_operations", "packaging_dunnage_optimization", "size_pack_optimization", "omnichannel_returns_in_store", "wismo_order_tracking_resolution"],
            },
        ],
    },
    {
        "id": "store_field_ops",
        "icon": "🏬",
        "title": "Store & Field Operations",
        "subtitle": "Labor Productivity, Planogram Compliance & Omnichannel BOPIS",
        "roles_summary": "Store General Managers, District Operations Directors, Store Fulfillment Leads, Loss Prevention Managers, and Visual Merchandisers.",
        "hours_saved": "Cycle Time: Days → Minutes",
        "decision_speed": "Effort: Hours → Minutes",
        "automated_pct": 60,
        "augmented_pct": 40,
        "automated_label": "Automated: Labor Variances, BOPIS Tracking & Till Audits",
        "augmented_label": "Augmented: Floor Staffing & Store Incident Defense",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Store Labor Scheduling & Traffic Variance Review",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Comparing printed store foot-traffic logs against yesterday's punch-clock timesheets to compute sales per labor hour (SPLH) manually.",
                "with_agents": "Receiving morning district labor alerts highlighting stores exceeding overtime limits or understaffed during peak shopping hours.",
                "automated_what": "BigQuery payroll and POS time-clock analysis with sales-per-labor-hour efficiency calculations.",
                "augmented_what": "Authorizing shift adjustments and cross-training assignments between checkout and curbside pickup teams.",
                "featured_agents": ["labor_productivity", "workforce_scheduling_fairness", "pos_checkout_queue_analytics", "store_pnl_operating_costs", "energy_facilities_maintenance", "capex_store_remodel_roi"],
            },
            {
                "time": "Stage 2",
                "stage": "Omnichannel BOPIS & Curbside Velocity Diagnosis",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Walking store staging areas to investigate why customer curbside wait times are exceeding store SLA thresholds.",
                "with_agents": "Conversing with the Curbside & Store Fulfillment agents to isolate picking bottlenecks, missing shelf locations, and order staging delays.",
                "automated_what": "Order pick-pack-stage cycle time tracking, picker path analysis, and dwell time anomaly detection.",
                "augmented_what": "Reallocating store floor associates to high-volume staging zones during peak midday click-and-collect surges.",
                "featured_agents": ["curbside_pickup_speed_accuracy", "store_fulfillment_execution", "omnichannel_returns_in_store", "sell_through_inventory_health", "size_pack_optimization", "store_associate_support_hotline"],
            },
            {
                "time": "Stage 3",
                "stage": "Local Events & Retail Foot-Traffic Context",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Wondering why foot traffic spiked unexpectedly or why competitor stores down the boulevard are running flash sales.",
                "with_agents": "Grounding store performance with local stadium events, weather forecasts, and competitor store circulars via Google Search.",
                "automated_what": "Real-time search synthesis of regional community events, severe weather advisories, and competitor store openings.",
                "augmented_what": "Adjusting store front-of-house displays and staging grab-and-go refreshments to capitalize on surge footfall.",
                "featured_agents": ["store_manager_operational_audit", "visual_merchandising_compliance", "price_matching_competitor_intel", "product_detail_page_optimization", "food_waste_spoilage_reduction"],
            },
            {
                "time": "Stage 4",
                "stage": "Shrinkage & Cash Variance Audit Sign-Off",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Counting register till discrepancy envelopes and reviewing CCTV logs manually to investigate cashier cash shortages.",
                "with_agents": "Reviewing automated POS till variance exception summaries and high-risk return transaction patterns flagged by Loss Prevention agents.",
                "automated_what": "Statistical cashier exception reporting, till reconciliation variance tracking, and sweet-hearting anomaly detection.",
                "augmented_what": "Initiating formal asset protection investigations and associate retraining programs.",
                "featured_agents": ["loss_prevention_shrinkage", "store_cash_management_tills", "store_safety_incident_management", "workplace_safety_workers_comp", "digital_promotions_coupon_abuse", "returns_appeals_exception_desk"],
            },
        ],
    },
    {
        "id": "ecommerce_digital",
        "icon": "🛒",
        "title": "Digital & E-Commerce Product",
        "subtitle": "Conversion Funnel, Cart Friction, Search & Gateway Health",
        "roles_summary": "VP of E-Commerce, Product Managers for Checkout & Search, Digital Merchandisers, Payment Fraud Analysts, and SEO Leads.",
        "hours_saved": "Cycle Time: Days → Minutes",
        "decision_speed": "Effort: Hours → Minutes",
        "automated_pct": 70,
        "augmented_pct": 30,
        "automated_label": "Automated: Funnel Diagnostics, Query Clusters & Seller SLAs",
        "augmented_label": "Augmented: Checkout UX & Search Merchandising Strategy",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Checkout Funnel Drop-Off & Error Spike Triage",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Logging into multiple web analytics dashboards, filtering desktop vs mobile checkout drop-offs, and querying logs for payment errors.",
                "with_agents": "Receiving an automated Checkout Health Alert identifying step-by-step funnel drop-offs, gateway timeout surges, and promo code failures.",
                "automated_what": "Hourly session log aggregation, funnel step conversion calculation, and error code anomaly detection.",
                "augmented_what": "Triggering emergency checkout UX hotfixes or failing over traffic to secondary payment processing gateways.",
                "featured_agents": ["cart_checkout_analytics", "payment_gateway_fraud_risk", "digital_site_performance_vitals", "digital_promotions_coupon_abuse"],
            },
            {
                "time": "Stage 2",
                "stage": "Zero-Result Site Search & Null Query Discovery",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Downloading massive search query CSV logs, manually categorizing misspelled queries, and adding manual synonym redirects one by one.",
                "with_agents": "Prompting the Search Merchandising agent to analyze top zero-result queries, suggest synonyms, and model search conversion lift.",
                "automated_what": "High-volume search query clustering, zero-result keyword extraction, and search-to-cart conversion correlation.",
                "augmented_what": "Approving automated query synonym rules and prioritizing high-demand unlisted product requests for category buyers.",
                "featured_agents": ["search_merchandising_personalization", "product_detail_page_optimization", "mobile_app_conversion_retention", "ai_chatbot_deflection_handoff"],
            },
            {
                "time": "Stage 3",
                "stage": "Competitive SEO Benchmarking & Keyword Grounding",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Manually searching competitive keywords in incognito browsers and paying for laggy third-party ranking reports.",
                "with_agents": "Using Google Search grounding to benchmark organic search ranking movements against leading e-commerce rivals for core category keywords.",
                "automated_what": "Real-time search engine result page (SERP) ranking checks, rich snippet validation, and competitor title tag audits.",
                "augmented_what": "Refining digital product detail page (PDP) schema metadata and editorial SEO content strategy.",
                "featured_agents": ["web_accessibility_seo_health", "curbside_pickup_speed_accuracy", "wismo_order_tracking_resolution"],
            },
            {
                "time": "Stage 4",
                "stage": "3P Marketplace Seller SLA & Buy-Box Evaluation",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Exporting third-party seller defect rates, late shipment percentages, and customer dispute tallies into manual spreadsheets.",
                "with_agents": "Reviewing Marketplace Seller Performance scorecards with automated Buy-Box suspension and fee withholding recommendations.",
                "automated_what": "Third-party seller SLA compliance computation, order defect rate (ODR) scoring, and buy-box eligibility calculation.",
                "augmented_what": "Authorizing marketplace merchant tier upgrades, suspension warnings, or merchant account closures.",
                "featured_agents": ["marketplace_seller_performance", "subscription_recurring_orders", "sales_tax_nexus_compliance", "extended_producer_responsibility_epr"],
            },
        ],
    },
    {
        "id": "marketing_loyalty",
        "icon": "📊",
        "title": "Marketing, CRM & Retail Media",
        "subtitle": "Blended ROAS, Omnichannel CDP, Churn Win-Back & RMN Yield",
        "roles_summary": "Chief Marketing Officer, Digital Acquisition Leads, CRM & Loyalty Managers, Retail Media Network Directors, and Brand Strategists.",
        "hours_saved": "Cycle Time: Days → Minutes",
        "decision_speed": "Effort: Days → Minutes",
        "automated_pct": 65,
        "augmented_pct": 35,
        "automated_label": "Automated: Multi-Touch ROAS, RFM Scoring & Ad Yield",
        "augmented_label": "Augmented: Campaign Creative & Loyalty Tier Design",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Multi-Channel ROAS & Campaign Pacing Screening",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Logging into Google Ads, Meta Ads, and DSP platforms separately to copy spend and revenue figures into a blended master spreadsheet.",
                "with_agents": "Reviewing an automated Marketing Performance Briefing tracking blended ROAS, customer acquisition cost (CAC), and channel spend pacing.",
                "automated_what": "Multi-channel advertising spend and attributed revenue aggregation with target variance flagging.",
                "augmented_what": "Reallocating daily ad budget caps from underperforming display channels into high-converting paid search campaigns.",
                "featured_agents": ["campaign_performance_roi", "customer_acquisition_cost_cac", "category_growth_strategy", "geotargeted_local_marketing"],
            },
            {
                "time": "Stage 2",
                "stage": "Customer Churn Prediction & Win-Back Cohort Slicing",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Hours",
                "without_agents": "Waiting weeks for the customer data science team to train and score churn probability propensity models.",
                "with_agents": "Prompting Customer Lifecycle & Churn agents to identify high-value customer cohorts whose purchase frequency slipped over the last 60 days.",
                "automated_what": "Recency-Frequency-Monetary (RFM) segmentation, churn risk scoring, and customer lifetime value (CLV) calculation.",
                "augmented_what": "Designing customized VIP incentive tiers, personalized win-back offers, and SMS push campaign journeys.",
                "featured_agents": ["customer_lifecycle_loyalty", "customer_churn_winback_analytics", "omnichannel_customer_cdp_insights", "subscription_recurring_orders"],
            },
            {
                "time": "Stage 3",
                "stage": "Brand Sentiment & Viral Social Trend Grounding",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Relying on anecdotal executive feedback or delayed monthly brand tracker survey readouts to gauge public brand sentiment.",
                "with_agents": "Grounding social sentiment, viral brand mentions, and influencer engagement spikes via real-time Google Search context.",
                "automated_what": "Social sentiment scraping, viral creator campaign tracking, and competitor brand health comparison.",
                "augmented_what": "Pivoting marketing creative themes and responding to public brand perception opportunities.",
                "featured_agents": ["brand_health_social_sentiment", "influencer_creator_campaign_roi", "omnichannel_social_support_desk", "seasonal_hiring_peak_readiness"],
            },
            {
                "time": "Stage 4",
                "stage": "Retail Media Network (RMN) Sponsored Ad Yield Review",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Manually calculating ad inventory fill rates, CPC yield, and brand sponsor ROAS across e-commerce search result banners.",
                "with_agents": "Reviewing automated RMN Yield Dashboards showing available on-site ad inventory, brand advertiser auction fill rates, and yield optimizations.",
                "automated_what": "Ad inventory fill rate calculation, eCPM yield optimization, and vendor co-op ad revenue attribution.",
                "augmented_what": "Presenting quarterly retail media advertising packages and guaranteed impression commitments to major CPG brand partners.",
                "featured_agents": ["retail_media_network_monetization", "email_sms_crm_orchestration", "mobile_app_conversion_retention", "digital_promotions_coupon_abuse"],
            },
        ],
    },
    {
        "id": "finance_fpa",
        "icon": "💰",
        "title": "Finance, FP&A & Real Estate",
        "subtitle": "Gross Margin Profitability, Store P&Ls, Leases & Capital ROI",
        "roles_summary": "Corporate Controllers, FP&A Directors, Commercial Finance Managers, Real Estate Lease Directors, and Inventory Accounting Leads.",
        "hours_saved": "Cycle Time: Weeks → Hours",
        "decision_speed": "Effort: Days → Minutes",
        "automated_pct": 75,
        "augmented_pct": 25,
        "automated_label": "Automated: Store P&L Matrices, LCM Reserves & CapEx Models",
        "augmented_label": "Augmented: Cash Allocation & Commercial Lease Strategy",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Store P&L Variance & Operating Expense Audit",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Running batch ERP trial balances and manually building store-by-store variance matrices against monthly financial plan forecasts.",
                "with_agents": "Receiving an automated Store P&L Exception Briefing ranking store locations with abnormal labor cost or facilities utility expense spikes.",
                "automated_what": "General ledger expense aggregation, plan-vs-actual variance calculation, and store operating cost ranking.",
                "augmented_what": "Directing field operations controllers to conduct targeted store energy and operational cost audits.",
                "featured_agents": ["store_pnl_operating_costs", "gross_margin_profitability", "corporate_budget_variance_fpna", "store_cash_management_tills", "energy_renewable_grid_transition"],
            },
            {
                "time": "Stage 2",
                "stage": "Working Capital, Cash Flow & Inventory LCM Provisions",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Hours",
                "without_agents": "Struggling with complex Excel macros to model lower-of-cost-or-market (LCM) reserve requirements and working capital conversion cycles.",
                "with_agents": "Executing conversational queries to project 90-day cash flow trajectories and model LCM inventory write-down provisions across aging categories.",
                "automated_what": "Cash conversion cycle calculation, aging inventory reserve modeling, and accounts payable cash outflow forecasting.",
                "augmented_what": "Advising the CFO on short-term credit line draws, vendor payment timing, and dividend distribution schedules.",
                "featured_agents": ["working_capital_cashflow", "inventory_valuation_provisions", "sell_through_inventory_health", "markdown_clearance_optimization", "multi_echelon_safety_stock"],
            },
            {
                "time": "Stage 3",
                "stage": "Interest Rates, FX Hedging & Commercial Lease Grounding",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Minutes",
                "without_agents": "Searching financial news terminals manually for central bank interest rate announcements and overseas currency exchange shifts.",
                "with_agents": "Grounding currency exposure, landed import costs, and commercial retail real estate rental indices via Google Search.",
                "automated_what": "Real-time foreign exchange rate synthesis, landed import cost inflation indexing, and commercial lease benchmark lookups.",
                "augmented_what": "Structuring currency hedging contracts for offshore manufacturing and renegotiating mall store anchor lease options.",
                "featured_agents": ["foreign_exchange_landed_costs", "store_real_estate_lease_mgmt", "sales_tax_nexus_compliance", "gift_card_breakage_liability", "b2b_wholesale_portal_analytics"],
            },
            {
                "time": "Stage 4",
                "stage": "Store Remodel CapEx ROI & Payback Modeling",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Piecing together construction invoices, fixture depreciation schedules, and post-remodel sales lift data across multiple department drives.",
                "with_agents": "Generating CapEx Store Remodel ROI models that calculate net present value (NPV), internal rate of return (IRR), and capital payback velocity.",
                "automated_what": "Remodel capital expenditure tracking, pre/post sales lift regression, and automated financial payback modeling.",
                "augmented_what": "Submitting capital expenditure recommendations to the board's Capital Investment Committee for store fleet modernization.",
                "featured_agents": ["capex_store_remodel_roi", "vendor_recovery_audit_compliance", "trade_spend_effectiveness", "customer_acquisition_cost_cac", "product_warranty_claims_repair"],
            },
        ],
    },
    {
        "id": "customer_care_cx",
        "icon": "🎧",
        "title": "Customer Experience & Care Leads",
        "subtitle": "First Contact Resolution, WISMO Inquiries & VoC Sentiment NLP",
        "roles_summary": "VP of Customer Experience, Contact Center Directors, Customer Service Leads, VoC Analytics Managers, and Warranty Operations Leads.",
        "hours_saved": "Cycle Time: Days → Minutes",
        "decision_speed": "Effort: Hours → Minutes",
        "automated_pct": 70,
        "augmented_pct": 30,
        "automated_label": "Automated: Queue Telemetry, WISMO Triage & VoC NLP Clusters",
        "augmented_label": "Augmented: Escalation Policies & Frontline Empowerment",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Queue Inflow & First Contact Resolution (FCR) Triage",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Reviewing telephony call-detail logs and chat transcripts manually to figure out why customer hold times spiked across digital channels.",
                "with_agents": "Receiving automated Contact Center Diagnostics displaying live FCR percentages, average handle times (AHT), and queue abandonment rates.",
                "automated_what": "Multi-queue telephony and digital chat telemetry analysis, FCR calculation, and SLA threshold breach alerting.",
                "augmented_what": "Reallocating frontline specialized support agents to high-volume billing and delivery tracking queues.",
                "featured_agents": ["contact_center_agent_performance", "store_associate_support_hotline", "curbside_pickup_speed_accuracy", "store_fulfillment_execution"],
            },
            {
                "time": "Stage 2",
                "stage": "WISMO Order Inquiries & Carrier Delay Root-Cause Analysis",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Manually checking carrier tracking numbers across disparate courier websites to answer angry customer 'Where Is My Order' inquiries.",
                "with_agents": "Using Conversational Analytics to query carrier transit delays, identify regional delivery hubs causing WISMO spikes, and trigger bulk proactive customer notifications.",
                "automated_what": "Automated carrier tracking status reconciliation, delivery exception clustering, and automated deflection scoring.",
                "augmented_what": "Authorizing automated courtesy goodwill credits and replacement order re-shipments for delayed parcel cohorts.",
                "featured_agents": ["wismo_order_tracking_resolution", "last_mile_delivery_dispatch", "damaged_goods_claims_resolution", "returns_appeals_exception_desk"],
            },
            {
                "time": "Stage 3",
                "stage": "Voice-of-Customer Sentiment NLP & Product Defect Grounding",
                "mode": "Augmented",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Reading through hundreds of free-text customer survey responses and social complaints to discover emerging product defect issues.",
                "with_agents": "Prompting the VoC Sentiment agent to run NLP clustering across survey feedback, chat logs, and public social support channels.",
                "automated_what": "NLP topic modeling, customer sentiment polarity scoring, and product issue cluster identification.",
                "augmented_what": "Escalating emerging product design flaws to quality assurance engineering and vendor sourcing leadership.",
                "featured_agents": ["voice_of_customer_sentiment_nlp", "omnichannel_social_support_desk", "product_detail_page_optimization"],
            },
            {
                "time": "Stage 4",
                "stage": "AI Bot Deflection & Human Handoff Optimization",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Listening to random call recordings to determine why customers repeatedly break out of automated self-service IVR menus.",
                "with_agents": "Reviewing automated AI Bot Deflection Funnels identifying high-friction intent paths, containment failures, and optimal human handoff triggers.",
                "automated_what": "Bot intent containment tracking, customer sentiment drop-off detection, and handoff latency measurement.",
                "augmented_what": "Refining conversational AI knowledge prompts, policy guardrails, and customer service escalation paths.",
                "featured_agents": ["ai_chatbot_deflection_handoff", "vip_clientele_concierge_support", "product_warranty_claims_repair"],
            },
        ],
    },
    {
        "id": "hr_esg_compliance",
        "icon": "🛡️",
        "title": "HR, Safety & ESG Officers",
        "subtitle": "Workforce Retention, Scope 1-3 Emissions & Ethical Sourcing",
        "roles_summary": "Chief Human Resources Officer, Chief Sustainability Officer, EHS Directors, Workforce Schedulers, and Ethical Sourcing Auditors.",
        "hours_saved": "Cycle Time: Weeks → Hours",
        "decision_speed": "Effort: Days → Minutes",
        "automated_pct": 65,
        "augmented_pct": 35,
        "automated_label": "Automated: Turnover Analytics, Scope 1-3 GHG & OSHA Audits",
        "augmented_label": "Augmented: Workforce Retention & ESG Capital Governance",
        "day_in_the_life": [
            {
                "time": "Stage 1",
                "stage": "Associate Turnover & Scheduling Fairness Screening",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Extracting store punch data across hundreds of locations to calculate monthly associate attrition rates and flag predictive scheduling violations.",
                "with_agents": "Receiving an automated Workforce Health Alert identifying store districts with elevated associate turnover and predictive scheduling clopening violations.",
                "automated_what": "Payroll turnover rate calculation, scheduling regularity variance tracking, and labor compliance rule audits.",
                "augmented_what": "Counseling district store managers on frontline retention interventions and shift schedule stabilization.",
                "featured_agents": ["store_associate_turnover_retention", "workforce_scheduling_fairness", "seasonal_hiring_peak_readiness", "associate_engagement_pulse_enps", "store_manager_bench_succession", "email_sms_crm_orchestration"],
            },
            {
                "time": "Stage 2",
                "stage": "Scope 1-3 Carbon Footprint & Energy Audit Modeling",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Hours",
                "without_agents": "Manually collecting utility invoices from hundreds of retail stores and distribution centers to calculate GHG Protocol carbon emissions.",
                "with_agents": "Executing Conversational Analytics queries against facility energy tables to model Scope 1, 2, and 3 carbon emissions against corporate net-zero targets.",
                "automated_what": "Kilowatt-hour and therm energy conversion into metric tons CO2e, baseline tracking, and emission factor attribution.",
                "augmented_what": "Prioritizing facility HVAC efficiency upgrades, LED retrofits, and renewable power purchase agreements.",
                "featured_agents": ["carbon_footprint_scope_emissions", "energy_renewable_grid_transition", "energy_facilities_maintenance", "water_conservation_facility_audit", "food_waste_spoilage_reduction", "packaging_dunnage_optimization"],
            },
            {
                "time": "Stage 3",
                "stage": "Regulatory Compliance & Ethical Labor Standards Grounding",
                "mode": "Augmented",
                "time_before": "Days",
                "time_after": "Minutes",
                "without_agents": "Searching federal regulatory portals and state legislative websites manually to track changing minimum wage laws and EPR recycling mandates.",
                "with_agents": "Grounding compliance research with real-time OSHA directives, state predictive scheduling statutes, and global supply chain labor audit news via Google Search.",
                "automated_what": "Real-time web retrieval of labor regulatory changes, restricted chemical standards, and EPR recycling regulations.",
                "augmented_what": "Updating corporate supplier codes of conduct and directing on-site ethical sourcing factory audits.",
                "featured_agents": ["ethical_sourcing_labor_audits", "extended_producer_responsibility_epr", "sustainable_packaging_circularity", "chemical_restricted_substances_rsl", "dei_supplier_diversity_spend", "labor_union_compliance_cba", "frontline_wage_market_benchmarks"],
            },
            {
                "time": "Stage 4",
                "stage": "OSHA Incident & Product Recall Readiness Audit",
                "mode": "Automated",
                "time_before": "Hours",
                "time_after": "Minutes",
                "without_agents": "Reviewing paper incident logs across retail store warehouses to assemble quarterly workers' compensation risk summaries.",
                "with_agents": "Reviewing automated Workplace Safety Scorecards ranking high-incident store locations and checking product safety recall trace readiness.",
                "automated_what": "OSHA recordable rate calculation, workers' comp reserve tracking, and lot-level product recall trace simulation.",
                "augmented_what": "Authorizing mandatory store safety retraining modules and issuing immediate product stop-sale directives.",
                "featured_agents": ["workplace_safety_workers_comp", "store_safety_incident_management", "product_safety_recall_readiness", "training_onboarding_compliance", "returns_appeals_exception_desk", "customer_churn_winback_analytics"],
            },
        ],
    },
]



AGENT_ACTION_TAGS: dict[str, str] = {
    "ai_chatbot_deflection_handoff": "Contain AI Bot Escalations",
    "associate_engagement_pulse_enps": "Benchmark Associate Pulse eNPS",
    "assortment_planning": "Audit Assortment Breadth",
    "b2b_wholesale_portal_analytics": "Track Wholesale Portal Volume",
    "brand_health_social_sentiment": "Analyze Social Brand Sentiment",
    "campaign_performance_roi": "Attribute Omnichannel Campaign ROAS",
    "capex_store_remodel_roi": "Model Remodel CapEx Payback",
    "carbon_footprint_scope_emissions": "Audit Scope 1-3 Carbon Footprint",
    "cart_checkout_analytics": "Diagnose Checkout Funnel Friction",
    "category_growth_strategy": "Screen Category Growth White-Space",
    "chemical_restricted_substances_rsl": "Screen RSL Chemical Compliance",
    "cold_chain_temperature_compliance": "Monitor Cold-Chain Temperatures",
    "contact_center_agent_performance": "Triage Contact Center FCR Rates",
    "corporate_budget_variance_fpna": "Reconcile Corporate Budget Variances",
    "cross_dock_flow_through": "Accelerate Cross-Dock Flow Velocity",
    "curbside_pickup_speed_accuracy": "Audit Curbside Fulfillment Speed",
    "customer_acquisition_cost_cac": "Optimize CAC Payback Velocity",
    "customer_churn_winback_analytics": "Score Churn Risk & Win-Back",
    "customer_lifecycle_loyalty": "Segment Customer Lifecycle CLV",
    "customs_import_tariff_compliance": "Verify Import Tariff Classifications",
    "damaged_goods_claims_resolution": "Recover Damaged Carrier Freight",
    "dc_automation_robotics_kpis": "Track DC Robotics Productivity",
    "dei_supplier_diversity_spend": "Track Diverse Supplier Spend",
    "digital_promotions_coupon_abuse": "Detect Promo Abuse & Fraud",
    "digital_site_performance_vitals": "Audit Core Web Vitals Latency",
    "email_sms_crm_orchestration": "Orchestrate CRM Email Journeys",
    "energy_facilities_maintenance": "Audit Store Facilities Utility Load",
    "energy_renewable_grid_transition": "Model Renewable Grid Transition",
    "ethical_sourcing_labor_audits": "Audit Sourcing Labor Standards",
    "extended_producer_responsibility_epr": "Track EPR Circularity Mandates",
    "food_waste_spoilage_reduction": "Minimize Fresh Food Spoilage",
    "foreign_exchange_landed_costs": "Hedge FX Landed Cost Exposure",
    "frontline_wage_market_benchmarks": "Benchmark Frontline Market Wages",
    "geotargeted_local_marketing": "Optimize Local Store Geotargeting",
    "gift_card_breakage_liability": "Forecast Gift Card Breakage",
    "gross_margin_profitability": "Audit Gross Margin Variances",
    "inbound_freight_optimization": "Optimize Inbound Freight Lanes",
    "influencer_creator_campaign_roi": "Measure Influencer Campaign ROI",
    "inventory_planning": "Balance Reorder Quantities",
    "inventory_valuation_provisions": "Calculate LCM Inventory Reserves",
    "item_lifecycle_rationalization": "Rationalize Long-Tail SKUs",
    "labor_productivity": "Audit Store Labor Scheduling",
    "labor_union_compliance_cba": "Audit Labor Union CBA Rules",
    "last_mile_delivery_dispatch": "Dispatch Last-Mile Routes",
    "localized_curation_clustering": "Cluster Store Assortment Curations",
    "logistics_operations": "Monitor Freight Transit Bottlenecks",
    "loss_prevention_shrinkage": "Detect Store Shrink & Cash Drift",
    "markdown_clearance_optimization": "Trigger Markdown Clearance Pricing",
    "marketplace_seller_performance": "Audit 3P Marketplace SLAs",
    "mobile_app_conversion_retention": "Optimize Mobile App Conversion",
    "multi_echelon_safety_stock": "Simulate Multi-Echelon Safety Stock",
    "omnichannel_customer_cdp_insights": "Unify Omnichannel Customer CDP",
    "omnichannel_returns_in_store": "Streamline In-Store BORIS Returns",
    "omnichannel_social_support_desk": "Triage Social Support Escalations",
    "packaging_dunnage_optimization": "Optimize Carton Dunnage Cube",
    "payment_gateway_fraud_risk": "Screen Payment Gateway Fraud",
    "pos_checkout_queue_analytics": "Reduce POS Register Queues",
    "price_matching_competitor_intel": "Monitor Competitor Price Match",
    "pricing_promotions": "Model Price Elasticity Lift",
    "private_brand_development": "Formulate Private Brand Margins",
    "product_detail_page_optimization": "Optimize PDP Media Engagement",
    "product_safety_recall_readiness": "Audit Product Recall Traceability",
    "product_warranty_claims_repair": "Process Warranty Repair Claims",
    "retail_media_network_monetization": "Maximize Retail Media Ad Yield",
    "returns_appeals_exception_desk": "Resolve Return Policy Appeals",
    "returns_reverse_logistics": "Optimize Reverse Returns Routing",
    "sales_tax_nexus_compliance": "Reconcile Multi-State Sales Tax",
    "search_merchandising_personalization": "Tune Site Search Merchandising",
    "seasonal_hiring_peak_readiness": "Forecast Peak Seasonal Staffing",
    "seasonal_transition_planning": "Plan Seasonal Assortment Reset",
    "sell_through_inventory_health": "Track SKU Sell-Through Velocity",
    "size_pack_optimization": "Optimize Case Pack Size Runs",
    "space_planning_micro_merch": "Rebalance Planogram Shelf Space",
    "store_associate_support_hotline": "Resolve POS Store Helpdesk Tickets",
    "store_associate_turnover_retention": "Analyze Frontline Turnover Drift",
    "store_cash_management_tills": "Reconcile Register Till Cash",
    "store_fulfillment_execution": "Accelerate BOPIS Store Picking",
    "store_manager_bench_succession": "Map Store Leadership Succession",
    "store_manager_operational_audit": "Audit Store Operational Standards",
    "store_pnl_operating_costs": "Audit Store Controllable P&L",
    "store_real_estate_lease_mgmt": "Audit Retail Real Estate Leases",
    "store_safety_incident_management": "Track Store Safety OSHA Incidents",
    "subscription_recurring_orders": "Retain Subscription Replenishments",
    "supplier_risk_resilience": "Assess Supplier Solvency Risk",
    "sustainable_packaging_circularity": "Assess Sustainable Packaging",
    "trade_spend_effectiveness": "Audit Trade Spend Allowances",
    "training_onboarding_compliance": "Track Retail Training Compliance",
    "vendor_negotiation_rebates": "Claw Back Vendor Rebate Allowances",
    "vendor_performance": "Score Vendor OTIF Compliance",
    "vendor_recovery_audit_compliance": "Audit Vendor Invoice Overpayments",
    "vip_clientele_concierge_support": "Elevate VIP Concierge Clienteling",
    "visual_merchandising_compliance": "Verify Planogram Visual Compliance",
    "voice_of_customer_sentiment_nlp": "Cluster Voice-of-Customer Feedback",
    "warehouse_dc_operations": "Audit Warehouse DC Flow Bottlenecks",
    "water_conservation_facility_audit": "Audit Facility Water Footprints",
    "web_accessibility_seo_health": "Audit SEO & Web Accessibility",
    "wismo_order_tracking_resolution": "Resolve WISMO Order Tracking",
    "workforce_scheduling_fairness": "Enforce Fair Predictive Scheduling",
    "working_capital_cashflow": "Project 90-Day Working Capital",
    "workplace_safety_workers_comp": "Mitigate Workers Comp Claims",
}

TASK_DISTRIBUTIONS: dict[str, dict[str, int]] = {
    "exec_leadership": {'unchanged_pct': 25, 'augmented_pct': 30, 'automated_pct': 25, 'new_ai_pct': 10, 'retired_pct': 10},
    "merchandising_buyers": {'unchanged_pct': 20, 'augmented_pct': 30, 'automated_pct': 30, 'new_ai_pct': 10, 'retired_pct': 10},
    "inventory_planners": {'unchanged_pct': 15, 'augmented_pct': 25, 'automated_pct': 40, 'new_ai_pct': 10, 'retired_pct': 10},
    "supply_chain_logistics": {'unchanged_pct': 20, 'augmented_pct': 25, 'automated_pct': 35, 'new_ai_pct': 10, 'retired_pct': 10},
    "store_field_ops": {'unchanged_pct': 30, 'augmented_pct': 25, 'automated_pct': 25, 'new_ai_pct': 10, 'retired_pct': 10},
    "ecommerce_digital": {'unchanged_pct': 15, 'augmented_pct': 30, 'automated_pct': 35, 'new_ai_pct': 10, 'retired_pct': 10},
    "marketing_loyalty": {'unchanged_pct': 20, 'augmented_pct': 30, 'automated_pct': 30, 'new_ai_pct': 10, 'retired_pct': 10},
    "finance_fpa": {'unchanged_pct': 15, 'augmented_pct': 30, 'automated_pct': 35, 'new_ai_pct': 10, 'retired_pct': 10},
    "customer_care_cx": {'unchanged_pct': 20, 'augmented_pct': 30, 'automated_pct': 30, 'new_ai_pct': 10, 'retired_pct': 10},
    "hr_esg_compliance": {'unchanged_pct': 25, 'augmented_pct': 25, 'automated_pct': 30, 'new_ai_pct': 10, 'retired_pct': 10},
}

STAGE_TASK_SPECS: dict[tuple[str, int], dict[str, str]] = {
    ('customer_care_cx', 0): {
        "retired": "Extract telephony call logs into Excel to find queue spikes",
        "auto1": "Track multi-queue contact center first contact resolution (FCR)",
        "auto2": "Monitor average handle time and queue abandonment rate anomalies",
        "aug": "Reallocate tier-2 specialist support agents to high-volume queues",
        "unchanged": "Deliver one-on-one empathy coaching to frontline care agents",
        "new": "Audit automated contact center queue capacity prediction models",
    },
    ('customer_care_cx', 1): {
        "retired": "Lookup tracking numbers across courier portals to answer WISMO",
        "auto1": "Reconcile carrier delivery tracking status against customer orders",
        "auto2": "Process damaged transit goods claims and carrier reimbursement",
        "aug": "Authorize proactive courtesy goodwill credits for delayed shipments",
        "unchanged": "Resolve high-profile executive escalations with aggrieved VIPs",
        "new": "Audit automated shipping delay notification deflection rates",
    },
    ('customer_care_cx', 2): {
        "retired": "Read customer CSAT survey comments line-by-line in spreadsheets",
        "auto1": "Cluster voice-of-customer sentiment and emerging product issues",
        "auto2": "Triage public social care mentions and brand support tickets",
        "aug": "Escalate critical product defect patterns to quality assurance",
        "unchanged": "Lead cross-functional customer advisory council feedback panels",
        "new": "Audit voice-of-customer sentiment NLP clustering accuracy",
    },
    ('customer_care_cx', 3): {
        "retired": "Listen to random IVR recordings to see why customers drop out",
        "auto1": "Track AI bot containment, intent drop-offs and deflection rates",
        "auto2": "Orchestrate high-CLV VIP clienteling and concierge service",
        "aug": "Tune conversational AI bot guardrails and human handoff triggers",
        "unchanged": "Host private client VIP styling and concierge loyalty sessions",
        "new": "Audit automated chatbot containment evaluation and guardrails",
    },
    ('ecommerce_digital', 0): {
        "retired": "Pull hourly web sessions into spreadsheets to spot cart drops",
        "auto1": "Track step-by-step cart and checkout conversion funnel drops",
        "auto2": "Screen payment gateway decline codes and fraud risk spikes",
        "aug": "Trigger checkout UX interventions and payment failover routing",
        "unchanged": "Lead digital design thinking workshops on customer UX flows",
        "new": "Audit payment gateway fraud scoring thresholds and friction",
    },
    ('ecommerce_digital', 1): {
        "retired": "Read massive site search logs line-by-line to identify nulls",
        "auto1": "Cluster zero-result site search queries and diagnose intent",
        "auto2": "Optimize product detail page media engagement and conversion",
        "aug": "Approve automated search synonyms and merchandised redirects",
        "unchanged": "Conduct qualitative user research and moderated usability tests",
        "new": "Audit conversational site search auto-redirect relevance rules",
    },
    ('ecommerce_digital', 2): {
        "retired": "Check search engine rankings manually across incognito tabs",
        "auto1": "Audit Core Web Vitals and organic SEO category rankings",
        "auto2": "Monitor digital coupon redemption spikes and promo code abuse",
        "aug": "Prioritize high-impact web performance and schema optimizations",
        "unchanged": "Review creative digital asset design with brand art director",
        "new": "Audit automated digital coupon abuse blocking rule accuracy",
    },
    ('ecommerce_digital', 3): {
        "retired": "Calculate marketplace merchant defect rates in manual sheets",
        "auto1": "Track 3P marketplace seller SLAs, late shipments and buy-box",
        "auto2": "Monitor subscription order churn and recurring renewal trends",
        "aug": "Enforce marketplace seller policy warnings or suspend accounts",
        "unchanged": "Recruit strategic third-party marketplace brand partners",
        "new": "Audit marketplace automated buy-box suppression mechanisms",
    },
    ('exec_leadership', 0): {
        "retired": "Consolidate manual PDF revenue summaries from 9 division heads",
        "auto1": "Aggregate gross margin, store P&L and cash metrics in BigQuery",
        "auto2": "Flag district payroll anomalies and inventory reserve spikes",
        "aug": "Evaluate enterprise capital allocation and strategic priorities",
        "unchanged": "Chair weekly executive operating committee review meeting",
        "new": "Audit automated executive P&L anomaly detection thresholds",
    },
    ('exec_leadership', 1): {
        "retired": "Sift through conflicting departmental quarterly variance logs",
        "auto1": "Decompose gross margin erosion into freight vs markdown drivers",
        "auto2": "Simulate forward working capital and budget variance trends",
        "aug": "Negotiate cross-functional mitigation across retail divisions",
        "unchanged": "Direct executive accountability on commercial commitments",
        "new": "Review conversational reasoning traces across FP&A and supply chain",
    },
    ('exec_leadership', 2): {
        "retired": "Wait days for third-party macro consulting trend reports",
        "auto1": "Synthesize macroeconomic competitor earnings and retail press",
        "auto2": "Map tariff classification changes and FX exposure to categories",
        "aug": "Formulate executive pricing defense and supply chain strategies",
        "unchanged": "Engage retail industry board peers and institutional investors",
        "new": "Validate external Google Search grounding source reliability",
    },
    ('exec_leadership', 3): {
        "retired": "Copy-paste charts into static quarterly executive slide decks",
        "auto1": "Generate interactive Canvas briefings with Matplotlib curves",
        "auto2": "Publish structured board performance memos with key metrics",
        "aug": "Align executive talking points ahead of quarterly earnings calls",
        "unchanged": "Present strategic vision and guidance to board committee",
        "new": "Audit executive Canvas briefing accuracy against master ledger",
    },
    ('finance_fpa', 0): {
        "retired": "Run batch ERP trial balances to build store-by-store variance decks",
        "auto1": "Track store controllable operating costs and labor variances",
        "auto2": "Decompose gross margin rate variances by category and region",
        "aug": "Direct field controllers to audit abnormal store expense spikes",
        "unchanged": "Review confidential financial audit findings with internal audit",
        "new": "Audit automated general ledger anomaly detection alert limits",
    },
    ('finance_fpa', 1): {
        "retired": "Maintain complex Excel macros for lower-of-cost-or-market reserves",
        "auto1": "Project 90-day working capital conversion and cash flow curves",
        "auto2": "Calculate LCM inventory valuation reserves across aging tiers",
        "aug": "Advise CFO on credit facility draws and vendor payment timing",
        "unchanged": "Maintain bank credit facility relationships and lender updates",
        "new": "Audit automated LCM reserve provision calculation algorithms",
    },
    ('finance_fpa', 2): {
        "retired": "Check financial news terminals manually for foreign currency shifts",
        "auto1": "Synthesize central bank interest rates and FX currency trends",
        "auto2": "Audit retail real estate lease obligations and store rent steps",
        "aug": "Structure currency hedges and renegotiate store anchor lease terms",
        "unchanged": "Lead commercial lease negotiations with shopping mall landlords",
        "new": "Verify automated lease accounting and FX rate conversion sources",
    },
    ('finance_fpa', 3): {
        "retired": "Collate remodeling invoices and post-remodel sales across drives",
        "auto1": "Calculate store remodel CapEx net present value and payback ROI",
        "auto2": "Audit vendor invoice overpayments and recover pricing discrepancies",
        "aug": "Submit capital expenditure proposals to board finance committee",
        "unchanged": "Evaluate enterprise strategic acquisitions and capital allocation",
        "new": "Audit automated vendor overpayment recovery dispute workflows",
    },
    ('hr_esg_compliance', 0): {
        "retired": "Collate store timecards manually to check predictive scheduling",
        "auto1": "Calculate store associate turnover and predict retention risks",
        "auto2": "Audit store predictive scheduling fairness and clopening rules",
        "aug": "Advise district store leaders on frontline retention action plans",
        "unchanged": "Conduct confidential stay interviews with high-potential staff",
        "new": "Audit predictive scheduling compliance rule validation engine",
    },
    ('hr_esg_compliance', 1): {
        "retired": "Gather paper utility power bills from hundreds of store locations",
        "auto1": "Aggregate kilowatt-hour data and model Scope 1-3 carbon emissions",
        "auto2": "Audit fresh grocery food waste diversion and store markdown velocity",
        "aug": "Prioritize store HVAC retrofits and corporate net-zero projects",
        "unchanged": "Engage community food bank partners on surplus food donation",
        "new": "Audit greenhouse gas emission factor calculations",
    },
    ('hr_esg_compliance', 2): {
        "retired": "Search government websites manually for labor and chemical updates",
        "auto1": "Ground compliance research with real-time OSHA and EPR statutes",
        "auto2": "Audit global supplier factory ethical labor standards and audits",
        "aug": "Update corporate supplier codes of conduct and trigger audits",
        "unchanged": "Lead annual supplier ethics conference and human rights summit",
        "new": "Verify automated regulatory statute extraction and freshness",
    },
    ('hr_esg_compliance', 3): {
        "retired": "Transcribe paper OSHA accident incident forms into logbooks",
        "auto1": "Track store warehouse OSHA recordables and workers comp reserves",
        "auto2": "Simulate lot-level product safety recall traceability readiness",
        "aug": "Mandate store safety retraining and issue stop-sale safety notices",
        "unchanged": "Comfort injured employees and review workplace ergonomic safety",
        "new": "Audit automated mock product recall traceability response time",
    },
    ('inventory_planners', 0): {
        "retired": "Export ERP shortage reports and calculate safety stocks in Excel",
        "auto1": "Track SKU sell-through velocity and lead-time drift in real time",
        "auto2": "Score supplier OTIF delivery trends and stockout vulnerability",
        "aug": "Prioritize expedited freight routes for high-velocity SKUs",
        "unchanged": "Negotiate emergency dock space with regional DC managers",
        "new": "Calibrate multi-echelon stockout risk scoring sensitivity",
    },
    ('inventory_planners', 1): {
        "retired": "Update static safety stock formulas annually in legacy MRP",
        "auto1": "Simulate multi-echelon safety stock across DCs and store hubs",
        "auto2": "Model seasonal inventory transition curves and pack-size runs",
        "aug": "Balance holding cost budgets against 98.5% on-shelf targets",
        "unchanged": "Align replenishment targets with merchandising leadership",
        "new": "Audit automated inventory reorder parameter recommendations",
    },
    ('inventory_planners', 2): {
        "retired": "Rely on carrier email alerts hours after supply disruptions",
        "auto1": "Ground logistics delays against live severe weather and ports",
        "auto2": "Track supplier solvency and geopolitical trade corridor risks",
        "aug": "Reroute purchase order containers to secondary cross-dock hubs",
        "unchanged": "Conduct emergency alignment with logistics freight dispatch",
        "new": "Validate external maritime disruption alert sources and impact",
    },
    ('inventory_planners', 3): {
        "retired": "Key purchase orders line-by-line into ERP green screens",
        "auto1": "Calculate economic order quantities (EOQ) and minimum constraints",
        "auto2": "Generate purchase order payloads for EDI supplier submission",
        "aug": "Conduct human-in-the-loop review on million-dollar commitments",
        "unchanged": "Review supplier SLA compliance with procurement leadership",
        "new": "Audit automated purchase order release thresholds and limits",
    },
    ('marketing_loyalty', 0): {
        "retired": "Log in to 6 ad platforms to copy spend into master spreadsheets",
        "auto1": "Aggregate multi-channel ad spend and attribute blended ROAS",
        "auto2": "Analyze CAC payback velocity across paid search, social and CTV",
        "aug": "Reallocate advertising budgets from lagging to winning channels",
        "unchanged": "Direct agency creative partners on emotional brand campaigns",
        "new": "Audit automated multi-touch ad attribution weight allocations",
    },
    ('marketing_loyalty', 1): {
        "retired": "Wait weeks for data science teams to score customer churn lists",
        "auto1": "Segment omnichannel customer CDP cohorts by RFM and lifetime value",
        "auto2": "Score customer churn risk and model win-back coupon lift",
        "aug": "Design personalized loyalty incentives for slipping VIP cohorts",
        "unchanged": "Lead customer focus groups on retail loyalty program perks",
        "new": "Audit customer churn predictive model features and drift metrics",
    },
    ('marketing_loyalty', 2): {
        "retired": "Rely on sporadic focus groups to gauge consumer brand perception",
        "auto1": "Analyze real-time brand sentiment and viral creator engagement",
        "auto2": "Evaluate influencer marketing campaign conversion lift and ROI",
        "aug": "Pivot marketing messaging to capitalize on emerging viral trends",
        "unchanged": "Cultivate relationships with tier-one brand ambassador creators",
        "new": "Audit social brand sentiment NLP topic classification accuracy",
    },
    ('marketing_loyalty', 3): {
        "retired": "Calculate on-site sponsored ad banner fill rates in Excel",
        "auto1": "Maximize retail media network sponsored ad auction yield",
        "auto2": "Orchestrate automated CRM email and SMS personalized journeys",
        "aug": "Package guaranteed RMN impression commitments for CPG partners",
        "unchanged": "Negotiate annual retail media contracts with major CPG brands",
        "new": "Audit retail media sponsored ad auction pricing fairness rules",
    },
    ('merchandising_buyers', 0): {
        "retired": "Download and VLOOKUP weekly POS spreadsheets across regions",
        "auto1": "Aggregate SKU velocity, sell-through % and inventory health",
        "auto2": "Flag clearance candidates and private label margin gaps",
        "aug": "Decide markdown timing vs promotional vendor funding allowances",
        "unchanged": "Inspect physical product samples and fabric hand-feel quality",
        "new": "Verify automated markdown clearance trigger elasticity models",
    },
    ('merchandising_buyers', 1): {
        "retired": "Build multi-tab regression sheets to guess promo price lift",
        "auto1": "Model promotional price elasticity and baseline sales lift",
        "auto2": "Forecast category cannibalization and trade spend ROI",
        "aug": "Finalize seasonal promotional calendar depth and co-op terms",
        "unchanged": "Lead face-to-face line reviews with key brand suppliers",
        "new": "Audit promotional lift forecast confidence intervals in BigQuery",
    },
    ('merchandising_buyers', 2): {
        "retired": "Manually browse competitor e-commerce sites to verify pricing",
        "auto1": "Monitor competitor price matching and promo circulars via Search",
        "auto2": "Benchmark category commodity input costs and tariff shifts",
        "aug": "Negotiate vendor cost allowances and claw back rebate gaps",
        "unchanged": "Build trusted long-term merchandising vendor partnerships",
        "new": "Verify competitor price-scrape match accuracy and freshness",
    },
    ('merchandising_buyers', 3): {
        "retired": "Draw planogram resets manually in legacy desktop CAD tools",
        "auto1": "Calculate store cluster space productivity and sales per sq.ft",
        "auto2": "Optimize assortment breadth vs depth by regional cluster",
        "aug": "Approve final seasonal floor reset layout and shelf allocations",
        "unchanged": "Walk flagship store floor with visual merchandising team",
        "new": "Audit micro-merchandising planogram clustering recommendations",
    },
    ('store_field_ops', 0): {
        "retired": "Match printed foot-traffic sheets with punch-clock timesheets",
        "auto1": "Track store traffic patterns and calculate sales per labor hour",
        "auto2": "Audit store labor schedule adherence against customer surges",
        "aug": "Reallocate hourly store staffing between registers and curbside",
        "unchanged": "Lead morning store team huddle and inspire frontline morale",
        "new": "Audit fair labor scheduling algorithms for compliance rules",
    },
    ('store_field_ops', 1): {
        "retired": "Walk retail aisles searching for unfulfilled BOPIS customer bags",
        "auto1": "Track curbside pickup staging speed and click-and-collect SLAs",
        "auto2": "Analyze omnichannel store order fulfillment picking accuracy",
        "aug": "Rebalance store floor associates during peak curbside surges",
        "unchanged": "Greet retail customers and resolve high-touch in-store issues",
        "new": "Audit automated order fulfillment queue routing efficiency",
    },
    ('store_field_ops', 2): {
        "retired": "Speculate on foot-traffic drops without local neighborhood data",
        "auto1": "Ground store foot traffic with local stadium events and weather",
        "auto2": "Audit visual merchandising planogram compliance across displays",
        "aug": "Stage grab-and-go product displays ahead of local event crowds",
        "unchanged": "Conduct walk-through audits with district store managers",
        "new": "Validate store operational audit computer vision detections",
    },
    ('store_field_ops', 3): {
        "retired": "Count register drawer envelopes manually to find cashier errors",
        "auto1": "Reconcile daily POS till cash and flag register drawer drift",
        "auto2": "Detect sweethearting, return fraud and store shrinkage anomalies",
        "aug": "Initiate loss prevention reviews and cash-handling retraining",
        "unchanged": "Deliver confidential coaching to store staff on compliance",
        "new": "Audit store loss prevention anomaly detection false-alarm rates",
    },
    ('supply_chain_logistics', 0): {
        "retired": "Radio gatehouse security to locate overdue freight trailers",
        "auto1": "Track yard gatehouse check-ins and dock door dwell telemetry",
        "auto2": "Monitor cold-chain temperature thresholds and detention risk",
        "aug": "Prioritize dock door sequencing for perishable cold-chain loads",
        "unchanged": "Inspect DC physical staging areas and conveyor safety checks",
        "new": "Audit IoT cold-chain sensor drift and automated alert triggers",
    },
    ('supply_chain_logistics', 1): {
        "retired": "Manually cross-check signed bills of lading against invoices",
        "auto1": "Score vendor OTIF fulfillment against purchase order lines",
        "auto2": "Audit freight invoice lane surcharges and accessorial fees",
        "aug": "Enforce vendor SLA chargeback penalties and resolve disputes",
        "unchanged": "Hold strategic quarterly business reviews with carrier CEOs",
        "new": "Verify automated OTIF penalty calculations before assessment",
    },
    ('supply_chain_logistics', 2): {
        "retired": "Query static freight rate subscription sheets for spot quotes",
        "auto1": "Ground spot market freight lane rates via Google Search",
        "auto2": "Audit customs tariff codes and import compliance documents",
        "aug": "Select dedicated fleet commitments versus spot carrier brokers",
        "unchanged": "Lead driver safety briefings and regional fleet check-ins",
        "new": "Audit automated customs tariff classification determinations",
    },
    ('supply_chain_logistics', 3): {
        "retired": "Print route manifests on clipboards for parcel delivery drivers",
        "auto1": "Optimize last-mile multi-stop parcel delivery dispatch routes",
        "auto2": "Monitor DC robotics pick rates and carton dunnage utilization",
        "aug": "Resolve dispatch exceptions and high-priority VIP parcel reroutes",
        "unchanged": "Coach delivery drivers and audit fleet vehicle road safety",
        "new": "Audit automated dispatch routing algorithms for driver fairness",
    },
}


def _enrich_persona_archetypes(archetypes: list[dict[str, Any]]) -> None:
    """Populates task_distribution, task_bundle, and agent_flow on each archetype and stage."""
    for arch in archetypes:
        arch_id = arch["id"]
        arch["task_distribution"] = dict(TASK_DISTRIBUTIONS[arch_id])

        for stage_idx, stage in enumerate(arch.get("day_in_the_life", [])):
            featured = stage.get("featured_agents", [])
            n = len(featured)

            stage["agent_flow"] = [
                {
                    "step": idx + 1,
                    "step_code": f"{idx + 1:02d}",
                    "slug": slug,
                    "action_tag": AGENT_ACTION_TAGS[slug],
                }
                for idx, slug in enumerate(featured)
            ]

            spec = STAGE_TASK_SPECS[(arch_id, stage_idx)]

            if n == 3:
                s2 = [1, 2]
                s3 = [2]
                s4 = [3]
                l2 = "STEP 01 · 02"
                l3 = "STEP 02"
                l4 = "STEP 03"
            elif n == 4:
                s2 = [1, 2]
                s3 = [2, 3]
                s4 = [3, 4]
                l2 = "STEP 01 · 02"
                l3 = "STEP 02 · 03"
                l4 = "STEP 03 · 04"
            else:  # n >= 5
                s2 = [1, 2]
                s3 = [3, 4]
                s4 = [4, 5]
                l2 = "STEP 01 · 02"
                l3 = "STEP 03 · 04"
                l4 = "STEP 04 · 05"

            s6 = list(range(1, n + 1))
            l6 = f"STEP 01–{n:02d}"

            stage["task_bundle"] = [
                {
                    "id": f"{arch_id}_s{stage_idx + 1}_t1_retired",
                    "label": spec["retired"],
                    "state": "retired",
                    "steps_label": "",
                    "step_indices": [],
                },
                {
                    "id": f"{arch_id}_s{stage_idx + 1}_t2_auto",
                    "label": spec["auto1"],
                    "state": "automated",
                    "steps_label": l2,
                    "step_indices": s2,
                },
                {
                    "id": f"{arch_id}_s{stage_idx + 1}_t3_auto",
                    "label": spec["auto2"],
                    "state": "automated",
                    "steps_label": l3,
                    "step_indices": s3,
                },
                {
                    "id": f"{arch_id}_s{stage_idx + 1}_t4_aug",
                    "label": spec["aug"],
                    "state": "augmented",
                    "steps_label": l4,
                    "step_indices": s4,
                },
                {
                    "id": f"{arch_id}_s{stage_idx + 1}_t5_unchanged",
                    "label": spec["unchanged"],
                    "state": "unchanged",
                    "steps_label": "",
                    "step_indices": [],
                },
                {
                    "id": f"{arch_id}_s{stage_idx + 1}_t6_new",
                    "label": spec["new"],
                    "state": "new",
                    "steps_label": l6,
                    "step_indices": s6,
                },
            ]


_enrich_persona_archetypes(PERSONA_ARCHETYPES)

def classify_persona_archetype(role_title: str, domain: str) -> str:
    """
    Deterministically maps a role title and parent domain to one of the 10
    PERSONA_ORDER archetype identifiers.
    """
    r = role_title.lower().strip()

    # 1. Executive Leadership
    if any(k in r for k in [
        "chief", "c-level", "csuite", "c-suite", "ceo", "cfo", "cmo", "chro", "cso",
        "cco", "general counsel", "board of directors", "executive committee"
    ]):
        return "exec_leadership"

    if ("vp" in r or "vice president" in r or "head of" in r):
        if any(k in r for k in [
            "retail operations", "corporate", "finance", "commercial", "enterprise",
            "strategic", "business development", "merchandising &", "omnichannel"
        ]):
            return "exec_leadership"

    # 2. Merchandising & Buyers
    if any(k in r for k in [
        "buyer", "category manager", "category merchandiser", "merchandise planner",
        "merchandiser", "assortment planner", "sourcing lead", "sourcing manager",
        "private brand", "pricing strategist", "pricing director", "pricing manager",
        "markdown", "planogram", "space planning", "trade spend", "rebate", "sku rationalization"
    ]):
        return "merchandising_buyers"

    # 3. Demand & Inventory Planners
    if any(k in r for k in [
        "inventory planner", "demand planner", "inventory controller", "replenishment",
        "allocation analyst", "safety stock", "stock controller", "inventory health",
        "inventory analyst", "stock turn"
    ]):
        return "inventory_planners"

    # 4. Supply Chain & DC Leaders
    if any(k in r for k in [
        "supply chain", "logistics", "warehouse", "dc ", "distribution center",
        "freight", "carrier", "customs", "tariff", "fleet", "last-mile", "last mile",
        "inbound", "cross-dock", "dunnage", "packaging engineering", "packaging director",
        "transportation", "cold chain", "fulfillment operations lead", "dock arrival", "reverse logistics"
    ]):
        return "supply_chain_logistics"

    # 5. Store & Field Operations
    if any(k in r for k in [
        "store manager", "store operations", "district manager", "field operations",
        "loss prevention", "shrinkage", "visual merchandising", "pos ", "cashier",
        "till", "checkout queue", "store safety", "curbside", "boris", "shift scheduler",
        "store systems", "field support", "store associate"
    ]):
        return "store_field_ops"

    # 6. Digital & E-Commerce Product
    if any(k in r for k in [
        "e-commerce", "ecommerce", "digital product", "cart", "checkout product",
        "payment gateway", "fraud", "marketplace", "mobile app", "pdp", "product detail",
        "seo", "accessibility", "web vitals", "b2b wholesale", "site merchandiser",
        "conversion rate", "self-service"
    ]):
        return "ecommerce_digital"

    # 7. Marketing, CRM & Retail Media
    if any(k in r for k in [
        "marketing", "campaign", "loyalty", "retail media", "rmn", "churn", "crm",
        "email", "sms", "influencer", "creator", "cac", "cdp", "geotargeted",
        "brand health", "social media", "social support", "pr & communications",
        "brand reputation", "acquisition"
    ]):
        return "marketing_loyalty"

    # 8. Finance, FP&A & Real Estate
    if any(k in r for k in [
        "finance", "financial", "fp&a", "fpa", "gross margin", "store p&l",
        "operating cost", "working capital", "cash flow", "cashflow", "capex",
        "remodel", "budget", "variance", "foreign exchange", "landed cost",
        "gift card", "lcm", "valuation", "sales tax", "nexus", "lease",
        "real estate", "vendor recovery", "audit & compliance", "controller",
        "accounting", "tax ", "treasury"
    ]):
        return "finance_fpa"

    # 9. Customer Experience & Care Leads
    if any(k in r for k in [
        "customer care", "contact center", "fcr", "wismo", "voice of customer",
        "voc", "warranty", "chatbot", "concierge", "vip clientele", "returns desk",
        "social care", "support hotline", "damaged goods", "claims resolution",
        "customer service", "customer experience", "clienteling"
    ]):
        return "customer_care_cx"

    # 10. HR, Safety & ESG Officers
    if any(k in r for k in [
        "human resources", "hr ", "turnover", "retention", "scheduling fairness",
        "training", "onboarding", "workplace safety", "workers' comp", "ehs",
        "succession", "seasonal hiring", "enps", "pulse", "labor union", "cba",
        "wage", "carbon", "emissions", "scope", "food waste", "circularity",
        "ethical sourcing", "labor audit", "product safety recall", "renewable energy",
        "water conservation", "restricted substances", "rsl", "supplier diversity",
        "epr", "sustainability", "talent", "diversity", "environmental"
    ]):
        return "hr_esg_compliance"

    # Domain Fallback
    domain_fallback = {
        "merchandising": "merchandising_buyers",
        "supply_chain": "supply_chain_logistics",
        "store_operations": "store_field_ops",
        "e_commerce": "ecommerce_digital",
        "marketing": "marketing_loyalty",
        "finance": "finance_fpa",
        "customer_care": "customer_care_cx",
        "human_resources": "hr_esg_compliance",
        "sustainability_compliance": "hr_esg_compliance",
    }
    return domain_fallback.get(domain, "exec_leadership")


def extract_personas_from_readme(
    content: str,
    display_name: str,
    domain: str,
    kpis: list[str],
    tables: list[str],
) -> list[dict[str, str]]:
    """
    Parses `### Target Personas` from README markdown content.

    Handles both bulleted `- **Role Title**: Description` (including colons inside
    bold like `- **Role Title:** Description`) and comma-separated role strings
    (e.g., in customer_care, human_resources, and sustainability_compliance),
    synthesizing rich agent-specific role descriptions for comma-separated roles.

    Returns at least 3 persona dicts: {"title": str, "description": str, "archetype": str}.
    """
    personas: list[dict[str, str]] = []

    m = re.search(
        r"###\s+Target Personas\s*\n+(.*?)(?=\n\s*###|\n\s*##|\n\s*---|\Z)",
        content,
        re.DOTALL,
    )

    if m:
        raw_text = m.group(1).strip()
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        bullet_lines = [l for l in lines if l.startswith(("-", "*"))]

        if bullet_lines:
            for b in bullet_lines:
                # Matches "- **Title**: Desc" or "- **Title:** Desc" or "- **Title** - Desc"
                bm = re.search(r"^[\-\*]\s+\*\*([^\*]+?):?\*\*\s*[:\-–—]?\s*(.+)$", b)
                if bm:
                    title = bm.group(1).strip()
                    desc = bm.group(2).strip()
                    desc = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", desc).replace("**", "").replace("*", "").strip()
                    if title and desc:
                        personas.append({
                            "title": title,
                            "description": desc,
                            "archetype": classify_persona_archetype(title, domain),
                        })
                else:
                    # Fallback for plain bullets without bolding
                    clean_b = re.sub(r"^[\-\*]\s+", "", b).strip()
                    if ":" in clean_b:
                        t, d = clean_b.split(":", 1)
                        personas.append({
                            "title": t.strip(),
                            "description": d.strip(),
                            "archetype": classify_persona_archetype(t.strip(), domain),
                        })

        if not personas and raw_text:
            # Comma-separated roles (Domains 7–9 or single-line fallback)
            clean_text = raw_text.replace("\n", " ").strip()
            role_titles = [r.strip() for r in clean_text.split(",") if r.strip()]
            for r_title in role_titles:
                clean_title = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", r_title).replace("**", "").replace("*", "").strip()
                if not clean_title:
                    continue
                desc = _synthesize_role_description(clean_title, display_name, domain, kpis, tables)
                personas.append({
                    "title": clean_title,
                    "description": desc,
                    "archetype": classify_persona_archetype(clean_title, domain),
                })

    # Guaranteed fallback: Ensure at least 3 structured personas exist
    if len(personas) < 3:
        clean_name = display_name.replace("Merchandising: ", "").replace("Supply Chain: ", "").replace("Store Operations: ", "").replace("E-Commerce: ", "").replace("Finance: ", "").replace("Marketing: ", "").replace("Customer Care: ", "").replace("HR: ", "").replace("ESG: ", "")
        default_roles = [
            (f"{clean_name} Director", f"Oversees strategic {clean_name.lower()} operations, targets SLA compliance, and guides cross-functional execution."),
            (f"{clean_name} Operations Lead", f"Monitors daily {clean_name.lower()} exception logs, tracks performance deviations, and executes corrective actions."),
            (f"{clean_name} Business Analyst", f"Analyzes underlying BigQuery data tables, models historical trends, and delivers weekly leadership readouts."),
        ]
        for t, d in default_roles:
            if not any(p["title"] == t for p in personas):
                personas.append({
                    "title": t,
                    "description": d,
                    "archetype": classify_persona_archetype(t, domain),
                })
            if len(personas) >= 3:
                break

    return personas


def _synthesize_role_description(
    role_title: str,
    display_name: str,
    domain: str,
    kpis: list[str],
    tables: list[str],
) -> str:
    """Synthesizes an agent-specific operational description for a role title."""
    clean_display = display_name.split(": ", 1)[-1] if ": " in display_name else display_name
    primary_kpi = kpis[0].split(":")[0].strip() if kpis else "key performance metrics"

    role_lower = role_title.lower()
    if any(k in role_lower for k in ["chief", "vp", "vice president", "head of", "director"]):
        return (
            f"Evaluates enterprise {clean_display.lower()} trends, tracks {primary_kpi} against operational targets, "
            f"and directs strategic resource allocation across business units."
        )
    elif any(k in role_lower for k in ["manager", "lead", "supervisor", "coordinator"]):
        return (
            f"Manages operational {clean_display.lower()} execution, investigates real-time performance variances, "
            f"and coordinates rapid intervention across frontline teams."
        )
    elif any(k in role_lower for k in ["analyst", "specialist", "engineer", "planner"]):
        return (
            f"Conducts deep-dive diagnostics on {clean_display.lower()} data tables, tracks root-cause anomalies, "
            f"and prepares optimization recommendations for leadership."
        )
    else:
        return (
            f"Leverages real-time insights from {clean_display} to audit {primary_kpi.lower()}, "
            f"streamline decision cycles, and eliminate operational bottlenecks."
        )


def build_agent_transformation(
    display_name: str,
    domain: str,
    description: str,
    personas: list[dict[str, str]],
    kpis: list[str],
    tables: list[str],
) -> dict[str, str]:
    """
    Builds structured Before/After and Automated/Augmented transformation strings
    tailored to the agent's problem domain, tables, KPIs, and target personas.
    """
    clean_display = display_name.split(": ", 1)[-1] if ": " in display_name else display_name
    kpi_summary = ", ".join(k.split(":")[0].strip() for k in kpis[:2]) if kpis else "core operational metrics"
    table_count = len(tables) if tables else 2

    # 1. As-Is Process (without_agent >= 40 chars)
    without_agent = (
        f"Manual reliance on siloed BI reports, multi-system CSV exports across disparate data stores, "
        f"and multi-day analyst turnaround times to diagnose {clean_display.lower()} variances and reconcile spreadsheets."
    )

    # 2. To-Be Process (with_agent >= 40 chars)
    with_agent = (
        f"Autonomous natural-language queries directly against {table_count} authoritative BigQuery tables, "
        f"instant anomaly detection on {kpi_summary}, Google Search market grounding, and real-time visual chart rendering."
    )

    # 3. Fully Automated Tasks (automated >= 25 chars)
    automated = (
        f"Multi-table SQL joins across {table_count} BigQuery tables, statistical anomaly detection, and automated Matplotlib chart rendering."
    )

    # 4. Augmented Decisions (augmented >= 25 chars)
    role_names = [p["title"] for p in personas[:2]]
    roles_str = " & ".join(role_names) if role_names else "operations leaders"
    augmented = (
        f"Empowers {roles_str} with verified analytical evidence to execute strategic business decisions and policy adjustments."
    )

    return {
        "without_agent": without_agent,
        "with_agent": with_agent,
        "automated": automated,
        "augmented": augmented,
    }
