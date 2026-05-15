/**
 * SQLite Schema Definitions
 * 
 * This file documents the SQLite schema used by both Python scrapers
 * and the Express backend. The actual schema is initialized in server/db.ts
 * when the database connection is first established.
 */

export interface User {
  id: number;
  openId: string;
  name: string | null;
  email: string | null;
  loginMethod: string | null;
  role: "user" | "admin";
  createdAt: string;
  updatedAt: string;
  lastSignedIn: string;
}

export interface WedgeProfile {
  id: string;
  wedge_name: string;
  wedge_score: number;
  detector_source: string;
  enterprise_value: "low" | "medium" | "high" | "very_high";
  complexity: "low" | "medium" | "high";
  to_10k_mrr_months: number;
  to_100k_mrr_months: number;
  evidence_json: string; // JSON stringified
  created_at: string;
  updated_at: string;
}

export interface Signal {
  id: string;
  source: string;
  type: string;
  title: string;
  description: string;
  score: number;
  url: string;
  metadata_json: string; // JSON stringified
  created_at: string;
  scraped_at: string;
}

export interface Watchlist {
  id: string;
  wedge_id: string;
  status: "watching" | "investigating" | "building" | "passed";
  notes: string | null;
  date_added: string;
  last_updated: string;
}

export interface RedditPost {
  id: string;
  subreddit: string;
  title: string;
  content: string;
  score: number;
  url: string;
  created_at: string;
  scraped_at: string;
}

export interface HNPost {
  id: string;
  title: string;
  url: string;
  score: number;
  created_at: string;
  scraped_at: string;
}

export interface AppStoreReview {
  id: string;
  app_name: string;
  rating: number;
  review_text: string;
  reviewer_name: string;
  review_date: string;
  scraped_at: string;
}

export interface PlayStoreReview {
  id: string;
  app_name: string;
  rating: number;
  review_text: string;
  reviewer_name: string;
  review_date: string;
  scraped_at: string;
}

export interface GoogleTrend {
  id: string;
  keyword: string;
  trend_score: number;
  region: string;
  category: string;
  timestamp: string;
  scraped_at: string;
}

export interface ProductHuntLaunch {
  id: string;
  product_name: string;
  tagline: string;
  url: string;
  votes: number;
  created_at: string;
  scraped_at: string;
}

export interface YCCompany {
  id: string;
  company_name: string;
  batch: string;
  vertical: string;
  description: string;
  url: string;
  founded_at: string;
  scraped_at: string;
}

export interface SECFiling {
  id: string;
  company_name: string;
  filing_type: string;
  content: string;
  filing_date: string;
  url: string;
  scraped_at: string;
}

export interface JobPosting {
  id: string;
  title: string;
  company: string;
  description: string;
  url: string;
  posted_date: string;
  scraped_at: string;
}

export interface OpenVCCompany {
  id: string;
  company_name: string;
  funding_amount: number;
  funding_date: string;
  vertical: string;
  url: string;
  scraped_at: string;
}

export interface WedgeCandidate {
  id: string;
  wedge_name: string;
  detector_source: string;
  raw_score: number;
  pain_score: number;
  spend_potential: number;
  growth_rate: number;
  expandability: number;
  distribution_score: number;
  competition_score: number;
  capital_required: number;
  regulatory_friction: number;
  created_at: string;
  updated_at: string;
}

export interface ScraperMetadata {
  scraper_name: string;
  last_run: string | null;
  last_successful_run: string | null;
  error_count: number;
  last_error: string | null;
  results_count: number;
}
