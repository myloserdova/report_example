# Weekly Client Status Report Generator

A small Python tool that turns a project task list (CSV) into a weekly client status report, in Markdown and as a styled HTML page.

Built for a demo web project, **Bean & Brew Website** (a coffee shop site: design, development, SEO, SMM, QA, launch).

## What it does

From a plain task spreadsheet, the script works out:

- **Progress**: how many tasks are done, as a percentage
- **Risks and issues**: overdue tasks and tasks marked high risk
- **Coming up**: open tasks due in the next 7 days
- **Action needed from the client**: blockers waiting on the client or a third party

The HTML report has a progress bar, colour-coded status tags, a mobile-friendly layout, dark mode, and print styles, so it can be saved as a PDF straight from the browser.

## Files

| File | Purpose |
|---|---|
| `tasks.csv` | Input: one row per task (`Task, Phase, Owner, Status, Deadline, Risk, Comment`) |
| `report.py` | The generator |
| `report.md` | Generated Markdown report |
| `report.html` | Generated HTML report |

## Usage

Requires Python 3.8+ and no extra packages.

```bash
python3 report.py                      # uses tasks.csv and the demo date
python3 report.py --date 2026-11-17    # report "as of" a given date
python3 report.py --csv my_tasks.csv --out report.md --html report.html
```

## Weekly workflow

1. Update statuses and deadlines in `tasks.csv`.
2. Run `python3 report.py --date <today>`.
3. Send the client `report.html` (or print it to PDF).
