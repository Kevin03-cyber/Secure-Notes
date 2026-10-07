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

- Create, view, and delete encrypted notes (the password is required to delete).
- Derive a separate encryption key for each note from its password.
- Failed-attempt lockout: 5 wrong passwords lock a note for 60 seconds, with a live countdown.
- Password strength meter on the create-note page, with server-side enforcement.
- Encryption info panel on each note page, showing how the note is protected.
- Store notes in a local SQLite database.
- Dark themed interface.

## How encryption works

1. The app generates a random 16-byte salt for each note.
2. It derives a 32-byte key from the note password and salt using PBKDF2-HMAC-SHA256 with 100,000 iterations.
3. The derived key is URL-safe Base64 encoded for Fernet.
4. Fernet encrypts the note content with AES-128-CBC and authenticates it with HMAC-SHA256 before it is saved in SQLite.
5. To unlock a note, the app derives the key again from the entered password and the saved salt. A wrong password fails authentication, so nothing is decrypted.

The salt is stored with the encrypted content. It is not a password and does not need to be secret.

**Metadata note:** The note title and creation time are stored unencrypted. Only the note content is encrypted. There is no password recovery, so a forgotten password means the note cannot be unlocked.

## Failed-attempt lockout

Each note tracks its own failed attempts. After 5 wrong passwords the note locks for 60 seconds. This applies to both unlocking and deleting. The server checks the lock before it tries to decrypt, so even the correct password is rejected while a note is locked.

The note page shows a live countdown and disables the form until the lock expires. The browser countdown is only a display aid; the server enforces the lock. The failure counter resets only after a correct password, so one more wrong guess after a lock expires locks the note again immediately.

## Password strength

The create-note page shows a live strength meter (Very weak to Strong) based on password length, character variety and a small list of common passwords. The server applies the same rules and rejects passwords below "Fair", so the check cannot be bypassed by skipping the browser.

## Encryption info panel

Each note page has a collapsible panel that explains the key derivation and encryption steps and shows that note's real salt, ciphertext size and ciphertext preview. It also lists what is not protected.

## Requirements

- Python 3.10 or newer
- Flask
- `cryptography`

## Run locally

1. Clone the repository and enter its directory:

```bash
   git clone https://github.com/Kevin03-cyber/secure-notes.git
   cd secure-notes
```

2. Create and activate a virtual environment.

   Windows PowerShell:

```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
```

   macOS or Linux:

```bash
   python3 -m venv venv
   source venv/bin/activate
```

3. Install dependencies:

```bash
   pip install flask cryptography
```

4. Start the app:

```bash
   python app.py
```

5. Open http://127.0.0.1:5002 in your browser.

The app creates its SQLite database locally when it starts.

## Project structure

```
secure-notes/
├── app.py
├── templates/
│   ├── index.html
│   ├── create.html
│   └── view.html
├── static/
│   └── style.css
└── README.md
```

## Security limitations

- This is an educational local project, not a production-ready secure storage service.
- The Flask development server and debug mode are for local development only. Do not expose them to the internet.
- Set a strong, private Flask `secret_key` before using the app beyond local development. Do not commit secrets to the repository.
- Note titles and creation times are visible in the SQLite database.
- The lockout protects only the running app. Someone who copies `notes.db` can guess passwords offline, where only password strength and the PBKDF2 iterations slow them down.
- Because the lockout is per note, someone with access to the app can deliberately lock a note to keep its owner out.
- Back up the database if you need to preserve notes. Forgotten note passwords cannot be recovered.

## Technologies

| Technology | Purpose |
|---|---|
| Python and Flask | Web application and routes |
| SQLite | Local note storage |
| Fernet (cryptography) | Encrypts and authenticates note content |
| PBKDF2-HMAC-SHA256 | Derives an encryption key from a password |
| HTML, CSS and JavaScript | User interface, countdown and strength meter |
