import { useState, useMemo } from "react";
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
import { TrendingUp, Search, Filter } from "lucide-react";
import { useLocation } from "wouter";

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

// Mock data - replace with tRPC query
const MOCK_WEDGES: Wedge[] = [
  {
    id: "1",
    wedge_name: "Construction Permit Automation",
    wedge_score: 8.5,
    detector_source: "pain_signal",
    enterprise_value: "high",
    complexity: "medium",
    mrr_timeline: { to_10k_mrr_months: 6, to_100k_mrr_months: 18 },
  },
  {
    id: "2",
    wedge_name: "Healthcare Compliance Software",
    wedge_score: 8.2,
    detector_source: "regulation_change",
    enterprise_value: "very_high",
    complexity: "high",
    mrr_timeline: { to_10k_mrr_months: 9, to_100k_mrr_months: 24 },
  },
  {
    id: "3",
    wedge_name: "Logistics Optimization",
    wedge_score: 7.9,
    detector_source: "margin_expansion",
    enterprise_value: "high",
    complexity: "medium",
    mrr_timeline: { to_10k_mrr_months: 8, to_100k_mrr_months: 20 },
  },
  {
    id: "4",
    wedge_name: "Real Estate Valuation API",
    wedge_score: 7.5,
    detector_source: "distribution_gap",
    enterprise_value: "medium",
    complexity: "low",
    mrr_timeline: { to_10k_mrr_months: 4, to_100k_mrr_months: 14 },
  },
  {
    id: "5",
    wedge_name: "Emerging Market SaaS",
    wedge_score: 7.2,
    detector_source: "geographic_wedge",
    enterprise_value: "medium",
    complexity: "medium",
    mrr_timeline: { to_10k_mrr_months: 7, to_100k_mrr_months: 19 },
  },
];

export default function Dashboard() {
  const [, navigate] = useLocation();
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState<"score" | "mrr" | "value">("score");
  const [filterDetector, setFilterDetector] = useState<string>("all");
  const [filterComplexity, setFilterComplexity] = useState<string>("all");

  const filteredAndSortedWedges = useMemo(() => {
    let filtered = MOCK_WEDGES.filter((wedge) => {
      const matchesSearch =
        wedge.wedge_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        wedge.detector_source.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesDetector =
        filterDetector === "all" || wedge.detector_source === filterDetector;

      const matchesComplexity =
        filterComplexity === "all" || wedge.complexity === filterComplexity;

      return matchesSearch && matchesDetector && matchesComplexity;
    });

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === "score") {
        return b.wedge_score - a.wedge_score;
      } else if (sortBy === "mrr") {
        return a.mrr_timeline.to_10k_mrr_months - b.mrr_timeline.to_10k_mrr_months;
      } else if (sortBy === "value") {
        const valueOrder = { low: 1, medium: 2, high: 3, very_high: 4 };
        return (
          (valueOrder[b.enterprise_value as keyof typeof valueOrder] || 0) -
          (valueOrder[a.enterprise_value as keyof typeof valueOrder] || 0)
        );
      }
      return 0;
    });

    return filtered;
  }, [searchTerm, sortBy, filterDetector, filterComplexity]);

  const detectors = Array.from(
    new Set(MOCK_WEDGES.map((w) => w.detector_source))
  );

  const getScoreBadgeColor = (score: number) => {
    if (score >= 8) return "bg-green-100 text-green-800";
    if (score >= 7) return "bg-blue-100 text-blue-800";
    return "bg-yellow-100 text-yellow-800";
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case "low":
        return "bg-green-50 border-green-200";
      case "medium":
        return "bg-yellow-50 border-yellow-200";
      case "high":
        return "bg-red-50 border-red-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-8 h-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-slate-900">Wedge Intelligence</h1>
          </div>
          <p className="text-slate-600">
            Discover untapped market opportunities ranked by potential and timing
          </p>
        </div>

        {/* Search & Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                <Input
                  placeholder="Search wedges..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Sort */}
            <Select value={sortBy} onValueChange={(v) => setSortBy(v as any)}>
              <SelectTrigger>
                <SelectValue placeholder="Sort by..." />
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
                <SelectValue placeholder="All detectors" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Detectors</SelectItem>
                {detectors.map((d) => (
                  <SelectItem key={d} value={d}>
                    {d.replace(/_/g, " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Complexity Filter */}
            <Select value={filterComplexity} onValueChange={setFilterComplexity}>
              <SelectTrigger>
                <SelectValue placeholder="All complexity" />
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

        {/* Results Count */}
        <div className="mb-4 text-sm text-slate-600">
          Showing {filteredAndSortedWedges.length} of {MOCK_WEDGES.length} wedges
        </div>

        {/* Wedge Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAndSortedWedges.map((wedge) => (
            <Card
              key={wedge.id}
              className={`cursor-pointer transition-all hover:shadow-lg hover:scale-105 border-l-4 ${getComplexityColor(
                wedge.complexity
              )}`}
              onClick={() => navigate(`/wedge/${wedge.id}`)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <CardTitle className="text-lg line-clamp-2">
                      {wedge.wedge_name}
                    </CardTitle>
                    <CardDescription className="text-xs mt-1">
                      {wedge.detector_source.replace(/_/g, " ")}
                    </CardDescription>
                  </div>
                  <Badge className={getScoreBadgeColor(wedge.wedge_score)}>
                    {wedge.wedge_score.toFixed(1)}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent>
                <div className="space-y-3">
                  {/* Metrics Grid */}
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="bg-white rounded p-2">
                      <div className="text-xs text-slate-500 font-medium">
                        To $10k MRR
                      </div>
                      <div className="text-lg font-bold text-slate-900">
                        {wedge.mrr_timeline.to_10k_mrr_months}mo
                      </div>
                    </div>
                    <div className="bg-white rounded p-2">
                      <div className="text-xs text-slate-500 font-medium">
                        Enterprise Value
                      </div>
                      <div className="text-lg font-bold text-slate-900 capitalize">
                        {wedge.enterprise_value.replace(/_/g, " ")}
                      </div>
                    </div>
                  </div>

                  {/* Badges */}
                  <div className="flex flex-wrap gap-1">
                    <Badge variant="outline" className="text-xs">
                      {wedge.complexity} complexity
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      {wedge.mrr_timeline.to_100k_mrr_months}mo to $100k
                    </Badge>
                  </div>

                  {/* CTA */}
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full mt-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/wedge/${wedge.id}`);
                    }}
                  >
                    View Details →
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {filteredAndSortedWedges.length === 0 && (
          <Card className="text-center py-12">
            <Filter className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">No wedges match your filters</p>
          </Card>
        )}
      </div>
    </div>
  );
}
