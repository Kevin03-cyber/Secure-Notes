# Secure Notes

A local Flask and SQLite application for creating and unlocking password-protected notes. Note content is encrypted before it is saved.

> **Educational project:** This application is intended for learning and portfolio use. Review the security limitations below before storing sensitive information.

## Screenshots

### Home page
<img width="1667" height="892" alt="image" src="https://github.com/user-attachments/assets/b91722f2-0f0a-4343-b9ab-5a77fbea0443" />

### Create a note
<img width="1476" height="937" alt="image" src="https://github.com/user-attachments/assets/faaab8dc-b990-4ed9-adb1-e64446582868" />

### Unlock a note
<img width="1646" height="888" alt="image" src="https://github.com/user-attachments/assets/6765f703-4284-4e15-8309-e836906def9b" />

<img width="1615" height="900" alt="image" src="https://github.com/user-attachments/assets/1eccefae-7cec-4a57-ad36-c2b87ab45670" />


## Features

- Create, view, and delete encrypted notes.
- Derive an encryption key from each note's password.
- Temporarily lock note unlock attempts after repeated incorrect passwords.
- Show an encryption information panel on the create-note page.
- Store notes in a local SQLite database.
- Use a dark themed interface.

A password strength meter is planned but is not included yet.

## How encryption works

1. The app generates a random 16-byte salt for each note.
2. It derives a 32-byte key from the note password and salt using PBKDF2-HMAC-SHA256 with 100,000 iterations.
3. The derived key is URL-safe Base64 encoded for Fernet.
4. Fernet encrypts and authenticates the note content before it is saved in SQLite.
5. To unlock a note, the app derives the key again from the entered password and saved salt.

The salt is stored with the encrypted content. It is not a password and does not need to be secret.

**Metadata note:** The note title and creation time are stored unencrypted. Only the note content is encrypted. There is no password recovery, so a forgotten password means the note cannot be unlocked.

## Failed-attempt lockout

After repeated incorrect passwords, the app temporarily prevents further unlock attempts for that note. The unlock page displays the remaining lockout time and disables the password field and button until the lockout ends. The server must enforce the lockout; the page countdown is only a display aid.

## Requirements

- Python 3.10 or newer
- Flask
- `cryptography`

## Run locally

1. Clone the repository and enter its directory:

   ```bash
   git clone https://github.com/Kevin03-cyber/secure-notes.git
   cd secure-notes
2. Create and activate a virtual environment.
   Windows PowerShell:
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   macOS or Linux:
   python3 -m venv venv
   source venv/bin/activate
3. Install dependencies:
   pip install flask cryptography
4. Start the app:
   python app.py
5. Open http://127.0.0.1:5002 in your browser.
The app creates its SQLite database locally when it starts.
Project structure
secure-notes/
├── app.py
├── templates/
│   ├── index.html
│   ├── create.html
│   └── view.html
├── static/
│   └── style.css
├── screenshots/
│   ├── home.png
│   ├── create-note.png
│   └── unlock-note.png
└── README.md


# Security limitations
- This is an educational local project, not a production-ready secure storage service.
- The Flask development server and debug mode are for local development only. Do not expose them to the internet.
- Set a strong, private Flask secret_key before using the app beyond local development. Do not commit secrets to the repository.
- Note titles and creation times are visible in the SQLite database.
- A browser countdown alone does not protect against password guessing; the server must reject unlock attempts while a lockout is active.
- Anyone with access to the app or its database files may be able to interfere with stored notes or metadata.
- Back up the database if you need to preserve notes. Forgotten note passwords cannot be recovered.
Technologies
Technology	Purpose
Python and Flask	Web application and routes
SQLite	Local note storage
Fernet (cryptography)	Encrypts and authenticates note content
PBKDF2-HMAC-SHA256	Derives an encryption key from a password
HTML and CSS	User interface


Planned
- Add a password strength meter to the create-note form.
