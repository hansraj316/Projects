# Data Quality Maturity Model for Medallion Architecture Pipelines

## Context

When migrating data from transactional/operational systems into a reporting data warehouse using a medallion architecture (Bronze → Silver → Gold), organizations face a fundamental tradeoff: **more comprehensive quality validation increases confidence but also increases cost** (compute, engineering effort, pipeline latency). This framework provides a structured way to evaluate where an organization sits on this spectrum and what level of investment is appropriate given their business context.

---

## The Two-Axis Model: Quality Coverage vs. Cost

```
Cost ($)
  ▲
  │                                          ● L5: Comprehensive
  │                                    ●
  │                              ● L4: Advanced
  │                        ●
  │                  ● L3: Proactive
  │            ●
  │      ● L2: Foundational
  │  ●
  │● L1: Reactive
  └──────────────────────────────────────────► Quality Coverage (%)
   0%    20%    40%    60%    80%    100%
```

The cost curve is **non-linear** — going from 80% to 95% coverage often costs as much as going from 0% to 80%.

---

## Five Maturity Levels

### Level 1: Reactive (~15-20% coverage | Lowest cost)

**Philosophy:** "We'll find out when something breaks."

| Dimension | What's Covered |
|-----------|---------------|
| **Schema** | None or manual |
| **Completeness** | None |
| **Freshness** | Manual checks ("is today's data there?") |
| **Reconciliation** | Occasional manual row counts |
| **Business Rules** | None |
| **Monitoring** | None — issues found by end users |

**Where checks live in medallion:**
- Bronze: Nothing automated
- Silver: Nothing automated
- Gold: Ad-hoc queries when reports look wrong

**Cost profile:** Near-zero tooling cost, but **high hidden cost** from bad decisions made on bad data, fire-fighting, and trust erosion.

**Typical org:** Early-stage startup, first data warehouse, no dedicated data team.

---

### Level 2: Foundational (~35-45% coverage | Low cost)

**Philosophy:** "Catch the obvious failures before they reach consumers."

| Dimension | What's Covered |
|-----------|---------------|
| **Schema** | Automated column presence + type checks |
| **Completeness** | Null checks on critical fields |
| **Uniqueness** | Primary key validation |
| **Freshness** | Automated "data arrived" checks with basic alerting |
| **Reconciliation** | Source vs. target row counts |
| **Business Rules** | None |
| **Monitoring** | Basic alerts (Slack/email) on check failures |

**Where checks live in medallion:**
- Bronze: Schema validation on ingestion, row count check
- Silver: PK uniqueness, null checks on key columns
- Gold: Basic row count reconciliation

**Cost profile:**
- Tooling: dbt tests, simple SQL assertions (~$0 for OSS)
- Compute: <5% overhead on pipeline runtime
- Engineering: 1-2 days setup per source system

**Typical org:** Growing company with a small data engineering team, basic BI dashboards.

---

### Level 3: Proactive (~55-65% coverage | Moderate cost)

**Philosophy:** "Validate data against known expectations before it moves downstream."

| Dimension | What's Covered |
|-----------|---------------|
| **Schema** | Full schema evolution detection (added/removed/renamed columns) |
| **Completeness** | Null rates tracked with thresholds, not just binary |
| **Uniqueness** | Composite key validation, near-duplicate detection |
| **Referential Integrity** | Foreign key relationships validated across tables |
| **Range/Domain** | Value range checks, enum validation, format validation |
| **Freshness** | SLA-based freshness with escalation policies |
| **Reconciliation** | Row counts + key aggregate comparisons (sums, averages) |
| **Statistical** | Baseline profiling — distribution snapshots for comparison |
| **Business Rules** | Critical rules only (e.g., "revenue should never be negative") |
| **Monitoring** | Centralized dashboard, trend tracking, alerting with severity |

**Where checks live in medallion:**
- Bronze: Schema drift detection, freshness SLAs, source reconciliation
- Silver: Referential integrity, dedup validation, range checks, null thresholds
- Gold: Aggregate reconciliation, critical business rule validation

