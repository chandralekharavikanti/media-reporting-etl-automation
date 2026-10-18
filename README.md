# Multi-Source Media Reporting ETL & Automation

**Portfolio demonstration using synthetic media data (not SME company data).**

## Business problem
A publisher receives disconnected digital traffic, print circulation, advertising bookings, and payment exports. This project consolidates four sources, validates records, loads SQLite, and generates daily, weekly, and monthly reporting tables.

## Architecture
Four source CSVs → Python validation and deduplication → SQLite warehouse → SQL reports + data-quality audit.

## Run
Python 3.10+; no third-party packages required.

```bash
python -m src.generate_sample_data
python -m src.pipeline
python -m unittest discover -s tests -v
```

## Definitions
Traffic measures sessions/pageviews; print circulation measures physical copies, not impressions. Booked revenue is not recognized revenue. Payments are simulated and not revenue recognition.

## Reporting
Daily and weekly traffic; monthly circulation and publication performance. All data and findings are synthetic.

## Portfolio scope
Pipeline source, tests, sample data, and report outputs are supplied in the project package.