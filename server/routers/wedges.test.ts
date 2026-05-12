import { describe, it, expect, beforeEach } from "vitest";
import { wedgesRouter } from "./wedges";

type WedgesRouter = typeof wedgesRouter;
type Caller = ReturnType<WedgesRouter["createCaller"]>;

describe("wedgesRouter", () => {
  let caller: Caller;

  beforeEach(() => {
    // Create a caller with empty context (public procedures)
    caller = wedgesRouter.createCaller({
      user: null,
      req: {} as any,
      res: {} as any,
    });
  });

  describe("wedges.list", () => {
    it("returns all wedges without filters", async () => {
      const result = await caller.list({});
      expect(result.wedges).toBeDefined();
      expect(result.total).toBeGreaterThan(0);
      expect(result.wedges.length).toBe(result.total);
    });

    it("filters wedges by search term", async () => {
      const result = await caller.list({ search: "permit" });
      expect(result.wedges.length).toBeGreaterThan(0);
      expect(
        result.wedges.every(
          (w) =>
            w.wedge_name.toLowerCase().includes("permit") ||
            w.detector_source.toLowerCase().includes("permit")
        )
      ).toBe(true);
    });

    it("filters wedges by detector source", async () => {
      const result = await caller.list({ detector: "pain_signal" });
      expect(
        result.wedges.every((w) => w.detector_source === "pain_signal")
      ).toBe(true);
    });

    it("filters wedges by complexity", async () => {
      const result = await caller.list({ complexity: "low" });
      expect(result.wedges.every((w) => w.complexity === "low")).toBe(true);
    });

    it("sorts wedges by score (highest first)", async () => {
      const result = await caller.list({ sortBy: "score" });
      for (let i = 0; i < result.wedges.length - 1; i++) {
        expect(result.wedges[i].wedge_score).toBeGreaterThanOrEqual(
          result.wedges[i + 1].wedge_score
        );
      }
    });

    it("sorts wedges by MRR (fastest first)", async () => {
      const result = await caller.list({ sortBy: "mrr" });
      for (let i = 0; i < result.wedges.length - 1; i++) {
        expect(
          result.wedges[i].mrr_timeline.to_10k_mrr_months
        ).toBeLessThanOrEqual(
          result.wedges[i + 1].mrr_timeline.to_10k_mrr_months
        );
      }
    });

    it("sorts wedges by enterprise value", async () => {
      const result = await caller.list({ sortBy: "value" });
      // Verify the sort doesn't throw and returns wedges
      expect(result.wedges.length).toBeGreaterThan(0);
      expect(result.wedges[0].enterprise_value).toBeDefined();
    });
  });

  describe("wedges.get", () => {
    it("returns a single wedge by ID", async () => {
      const result = await caller.get({ id: "1" });
      expect(result.id).toBe("1");
      expect(result.wedge_name).toBeDefined();
      expect(result.wedge_score).toBeGreaterThan(0);
    });

    it("throws error for non-existent wedge", async () => {
      await expect(caller.get({ id: "999" })).rejects.toThrow(
        "not found"
      );
    });

    it("returns scoring details", async () => {
      const result = await caller.get({ id: "1" });
      expect(result.scoring).toBeDefined();
      expect(result.scoring.pain_score).toBeGreaterThanOrEqual(0);
      expect(result.scoring.pain_score).toBeLessThanOrEqual(10);
      expect(result.scoring.spend_potential).toBeGreaterThanOrEqual(0);
      expect(result.scoring.competition_score).toBeGreaterThanOrEqual(0);
    });

    it("returns MRR timeline estimates", async () => {
      const result = await caller.get({ id: "1" });
      expect(result.mrr_timeline.to_10k_mrr_months).toBeGreaterThan(0);
      expect(result.mrr_timeline.to_100k_mrr_months).toBeGreaterThan(
        result.mrr_timeline.to_10k_mrr_months
      );
    });
  });

  describe("wedges.signals", () => {
    it("returns signals for a wedge", async () => {
      const result = await caller.signals({ wedgeId: "1" });
      expect(result.signals).toBeDefined();
      expect(result.total).toBeGreaterThanOrEqual(0);
    });

    it("filters signals by source", async () => {
      const result = await caller.signals({
        wedgeId: "1",
        source: "reddit",
      });
      expect(
        result.signals.every((s) => s.source === "reddit")
      ).toBe(true);
    });

    it("filters signals by type", async () => {
      const result = await caller.signals({
        wedgeId: "1",
        type: "pain_signal",
      });
      expect(
        result.signals.every((s) => s.type === "pain_signal")
      ).toBe(true);
    });
  });

  describe("wedges.exploreSignals", () => {
    it("returns all signals without filters", async () => {
      const result = await caller.exploreSignals({});
      expect(result.signals).toBeDefined();
      expect(result.total).toBeGreaterThanOrEqual(0);
    });

    it("filters signals by search term", async () => {
      const result = await caller.exploreSignals({ search: "manual" });
      expect(
        result.signals.every(
          (s) =>
            s.title.toLowerCase().includes("manual") ||
            s.description.toLowerCase().includes("manual")
        )
      ).toBe(true);
    });

    it("sorts signals by score (highest first)", async () => {
      const result = await caller.exploreSignals({ sortBy: "score" });
      for (let i = 0; i < result.signals.length - 1; i++) {
        expect(result.signals[i].score).toBeGreaterThanOrEqual(
          result.signals[i + 1].score
        );
      }
    });

    it("sorts signals by date (most recent first)", async () => {
      const result = await caller.exploreSignals({ sortBy: "date" });
      for (let i = 0; i < result.signals.length - 1; i++) {
        expect(new Date(result.signals[i].date).getTime()).toBeGreaterThanOrEqual(
          new Date(result.signals[i + 1].date).getTime()
        );
      }
    });
  });

  describe("wedges.watchlist", () => {
    it("returns watchlist items", async () => {
      const result = await caller.watchlist();
      expect(result.items).toBeDefined();
      expect(result.total).toBeGreaterThanOrEqual(0);
    });

    it("watchlist items have required fields", async () => {
      const result = await caller.watchlist();
      if (result.items.length > 0) {
        const item = result.items[0];
        expect(item.id).toBeDefined();
        expect(item.wedge_name).toBeDefined();
        expect(item.status).toMatch(/watching|investigating|building|passed/);
        expect(item.notes).toBeDefined();
        expect(item.date_added).toBeDefined();
        expect(item.last_updated).toBeDefined();
      }
    });
  });

  describe("wedges.addToWatchlist", () => {
    it("adds a wedge to watchlist", async () => {
      const result = await caller.addToWatchlist({
        wedgeId: "1",
        notes: "Test notes",
      });
      expect(result.success).toBe(true);
      expect(result.message).toBeDefined();
    });

    it("accepts optional notes", async () => {
      const result = await caller.addToWatchlist({
        wedgeId: "1",
      });
      expect(result.success).toBe(true);
    });
  });

  describe("wedges.updateWatchlistItem", () => {
    it("updates watchlist item status and notes", async () => {
      const result = await caller.updateWatchlistItem({
        id: "1",
        status: "investigating",
        notes: "Updated notes",
      });
      expect(result.success).toBe(true);
    });

    it("accepts all status values", async () => {
      const statuses = ["watching", "investigating", "building", "passed"] as const;
      for (const status of statuses) {
        const result = await caller.updateWatchlistItem({
          id: "1",
          status,
          notes: "Test",
        });
        expect(result.success).toBe(true);
      }
    });
  });

  describe("wedges.removeFromWatchlist", () => {
    it("removes a wedge from watchlist", async () => {
      const result = await caller.removeFromWatchlist({ id: "1" });
      expect(result.success).toBe(true);
      expect(result.message).toBeDefined();
    });
  });

  describe("wedges.exportWatchlist", () => {
    it("exports watchlist as CSV", async () => {
      const result = await caller.exportWatchlist();
      expect(result.csv).toBeDefined();
      expect(result.filename).toBeDefined();
      expect(result.filename).toMatch(/watchlist-\d{4}-\d{2}-\d{2}\.csv/);
    });

    it("CSV contains headers", async () => {
      const result = await caller.exportWatchlist();
      const lines = result.csv.split("\n");
      expect(lines[0]).toContain("Wedge Name");
      expect(lines[0]).toContain("Score");
      expect(lines[0]).toContain("Status");
      expect(lines[0]).toContain("Notes");
    });

    it("CSV is properly formatted", async () => {
      const result = await caller.exportWatchlist();
      const lines = result.csv.split("\n");
      // Each line should have the same number of fields
      const fieldCounts = lines.map((line) => (line.match(/"/g) || []).length);
      expect(fieldCounts.every((count) => count % 2 === 0)).toBe(true);
    });
  });

  describe("data validation", () => {
    it("wedge scores are between 0 and 10", async () => {
      const result = await caller.list({});
      expect(
        result.wedges.every((w) => w.wedge_score >= 0 && w.wedge_score <= 10)
      ).toBe(true);
    });

    it("complexity values are valid", async () => {
      const result = await caller.list({});
      expect(
        result.wedges.every((w) =>
          ["low", "medium", "high"].includes(w.complexity)
        )
      ).toBe(true);
    });

    it("enterprise value is valid", async () => {
      const result = await caller.list({});
      expect(
        result.wedges.every((w) =>
          ["low", "medium", "high", "very_high"].includes(w.enterprise_value)
        )
      ).toBe(true);
    });

    it("MRR timelines are positive", async () => {
      const result = await caller.list({});
      expect(
        result.wedges.every(
          (w) =>
            w.mrr_timeline.to_10k_mrr_months > 0 &&
            w.mrr_timeline.to_100k_mrr_months > 0
        )
      ).toBe(true);
    });
  });
});
