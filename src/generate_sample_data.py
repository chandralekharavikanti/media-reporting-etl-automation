"""Generate deterministic synthetic publisher exports; no real advertiser or audience data."""
import csv, random
from datetime import date, timedelta
from pathlib import Path
random.seed(42)
out = Path(__file__).resolve().parents[1] / "data/sample_inputs"
out.mkdir(parents=True, exist_ok=True)
def write(name, fields, rows):
    with (out / (name + ".csv")).open("w", newline="") as f:
        w=csv.writer(f); w.writerow(fields); w.writerows(rows)
pubs=["Manufacturing Today","Automation Review","Industry Insights"]
dates=[date(2025,1,1)+timedelta(days=i) for i in range(365)]
write("traffic",["date","publication","sessions","pageviews"],[(str(d),p,random.randint(200,1500),random.randint(1600,4000)) for d in dates for p in pubs])
write("circulation",["issue_date","publication","circulation"],[(f"2025-{m:02d}-01",p,random.randint(5000,25000)) for m in range(1,13) for p in pubs])
bookings=[(f"C{i:04d}",str(random.choice(dates)),random.choice(pubs),random.choice(["Print","Display","Newsletter","Sponsored Content"]),random.randint(1000,16000)) for i in range(1,301)]
write("bookings",["campaign_id","date","publication","product","booked_revenue"],bookings)
write("payments",["campaign_id","paid_revenue"],[(cid,round(amount*random.uniform(.6,1),2)) for cid,_,_,_,amount in bookings])
print("Synthetic sample inputs generated in",out)
