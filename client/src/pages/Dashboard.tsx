import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Search, Filter, Loader2 } from "lucide-react";
import { useLocation } from "wouter";
import { trpc } from "@/lib/trpc";
import { useMemo, useState } from "react";

interface Wedge {
  id: string;
  wedge_name: string;
  wedge_score: number;
  detector_source: string;
  enterprise_value: string;
  complexity: string;
  mrr_timeline: {
    to_10k_mrr_months: number;
    to_100k_mrr_months: number;
  };
}

export default function Dashboard() {
  const [, navigate] = useLocation();
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState<"score" | "mrr" | "value">("score");
  const [filterDetector, setFilterDetector] = useState<string>("all");
  const [filterComplexity, setFilterComplexity] = useState<string>("all");

  // Fetch real data from tRPC
  const { data, isLoading, error } = trpc.wedges.list.useQuery({
    search: searchTerm || undefined,
    detector: filterDetector === "all" ? undefined : filterDetector,
    complexity: filterComplexity === "all" ? undefined : filterComplexity,
  });

  const wedges = data?.wedges || [];

  const filteredAndSortedWedges = useMemo(() => {
    return wedges;
  }, [wedges]);

  const detectors = Array.from(
    new Set(wedges.map((w: any) => w.detector))
  );

  const getScoreBadgeColor = (score: number) => {
    if (score >= 8) return "bg-green-100 text-green-800";
    if (score >= 7) return "bg-blue-100 text-blue-800";
    return "bg-yellow-100 text-yellow-800";
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case "low":
        return "bg-green-50 text-green-700 border border-green-200";
      case "medium":
        return "bg-yellow-50 text-yellow-700 border border-yellow-200";
      case "high":
        return "bg-red-50 text-red-700 border border-red-200";
      default:
        return "bg-slate-50 text-slate-700 border border-slate-200";
    }
  };

  const getValueColor = (value: string) => {
    switch (value) {
      case "low":
        return "text-slate-600";
      case "medium":
        return "text-blue-600";
      case "high":
        return "text-green-600";
      case "very_high":
        return "text-emerald-600";
      default:
        return "text-slate-600";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-8 h-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-slate-900">Wedge Intelligence</h1>
          </div>
          <p className="text-lg text-slate-600">Discover untapped market opportunities ranked by potential and timing</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search wedges..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Sort */}
            <Select value={sortBy} onValueChange={(value) => setSortBy(value as any)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="score">Highest Score</SelectItem>
                <SelectItem value="mrr">Fastest to $10k MRR</SelectItem>
                <SelectItem value="value">Highest Value</SelectItem>
              </SelectContent>
            </Select>

            {/* Detector Filter */}
            <Select value={filterDetector} onValueChange={setFilterDetector}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Detectors</SelectItem>
                {detectors.map((detector: any) => (
                  <SelectItem key={String(detector)} value={String(detector)}>
                    {String(detector).replace(/_/g, " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Complexity Filter */}
            <Select value={filterComplexity} onValueChange={setFilterComplexity}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Complexity</SelectItem>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
            <p className="text-slate-600">Loading wedges...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-800">
            <p className="font-semibold">Error loading wedges</p>
            <p className="text-sm mt-1">{error.message}</p>
          </div>
        ) : filteredAndSortedWedges.length === 0 ? (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-12 text-center">
            <p className="text-slate-600 text-lg">No wedges found matching your filters</p>
            <p className="text-slate-500 text-sm mt-2">Try adjusting your search or filters</p>
          </div>
        ) : (
          <>
            <p className="text-slate-600 mb-4">Showing {filteredAndSortedWedges.length} of {wedges.length} wedges</p>

            {/* Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAndSortedWedges.map((wedge: Wedge) => (
                <Card
                  key={wedge.id}
                  className={`cursor-pointer hover:shadow-lg transition-all border-l-4 ${
                    wedge.detector_source === "pain_signal"
                      ? "border-l-yellow-400"
                      : wedge.detector_source === "regulation_change"
                      ? "border-l-red-400"
                      : wedge.detector_source === "margin_expansion"
                      ? "border-l-green-400"
                      : "border-l-blue-400"
                  }`}
                  onClick={() => navigate(`/wedge/${wedge.id}`)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{wedge.wedge_name}</CardTitle>
                        <CardDescription className="capitalize text-xs mt-1">
                          {wedge.detector_source.replace(/_/g, " ")}
                        </CardDescription>
                      </div>
                      <Badge className={`${getScoreBadgeColor(wedge.wedge_score)} text-sm font-bold`}>
                        {wedge.wedge_score.toFixed(1)}
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs text-slate-500 font-semibold">To $10k MRR</p>
                        <p className="text-lg font-bold text-slate-900">{wedge.mrr_timeline.to_10k_mrr_months}mo</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 font-semibold">Enterprise Value</p>
                        <p className={`text-lg font-bold capitalize ${getValueColor(wedge.enterprise_value)}`}>
                          {wedge.enterprise_value}
                        </p>
                      </div>
                    </div>

                    {/* Complexity Badge */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-600">Complexity</span>
                      <Badge variant="outline" className={`capitalize ${getComplexityColor(wedge.complexity)}`}>
                        {wedge.complexity}
                      </Badge>
                    </div>

                    {/* MRR Range */}
                    <div className="text-xs text-slate-600 border-t pt-3">
                      <p>
                        {wedge.mrr_timeline.to_10k_mrr_months}mo to $10k • {wedge.mrr_timeline.to_100k_mrr_months}mo to $100k
                      </p>
                    </div>

                    {/* CTA */}
                    <Button className="w-full mt-2" variant="default" size="sm">
                      View Details →
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
