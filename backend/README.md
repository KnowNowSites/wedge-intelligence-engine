# WIE Backend - Python Modules

This directory contains all Python backend modules for data scraping, detection, and analysis.

## Directory Structure

```
backend/
├── scrapers/           # 9 data scraper modules
├── detectors/          # 7 wedge detector modules
├── database.py         # SQLite schema and initialization
├── config.py           # Environment configuration
├── utils.py            # Shared utilities (retry, logging, delays)
├── scoring.py          # Wedge scoring formula
├── scheduler.py        # APScheduler setup and job management
├── wedge_profile_generator.py  # Profile generation and filtering
└── main.py             # FastAPI entry point (optional)
```

## Core Modules

### database.py
Manages SQLite database schema and initialization.

**Key Functions:**
- `init_db()` - Create all 11 tables if they don't exist
- `get_db()` - Get database connection
- `insert_signal()` - Save scraped signal to appropriate table
- `get_candidates()` - Query wedge candidates

**Tables:**
- Signal tables: `reddit_posts`, `hn_posts`, `app_store_reviews`, etc.
- Analysis tables: `wedge_candidates`, `wedge_profiles`, `watchlist`
- Metadata: `scraper_metadata`

### config.py
Environment variable loading and validation.

**Key Functions:**
- `load_config()` - Load .env file and validate required vars
- `get_config()` - Get config singleton

**Environment Variables:**
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` - Optional Reddit OAuth
- `PRODUCTHUNT_API_TOKEN` - Optional Product Hunt API token
- `DATABASE_URL` - SQLite connection string (default: `wie.db`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

### utils.py
Shared utilities for all scrapers and detectors.

**Key Functions:**
- `safe_scraper_execution()` - Decorator for error handling
- `retry_with_backoff()` - Exponential backoff retry logic
- `random_delay()` - Randomized 2-5 second delays
- `setup_logging()` - Configure structured logging
- `sentiment_score()` - Simple sentiment analysis

### scoring.py
Wedge scoring formula and helper functions.

**Key Functions:**
- `calculate_wedge_score()` - Main scoring formula
- `estimate_mrr_timeline()` - Estimate months to $10k and $100k MRR
- `classify_enterprise_value()` - Classify as low/medium/high/very_high
- `classify_complexity()` - Classify as low/medium/high

**Formula:**
```
score = (pain × spend × growth × expandability × distribution) 
        ÷ (competition × capital × regulatory)
```

### scheduler.py
APScheduler setup and background job management.

**Key Functions:**
- `start_scheduler()` - Initialize and start APScheduler
- `schedule_scraper()` - Add scraper to schedule
- `run_scraper()` - Execute scraper and run detectors after
- `get_scheduler_status()` - Return status of all jobs

**Scraper Cadences:**
- Reddit: 24h
- Google Trends: 48h
- App Store: 48h
- Play Store: 48h
- Product Hunt: 24h
- Y Combinator: 72h
- SEC EDGAR: 72h
- Hacker News: 24h
- Job Postings: 48h
- OpenVC: 72h

### wedge_profile_generator.py
Auto-generate profiles for high-scoring wedges.

**Key Functions:**
- `generate_profiles()` - Create profiles for candidates scoring > 15.0
- `apply_rejection_filters()` - Filter out low-quality candidates
- `generate_expansion_map()` - Create adjacent market opportunities

**Rejection Filters:**
1. Duplicate detection (same market, different source)
2. Saturation check (too many competitors)
3. Market size validation (minimum addressable market)
4. Trend momentum check (declining trends filtered)
5. Regulatory risk assessment

## Scraper Modules

All scrapers follow the same pattern:

```python
@safe_scraper_execution
def run():
    """Main scraper function"""
    results = []
    # Fetch data from source
    # Parse and extract signals
    # Save to database
    return results
