# WIE Project TODO

## Phase 0: Project Structure & Database
- [x] Create backend directory structure with scrapers/, detectors/, and core modules
- [x] Create SQLite database schema with all 11 tables
- [x] Set up environment variables and .env file
- [x] Create Makefile and docker-compose.yml for single-command startup
- [x] Create README with setup instructions

## Phase 1: Data Scrapers (9 modules - FULL IMPLEMENTATION)
- [x] reddit_scraper.py - Playwright-based Reddit scraper with real logic
- [x] google_trends_scraper.py - pytrends-based trending keywords detector
- [x] app_store_scraper.py - Apple App Store reviews (1-2 star only)
- [x] play_store_scraper.py - Google Play Store reviews (1-2 star only)
- [x] producthunt_scraper.py - Product Hunt GraphQL API integration
- [x] yc_scraper.py - Y Combinator companies scraper
- [x] sec_edgar_scraper.py - SEC EDGAR filings keyword detector
- [x] hackernews_scraper.py - HN Algolia API integration
- [x] job_postings_scraper.py - Indeed RSS job postings scraper
- [x] openvc_scraper.py - OpenVC startup funding data
- [x] amazon_reviews_scraper.py - TODO stub (residential proxy cost)
- [x] g2_scraper.py - TODO stub (bot protection too aggressive)
- [ ] Integrate scrapers into Express backend as background services
- [ ] Add POST /api/scrapers/run/:scraper_name endpoint for manual testing
- [ ] Implement graceful degradation for missing credentials

## Phase 2: Wedge Detectors & Scoring
- [x] pain_signal.py - Detect high-volume complaints and negative sentiment
- [x] incumbent_weakness.py - Group complaints by company/software
- [x] emerging_category.py - Find fragmented markets with multiple players
- [x] distribution_gap.py - Find rising keywords with no clear SaaS leader
- [x] regulation_change.py - Cluster regulatory mentions across sources
- [x] margin_expansion.py - Identify high-margin manual service opportunities
- [x] geographic_wedge.py - Find geographic arbitrage opportunities
- [x] scoring.py - Implement wedge_score formula and helper functions
- [x] wedge_profile_generator.py - Auto-generate profiles for scores > 15.0

## Phase 3: Scheduler & Background Jobs
- [x] scheduler.py - APScheduler setup with 24h-72h cadences per scraper
- [x] Background task runner - Re-run detectors after each scraper
- [x] Last-refreshed timestamp tracking

## Phase 4: React Frontend Dashboard
- [x] Dashboard page (/) - Ranked wedge cards with filters and sort
- [x] Wedge Detail page (/wedge/:id) - Full profile, expansion map, evidence
- [x] Signal Explorer page (/signals) - Raw signal feed with filters
- [x] Watchlist page (/watchlist) - Notes field, status column, CSV export
- [x] Navigation header with routing
- [x] tRPC routers for wedges, signals, watchlist

## Phase 5: Integration & Testing
- [ ] All scrapers run independently without crashing each other
- [ ] Database populates with real records from each source
- [ ] All 7 detectors return at least 5 candidates each
- [ ] Scoring formula correctly ranks candidates
- [ ] Dashboard loads and displays top wedges with working filters
- [ ] Wedge detail page renders full profile + expansion map
- [ ] Signal Explorer shows raw records with source attribution
- [ ] Watchlist saves, persists, and exports correctly
- [ ] Scheduler runs without blocking the server
- [ ] Single startup command works: make run or docker-compose up

## Phase 6: Documentation & Delivery
- [x] Complete README with architecture overview (README_COMPLETE.md)
- [x] Setup instructions for API credentials
- [x] Example .env file (.env.example)
- [x] Architecture diagram (ARCHITECTURE.md)
- [x] Integration guide (INTEGRATION_GUIDE.md)
- [x] Backend module documentation (backend/README.md)
- [ ] Final testing and bug fixes
- [ ] Publish to production
