# Wedge Intelligence Engine (WIE)

A full-stack market wedge detection system that automatically scrapes signals from 9 data sources, detects strategic opportunities using 7 detectors, scores them with a proprietary formula, and surfaces everything through an interactive React dashboard.

**Launch with a single command:** `make run` or `docker-compose up`

## 🎯 What is a Market Wedge?

A **market wedge** is an underserved customer segment or use case where:
- **Pain is acute** (customers actively complaining)
- **Spend is concentrated** (clear budget allocation)
- **Growth is accelerating** (rising demand signals)
- **Distribution is fragmented** (no clear SaaS leader)
- **Competition is weak** (low incumbent strength)

WIE identifies these opportunities by analyzing signals across Reddit, Hacker News, App Store reviews, Google Trends, Product Hunt, SEC filings, job postings, and more.

## 🚀 Quick Start

### Prerequisites
- Node.js 22+
- Python 3.11+
- Docker & Docker Compose (optional)

### Local Development

```bash
# Clone and setup
cd /home/ubuntu/wie

# Install dependencies
pnpm install
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to add optional API credentials (Reddit, Product Hunt, etc.)

# Start everything
make run
```

This starts:
- **Express backend** on http://localhost:3000
- **React frontend** with HMR
- **SQLite database** (wie.db)
- **APScheduler** (background scraper jobs)

### Docker

```bash
docker-compose up
```

Access the dashboard at http://localhost:3000

## 📊 Dashboard Features

### 1. Main Dashboard (`/`)
- **Ranked wedge cards** sorted by score, MRR timeline, or enterprise value
- **Filters**: Detector source, complexity level, global search
- **Quick stats**: Score, time to $10k MRR, enterprise value, build complexity
- **Click to explore**: View full profile on detail page

### 2. Wedge Detail (`/wedge/:id`)
- **Scoring breakdown**: 8-factor analysis (pain, spend, growth, expandability, distribution, competition, capital, regulation)
- **Evidence panel**: Raw signals from each source with counts and examples
- **Expansion map**: Adjacent markets, geographic opportunities, product extensions, revenue models
- **Save to watchlist**: Track opportunities you're investigating

### 3. Signal Explorer (`/signals`)
- **Raw signal feed**: Browse all scraped data across 9 sources
- **Filters**: By source (Reddit, HN, App Store, etc.) or signal type (pain, regulation, etc.)
- **Sort**: By score or date
- **External links**: Jump to original source

### 4. Watchlist (`/watchlist`)
- **Track status**: Watching, Investigating, Building, Passed
- **Add notes**: Document your research and decisions
- **Export CSV**: Share findings with team
- **Stats dashboard**: Overview of tracked opportunities

## 🔧 Architecture

### Backend Stack
- **Express.js** - REST/tRPC API server
- **tRPC** - Type-safe API layer
- **SQLite** - Local database (11 tables)
- **APScheduler** - Background job scheduler
- **Python** - Scraper and detector modules

### Frontend Stack
- **React 19** - UI framework
- **Tailwind CSS 4** - Styling
- **shadcn/ui** - Component library
- **Wouter** - Lightweight router
- **tRPC Client** - Type-safe API calls

### Data Pipeline
```
Scrapers (9 modules)
    ↓
SQLite Database
    ↓
Detectors (7 modules)
    ↓
Scoring Engine
    ↓
Profile Generator
    ↓
React Dashboard
```

## 📡 Data Sources

| Source | Cadence | Signal Type | Status |
|--------|---------|-------------|--------|
| **Reddit** | 24h | Pain signals, complaints | ✅ Active |
| **Hacker News** | 24h | Problem statements | ✅ Active |
| **Google Trends** | 48h | Rising keywords | ✅ Active |
| **App Store** | 48h | 1-2 star reviews | ✅ Active |
| **Play Store** | 48h | 1-2 star reviews | ✅ Active |
| **Product Hunt** | 24h | New launches | ✅ Active |
| **SEC EDGAR** | 72h | Regulatory signals | ✅ Active |
| **Job Postings** | 48h | Manual roles | ✅ Active |
| **OpenVC** | 72h | Startup funding | ✅ Active |
| **Amazon Reviews** | — | Low-rated reviews | ⏸️ TODO (expensive proxies) |
| **G2** | — | Competitor reviews | ⏸️ TODO (bot protection) |

