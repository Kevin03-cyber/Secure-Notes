from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken

app = Flask(__name__)
app.secret_key = 'secure_notes_secret_2026'

DATABASE = 'notes.db'

# ── Database ──────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            encrypted_content BLOB NOT NULL,
            salt BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ── Encryption helpers ────────────────────────────────────
def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_note(content, password):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(content.encode())
    return encrypted, salt

def decrypt_note(encrypted_content, password, salt):
    key = derive_key(password, salt)
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_content).decode()
    except InvalidToken:
        return None

# ── Routes ────────────────────────────────────────────────
@app.route('/')
def index():
    conn = get_db()
    notes = conn.execute(
        'SELECT id, title, created_at FROM notes ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return render_template('index.html', notes=notes)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        password = request.form['password']

        if not title or not content or not password:
            flash('All fields are required!', 'error')
            return render_template('create.html')

        encrypted_content, salt = encrypt_note(content, password)

        conn = get_db()
        conn.execute(
            'INSERT INTO notes (title, encrypted_content, salt) VALUES (?, ?, ?)',
            (title, encrypted_content, salt)
        )
        conn.commit()
        conn.close()

        flash('Note encrypted and saved!', 'success')
        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/view/<int:note_id>', methods=['GET', 'POST'])
def view(note_id):
    conn = get_db()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()

    if not note:
        flash('Note not found!', 'error')
        return redirect(url_for('index'))

    decrypted_content = None
    wrong_password = False

    if request.method == 'POST':
        password = request.form['password']
        decrypted_content = decrypt_note(note['encrypted_content'], password, note['salt'])
        if decrypted_content is None:
            wrong_password = True
            flash('Wrong password — note could not be decrypted.', 'error')

    return render_template('view.html', note=note,
                           content=decrypted_content,
                           wrong_password=wrong_password)

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete(note_id):
    password = request.form['password']

    conn = get_db()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()

    if not note:
        conn.close()
        flash('Note not found!', 'error')
        return redirect(url_for('index'))

    decrypted = decrypt_note(note['encrypted_content'], password, note['salt'])

    if decrypted is None:
        conn.close()
        flash('Wrong password — cannot delete this note.', 'error')
        return redirect(url_for('view', note_id=note_id))

    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()

    flash('Note deleted!', 'success')
    return redirect(url_for('index'))

# ── Run ───────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5002)