**Cost profile:**
- Tooling: Great Expectations / Soda Core / dbt + elementary (~$0-5K/mo)
- Compute: 10-20% overhead on pipeline runtime
- Engineering: 1-2 weeks per source system, ongoing maintenance
- Storage: Validation result history (~minimal)

**Typical org:** Mid-size company with dedicated data team, regulatory awareness, multiple data consumers.

---

### Level 4: Advanced (~75-85% coverage | High cost)

**Philosophy:** "Detect anomalies before humans notice them."

| Dimension | What's Covered |
|-----------|---------------|
| **All of Level 3** | + the following |
| **Anomaly Detection** | ML-based drift detection on distributions, volumes, patterns |
| **Cross-System Reconciliation** | End-to-end source-to-gold validation with drill-down |
| **Business Rules** | Comprehensive business logic validation (cross-table, temporal) |
| **Data Lineage** | Impact analysis — know what downstream breaks if a source changes |
| **Timeliness** | Per-record latency tracking, not just batch-level freshness |
| **Historical Consistency** | Late-arriving data detection, retroactive change monitoring |
| **Semantic Validation** | ML-based checks for semantic correctness (e.g., city matches zip code) |

**Where checks live in medallion:**
- Bronze: Anomaly detection on incoming volumes/patterns, schema contract enforcement
- Silver: Cross-table integrity, historical consistency, semantic validation
- Gold: Full business rule suites, end-to-end reconciliation, lineage-aware impact checks

**Cost profile:**
- Tooling: Monte Carlo / Bigeye / Soda Cloud / Atlan ($5K-30K/mo)
- Compute: 20-40% overhead on pipeline runtime
- Engineering: Dedicated data quality team (1-3 engineers)
- Storage: Historical profiles, anomaly baselines, lineage graphs

**Typical org:** Enterprise with regulatory requirements (SOX, GDPR), data mesh or data product thinking, executive-level data quality KPIs.

---

### Level 5: Comprehensive (~95%+ coverage | Highest cost)

**Philosophy:** "Data is a product with SLAs, and quality is continuously measured and improved."

| Dimension | What's Covered |
|-----------|---------------|
| **All of Level 4** | + the following |
| **Real-time Validation** | Stream-level checks for real-time pipelines |
| **Self-healing** | Automated remediation (quarantine bad records, retry, fallback) |
| **Predictive Quality** | Predict quality degradation before it happens |
| **Regulatory Audit Trail** | Full lineage + validation history for compliance audits |
| **Data Contracts** | Producer-consumer contracts with automated enforcement |
| **Chaos Engineering** | Intentional fault injection to validate pipeline resilience |
| **Cost Attribution** | Quality cost tracked per data product/domain |

**Where checks live in medallion:**
- Bronze: Real-time schema contract enforcement, automated quarantine, chaos tests
- Silver: Self-healing transformations, predictive quality, automated remediation
- Gold: Data product SLA monitoring, consumer contract validation, audit trails

**Cost profile:**
- Tooling: Enterprise platforms + custom ($30K-100K+/mo)
- Compute: 40-60% overhead (or separate validation infrastructure)
- Engineering: Dedicated team (3-5+ engineers) + data stewards per domain
- Organizational: Data quality council, cross-functional ownership

**Typical org:** Large enterprise, financial services, healthcare, heavily regulated industries.

---

## Quality Dimensions Taxonomy

The framework evaluates quality across **10 dimensions**, each with its own cost/coverage characteristics:

| # | Dimension | Cheap to Check | Expensive to Check |
|---|-----------|---------------|-------------------|
| 1 | **Schema** | Column exists, type matches | Schema evolution tracking, contract enforcement |
| 2 | **Completeness** | IS NOT NULL | Null rate trends, conditional completeness rules |
| 3 | **Uniqueness** | PK uniqueness | Near-duplicate detection, fuzzy matching |
| 4 | **Freshness** | Partition exists | Per-record latency, SLA tracking |
| 5 | **Volume** | Row count != 0 | Statistical volume anomaly detection |
| 6 | **Referential Integrity** | FK exists in parent | Cross-system, cross-database FK validation |
| 7 | **Range/Domain** | Value in enum list | Statistical distribution monitoring |
| 8 | **Business Rules** | Simple field-level rules | Complex cross-table temporal logic |
| 9 | **Reconciliation** | Source vs. target count | Full aggregate reconciliation with drill-down |
| 10 | **Consistency** | Format standardization | Cross-system semantic consistency |

