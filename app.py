import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .database import init_db, get_db_connection
from .routes import api_bp, SAMPLE_STARTUP
from .models import create_startup_idea, save_validation_report, get_startup_by_id, update_report_pdf
from .ai_engine import analyze_startup_idea
from .report_generator import generate_pdf_report

def seed_sample_if_empty():
    """Seeds the initial LocalStyle AI startup if database has 0 ideas."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM startup_ideas")
        count = cursor.fetchone()['count']
        conn.close()

        if count == 0:
            print("[Database] Seeding sample showcase startup: LocalStyle AI...")
            startup_id = create_startup_idea(SAMPLE_STARTUP)
            analysis = analyze_startup_idea(SAMPLE_STARTUP)
            report_id = save_validation_report(startup_id, analysis)

            # Generate sample PDF
            full_data = get_startup_by_id(startup_id)
            if full_data and full_data.get('report'):
                pdf_path = generate_pdf_report(
                    full_data['startup'],
                    full_data['report'],
                    full_data['scores'],
                    full_data['recommendations']
                )
                update_report_pdf(report_id, pdf_path)
            print(f"[Database] Sample startup seeded successfully (ID: {startup_id}, Report ID: {report_id})")
    except Exception as e:
        print(f"[Database Seed Warning] Could not auto-seed sample: {e}")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ai_startup_validator_secret_key_2026')

    # Enable Cross-Origin Resource Sharing
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize SQLite database schema
    init_db()

    # Pre-seed initial showcase startup
    seed_sample_if_empty()

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')

    # Serve built React frontend from frontend/dist if available
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dist = os.path.join(base_dir, 'frontend', 'dist')

    from flask import send_from_directory

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path.startswith('api'):
            return jsonify({
                "success": False,
                "message": "The requested API endpoint was not found."
            }), 404
        if os.path.exists(os.path.join(frontend_dist, path)) and path != '':
            return send_from_directory(frontend_dist, path)
        if os.path.exists(os.path.join(frontend_dist, 'index.html')):
            return send_from_directory(frontend_dist, 'index.html')
        return jsonify({
            "status": "healthy",
            "message": "AI Startup Validator Backend running. Access Vite frontend or build frontend to serve from port 5000."
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "message": "The requested API endpoint was not found."
        }), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "success": False,
            "message": "An internal server error occurred."
        }), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 AI Startup Validator Backend listening on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
