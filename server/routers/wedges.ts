import { z } from "zod";
import { publicProcedure, protectedProcedure, router } from "../_core/trpc";
import * as db from "../db";

export const wedgesRouter = router({
  list: publicProcedure
    .input(
      z.object({
        limit: z.number().default(50),
        offset: z.number().default(0),
        detector: z.string().optional(),
        complexity: z.string().optional(),
        search: z.string().optional(),
      }).optional()
    )
    .query(async ({ input }) => {
      const wedges = await db.getWedges({
        limit: input?.limit,
        offset: input?.offset,
        detector: input?.detector,
        complexity: input?.complexity,
        search: input?.search,
      });

      return {
        total: wedges.length,
        wedges: (wedges || []).map((w: any) => ({
          id: w.id || w.wedge_id,
          name: w.wedge_name || w.name,
          score: w.wedge_score || w.score,
          detector: w.detector_source || w.detector,
          complexity: w.complexity,
          enterprise_value: w.enterprise_value,
          to_10k_mrr_months: w.to_10k_mrr_months,
          to_100k_mrr_months: w.to_100k_mrr_months,
          created_at: w.created_at,
        })),
      };
    }),

  get: publicProcedure
    .input(z.object({ wedge_id: z.string() }))
    .query(async ({ input }) => {
      const wedge = await db.getWedgeById(input.wedge_id);
      if (!wedge) {
        return null;
      }

      return {
        id: wedge.id || wedge.wedge_id,
        name: wedge.wedge_name || wedge.name,
        score: wedge.wedge_score || wedge.score,
        detector: wedge.detector_source || wedge.detector,
        complexity: wedge.complexity,
        enterprise_value: wedge.enterprise_value,
        to_10k_mrr_months: wedge.to_10k_mrr_months,
        to_100k_mrr_months: wedge.to_100k_mrr_months,
        evidence: wedge.evidence_json ? JSON.parse(wedge.evidence_json) : {},
        created_at: wedge.created_at,
      };
    }),

  signals: publicProcedure
    .input(z.object({ wedge_id: z.string() }))
    .query(async ({ input }) => {
      // Get signals related to this wedge
      const signals = await db.getSignals({ limit: 100 });
      return {
        signals: (signals || []).map((s: any) => ({
          id: s.id,
          source: s.source,
          type: s.type,
          title: s.title,
          description: s.description,
          score: s.score,
          url: s.url,
          date: s.created_at || s.scraped_at,
        })),
      };
    }),

  exploreSignals: publicProcedure
    .input(
      z.object({
        source: z.string().optional(),
        type: z.string().optional(),
        limit: z.number().default(50),
        offset: z.number().default(0),
      }).optional()
    )
    .query(async ({ input }) => {
      const signals = await db.getSignals({
        source: input?.source,
        type: input?.type,
        limit: input?.limit,
        offset: input?.offset,
      });

      return {
        total: signals.length,
        signals: (signals || []).map((signal: any) => ({
          id: signal.id,
          source: signal.source,
          type: signal.type,
          title: signal.title,
          description: signal.description,
          score: signal.score,
          url: signal.url,
          date: signal.created_at || signal.scraped_at,
        })),
      };
    }),

  addToWatchlist: protectedProcedure
    .input(z.object({ wedge_id: z.string(), notes: z.string().optional() }))
    .mutation(async ({ input }) => {
      const result = await db.addToWatchlist(input.wedge_id, input.notes);
      return result || { success: false };
    }),

  removeFromWatchlist: protectedProcedure
    .input(z.object({ watchlist_id: z.string() }))
    .mutation(async ({ input }) => {
      const success = await db.removeFromWatchlist(input.watchlist_id);
      return { success };
    }),

  watchlist: publicProcedure.query(async () => {
    const items = await db.getWatchlist();
    return {
      items: (items || []).map((item: any) => ({
        id: item.id,
        wedge_name: item.wedge_name,
        wedge_score: item.wedge_score,
        status: item.status,
        notes: item.notes,
        date_added: item.date_added,
      })),
    };
  }),

  updateWatchlistNotes: protectedProcedure
    .input(z.object({ watchlist_id: z.string(), notes: z.string() }))
    .mutation(async ({ input }) => {
      const updated = await db.updateWatchlistNotes(input.watchlist_id, input.notes);
      return updated || { success: false };
    }),

  exportWatchlistCSV: publicProcedure.query(async () => {
    const items = await db.getWatchlist();
    const csv = [
      ['Wedge Name', 'Score', 'Status', 'Notes', 'Date Added'].join(','),
      ...(items || []).map((item: any) =>
        [
          `"${item.wedge_name}"`,
          item.wedge_score,
          item.status,
          `"${item.notes || ''}"`,
          item.date_added,
        ].join(',')
      ),
    ].join('\n');

    return { csv };
  }),
});
