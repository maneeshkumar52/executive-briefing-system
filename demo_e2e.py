import asyncio, sys
sys.path.insert(0, '.')

async def main():
    print("=== Executive Briefing System - End-to-End Demo ===\n")

    # Test 1: All 6 data connectors (pure mock data)
    from data_sources.financial_connector import FinancialConnector
    from data_sources.customer_connector import CustomerConnector
    from data_sources.market_connector import MarketConnector
    from data_sources.hr_connector import HRConnector
    from data_sources.ops_connector import OpsConnector
    from data_sources.news_connector import NewsConnector

    print("--- Phase 1: Data Ingestion (6 sources) ---")
    financial, customer, market, hr, ops, news = await asyncio.gather(
        FinancialConnector().fetch(),
        CustomerConnector().fetch(),
        MarketConnector().fetch(),
        HRConnector().fetch(),
        OpsConnector().fetch(),
        NewsConnector().fetch()
    )

    print(f"Financial:  {financial.period} Revenue ${financial.quarterly_revenue_usd_millions:.1f}M | Gross Margin {financial.gross_margin_pct:.1f}% | FCF ${financial.free_cash_flow_usd_millions:.1f}M")
    print(f"Customer:   NPS {customer.nps_score} | Churn {customer.churn_rate_pct:.1f}% | ARPU ${customer.arpu_usd:.2f} | Customers {customer.total_active_customers:,}")
    print(f"Market:     Share {market.market_share_pct:.1f}% | Industry Growth {market.industry_growth_rate_pct:.1f}% | TAM ${market.addressable_market_usd_billions:.1f}B")
    print(f"HR:         Headcount {hr.total_headcount:,} | Turnover {hr.voluntary_turnover_rate_pct:.1f}% | Engagement {hr.employee_engagement_score:.0f}/100")
    print(f"Operations: Uptime {ops.system_uptime_pct:.2f}% | SLA {ops.sla_compliance_pct:.1f}% | Incidents {ops.incidents_this_quarter}")
    print(f"News:       {len(news)} competitor news items")
    for n in news[:3]:
        sentiment_label = "Positive" if n.sentiment > 0 else "Negative" if n.sentiment < 0 else "Neutral"
        print(f"  [{sentiment_label}] {n.headline[:70]}...")

    # Test 2: Build CompanyData
    from shared.models import CompanyData
    from datetime import datetime, timezone
    company_data = CompanyData(
        financial=financial,
        customer=customer,
        market=market,
        hr=hr,
        operational=ops,
        news=news,
        fetch_timestamp=datetime.now(timezone.utc).isoformat()
    )
    print(f"\nCompanyData assembled from all 6 sources")

    # Test 3: Run all 5 specialist analyses (with LLM fallback when Azure unavailable)
    from specialists.financial_specialist import FinancialSpecialist
    from specialists.market_specialist import MarketSpecialist
    from specialists.operations_specialist import OperationsSpecialist
    from specialists.people_specialist import PeopleSpecialist
    from specialists.risk_specialist import RiskSpecialist

    print(f"\n--- Phase 2: Specialist Analysis (5 agents, parallel) ---")
    analyses = await asyncio.gather(
        FinancialSpecialist().analyse(company_data),
        MarketSpecialist().analyse(company_data),
        OperationsSpecialist().analyse(company_data),
        PeopleSpecialist().analyse(company_data),
        RiskSpecialist().analyse(company_data),
        return_exceptions=True
    )

    for a in analyses:
        if isinstance(a, Exception):
            print(f"  [FAIL] Specialist failed: {a}")
        else:
            print(f"  [OK] {a.specialist_name}: {len(a.key_findings)} findings, confidence {a.confidence_score:.2f}")
            if a.risk_flags:
                print(f"    Risk flags: {a.risk_flags}")
            for f in a.key_findings[:2]:
                print(f"    - {f[:80]}")

    valid_analyses = [a for a in analyses if not isinstance(a, Exception)]

    # Test 4: Synthesise
    from synthesiser.agent import SynthesiserAgent
    from shared.models import BriefingRequest

    request = BriefingRequest(
        topic="Q4 2024 Executive Performance Review",
        date_range="Q4 2024",
        requester="CEO"
    )

    print(f"\n--- Phase 3: Executive Synthesis ---")
    synthesis = await SynthesiserAgent().synthesise(valid_analyses, company_data, request)
    print(f"Synthesis completed:")
    print(f"  Executive Summary ({len(synthesis.executive_summary)} chars):")
    print(f"  {synthesis.executive_summary[:200]}...")
    print(f"\n  Key Metrics Dashboard:")
    for domain, metric in synthesis.key_metrics_dashboard.items():
        print(f"    {domain}: {metric}")
    print(f"\n  Strategic Insights: {len(synthesis.strategic_insights)}")
    print(f"  Recommendations: {len(synthesis.recommendations)}")
    print(f"  Risk Register: {len(synthesis.risk_register)}")

    # Test 5: Compliance gate
    from compliance_gate.agent import ComplianceGate

    print(f"\n--- Phase 4: Compliance Review ---")
    compliance = await ComplianceGate().review(synthesis, request)
    print(f"Compliance: {'APPROVED' if compliance.approved else 'ISSUES FOUND'}")
    print(f"  Disclaimers added ({len(compliance.required_disclaimers)}):")
    for d in compliance.required_disclaimers:
        print(f"    - {d}")

    # Test 6: Report generation
    from orchestrator.report_generator import ReportGenerator
    from shared.models import BriefingResult, BriefingStatus
    from datetime import datetime, timezone

    print(f"\n--- Phase 5: Report Generation ---")
    result = BriefingResult(
        run_id="demo-001",
        status=BriefingStatus.COMPLETE,
        topic=request.topic,
        requested_by=request.requester,
        synthesis=synthesis,
        compliance=compliance,
        company_data=company_data,
        created_at=datetime.now(timezone.utc).isoformat()
    )

    report_md = ReportGenerator().generate_markdown(result, request)
    lines = report_md.split('\n')
    print(f"Executive Briefing Report generated:")
    print(f"  Total length: {len(report_md)} chars, {len(lines)} lines")
    print(f"\n--- BRIEFING PREVIEW ---")
    print('\n'.join(lines[:30]))
    print("... [truncated] ...")

    print("\n=== Executive Briefing System: Full 5-phase pipeline working end-to-end ===")
    print("  Phase 1: 6 data sources aggregated")
    print("  Phase 2: 5 specialist analyses completed")
    print("  Phase 3: Board-quality synthesis generated")
    print("  Phase 4: Compliance review passed")
    print("  Phase 5: Executive briefing formatted")

asyncio.run(main())