---

## Cost Model Breakdown

### Cost Categories

| Category | Description | Scales With |
|----------|-------------|-------------|
| **Compute** | Running validation queries | Data volume x number of checks |
| **Tooling** | SaaS/OSS platform costs | Number of data sources and checks |
| **Engineering** | Building + maintaining checks | Complexity of rules x number of sources |
| **Storage** | Validation history, profiles | Retention period x check frequency |
| **Latency** | Pipeline slowdown from checks | Number and complexity of checks |
| **Operational** | Alert triage, remediation | Alert volume x severity |

### Cost Optimization Strategies

1. **Sampling** (L2+): Run expensive checks on samples, not full datasets — 90% cost reduction for statistical checks
2. **Tiered frequency**: Critical checks every run, expensive checks daily/weekly
3. **Pushdown**: Run checks inside the warehouse engine (Soda SQL, dbt) vs. pulling data out
4. **Incremental validation**: Only validate new/changed data, not full table rescans
5. **Risk-based coverage**: Invest more in high-impact, high-change-frequency data assets

---

## Medallion Layer × Maturity Matrix

| Check Type | Bronze (Ingestion) | Silver (Conformance) | Gold (Business) |
|-----------|-------------------|---------------------|-----------------|
| **L1** | — | — | Manual spot checks |
| **L2** | Schema, row count | PK, nulls | Row count match |
| **L3** | + drift detection, freshness SLA | + referential integrity, ranges | + aggregate reconciliation, critical rules |
| **L4** | + anomaly detection, contracts | + semantic validation, historical | + full business rules, lineage |
| **L5** | + real-time, quarantine, chaos | + self-healing, predictive | + SLA monitoring, audit trail |

---

## Choosing Your Target Level

### Decision Framework

| Factor | Points to Lower Level (L1-L2) | Points to Higher Level (L4-L5) |
|--------|-------------------------------|-------------------------------|
| **Regulatory** | No compliance requirements | SOX, GDPR, HIPAA, financial reporting |
| **Business Impact** | Internal analytics only | Revenue-critical, customer-facing |
| **Data Volume** | Small (<1M rows/day) | Large (>100M rows/day) |
| **Source Volatility** | Stable schemas, reliable sources | Frequent changes, unreliable vendors |
| **Consumer Count** | 1-2 teams | Organization-wide, external |
| **Cost of Bad Data** | Low — wrong chart in a dashboard | High — wrong financial report, bad ML model |

### Recommended Starting Points

- **Startups / Internal analytics**: Start at **L2**, grow to L3 as pain points emerge
- **Mid-market / Multiple consumers**: Start at **L3**, targeted L4 for critical paths
- **Enterprise / Regulated**: Start at **L4**, targeted L5 for audit-critical paths
- **Financial services / Healthcare**: **L4-L5** from the start for regulated data

---

## Implementation Roadmap

**Phase 1 (Week 1-2):** Implement L2 checks using dbt tests or Soda Core
**Phase 2 (Month 1-2):** Elevate to L3 — add profiling baselines, referential integrity, freshness SLAs
**Phase 3 (Quarter 2):** Selective L4 — anomaly detection and business rules for top 10 critical tables
**Phase 4 (Quarter 3-4):** Expand L4 coverage, introduce data contracts for key producer-consumer pairs
**Phase 5 (Year 2+):** L5 capabilities where justified by regulatory or business requirements

---

## Tooling by Level

| Level | Open Source Options | Commercial Options |
|-------|--------------------|--------------------|
| L1 | Manual SQL | — |
| L2 | dbt tests, simple assertions | — |
| L3 | Great Expectations, Soda Core, dbt + Elementary | Soda Cloud |
| L4 | GX + custom ML checks | Monte Carlo, Bigeye, Atlan, Anomalo |
| L5 | Custom platform on OSS stack | Collibra, Informatica, Alation + custom |

---

## Decision Matrix: Source System × Analytics Solution Parameters

### A. Source/Transactional System Parameters (Score 1-5 each)

