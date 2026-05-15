"""
Simple HTTP API server for database access.
Runs on port 5000 and exposes database operations as REST endpoints.
"""

import json
import sqlite3
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [API] %(message)s'
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent / "wie.db"

class DatabaseHandler(BaseHTTPRequestHandler):
    """HTTP request handler for database operations"""

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        try:
            # Wedges endpoints
            if path == "/api/wedges":
                self.handle_get_wedges(query_params)
            elif path.startswith("/api/wedges/"):
                wedge_id = path.split("/")[-1]
                self.handle_get_wedge(wedge_id)
            
            # Signals endpoints
            elif path == "/api/signals":
                self.handle_get_signals(query_params)
            
            # Watchlist endpoints
            elif path == "/api/watchlist":
                self.handle_get_watchlist()
            
            # Scraper metadata
            elif path.startswith("/api/scrapers/metadata/"):
                scraper_name = path.split("/")[-1]
                self.handle_get_scraper_metadata(scraper_name)
            
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling GET {path}: {e}")
            self.send_error(500, str(e))

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            # Watchlist endpoints
            if path == "/api/watchlist":
                data = json.loads(body) if body else {}
                self.handle_add_watchlist(data)
            
            # Scraper metadata
            elif path.startswith("/api/scrapers/metadata/"):
                scraper_name = path.split("/")[-1]
                data = json.loads(body) if body else {}
                self.handle_update_scraper_metadata(scraper_name, data)
            
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling POST {path}: {e}")
            self.send_error(500, str(e))

    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            if path.startswith("/api/watchlist/"):
                watchlist_id = path.split("/")[-1]
                self.handle_delete_watchlist(watchlist_id)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling DELETE {path}: {e}")
            self.send_error(500, str(e))

    def do_PATCH(self):
        """Handle PATCH requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            if path.startswith("/api/watchlist/"):
                watchlist_id = path.split("/")[-1]
                data = json.loads(body) if body else {}
                self.handle_update_watchlist(watchlist_id, data)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling PATCH {path}: {e}")
            self.send_error(500, str(e))

    # GET handlers
    def handle_get_wedges(self, query_params):
        """Get all wedges with optional filters"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM wedge_profiles"
            params = []

            # Apply filters
            if 'detector' in query_params:
                query += " WHERE detector_source = ?"
                params.append(query_params['detector'][0])

            if 'complexity' in query_params:
                if 'WHERE' in query:
                    query += " AND complexity = ?"
                else:
                    query += " WHERE complexity = ?"
                params.append(query_params['complexity'][0])

            query += " ORDER BY wedge_score DESC"

            # Apply limit/offset
            limit = int(query_params.get('limit', ['50'])[0])
            offset = int(query_params.get('offset', ['0'])[0])
            query += f" LIMIT {limit} OFFSET {offset}"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            wedges = []
            for row in rows:
                wedges.append(dict(row))

            self.send_json({"total": len(wedges), "wedges": wedges})
        finally:
            conn.close()

    def handle_get_wedge(self, wedge_id):
        """Get a single wedge by ID"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM wedge_profiles WHERE id = ?", (wedge_id,))
            row = cursor.fetchone()

            if row:
                self.send_json(dict(row))
            else:
                self.send_error(404, "Wedge not found")
        finally:
            conn.close()

    def handle_get_signals(self, query_params):
        """Get signals with optional filters"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM signals"
            params = []

            # Apply filters
            if 'source' in query_params:
                query += " WHERE source = ?"
                params.append(query_params['source'][0])

            if 'type' in query_params:
                if 'WHERE' in query:
                    query += " AND type = ?"
                else:
                    query += " WHERE type = ?"
                params.append(query_params['type'][0])

            query += " ORDER BY created_at DESC"

            # Apply limit/offset
            limit = int(query_params.get('limit', ['50'])[0])
            offset = int(query_params.get('offset', ['0'])[0])
            query += f" LIMIT {limit} OFFSET {offset}"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            signals = []
            for row in rows:
                signals.append(dict(row))

            self.send_json({"total": len(signals), "signals": signals})
        finally:
            conn.close()

    def handle_get_watchlist(self):
        """Get watchlist items"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT w.*, p.wedge_name, p.wedge_score
                FROM watchlist w
                LEFT JOIN wedge_profiles p ON w.wedge_id = p.id
                ORDER BY w.date_added DESC
            """)
            rows = cursor.fetchall()

            items = []
            for row in rows:
                items.append(dict(row))

            self.send_json({"items": items})
        finally:
            conn.close()

    def handle_get_scraper_metadata(self, scraper_name):
        """Get scraper metadata"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM scraper_metadata WHERE scraper_name = ?", (scraper_name,))
            row = cursor.fetchone()

            if row:
                self.send_json(dict(row))
            else:
                self.send_json({
                    "scraper_name": scraper_name,
                    "last_run": None,
                    "last_successful_run": None,
                    "error_count": 0,
                    "last_error": None,
                    "results_count": 0
                })
        finally:
            conn.close()

    # POST handlers
    def handle_add_watchlist(self, data):
        """Add item to watchlist"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO watchlist (wedge_id, notes, status)
                VALUES (?, ?, ?)
            """, (data.get('wedge_id'), data.get('notes', ''), 'watching'))

            conn.commit()
            self.send_json({"success": True, "id": cursor.lastrowid})
        finally:
            conn.close()

    def handle_update_scraper_metadata(self, scraper_name, data):
        """Update scraper metadata"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            # Check if exists
            cursor.execute("SELECT id FROM scraper_metadata WHERE scraper_name = ?", (scraper_name,))
            exists = cursor.fetchone()

            if exists:
                cursor.execute("""
                    UPDATE scraper_metadata
                    SET last_run = ?, last_successful_run = ?, error_count = ?, last_error = ?, results_count = ?
                    WHERE scraper_name = ?
                """, (
                    data.get('last_run'),
                    data.get('last_successful_run'),
                    data.get('error_count', 0),
                    data.get('last_error'),
                    data.get('results_count', 0),
                    scraper_name
                ))
            else:
                cursor.execute("""
                    INSERT INTO scraper_metadata (scraper_name, last_run, last_successful_run, error_count, last_error, results_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    scraper_name,
                    data.get('last_run'),
                    data.get('last_successful_run'),
                    data.get('error_count', 0),
                    data.get('last_error'),
                    data.get('results_count', 0)
                ))

            conn.commit()
            self.send_json({"success": True})
        finally:
            conn.close()

    # DELETE handlers
    def handle_delete_watchlist(self, watchlist_id):
        """Remove item from watchlist"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM watchlist WHERE id = ?", (watchlist_id,))
            conn.commit()
            self.send_json({"success": True})
        finally:
            conn.close()

    # PATCH handlers
    def handle_update_watchlist(self, watchlist_id, data):
        """Update watchlist item"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE watchlist
                SET notes = ?, status = ?
                WHERE id = ?
            """, (data.get('notes', ''), data.get('status', 'watching'), watchlist_id))

            conn.commit()
            self.send_json({"success": True})
        finally:
            conn.close()

    # Utility methods
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_error(self, code, message=""):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(format % args)


def run_server(port=5000):
    """Start the HTTP API server"""
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, DatabaseHandler)
    logger.info(f"API Server starting on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("API Server shutting down")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()
