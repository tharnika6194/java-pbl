import json
import os
from .database import get_db_connection

def create_startup_idea(data):
    """Inserts a new startup idea into startup_ideas table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO startup_ideas (
        user_id, startup_name, idea_description, problem_statement,
        target_customers, industry, target_market, business_model,
        initial_budget, competitors, unique_features, technology_used, revenue_model
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('user_id', 1),
        data.get('startup_name', '').strip(),
        data.get('idea_description', '').strip(),
        data.get('problem_statement', '').strip(),
        data.get('target_customers', '').strip(),
        data.get('industry', 'Technology').strip(),
        data.get('target_market', 'Global / Regional').strip(),
        data.get('business_model', 'SaaS / Subscription').strip(),
        data.get('initial_budget', '$10,000 - $25,000').strip(),
        data.get('competitors', '').strip(),
        data.get('unique_features', '').strip(),
        data.get('technology_used', '').strip(),
        data.get('revenue_model', '').strip()
    ))
    startup_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return startup_id

def save_validation_report(startup_id, analysis_result, pdf_path=None):
    """Saves full analysis report, associated scores, and recommendations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    overall_score = analysis_result.get('overall_score', 75)
    validation_status = analysis_result.get('validation_status', 'Promising')
    summary = analysis_result.get('summary', '')

    cursor.execute('''
    INSERT INTO validation_reports (
        startup_id, overall_score, validation_status, summary,
        problem_analysis, customer_analysis, market_analysis, competitor_analysis,
        uvp_analysis, business_model_analysis, cost_estimation, risk_analysis,
        scalability_analysis, tech_feasibility, roadmap, pdf_path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        startup_id,
        overall_score,
        validation_status,
        summary,
        json.dumps(analysis_result.get('problem_analysis', {})),
        json.dumps(analysis_result.get('customer_analysis', {})),
        json.dumps(analysis_result.get('market_analysis', {})),
        json.dumps(analysis_result.get('competitor_analysis', {})),
        json.dumps(analysis_result.get('uvp_analysis', {})),
        json.dumps(analysis_result.get('business_model_analysis', {})),
        json.dumps(analysis_result.get('cost_estimation', {})),
        json.dumps(analysis_result.get('risk_analysis', {})),
        json.dumps(analysis_result.get('scalability_analysis', {})),
        json.dumps(analysis_result.get('tech_feasibility', {})),
        json.dumps(analysis_result.get('roadmap', [])),
        pdf_path
    ))
    report_id = cursor.lastrowid

    # Insert individual scores
    scores = analysis_result.get('scores', {})
    cursor.execute('''
    INSERT INTO analysis_scores (
        report_id, startup_id, problem_fit, market_potential, competition,
        business_model, revenue_potential, scalability, tech_feasibility,
        risk_score, overall_score
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        report_id,
        startup_id,
        scores.get('problem_fit', 75),
        scores.get('market_potential', 75),
        scores.get('competition', 70),
        scores.get('business_model', 75),
        scores.get('revenue_potential', 70),
        scores.get('scalability', 75),
        scores.get('tech_feasibility', 80),
        scores.get('risk_score', 65),
        overall_score
    ))

    # Insert recommendations
    recs = analysis_result.get('recommendations', [])
    for idx, r in enumerate(recs, 1):
        if isinstance(r, dict):
            cursor.execute('''
            INSERT INTO recommendations (
                report_id, startup_id, recommendation_order, category, title, description, impact
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                report_id,
                startup_id,
                idx,
                r.get('category', 'Strategy'),
                r.get('title', f'Recommendation #{idx}'),
                r.get('description', ''),
                r.get('impact', 'High')
            ))
        elif isinstance(r, str):
            cursor.execute('''
            INSERT INTO recommendations (
                report_id, startup_id, recommendation_order, category, title, description, impact
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                report_id,
                startup_id,
                idx,
                'Actionable Step',
                f'Action {idx}',
                r,
                'High'
            ))

    conn.commit()
    conn.close()
    return report_id

def update_report_pdf(report_id, pdf_path):
    """Updates the PDF path of an existing validation report."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE validation_reports SET pdf_path = ? WHERE id = ?', (pdf_path, report_id))
    conn.commit()
    conn.close()

def get_startup_by_id(startup_id):
    """Retrieves full startup idea details, its latest validation report, scores, and recommendations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM startup_ideas WHERE id = ?', (startup_id,))
    startup_row = cursor.fetchone()
    if not startup_row:
        conn.close()
        return None

    startup = dict(startup_row)

    # Fetch latest validation report
    cursor.execute('''
    SELECT * FROM validation_reports
    WHERE startup_id = ?
    ORDER BY created_at DESC LIMIT 1
    ''', (startup_id,))
    report_row = cursor.fetchone()

    report = None
    scores = None
    recommendations = []

    if report_row:
        report = dict(report_row)
        for key in ['problem_analysis', 'customer_analysis', 'market_analysis',
                    'competitor_analysis', 'uvp_analysis', 'business_model_analysis',
                    'cost_estimation', 'risk_analysis', 'scalability_analysis',
                    'tech_feasibility', 'roadmap']:
            if report.get(key):
                try:
                    report[key] = json.loads(report[key])
                except Exception:
                    pass

        # Fetch scores
        cursor.execute('SELECT * FROM analysis_scores WHERE report_id = ?', (report['id'],))
        score_row = cursor.fetchone()
        if score_row:
            scores = dict(score_row)

        # Fetch recommendations
        cursor.execute('''
        SELECT * FROM recommendations
        WHERE report_id = ?
        ORDER BY recommendation_order ASC
        ''', (report['id'],))
        recommendations = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        'startup': startup,
        'report': report,
        'scores': scores,
        'recommendations': recommendations
    }

def list_all_startups():
    """Lists all startup ideas with summary information, score, and report status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT
        s.id,
        s.startup_name,
        s.idea_description,
        s.industry,
        s.target_market,
        s.created_at,
        r.id AS report_id,
        r.overall_score,
        r.validation_status,
        r.pdf_path
    FROM startup_ideas s
    LEFT JOIN validation_reports r ON r.startup_id = s.id
        AND r.id = (SELECT MAX(id) FROM validation_reports WHERE startup_id = s.id)
    ORDER BY s.created_at DESC
    ''')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def delete_startup_by_id(startup_id):
    """Deletes startup and removes generated PDF if present."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find associated pdf
    cursor.execute('SELECT pdf_path FROM validation_reports WHERE startup_id = ?', (startup_id,))
    pdf_rows = cursor.fetchall()

    cursor.execute('DELETE FROM startup_ideas WHERE id = ?', (startup_id,))
    conn.commit()
    conn.close()

    # Clean up PDF files if exist
    for r in pdf_rows:
        p = r['pdf_path']
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
    return True

def get_dashboard_metrics():
    """Calculates high-level metrics for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM startup_ideas')
    total_ideas = cursor.fetchone()['count']

    cursor.execute('SELECT AVG(overall_score) as avg_score, MAX(overall_score) as max_score FROM validation_reports')
    score_data = cursor.fetchone()
    avg_score = round(score_data['avg_score'] or 0, 1) if score_data['avg_score'] is not None else 0
    max_score = score_data['max_score'] or 0

    cursor.execute('''
    SELECT validation_status, COUNT(*) as count
    FROM validation_reports
    GROUP BY validation_status
    ''')
    status_counts = {r['validation_status']: r['count'] for r in cursor.fetchall()}

    conn.close()
    return {
        'total_ideas': total_ideas,
        'avg_score': avg_score,
        'max_score': max_score,
        'status_counts': status_counts
    }