## 🧠 Wedge Detectors

| Detector | Input Tables | Output | Status |
|----------|-------------|--------|--------|
| **Pain Signal** | App/Play Store, Reddit, HN | High-volume complaints | ✅ Active |
| **Incumbent Weakness** | App/Play Store | Weak incumbents with 10+ complaints | ✅ Active |
| **Emerging Category** | YC, OpenVC | Fragmented markets with 5+ players | ✅ Active |
| **Distribution Gap** | Google Trends, Product Hunt | Rising keywords with no SaaS leader | ✅ Active |
| **Regulation Change** | SEC, Reddit, HN | Regulation-triggered opportunities | ✅ Active |
| **Margin Expansion** | Job Postings | High-margin manual service opportunities | ✅ Active |
| **Geographic Wedge** | YC, OpenVC | Geographic expansion opportunities | ✅ Active |

## 📈 Scoring Formula

```
Wedge Score = (pain × spend × growth × expandability × distribution) 
              ÷ (competition × capital × regulatory)
```

**Factors (0-10 scale):**
- **Pain**: Complaint volume and sentiment intensity
- **Spend**: Estimated customer budget allocation
- **Growth**: YoY trend acceleration
- **Expandability**: Potential for vertical/horizontal expansion
- **Distribution**: Ease of reaching target customers
- **Competition**: Incumbent strength and market saturation
- **Capital**: Required startup capital
- **Regulatory**: Friction from compliance requirements

**Profile Generation Threshold:** Wedges scoring > 15.0 auto-generate full JSON profiles with expansion opportunities.

## 🔑 API Credentials (Optional)

WIE works without any paid APIs. Optional credentials enable enhanced data collection:

### Reddit
1. Go to https://www.reddit.com/prefs/apps
2. Create a "script" app
3. Add to `.env`:
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=WIE/1.0
```

### Product Hunt
1. Go to https://www.producthunt.com/v2/oauth/applications
2. Create an application
3. Add to `.env`:
```env
PRODUCTHUNT_API_TOKEN=your_api_token
```

### Other Sources
- **Google Trends**: No API key needed (uses pytrends library)
- **Hacker News**: Free Algolia API (no key needed)
- **App Store**: Uses app-store-scraper library (no key needed)
- **Play Store**: Uses google-play-scraper library (no key needed)
- **SEC EDGAR**: Free API (no key needed)
- **Product Hunt**: GraphQL API (optional token for higher limits)
- **Y Combinator**: Web scraping (no key needed)
- **OpenVC**: Web scraping (no key needed)
- **Indeed**: RSS feeds (no key needed)

## 🚦 Manual Scraper Triggers

Run individual scrapers without waiting for the schedule:

```bash
# Via tRPC endpoint
curl -X POST http://localhost:3000/api/trpc/scrapers.run \
  -H "Content-Type: application/json" \
  -d '{"scraper":"reddit"}'

