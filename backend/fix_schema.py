#!/usr/bin/env python3
"""
Fix schema errors by adding missing columns to tables.
"""
import sqlite3

c = sqlite3.connect('wie.db')

# Fix google_trends table
try:
    c.execute("ALTER TABLE google_trends ADD COLUMN is_breakout INTEGER DEFAULT 0")
    print("✓ Added is_breakout to google_trends")
except Exception as e:
    print(f"google_trends: {e}")

# Fix sec_filings table
try:
    c.execute("ALTER TABLE sec_filings ADD COLUMN industry_sic_code TEXT")
    print("✓ Added industry_sic_code to sec_filings")
except Exception as e:
    print(f"sec_filings: {e}")

# Fix job_postings table
try:
    c.execute("ALTER TABLE job_postings ADD COLUMN inferred_industry TEXT")
    print("✓ Added inferred_industry to job_postings")
except Exception as e:
    print(f"job_postings: {e}")

# Fix openvc_companies table
try:
    c.execute("ALTER TABLE openvc_companies ADD COLUMN country TEXT")
    print("✓ Added country to openvc_companies")
except Exception as e:
    print(f"openvc_companies: {e}")

c.commit()
print("Schema fixed.")
c.close()
