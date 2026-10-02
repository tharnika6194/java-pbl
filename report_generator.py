import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

def generate_pdf_report(startup, report, scores, recommendations):
    """
    Generates a professional, multi-page PDF startup validation report.
    Returns the absolute path to the generated PDF file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    startup_name = startup.get('startup_name', 'Startup').strip()
    safe_name = "".join(c for c in startup_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    report_id = report.get('id', 1)
    filename = f"Validation_Report_{safe_name}_{report_id}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom color palette
    c_navy = colors.HexColor('#0F172A')
    c_blue = colors.HexColor('#2563EB')
    c_purple = colors.HexColor('#7C3AED')
    c_bg_light = colors.HexColor('#F8FAFC')
    c_border = colors.HexColor('#E2E8F0')
    c_text_dark = colors.HexColor('#1E293B')
    c_text_muted = colors.HexColor('#64748B')
    c_green = colors.HexColor('#059669')

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.white,
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#E2E8F0'),
        alignment=TA_LEFT
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_navy,
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_blue,
        spaceBefore=6,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text_dark,
        alignment=TA_JUSTIFY
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_navy
    )

    small_muted = ParagraphStyle(
        'SmallMuted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text_muted
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("AI STARTUP VALIDATOR", title_style),
            Paragraph(f"OVERALL VIABILITY<br/><b>{report.get('overall_score', 75)}/100</b>", badge_style)
        ],
        [
            Paragraph("AI-Powered Startup Idea Evaluation & Business Feasibility Platform", subtitle_style),
            Paragraph(f"Status: {report.get('validation_status', 'Promising')}", subtitle_style)
        ]
    ]

    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_navy),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    # 2. Startup Profile Metadata Table
    created_date = startup.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))
    meta_data = [
        [
            Paragraph("<b>Startup Name:</b>", bold_body), Paragraph(startup.get('startup_name', 'N/A'), body_style),
            Paragraph("<b>Target Market:</b>", bold_body), Paragraph(startup.get('target_market', 'N/A'), body_style)
        ],
        [
            Paragraph("<b>Industry / Category:</b>", bold_body), Paragraph(startup.get('industry', 'N/A'), body_style),
            Paragraph("<b>Initial Budget:</b>", bold_body), Paragraph(startup.get('initial_budget', 'N/A'), body_style)
        ],
        [
            Paragraph("<b>Business Model:</b>", bold_body), Paragraph(startup.get('business_model', 'N/A'), body_style),
            Paragraph("<b>Report Date:</b>", bold_body), Paragraph(str(created_date)[:16], body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[100, 170, 100, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Startup Concept & Description
    story.append(Paragraph("Startup Concept & Description", h1_style))
    story.append(Paragraph(startup.get('idea_description', 'No description provided.'), body_style))
    story.append(Spacer(1, 8))

    # 4. Executive Summary Callout
    story.append(Paragraph("Executive Summary", h1_style))
    exec_summary_text = report.get('summary', 'Validation assessment completed.')
    summary_table = Table([[Paragraph(exec_summary_text, body_style)]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
        ('BOX', (0, 0), (-1, -1), 1.5, c_blue),
        ('PADDING', (0, 0), (-1, -1), 9),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # 5. Validation Scores Matrix Table
    story.append(Paragraph("Validation Scorecard", h1_style))
    sc = scores or {}
    score_rows = [
        [
            Paragraph("<b>Evaluation Dimension</b>", bold_body),
            Paragraph("<b>Score (0-100)</b>", bold_body),
            Paragraph("<b>Viability Assessment</b>", bold_body)
        ],
        [Paragraph("Problem-Solution Fit", body_style), str(sc.get('problem_fit', 75)), "High relevance and acute customer pain alignment" if sc.get('problem_fit', 75) >= 75 else "Moderate relevance; pain point needs sharper focus"],
        [Paragraph("Market Potential & Demand", body_style), str(sc.get('market_potential', 75)), "Sizable target addressable market with expansion catalysts" if sc.get('market_potential', 75) >= 75 else "Niche addressable market segment"],
        [Paragraph("Competitive Differentiation", body_style), str(sc.get('competition', 70)), "Noticeable defensibility gap against legacy options" if sc.get('competition', 70) >= 70 else "High competition intensity; requires stronger moat"],
        [Paragraph("Business Model Viability", body_style), str(sc.get('business_model', 75)), "Clear recurring revenue potential and monetization channels" if sc.get('business_model', 75) >= 75 else "Monetization model requires unit-economic stress testing"],
        [Paragraph("Revenue Potential", body_style), str(sc.get('revenue_potential', 75)), "Strong gross margin upside and compounding ARR potential" if sc.get('revenue_potential', 75) >= 75 else "Moderate unit margins; monitor customer acquisition costs"],
        [Paragraph("Scalability (Tech & Geo)", body_style), str(sc.get('scalability', 75)), "High leverage software model with low marginal cost" if sc.get('scalability', 75) >= 75 else "Operational friction may constrain rapid regional scaling"],
        [Paragraph("Technology Feasibility", body_style), str(sc.get('tech_feasibility', 80)), "Proven, dependable modern technology architecture" if sc.get('tech_feasibility', 80) >= 75 else "Complex architecture with external engineering dependencies"],
        [Paragraph("Risk & Resilience Score", body_style), str(sc.get('risk_score', 65)), "Manageable execution risk with structured mitigations" if sc.get('risk_score', 65) >= 65 else "Elevated market and regulatory uncertainty"],
        [Paragraph("<b>OVERALL VALIDATION SCORE</b>", bold_body), Paragraph(f"<b>{report.get('overall_score', 75)}/100</b>", bold_body), Paragraph(f"<b>{report.get('validation_status', 'Promising')}</b>", bold_body)]
    ]
    scores_table = Table(score_rows, colWidths=[180, 90, 270])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#DBEAFE')),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 4.5),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(scores_table)
    story.append(Spacer(1, 12))

    # 6. Detailed Analysis Sections
    prob = report.get('problem_analysis', {})
    cust = report.get('customer_analysis', {})
    mkt = report.get('market_analysis', {})
    comp = report.get('competitor_analysis', {})
    uvp = report.get('uvp_analysis', {})
    bm = report.get('business_model_analysis', {})
    cost = report.get('cost_estimation', {})
    scal = report.get('scalability_analysis', {})
    tech = report.get('tech_feasibility', {})
    risks = report.get('risk_analysis', [])

    # A. Problem & Target Customer
    story.append(Paragraph("A. Problem Validation & Target Customer", h1_style))
    p_text = f"<b>Problem Solved:</b> {prob.get('problem_solved', 'N/A')}<br/>" \
             f"<b>Problem Significance:</b> {prob.get('significance', 'N/A')}<br/>" \
             f"<b>Who Experiences It:</b> {prob.get('who_experiences_it', 'N/A')}<br/>" \
             f"<b>Problem Severity:</b> {prob.get('severity_score', '8')}/10 ({prob.get('severity_label', 'High')})"
    story.append(Paragraph(p_text, body_style))
    story.append(Spacer(1, 5))

    c_text = f"<b>Primary Target Customer:</b> {cust.get('primary_customers', 'N/A')}<br/>" \
             f"<b>Secondary Target Customer:</b> {cust.get('secondary_customers', 'N/A')}<br/>"
    if isinstance(cust.get('customer_persona'), dict):
        persona = cust['customer_persona']
        c_text += f"<b>Customer Persona:</b> {persona.get('demographics', '')} — {persona.get('buying_behavior', '')}"
    story.append(Paragraph(c_text, body_style))
    story.append(Spacer(1, 10))

    # B. Market Opportunity (TAM/SAM/SOM)
    story.append(Paragraph("B. Market Opportunity & Sizing", h1_style))
    m_text = f"{mkt.get('market_opportunity', '')} {mkt.get('potential_demand', '')}"
    story.append(Paragraph(m_text, body_style))
    story.append(Spacer(1, 5))

    tam_table_data = [
        [Paragraph("<b>Metric</b>", bold_body), Paragraph("<b>Estimated Value</b>", bold_body), Paragraph("<b>Market Definition</b>", bold_body)],
        [Paragraph("TAM (Total Addressable Market)", body_style), Paragraph(mkt.get('tam', '$10B+'), body_style), Paragraph("Total global market demand in this category.", body_style)],
        [Paragraph("SAM (Serviceable Addressable)", body_style), Paragraph(mkt.get('sam', '$1.5B'), body_style), Paragraph("Segment of TAM targeted by your product reach.", body_style)],
        [Paragraph("SOM (Serviceable Obtainable)", body_style), Paragraph(mkt.get('som', '$20M'), body_style), Paragraph("Realistic 3-year market share capture objective.", body_style)],
    ]
    tam_table = Table(tam_table_data, colWidths=[160, 140, 240])
    tam_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(tam_table)
    story.append(Paragraph(f"<i>Note: {mkt.get('market_disclaimer', 'Algorithmic estimates.')}</i>", small_muted))
    story.append(Spacer(1, 10))

    # C. Competitor & UVP
    story.append(Paragraph("C. Competitor Analysis & Unique Value Proposition", h1_style))
    story.append(Paragraph(f"<b>Core UVP:</b> {uvp.get('core_uvp', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Customer Benefit:</b> {uvp.get('customer_benefit', 'N/A')}", body_style))
    story.append(Paragraph(f"<b>Differentiation Strategy:</b> {uvp.get('differentiation_strategy', 'N/A')}", body_style))
    story.append(Spacer(1, 6))

    competitors_list = comp.get('competitors', [])
    if competitors_list:
        comp_rows = [[Paragraph("<b>Competitor</b>", bold_body), Paragraph("<b>Strengths</b>", bold_body), Paragraph("<b>Weaknesses</b>", bold_body), Paragraph("<b>Differentiation</b>", bold_body)]]
        for c in competitors_list[:3]:
            comp_rows.append([
                Paragraph(c.get('name', ''), bold_body),
                Paragraph(c.get('strengths', ''), body_style),
                Paragraph(c.get('weaknesses', ''), body_style),
                Paragraph(c.get('differentiation', ''), body_style)
            ])
        comp_table = Table(comp_rows, colWidths=[100, 140, 140, 160])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
            ('BOX', (0, 0), (-1, -1), 1, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(comp_table)
        story.append(Paragraph(f"<i>{comp.get('verification_note', 'Assumptions based on founder inputs.')}</i>", small_muted))
    story.append(Spacer(1, 10))

    # D. Cost Estimation
    story.append(Paragraph("D. Estimated Initial Cost Breakdown", h1_style))
    cost_rows = [
        [Paragraph("<b>Expense Category</b>", bold_body), Paragraph("<b>Estimated Budget (MVP Phase)</b>", bold_body)],
        [Paragraph("Development & Engineering", body_style), Paragraph(str(cost.get('development', 'N/A')), body_style)],
        [Paragraph("Infrastructure & Cloud APIs", body_style), Paragraph(str(cost.get('infrastructure', 'N/A')), body_style)],
        [Paragraph("Marketing & User Acquisition", body_style), Paragraph(str(cost.get('marketing', 'N/A')), body_style)],
        [Paragraph("Operations & Compliance", body_style), Paragraph(str(cost.get('operations', 'N/A')), body_style)],
        [Paragraph("Contingency & Other", body_style), Paragraph(str(cost.get('other_expenses', 'N/A')), body_style)],
        [Paragraph("<b>TOTAL ESTIMATED INITIAL COST</b>", bold_body), Paragraph(f"<b>{cost.get('total_estimated', 'N/A')}</b>", bold_body)]
    ]
    cost_table = Table(cost_rows, colWidths=[240, 300])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(cost_table)
    story.append(Paragraph(f"<i>{cost.get('cost_disclaimer', 'Directional estimates.')}</i>", small_muted))
    story.append(Spacer(1, 10))

    # E. Risk Analysis & Mitigation
    story.append(Paragraph("E. Risk Analysis & Mitigation Strategies", h1_style))
    if risks:
        risk_rows = [[Paragraph("<b>Risk Category</b>", bold_body), Paragraph("<b>Level</b>", bold_body), Paragraph("<b>Key Threat / Reason</b>", bold_body), Paragraph("<b>Recommended Mitigation</b>", bold_body)]]
        for r in risks:
            level = r.get('risk_level', 'Medium')
            lvl_color = c_green if level == 'Low' else (colors.HexColor('#D97706') if level == 'Medium' else colors.HexColor('#DC2626'))
            risk_rows.append([
                Paragraph(r.get('risk_type', ''), bold_body),
                Paragraph(f"<font color='{lvl_color.hexval()}'><b>{level}</b></font>", bold_body),
                Paragraph(r.get('reason', ''), body_style),
                Paragraph(r.get('mitigation', ''), body_style)
            ])
        risk_table = Table(risk_rows, colWidths=[120, 60, 180, 180])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
            ('BOX', (0, 0), (-1, -1), 1, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(risk_table)
    story.append(Spacer(1, 10))

    # F. Scalability & Technical Feasibility
    story.append(Paragraph("F. Scalability & Technical Feasibility", h1_style))
    tech_text = f"<b>Customer Scalability:</b> {scal.get('customer_scalability', 'N/A')}<br/>" \
                f"<b>Technical Scalability:</b> {scal.get('technical_scalability', 'N/A')}<br/>" \
                f"<b>Geographic Scalability:</b> {scal.get('geographic_scalability', 'N/A')}<br/>" \
                f"<b>Tech Architecture:</b> {tech.get('backend_requirements', 'N/A')}<br/>" \
                f"<b>AI/ML Requirements:</b> {tech.get('ai_ml_requirements', 'N/A')}"
    story.append(Paragraph(tech_text, body_style))
    story.append(Spacer(1, 10))

    # G. AI Actionable Recommendations
    story.append(Paragraph("G. Actionable AI Recommendations", h1_style))
    rec_rows = [[Paragraph("<b>#</b>", bold_body), Paragraph("<b>Strategic Focus</b>", bold_body), Paragraph("<b>Actionable Recommendation</b>", bold_body), Paragraph("<b>Priority</b>", bold_body)]]
    for idx, rec in enumerate(recommendations, 1):
        rec_rows.append([
            str(idx),
            Paragraph(rec.get('title', ''), bold_body),
            Paragraph(rec.get('description', ''), body_style),
            Paragraph(rec.get('impact', 'High'), bold_body)
        ])
    rec_table = Table(rec_rows, colWidths=[25, 150, 305, 60])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 10))

    # H. 6-Phase MVP Execution Roadmap
    story.append(Paragraph("H. 6-Phase Startup Execution Roadmap", h1_style))
    roadmap = report.get('roadmap', [])
    if roadmap:
        road_rows = [[Paragraph("<b>Phase & Objective</b>", bold_body), Paragraph("<b>Key Action Tasks</b>", bold_body), Paragraph("<b>Expected Milestone</b>", bold_body)]]
        for phase in roadmap:
            tasks_formatted = "<br/>• ".join([""] + phase.get('tasks', [])) if isinstance(phase.get('tasks'), list) else str(phase.get('tasks', ''))
            road_rows.append([
                Paragraph(f"<b>{phase.get('phase', '')}</b><br/>{phase.get('objective', '')}", body_style),
                Paragraph(tasks_formatted, body_style),
                Paragraph(phase.get('expected_outcome', ''), body_style)
            ])
        road_table = Table(road_rows, colWidths=[160, 230, 150])
        road_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
            ('BOX', (0, 0), (-1, -1), 1, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(road_table)
    story.append(Spacer(1, 12))

    # I. Formal Disclaimer Box
    disclaimer_text = (
        "<b>OFFICIAL DISCLAIMER:</b> This validation report is an AI-assisted heuristic and algorithmic assessment "
        "generated for educational, academic, and pre-venture planning purposes. The scores, market projections, "
        "and estimates provided herein do not constitute guaranteed commercial success, formal investment advice, "
        "or legally binding financial audits. Aspiring founders must conduct primary customer discovery and due diligence."
    )
    disc_table = Table([[Paragraph(disclaimer_text, small_muted)]], colWidths=[540])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FEF3C7')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#F59E0B')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(disc_table)

    # Build the PDF
    doc.build(story)
    return filepath
