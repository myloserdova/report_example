"""Weekly client status report generator (demo project: Bean & Brew website).

Usage:
    python report.py                      # uses tasks.csv and the demo date
    python report.py --date 2026-11-10    # set the "today" date
    python report.py --csv my_tasks.csv --out report.md --html report.html
"""
import argparse
import csv
import html
from datetime import date, datetime, timedelta

PROJECT = "Bean & Brew Website"
DEFAULT_DATE = "2026-11-10"  # fixed so the demo output is reproducible
UPCOMING_DAYS = 7


def load_tasks(path):
    with open(path, newline="", encoding="utf-8") as f:
        tasks = list(csv.DictReader(f))
    for t in tasks:
        t["Deadline"] = datetime.strptime(t["Deadline"], "%Y-%m-%d").date()
    return tasks


def analyze(tasks, today):
    open_tasks = [t for t in tasks if t["Status"] != "Done"]
    done = len(tasks) - len(open_tasks)
    return {
        "total": len(tasks),
        "done": done,
        "percent": round(done / len(tasks) * 100),
        "overdue": [t for t in open_tasks if t["Deadline"] < today],
        "upcoming": sorted(
            [t for t in open_tasks
             if today <= t["Deadline"] <= today + timedelta(days=UPCOMING_DAYS)],
            key=lambda t: t["Deadline"]),
        "high_risk": [t for t in open_tasks if t["Risk"] == "High"],
        "blockers": [t for t in open_tasks
                     if t["Comment"] and t["Status"] in ("Delayed", "In progress")
                     and t["Risk"] in ("High", "Medium")],
    }


def fmt(d):
    return d.strftime("%d %b")


def client_asks(m):
    return [t for t in m["blockers"] if "client" in t["Comment"].lower()
            or "pending" in t["Comment"].lower()]


def build_report(m, today):
    lines = [
        f"# Weekly Status Report: {PROJECT}",
        f"**Report date:** {today:%d %B %Y}",
        "",
        "## Progress",
        f"{m['done']} of {m['total']} tasks are complete (**{m['percent']}%**).",
        "",
    ]

    lines.append("## Risks and issues")
    if m["overdue"]:
        for t in m["overdue"]:
            days = (today - t["Deadline"]).days
            lines.append(f"- **Overdue:** {t['Task']} ({t['Owner']}), "
                         f"{days} day(s) past the {fmt(t['Deadline'])} deadline. {t['Comment']}")
    for t in m["high_risk"]:
        if t not in m["overdue"]:
            lines.append(f"- **High risk:** {t['Task']} ({t['Owner']}), "
                         f"due {fmt(t['Deadline'])}. {t['Comment']}")
    if not (m["overdue"] or m["high_risk"]):
        lines.append("- No critical risks this week.")
    lines.append("")

    lines.append("## Coming up in the next 7 days")
    for t in m["upcoming"]:
        lines.append(f"- {fmt(t['Deadline'])}: {t['Task']} ({t['Owner']}, {t['Status']})")
    if not m["upcoming"]:
        lines.append("- Nothing due this week.")
    lines.append("")

    lines.append("## Action needed from the client")
    asks = client_asks(m)
    for t in asks:
        lines.append(f"- {t['Comment']} (blocks: {t['Task']})")
    if not asks:
        lines.append("- No action needed at this time.")
    lines.append("")
    return "\n".join(lines)


HTML_STYLE = """
:root {
  --bg: #f4f1ec; --card: #ffffff; --text: #2b2420; --muted: #7a6e66;
  --line: #e7e1d9; --accent: #8a5a3b; --track: #efe8df;
  --red: #c0392b; --red-bg: #fbecea; --amber: #b9770e; --amber-bg: #fdf3e1;
  --green: #2e7d4f; --blue: #2c6e9b; --blue-bg: #e8f1f8; --grey-bg: #f0eeeb;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1c1916; --card: #26221e; --text: #f0ebe5; --muted: #a89c92;
    --line: #3a342e; --accent: #d39b72; --track: #3a342e;
    --red: #ef7b6c; --red-bg: #3d2420; --amber: #f0b54d; --amber-bg: #3b2f18;
    --green: #6cc795; --blue: #7ab8e0; --blue-bg: #1f3040; --grey-bg: #34302b;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
main { max-width: 760px; margin: 0 auto; padding: 40px 16px 64px; }
header { margin-bottom: 28px; }
.eyebrow { color: var(--accent); font-weight: 600; font-size: 13px;
  letter-spacing: .08em; text-transform: uppercase; }
h1 { margin: 6px 0 4px; font-size: 30px; line-height: 1.2; }
.date { color: var(--muted); }
section { background: var(--card); border: 1px solid var(--line);
  border-radius: 14px; padding: 22px 24px; margin-bottom: 16px; }
h2 { margin: 0 0 14px; font-size: 17px; }
.progress-row { display: flex; align-items: baseline; gap: 12px; margin-bottom: 10px; }
.big { font-size: 40px; font-weight: 700; line-height: 1; }
.bar { height: 10px; background: var(--track); border-radius: 99px; overflow: hidden; }
.bar > div { height: 100%; background: var(--green); border-radius: 99px; }
ul { list-style: none; margin: 0; padding: 0; }
li { padding: 12px 0; border-top: 1px solid var(--line); }
li:first-child { border-top: 0; padding-top: 0; }
li:last-child { padding-bottom: 0; }
.task { font-weight: 600; }
.meta { color: var(--muted); font-size: 14px; }
.note { margin-top: 4px; font-size: 14px; }
.tag { display: inline-block; font-size: 12px; font-weight: 600; padding: 2px 8px;
  border-radius: 99px; margin-right: 6px; vertical-align: 1px; }
.tag.red { color: var(--red); background: var(--red-bg); }
.tag.amber { color: var(--amber); background: var(--amber-bg); }
.tag.blue { color: var(--blue); background: var(--blue-bg); }
.tag.grey { color: var(--muted); background: var(--grey-bg); }
.upcoming li { display: flex; gap: 16px; align-items: baseline; }
.day { flex: 0 0 56px; font-weight: 700; color: var(--accent); }
.empty { color: var(--muted); }
@media print { body { background: #fff; } section { break-inside: avoid; } }
"""

