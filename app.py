from flask import Flask, jsonify, request, g
from datetime import datetime
import logging
import os
import sqlite3

app = Flask(__name__)

# Paths
LOG_DIR = "/app/logs"
DATA_DIR = "/app/data"
DB_PATH = os.path.join(DATA_DIR, "books.db")

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=f"{LOG_DIR}/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_db():
    """Open a database connection and store it on flask.g"""
    if 'db' not in g:
        conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create the books table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            year INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


app.teardown_appcontext(close_db)

# Initialize DB on startup
try:
    init_db()
except Exception:
    logging.exception("Failed to initialize the database")


@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Books API",
        "version": "1.0",
        "endpoints": {
            "GET /books": "List all books",
            "GET /books/<id>": "Get a specific book",
            "POST /books": "Add a new book",
            "PUT /books/<id>": "Update a book",
            "DELETE /books/<id>": "Delete a book",
            "GET /health": "Health check"
        }
    })


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/books', methods=['GET'])
def get_books():
    logging.info("GET /books endpoint called")
    db = get_db()
    cur = db.execute('SELECT id, title, author, year FROM books')
    rows = cur.fetchall()
    books = [dict(r) for r in rows]
    return jsonify({"books": books, "count": len(books)})


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    db = get_db()
    cur = db.execute('SELECT id, title, author, year FROM books WHERE id = ?', (book_id,))
    row = cur.fetchone()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Book not found"}), 404


@app.route('/books', methods=['POST'])
def add_book():
    if not request.json or not all(k in request.json for k in ['title', 'author', 'year']):
        return jsonify({"error": "Missing required fields"}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute(
        'INSERT INTO books (title, author, year) VALUES (?, ?, ?)',
        (request.json['title'], request.json['author'], request.json['year'])
    )
    db.commit()
    new_id = cur.lastrowid
    cur = db.execute('SELECT id, title, author, year FROM books WHERE id = ?', (new_id,))
    row = cur.fetchone()
    return jsonify(dict(row)), 201


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    db = get_db()
    cur = db.execute('SELECT id FROM books WHERE id = ?', (book_id,))
    if not cur.fetchone():
        return jsonify({"error": "Book not found"}), 404

    fields = {k: v for k, v in request.json.items() if k in ['title', 'author', 'year']} if request.json else {}
    if not fields:
        cur = db.execute('SELECT id, title, author, year FROM books WHERE id = ?', (book_id,))
        return jsonify(dict(cur.fetchone()))

    cols = ', '.join([f"{k} = ?" for k in fields.keys()])
    params = list(fields.values()) + [book_id]
    db.execute(f'UPDATE books SET {cols} WHERE id = ?', params)
    db.commit()
    cur = db.execute('SELECT id, title, author, year FROM books WHERE id = ?', (book_id,))
    return jsonify(dict(cur.fetchone()))


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    db = get_db()
    cur = db.execute('SELECT id FROM books WHERE id = ?', (book_id,))
    if not cur.fetchone():
        return jsonify({"error": "Book not found"}), 404

    db.execute('DELETE FROM books WHERE id = ?', (book_id,))
    db.commit()
    return jsonify({"message": "Book deleted successfully"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)