| # | Parameter | Score 1 (Simple) | Score 3 (Moderate) | Score 5 (Complex) |
|---|-----------|-----------------|-------------------|-------------------|
| A1 | **Data Volume** | <100K rows/day | 1-50M rows/day | >100M rows/day |
| A2 | **Source Count** | 1-2 systems | 5-10 systems | 20+ systems |
| A3 | **Schema Stability** | Rarely changes | Quarterly changes | Weekly/unannounced changes |
| A4 | **Source Reliability** | 99.9% uptime, clean data | Occasional issues | Frequent outages, dirty data |
| A5 | **Data Complexity** | Flat relational tables | Some nested/JSON fields | Complex semi-structured, multi-format |
| A6 | **Data Sensitivity** | Non-sensitive internal data | Some PII, basic compliance | Financial/health/regulated PII |
| A7 | **CDC Capability** | Full CDC support | Partial (timestamps only) | No CDC, full loads only |
| A8 | **Change Frequency** | Daily batch | Hourly/micro-batch | Real-time/streaming |
| A9 | **Documentation** | Well-documented schemas | Partial documentation | Undocumented, tribal knowledge |
| A10 | **Extraction Method** | Direct DB access | API with rate limits | File drops, screen scraping |

### B. Analytics/Target Solution Parameters (Score 1-5 each)

| # | Parameter | Score 1 (Basic) | Score 3 (Growing) | Score 5 (Mission-Critical) |
|---|-----------|----------------|-------------------|---------------------------|
| B1 | **Consumer Count** | 1-2 analysts | 5-20 users, multiple teams | Org-wide, 100+ users, external |
| B2 | **Regulatory Need** | None | SOC2, basic compliance | SOX, HIPAA, GDPR, financial audit |
| B3 | **Consumption Pattern** | Weekly reports | Daily dashboards | Real-time decisions, customer-facing |
| B4 | **ML/AI Dependency** | None | Experimental models | Production ML models, AI products |
| B5 | **SLA Requirements** | Best-effort | Next-day availability | <1 hour latency, contractual SLAs |
| B6 | **Cost of Bad Data** | Wrong chart | Incorrect internal report | Wrong financial filing, bad ML prediction |
| B7 | **Team Maturity** | 1 data person, part-time | 3-5 dedicated data engineers | 10+ data team, platform team |
| B8 | **Self-Service Level** | SQL-only, tech users | BI tool for analysts | Self-service for business users |
| B9 | **Data Product Thinking** | Ad-hoc queries | Defined datasets | Published data products with SLAs |
| B10 | **Budget for Quality** | $0 (OSS only) | $1-10K/month | $10K+/month |

### Scoring → Recommended Level

| Source Score (A) | Analytics Score (B) | Recommended Level | Rationale |
|-----------------|--------------------|--------------------|-----------|
| 10-18 | 10-18 | **L2: Foundational** | Simple sources, basic consumers — catch obvious failures |
| 10-18 | 19-30 | **L3: Proactive** | Simple sources but important consumers — validate proactively |
| 19-30 | 10-18 | **L3: Proactive** | Complex sources need more validation even for basic consumers |
| 19-30 | 19-30 | **L3-L4: Proactive/Advanced** | Both sides have complexity — invest in quality |
| 19-30 | 31-50 | **L4: Advanced** | Complex sources feeding mission-critical analytics |
| 31-50 | 19-30 | **L4: Advanced** | Highly complex sources need advanced monitoring |
| 31-50 | 31-50 | **L4-L5: Advanced/Comprehensive** | Both sides are complex — comprehensive quality program |
| Any | 40+ | **L5: Comprehensive** | Mission-critical analytics demands the highest quality |
| 40+ | Any | **L5: Comprehensive** | Extremely complex sources demand the highest monitoring |

### Override Rules

Certain parameters should **automatically escalate** the recommended level regardless of total score:
- **B2 (Regulatory) = 5** → Minimum L4 for regulated data paths
- **B6 (Cost of Bad Data) = 5** → Minimum L4 for those specific pipelines
- **A6 (Data Sensitivity) = 5** → Minimum L4 with audit trail
- **B4 (ML/AI Dependency) = 5** → Minimum L3 with statistical drift detection
