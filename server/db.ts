import { ENV } from './_core/env';

/**
 * Database layer that proxies to Python backend for signal/wedge data
 * and uses in-memory storage for user auth (compatible with Manus template)
 */

// In-memory user store for auth (can be replaced with actual DB later)
const userStore = new Map<string, any>();

export async function getDb() {
  // Return null - we're using Python backend API instead
  return null;
}

export async function upsertUser(user: any): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const existingUser = userStore.get(user.openId);
  const now = new Date();

  const updatedUser = {
    id: existingUser?.id || userStore.size + 1,
    openId: user.openId,
    name: user.name ?? existingUser?.name ?? null,
    email: user.email ?? existingUser?.email ?? null,
    loginMethod: user.loginMethod ?? existingUser?.loginMethod ?? null,
    role: user.role ?? (user.openId === ENV.ownerOpenId ? 'admin' : 'user'),
    createdAt: existingUser?.createdAt ?? now,
    updatedAt: now,
    lastSignedIn: user.lastSignedIn ?? now,
  };

  userStore.set(user.openId, updatedUser);
}

export async function getUserByOpenId(openId: string) {
  return userStore.get(openId);
}

/**
 * Proxy functions that call the Python backend API
 */

export async function getWedges(options?: {
  limit?: number;
  offset?: number;
  detector?: string;
  complexity?: string;
  search?: string;
}) {
  try {
    const params = new URLSearchParams();
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());
    if (options?.detector) params.append('detector', options.detector);
    if (options?.complexity) params.append('complexity', options.complexity);
    if (options?.search) params.append('search', options.search);

    const response = await fetch(`http://localhost:5000/api/wedges?${params}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      console.warn(`[DB] Failed to fetch wedges: ${response.status}`);
      return [];
    }

    const data = await response.json();
    return data.wedges || [];
  } catch (error) {
    console.warn('[DB] Error fetching wedges:', error);
    return [];
  }
}

export async function getWedgeById(wedgeId: string) {
  try {
    const response = await fetch(`http://localhost:5000/api/wedges/${wedgeId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      console.warn(`[DB] Failed to fetch wedge: ${response.status}`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.warn('[DB] Error fetching wedge:', error);
    return null;
  }
}

export async function getSignals(options?: {
  source?: string;
  type?: string;
  limit?: number;
  offset?: number;
}) {
  try {
    const params = new URLSearchParams();
    if (options?.source) params.append('source', options.source);
    if (options?.type) params.append('type', options.type);
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());

    const response = await fetch(`http://localhost:5000/api/signals?${params}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      console.warn(`[DB] Failed to fetch signals: ${response.status}`);
      return [];
    }

    const data = await response.json();
    return data.signals || [];
  } catch (error) {
    console.warn('[DB] Error fetching signals:', error);
    return [];
  }
}

export async function getWatchlist() {
  try {
    const response = await fetch('http://localhost:5000/api/watchlist', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      console.warn(`[DB] Failed to fetch watchlist: ${response.status}`);
      return [];
    }

    const data = await response.json();
    return data.watchlist || [];
  } catch (error) {
    console.warn('[DB] Error fetching watchlist:', error);
    return [];
  }
}

export async function addToWatchlist(wedgeId: string, notes?: string) {
  try {
    const response = await fetch('http://localhost:5000/api/watchlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wedge_id: wedgeId, notes }),
    });

    if (!response.ok) {
      console.warn(`[DB] Failed to add to watchlist: ${response.status}`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.warn('[DB] Error adding to watchlist:', error);
    return null;
  }
}

export async function removeFromWatchlist(watchlistId: string) {
  try {
    const response = await fetch(`http://localhost:5000/api/watchlist/${watchlistId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      console.warn(`[DB] Failed to remove from watchlist: ${response.status}`);
      return false;
    }

    return true;
  } catch (error) {
    console.warn('[DB] Error removing from watchlist:', error);
    return false;
  }
}

export async function updateWatchlistNotes(watchlistId: string, notes: string) {
  try {
    const response = await fetch(`http://localhost:5000/api/watchlist/${watchlistId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes }),
    });

    if (!response.ok) {
      console.warn(`[DB] Failed to update watchlist: ${response.status}`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.warn('[DB] Error updating watchlist:', error);
    return null;
  }
}


export async function getScraperMetadata(scraperName: string) {
  try {
    const response = await fetch(`http://localhost:5000/api/scrapers/metadata/${scraperName}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.warn('[DB] Error fetching scraper metadata:', error);
    return null;
  }
}

export async function updateScraperMetadata(scraperName: string, metadata: any) {
  try {
    const response = await fetch(`http://localhost:5000/api/scrapers/metadata/${scraperName}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metadata),
    });

    if (!response.ok) {
      console.warn(`[DB] Failed to update scraper metadata: ${response.status}`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.warn('[DB] Error updating scraper metadata:', error);
    return null;
  }
}
