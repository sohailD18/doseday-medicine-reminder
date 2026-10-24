# DoseDay – Medicine Reminder & Adherence Tracker

A small healthcare web app that helps people track their daily medicines, plus a Python script that analyses their adherence from an exported CSV file.

**Live demo:** https://YOUR-USERNAME.github.io/doseday-medicine-reminder/

> Tip for reviewers: click **Load demo data** to see a full year of sample history instantly.

## Features (web app)
- Add medicines with a name, dosage, **several times per day** and an optional note
- Today's checklist: tick a dose to strike it through, with a live progress bar; the list scrolls when it gets long
- Edit and delete (the trash icon removes only the dose you click), with form validation, duplicate-name blocking and clear error messages
- **Adherence chart with three views**
  - **7 days:** bars for the last week
  - **Month:** pick any month and see every day of it
  - **Year:** see all 12 months; click a month to open its days
- **Click any past day** in the chart and the schedule list shows that day's doses (Taken / Missed)
- Export the full history as `adherence_log.csv`
- Dark / light mode (remembered between visits)
- Dose-time reminders on screen and, if allowed, as browser notifications (only while the page is open)
- Data stays in your browser (localStorage, up to ~400 days); nothing is sent to a server
- Responsive layout (two columns on desktop, one column on phones) and ARIA labels for accessibility

## Python adherence report
`adherence_report.py` reads the exported CSV and prints compliance totals, a daily (or monthly) breakdown, a per-medicine breakdown and short insights. It uses only the Python standard library (Python 3.8+).

```bash
python adherence_report.py adherence_log.csv                  # last 7 days (default)
python adherence_report.py adherence_log.csv --days 30        # last 30 days
python adherence_report.py adherence_log.csv --days 365       # last year, shown month by month
python adherence_report.py adherence_log.csv --month 2026-10  # one calendar month
```

Try it straight away with the included sample file:

```bash
python adherence_report.py sample_adherence_log.csv --days 30
```

### CSV format
```
date,medicine,dosage,scheduled_time,status
2026-10-23,Metformin,500 mg,08:00,Taken
2026-10-23,Metformin,500 mg,20:00,Missed
```
`status` is `Taken` or `Missed`. Doses scheduled for today that are not ticked yet are exported as `Missed`.

## Files
| File | Purpose |
|---|---|
| `index.html` | The complete web app (HTML, Tailwind CSS via CDN, vanilla JavaScript) |
| `adherence_report.py` | Python analytics script for the exported CSV |
| `sample_adherence_log.csv` | Example data (about 2 months) for trying the script |
| `README.md` | This file |

## How to run
Open `index.html` in any modern browser; there is no build step. Browser notifications need `https://` or `localhost`, so use the live link for them.

## Built with AI
Planned with Gemini and built iteratively with Claude, then tested manually. The prompts and revisions are in the prompt documentation submitted with this project.

## Limitations and next steps
- Reminders only fire while the page is open; a backend or mobile app would be needed for background alerts.
- No user accounts, by design: data stays on the device. A backend (for example Flask with a database) would be needed for sync across devices.
- Idea: connect the exported CSV to an automation tool to send weekly adherence summaries by email or WhatsApp.

*Disclaimer: This app is a reminder tool and does not constitute medical advice.*
