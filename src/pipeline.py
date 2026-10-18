import csv, sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = {
    "traffic": ("date", "publication", "sessions", "pageviews"),
    "circulation": ("issue_date", "publication", "circulation"),
    "bookings": ("campaign_id", "date", "publication", "product", "booked_revenue"),
    "payments": ("campaign_id", "paid_revenue"),
}
NUMERIC = {"sessions", "pageviews", "circulation", "booked_revenue", "paid_revenue"}

def validate(source, row):
    for field in SCHEMA[source]:
        if not row.get(field):
            return f"missing {field}"
        if field in NUMERIC:
            try:
                if float(row[field]) < 0:
                    return f"negative {field}"
            except ValueError:
                return f"invalid {field}"
        if field in {"date", "issue_date"}:
            try:
                datetime.strptime(row[field], "%Y-%m-%d")
            except ValueError:
                return f"invalid {field}"
    return None

def run(input_dir=None, report_dir=None):
    input_dir = Path(input_dir or ROOT / "data/sample_inputs")
    report_dir = Path(report_dir or ROOT / "reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(report_dir / "media.db")
    con.executescript("""
    DROP TABLE IF EXISTS traffic;
    DROP TABLE IF EXISTS circulation;
    DROP TABLE IF EXISTS bookings;
    DROP TABLE IF EXISTS payments;
    CREATE TABLE traffic(date TEXT, publication TEXT, sessions INTEGER, pageviews INTEGER, UNIQUE(date, publication));
    CREATE TABLE circulation(issue_date TEXT, publication TEXT, circulation INTEGER, UNIQUE(issue_date, publication));
    CREATE TABLE bookings(campaign_id TEXT PRIMARY KEY, date TEXT, publication TEXT, product TEXT, booked_revenue REAL);
    CREATE TABLE payments(campaign_id TEXT PRIMARY KEY, paid_revenue REAL);
    """)
    audit = []
    for table, columns in SCHEMA.items():
        seen = set()
        with (input_dir / (table + ".csv")).open(newline="") as handle:
            for line, row in enumerate(csv.DictReader(handle), 2):
                key = (row.get("date") or row.get("issue_date"), row.get("publication")) if table in ("traffic", "circulation") else row.get("campaign_id")
                issue = validate(table, row)
                if key in seen:
                    issue = issue or "duplicate business key"
                if issue:
                    audit.append((table, line, issue))
                    continue
                seen.add(key)
                try:
                    con.execute(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", [row[c] for c in columns])
                except sqlite3.IntegrityError:
                    audit.append((table, line, "database key conflict"))
    for (cid,) in con.execute("SELECT campaign_id FROM payments WHERE campaign_id NOT IN (SELECT campaign_id FROM bookings)"):
        audit.append(("payments", cid, "orphan payment"))
    con.commit()
    queries = {
        "daily_traffic.csv": "SELECT date, SUM(sessions) sessions, SUM(pageviews) pageviews FROM traffic GROUP BY date ORDER BY date",
        "weekly_traffic.csv": "SELECT strftime('%Y-W%W',date) week, SUM(sessions) sessions, SUM(pageviews) pageviews FROM traffic GROUP BY week ORDER BY week",
        "monthly_summary.csv": """SELECT substr(t.date,1,7) month, t.publication, SUM(t.sessions) sessions, SUM(t.pageviews) pageviews,
          COALESCE((SELECT SUM(b.booked_revenue) FROM bookings b WHERE substr(b.date,1,7)=substr(t.date,1,7) AND b.publication=t.publication),0) booked_revenue
          FROM traffic t GROUP BY month,t.publication ORDER BY month,t.publication""",
        "monthly_circulation.csv": "SELECT substr(issue_date,1,7) month, publication, SUM(circulation) circulation FROM circulation GROUP BY month,publication ORDER BY month,publication",
    }
    for filename, sql in queries.items():
        cursor = con.execute(sql)
        with (report_dir / filename).open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow([c[0] for c in cursor.description])
            writer.writerows(cursor.fetchall())
    with (report_dir / "quality_audit.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "row_or_id", "issue"])
        writer.writerows(audit)
    con.close()
    return len(audit)

if __name__ == "__main__":
    print("Data quality findings:", run())