# Via Python directly
python -m backend.scrapers.reddit_scraper
```

Available scrapers: `reddit`, `google_trends`, `app_store`, `play_store`, `producthunt`, `yc`, `sec_edgar`, `hackernews`, `job_postings`, `openvc`

## 📊 Database Schema

### Signal Tables
- `reddit_posts` - Reddit scraper results
- `hn_posts` - Hacker News results
- `app_store_reviews` - App Store 1-2 star reviews
- `play_store_reviews` - Play Store 1-2 star reviews
- `google_trends` - Trending keywords
- `producthunt_launches` - Product Hunt launches
- `sec_filings` - SEC EDGAR filings
- `job_postings` - Job posting data
- `yc_companies` - Y Combinator companies
- `openvc_companies` - OpenVC startup data

### Analysis Tables
- `wedge_candidates` - Detector output (raw candidates)
- `wedge_profiles` - Generated profiles (scores > 15.0)
- `watchlist` - User-tracked opportunities
- `scraper_metadata` - Scheduler tracking (last run, error count, etc.)

## 🧪 Testing

### Run Tests
```bash
pnpm test
```

### Manual Testing Checklist
- [ ] Start app: `make run`
- [ ] Dashboard loads with 5+ wedges
- [ ] Filters work (detector, complexity, search)
- [ ] Sort changes ranking correctly
- [ ] Click "View Details" → detail page loads
- [ ] Evidence panel shows signals from multiple sources
- [ ] Expansion map displays 4 opportunity types
- [ ] Save to watchlist → appears in /watchlist
- [ ] Signals page shows raw feed with filters
- [ ] Watchlist shows notes, status, and CSV export
- [ ] Run manual scraper: `curl -X POST http://localhost:3000/api/trpc/scrapers.run -H "Content-Type: application/json" -d '{"scraper":"reddit"}'`
- [ ] Check database: `sqlite3 wie.db "SELECT COUNT(*) FROM reddit_posts;"`

## 📦 Deployment

### Manus Hosting
WIE is built on the Manus template and deploys automatically:

1. Click **Publish** in the Manus UI
2. Choose custom domain or use auto-generated `xxx.manus.space`
3. Database and environment variables managed by Manus

### External Hosting
If deploying elsewhere (Railway, Render, Vercel):

1. Build: `pnpm build`
2. Start: `pnpm start`
3. Ensure `DATABASE_URL` points to SQLite file
4. Scheduler runs in background automatically

## 🐛 Troubleshooting

### "No wedges showing on dashboard"
1. Run a scraper manually: `python -m backend.scrapers.reddit_scraper`
2. Check database: `sqlite3 wie.db "SELECT COUNT(*) FROM wedge_profiles;"`
3. Verify detectors ran: `sqlite3 wie.db "SELECT DISTINCT detector_source FROM wedge_candidates;"`

### "Scraper fails with credential error"
1. Check `.env` file exists and is readable
2. Verify credentials are correct (test with source's CLI tool)
3. Scrapers gracefully skip if credentials missing — check logs for warnings

### "Scheduler not running"
1. Check logs: `tail -f .manus-logs/devserver.log | grep Scheduler`
2. Verify Python environment: `python --version` (should be 3.11+)
3. Check system resources: `free -h` (need at least 512MB RAM)

### "Database locked error"
1. Ensure only one process is writing to `wie.db`
2. Check for stale processes: `lsof wie.db`
3. Delete lock file if needed: `rm wie.db-wal wie.db-shm`

## 📚 Documentation

- **ARCHITECTURE.md** - System design and data flow diagrams
- **INTEGRATION_GUIDE.md** - Backend integration details
- **backend/README.md** - Python module documentation
- **client/README.md** - React component documentation

## 🤝 Contributing

To add a new scraper:

1. Create `backend/scrapers/newscraper_scraper.py`
2. Implement `run()` function that returns list of signals
3. Add to `VALID_SCRAPERS` in `server/routers/scrapers.ts`
4. Update `.env.example` with any new credentials
5. Test: `python -m backend.scrapers.newscraper_scraper`

To add a new detector:

1. Create `backend/detectors/newdetector.py`
2. Implement `detect(db)` function that queries signals and writes candidates
3. Add to detector list in `backend/scheduler.py`
4. Test: `python -m backend.detectors.newdetector`

## 📄 License

MIT

## 🎓 Learning Resources

- [Market Wedge Strategy](https://www.sequoiacap.com/article/wedge-strategy/)
- [Startup Signals](https://www.paulgraham.com/startupideas.html)
- [tRPC Documentation](https://trpc.io)
- [Tailwind CSS](https://tailwindcss.com)
- [SQLite](https://www.sqlite.org)

## 📞 Support

For issues or questions:
1. Check logs: `.manus-logs/devserver.log`
2. Review INTEGRATION_GUIDE.md
3. Test components individually (scrapers, detectors, frontend)
4. Check database state: `sqlite3 wie.db ".schema"`

---

**Built with ❤️ using React, Express, Python, and SQLite**