STATUS_TAG = {"In progress": "blue", "Delayed": "red", "Not started": "grey"}


def build_html(m, today):
    e = html.escape
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        f"<title>Status Report: {e(PROJECT)}</title><style>{HTML_STYLE}</style></head><body><main>",
        "<header><div class='eyebrow'>Weekly status report</div>",
        f"<h1>{e(PROJECT)}</h1><div class='date'>{today:%d %B %Y}</div></header>",
        "<section><h2>Progress</h2><div class='progress-row'>",
        f"<span class='big'>{m['percent']}%</span>",
        f"<span class='meta'>{m['done']} of {m['total']} tasks complete</span></div>",
        f"<div class='bar'><div style='width:{m['percent']}%'></div></div></section>",
    ]

    parts.append("<section><h2>Risks and issues</h2><ul>")
    for t in m["overdue"]:
        days = (today - t["Deadline"]).days
        parts.append(
            f"<li><span class='tag red'>Overdue {days}d</span><span class='task'>{e(t['Task'])}</span>"
            f"<div class='meta'>{e(t['Owner'])} · deadline {fmt(t['Deadline'])}</div>"
            f"<div class='note'>{e(t['Comment'])}</div></li>")
    for t in m["high_risk"]:
        if t not in m["overdue"]:
            parts.append(
                f"<li><span class='tag amber'>High risk</span><span class='task'>{e(t['Task'])}</span>"
                f"<div class='meta'>{e(t['Owner'])} · due {fmt(t['Deadline'])}</div>"
                f"<div class='note'>{e(t['Comment'])}</div></li>")
    if not (m["overdue"] or m["high_risk"]):
        parts.append("<li class='empty'>No critical risks this week.</li>")
    parts.append("</ul></section>")

    parts.append(f"<section class='upcoming'><h2>Coming up in the next {UPCOMING_DAYS} days</h2><ul>")
    for t in m["upcoming"]:
        tag = STATUS_TAG.get(t["Status"], "grey")
        parts.append(
            f"<li><span class='day'>{fmt(t['Deadline'])}</span><div>"
            f"<span class='task'>{e(t['Task'])}</span>"
            f"<div class='meta'><span class='tag {tag}'>{e(t['Status'])}</span>{e(t['Owner'])}</div>"
            "</div></li>")
    if not m["upcoming"]:
        parts.append("<li class='empty'>Nothing due this week.</li>")
    parts.append("</ul></section>")

    parts.append("<section><h2>Action needed from the client</h2><ul>")
    asks = client_asks(m)
    for t in asks:
        parts.append(f"<li><span class='task'>{e(t['Comment'])}</span>"
                     f"<div class='meta'>Blocks: {e(t['Task'])}</div></li>")
    if not asks:
        parts.append("<li class='empty'>No action needed at this time.</li>")
    parts.append("</ul></section></main></body></html>")
    return "\n".join(parts)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="tasks.csv")
    p.add_argument("--out", default="report.md")
    p.add_argument("--html", default="report.html")
    p.add_argument("--date", default=DEFAULT_DATE)
    args = p.parse_args()

    today = datetime.strptime(args.date, "%Y-%m-%d").date()
    metrics = analyze(load_tasks(args.csv), today)
    report = build_report(metrics, today)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)
    with open(args.html, "w", encoding="utf-8") as f:
        f.write(build_html(metrics, today))
    print(report)
    print(f"\nHTML report saved to {args.html}")


if __name__ == "__main__":
    main()
