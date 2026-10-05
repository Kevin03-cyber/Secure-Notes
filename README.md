# 🔐 Secure Notes App

A web application that lets users create, store, and retrieve private notes protected by **real encryption**. Built with Python and Flask as part of a cyber security portfolio.

---

## 📸 Screenshots

### Home Page
<img width="1907" height="978" alt="Screenshot 2026-10-05 222155" src="https://github.com/user-attachments/assets/61efd543-ed4f-4b39-8113-3761bbbfcc3a" />

### Create a Note
<img width="1892" height="975" alt="Screenshot 2026-10-05 221819" src="https://github.com/user-attachments/assets/bba5e447-c630-487c-b583-9517cc6803af" />


### Unlock a Note
<img width="1917" height="1078" alt="Screenshot 2026-10-05 221925" src="https://github.com/user-attachments/assets/9c88eba2-514d-414d-ae27-7ab999f7f2de" />
<img width="1900" height="976" alt="Screenshot 2026-10-05 222039" src="https://github.com/user-attachments/assets/67ce1715-52f3-41a9-b6bf-e75ee98bf9eb" />


---

## 🛡️ How the Security Works

- Notes are encrypted using **Fernet symmetric encryption** from Python's `cryptography` library
- The encryption key is **derived from your password** using **PBKDF2 with SHA-256** (100,000 iterations)
- A unique **random salt** is generated for every note — meaning two notes with the same password still encrypt differently
- The raw note content is **never stored in plain text** — only unreadable encrypted bytes are saved
- If you enter the wrong password, the note **cannot be decrypted** — there is no backdoor

---

## ✨ Features

- ✅ Create encrypted notes with a title, content, and password
- ✅ View notes by entering the correct password
- ✅ Wrong password = note stays locked
- ✅ Delete notes (password required to confirm)
- ✅ Dark themed UI
- ✅ SQLite database for local storage

---

## 🚀 How to Run Locally

**1. Clone the repository**
```
git clone https://github.com/Kevin03-cyber/secure-notes.git
cd secure-notes
```

**2. Create and activate a virtual environment**
```
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```
pip install flask cryptography
```

**4. Run the app**
```
python app.py
```

**5. Open your browser and go to:**
```
http://127.0.0.1:5002
```

---

## 🗂️ Project Structure

```
secure-notes/
│
├── app.py              # Main Flask app with encryption logic
├── templates/
│   ├── index.html      # Home page — lists all notes
│   ├── create.html     # Create a new encrypted note
│   └── view.html       # Unlock and view a note
├── static/
│   └── style.css       # Dark theme styling
└── README.md
```

---

## 🔧 Technologies Used

| Technology | Purpose |
|---|---|
| Python + Flask | Web framework |
| Cryptography (Fernet) | Note encryption/decryption |
| PBKDF2 + SHA-256 | Key derivation from password |
| SQLite | Local database storage |
| HTML + CSS | Dark themed front end |

---

## ⚠️ Important Note

This app is built for **educational and portfolio purposes**. Notes are stored locally on your machine. Do not use this to store real sensitive information in a production environment.

---

*Built as part of a cyber security student portfolio.*
