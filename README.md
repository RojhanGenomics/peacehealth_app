# PeaceHealth Insights

A multilingual (Persian / English / Arabic) web tool that lets people in conflict-affected communities anonymously self-report well-being indicators — using the validated PHQ-4 screener plus conflict-exposure and situational indicators — so that humanitarian and research organizations can better understand how conflict affects mental health.

**Live demo:** https://peacehealthapp-n74abyvxomzlztjnbbpbe7.streamlit.app/
**Methodology & research ethics document:** see `PeaceHealth_Methodology_Ethics.docx` in this repository.

---

## What this solution does

- Presents an informed-consent screen, then a short daily questionnaire (PHQ-4 well-being screener, conflict-exposure questions, displacement/access-to-basic-needs indicators, coping mechanisms).
- Supports Persian, English, and Arabic, with correct RTL/LTR layout and localized calendars/numerals.
- Stores responses with no name, phone number, or other identifying data — only a self-generated, non-identifying pseudonymous code (derived from two fixed, non-identifying personal facts) used to reduce duplicate submissions and enable longitudinal tracking of the same respondent over time.
- Includes a best-effort, privacy-preserving daily submission lock (browser-local, not server-side identity tracking).
- Provides a simple aggregate "Community Health Monitor" view (table + line chart) of recent responses.

## Technical architecture

| Layer | Technology |
|---|---|
| Application / UI | [Streamlit](https://streamlit.io) (Python) |
| Data storage | Google Sheets, accessed via [gspread](https://docs.gspread.org/) and a scoped Google Cloud service account |
| Hosting | Streamlit Community Cloud |
| PWA support | Static `manifest.json` + minimal service worker (`static/sw.js`), enabling "Add to Home Screen" on mobile |

The application is a single Python script (`app.py`). All data-storage logic is isolated in two functions — `append_response()` and `load_responses()` — so the Google Sheets backend can be swapped for any other database (e.g., PostgreSQL, SQLite) without touching the rest of the application.

## Repository structure

```
peacehealth_app/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                 # Enables static file serving (for PWA assets)
├── static/
│   ├── manifest.json               # PWA manifest
│   ├── sw.js                       # Minimal service worker
│   ├── icon-192.png / icon-512.png # App icons
├── PeaceHealth_Methodology_Ethics.docx  # Data methodology & research ethics statement
└── README.md                       # This file
```

## Running it yourself (for developers)

### Prerequisites
- Python 3.10+
- A Google Cloud project with the Google Sheets API and Google Drive API enabled
- A Google Cloud service account with edit access to a target Google Sheet (see the methodology document for the exact setup steps)

### Setup

```bash
git clone https://github.com/RojhanGenomics/peacehealth_app.git
cd peacehealth_app
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` (not committed to version control) with your service account credentials:

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

Create a Google Sheet named `PeaceHealth Data` and share it with the service account's `client_email` (Editor access).

Run the app locally:

```bash
streamlit run app.py
```

### Deploying

The app is designed to run unmodified on [Streamlit Community Cloud](https://streamlit.io/cloud): connect your fork of this repository, set the main file to `app.py`, and add the secrets above via the app's Settings → Secrets panel.

## Data handling, privacy, and ethics

Full details — what is collected, how consent is obtained, how anonymization and de-duplication work, current limitations, and the safeguards roadmap — are documented in `PeaceHealth_Methodology_Ethics.docx` in this repository. In summary: no names, phone numbers, or government IDs are ever collected; data minimization is applied throughout; and known limitations (e.g., the impossibility of perfectly preventing repeat submissions in a fully anonymous tool) are disclosed rather than hidden.

## License

See `LICENSE` in this repository.

## Contact

Dr. Mahdieh Rojhannezhad, Ph.D. in Genetics
Email: mahdiehrojhan@gmail.com
GitHub: [github.com/RojhanGenomics](https://github.com/RojhanGenomics)
Portfolio: [RojhanGenomics.github.io](https://RojhanGenomics.github.io)
