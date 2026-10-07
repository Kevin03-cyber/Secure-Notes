from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import base64
import time
import math
import re
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # Migrate an existing notes.db that predates these columns
    cols = [row['name'] for row in conn.execute('PRAGMA table_info(notes)')]
    if 'failed_attempts' not in cols:
        conn.execute('ALTER TABLE notes ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0')
    if 'locked_until' not in cols:
        conn.execute('ALTER TABLE notes ADD COLUMN locked_until INTEGER NOT NULL DEFAULT 0')

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

# ── Lockout helpers ───────────────────────────────────────
MAX_ATTEMPTS = 5
LOCK_SECONDS = 60

def lock_seconds_left(note):
    """Seconds remaining on a note's lock, 0 if it isn't locked."""
    return max(0, math.ceil(note['locked_until'] - time.time()))

def register_failure(conn, note_id):
    """Count a wrong password. Locks the note once the limit is reached.
    Returns the new failure count."""
    conn.execute(
        'UPDATE notes SET failed_attempts = failed_attempts + 1 WHERE id = ?',
        (note_id,)
    )
    attempts = conn.execute(
        'SELECT failed_attempts FROM notes WHERE id = ?', (note_id,)
    ).fetchone()['failed_attempts']

    if attempts >= MAX_ATTEMPTS:
        conn.execute(
            'UPDATE notes SET locked_until = ? WHERE id = ?',
            (int(time.time()) + LOCK_SECONDS, note_id)
        )
    conn.commit()
    return attempts

def reset_failures(conn, note_id):
    """Clear the counter and any lock after a correct password."""
    conn.execute(
        'UPDATE notes SET failed_attempts = 0, locked_until = 0 WHERE id = ?',
        (note_id,)
    )
    conn.commit()

    

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
            if password_score(password) < MIN_PASSWORD_SCORE:
                flash('Password is too weak. Use at least 8 characters mixing letters, '
                  'numbers and symbols, or a longer passphrase.', 'error')
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

    if not note:
        conn.close()
        flash('Note not found!', 'error')
        return redirect(url_for('index'))

    decrypted_content = None
    wrong_password = False

    if request.method == 'POST':
        seconds_left = lock_seconds_left(note)

        if seconds_left > 0:
            # Locked: reject BEFORE trying to decrypt
            flash(f'Too many failed attempts. Try again in {seconds_left} seconds.', 'error')
        else:
            password = request.form['password']
            decrypted_content = decrypt_note(note['encrypted_content'], password, note['salt'])

            if decrypted_content is None:
                wrong_password = True
                attempts = register_failure(conn, note_id)
                if attempts >= MAX_ATTEMPTS:
                    flash(f'Wrong password. Note locked for {LOCK_SECONDS} seconds.', 'error')
                else:
                    flash(f'Wrong password — {MAX_ATTEMPTS - attempts} attempts left.', 'error')
            else:
                reset_failures(conn, note_id)

           # Re-read the row so the lock status includes any failure just recorded
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    seconds_left = lock_seconds_left(note)
    conn.close()
    return render_template('view.html', note=note,
                           content=decrypted_content,
                           wrong_password=wrong_password,
                           seconds_left=seconds_left)

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete(note_id):
    password = request.form['password']

    conn = get_db()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()

    if not note:
        conn.close()
        flash('Note not found!', 'error')
        return redirect(url_for('index'))

    seconds_left = lock_seconds_left(note)
    if seconds_left > 0:
        conn.close()
        flash(f'Too many failed attempts. Try again in {seconds_left} seconds.', 'error')
        return redirect(url_for('view', note_id=note_id))

    decrypted = decrypt_note(note['encrypted_content'], password, note['salt'])

    if decrypted is None:
        attempts = register_failure(conn, note_id)
        conn.close()
        if attempts >= MAX_ATTEMPTS:
            flash(f'Wrong password. Note locked for {LOCK_SECONDS} seconds.', 'error')
        else:
            flash(f'Wrong password — {MAX_ATTEMPTS - attempts} attempts left.', 'error')
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