```

### reddit_scraper.py
Extracts pain signals from targeted subreddits using Playwright.

**Subreddits Monitored:**
- r/entrepreneur - Business pain points
- r/startups - Startup challenges
- r/SaaS - SaaS-specific issues
- r/webdev - Development problems
- r/business - General business issues

**Output:** `reddit_posts` table

### google_trends_scraper.py
Detects rising keywords in B2B/vertical SaaS using pytrends.

**Keywords Monitored:**
- SaaS vertical keywords (e.g., "construction management", "healthcare compliance")
- Automation keywords
- Integration keywords

**Output:** `google_trends` table

### app_store_scraper.py
Scrapes 1-2 star App Store reviews indicating unmet needs.

**Categories:** Business, Productivity, Finance, Healthcare

**Output:** `app_store_reviews` table

### play_store_scraper.py
Scrapes 1-2 star Google Play Store reviews.

**Categories:** Business, Productivity, Finance, Healthcare

**Output:** `play_store_reviews` table

### producthunt_scraper.py
Fetches new product launches from last 90 days via GraphQL API.

**Data Collected:**
- Product name, description, category
- Upvotes, comments, launch date
- Maker information

**Output:** `producthunt_launches` table

### yc_scraper.py
Extracts Y Combinator companies by batch and vertical using BeautifulSoup.

**Data Collected:**
- Company name, description, batch
- Vertical/industry
- Founding date

**Output:** `yc_companies` table

### sec_edgar_scraper.py
Finds regulatory and market signals in SEC EDGAR filings.

**Signals Detected:**
- Regulatory changes
- Market disruption mentions
- Compliance requirements

**Output:** `sec_filings` table

### hackernews_scraper.py
Extracts problem statements from Hacker News using Algolia API.

**Queries:**
- "Why doesn't someone build..."
- "This is broken..."
- "Needs automation..."

**Output:** `hn_posts` table

### job_postings_scraper.py
Detects manual job titles indicating scaling gaps.

**Job Titles Monitored:**
- "Data entry specialist"
- "Manual coordinator"
- "Process analyst"
- "Compliance officer"

**Sources:** Indeed RSS, RemoteOK API

**Output:** `job_postings` table

### openvc_scraper.py
Gathers startup funding data (free Crunchbase alternative).

**Data Collected:**
- Company name, funding amount
- Industry, stage
- Founding date

**Output:** `openvc_companies` table

### amazon_reviews_scraper.py
⏸️ **TODO** - Blocked by expensive residential proxy requirements.

### g2_scraper.py
⏸️ **TODO** - Blocked by aggressive bot protection.

## Detector Modules

All detectors follow the same pattern:

```python
def detect(db):
    """Main detector function"""
    candidates = []
    # Query relevant signal tables
    # Apply detection logic
    # Write to wedge_candidates table
    return candidates
```

### pain_signal.py
Detects high-volume complaints and negative sentiment.

**Logic:**
- Count 1-2 star reviews per product/company
- Identify keywords indicating pain (broken, impossible, frustrating)
- Cluster by problem domain
- Score by volume and sentiment intensity

**Output:** `wedge_candidates` with `detector_source='pain_signal'`

### incumbent_weakness.py
Groups complaints by company/software to identify weak incumbents.

**Logic:**
- Aggregate complaints per incumbent
- Calculate complaint density (complaints per user)
- Identify products with 10+ complaints
- Score by weakness intensity

**Output:** `wedge_candidates` with `detector_source='incumbent_weakness'`

### emerging_category.py
Finds fragmented markets with multiple players.

**Logic:**
- Identify YC/OpenVC companies in same vertical
- Count unique companies per vertical
- Filter for 5+ players (fragmentation indicator)
- Score by market size and growth

**Output:** `wedge_candidates` with `detector_source='emerging_category'`

### distribution_gap.py
Finds rising keywords with no clear SaaS leader.

**Logic:**
- Get trending keywords from Google Trends
- Search Product Hunt for related products
- Identify keywords with <3 related products
- Score by trend momentum

**Output:** `wedge_candidates` with `detector_source='distribution_gap'`

### regulation_change.py
Clusters regulatory mentions across sources.

**Logic:**
- Extract regulatory keywords from SEC filings
- Find matching Reddit/HN discussions
- Cluster by regulation type
- Score by compliance urgency

**Output:** `wedge_candidates` with `detector_source='regulation_change'`

### margin_expansion.py
Identifies high-margin manual service opportunities.

**Logic:**
- Count job postings for manual roles
- Estimate hourly cost (salary ÷ 2000 hours)
- Identify high-margin opportunities (>$50/hr)
- Score by job volume and margin

**Output:** `wedge_candidates` with `detector_source='margin_expansion'`

### geographic_wedge.py
Finds geographic expansion opportunities.

**Logic:**
- Identify YC/OpenVC companies by geography
- Find US-only companies with strong signals
- Identify underserved international markets
- Score by market size and growth

**Output:** `wedge_candidates` with `detector_source='geographic_wedge'`

## Running Modules Manually

### Run a Single Scraper
```bash
python -m backend.scrapers.reddit_scraper
```

### Run a Single Detector
```bash
python -m backend.detectors.pain_signal
```

### Run the Scheduler
```bash
python -m backend.scheduler
```

### Generate Profiles
```bash
python -m backend.wedge_profile_generator
```

## Error Handling

All scrapers implement:
- **Retry logic**: 3 retries with exponential backoff (1s, 2s, 4s)
- **Timeout**: 30-second timeout per request
- **Graceful degradation**: Missing credentials → skip scraper, log warning
- **Isolated failures**: One scraper failure doesn't crash others

## Logging

Logs are written to `.manus-logs/devserver.log` with format:
```
[2026-05-11T14:39:24.495Z] [scrapers.reddit] Starting scraper...
[2026-05-11T14:39:45.123Z] [scrapers.reddit] Fetched 42 posts
[2026-05-11T14:39:46.456Z] [scrapers.reddit] Saved 38 signals to database
```

## Performance Tips

1. **Parallel Execution**: Scrapers run in parallel via APScheduler
2. **Database Indexing**: Indexes on `wedge_score`, `detector_source`, `date_created`
3. **Caching**: Consider Redis for frequently accessed data
4. **Batch Inserts**: Use batch insert for large result sets

## Adding a New Scraper

1. Create `backend/scrapers/newscraper_scraper.py`
2. Implement `run()` function
3. Add to `VALID_SCRAPERS` in `server/routers/scrapers.ts`
4. Update `.env.example` with credentials
5. Add to scheduler in `backend/scheduler.py`

Example:
```python
from backend.utils import safe_scraper_execution, random_delay
from backend.database import insert_signal

@safe_scraper_execution
def run():
    results = []
    # Fetch data
    for item in fetch_data():
        signal = {
            'title': item['title'],
            'description': item['description'],
            'source_url': item['url'],
            'date_created': item['date'],
        }
        insert_signal('newscraper_posts', signal)
        results.append(signal)
        random_delay()
    return results

if __name__ == '__main__':
    run()
```

## Testing

```bash
# Test database initialization
python -c "from backend.database import init_db; init_db()"

# Test a scraper
python -m backend.scrapers.reddit_scraper

# Test a detector
python -m backend.detectors.pain_signal

# Check database
sqlite3 wie.db "SELECT COUNT(*) FROM wedge_profiles;"
```

## Dependencies

See `requirements.txt` for full list. Key packages:
- `playwright` - Browser automation for Reddit
- `pytrends` - Google Trends scraping
- `app-store-scraper` - App Store reviews
- `google-play-scraper` - Play Store reviews
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `apscheduler` - Job scheduling
- `sqlite3` - Database (built-in)

---

**For integration with Express backend, see INTEGRATION_GUIDE.md**
