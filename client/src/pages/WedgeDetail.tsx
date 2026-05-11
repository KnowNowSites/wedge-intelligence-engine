import { useState } from "react";
import { useRoute, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Heart, Share2, Download } from "lucide-react";

interface WedgeProfile {
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
  scoring: {
    pain_score: number;
    spend_potential: number;
    growth_rate: number;
    expandability: number;
    distribution_score: number;
    competition_score: number;
    capital_required: number;
    regulatory_friction: number;
  };
  evidence: {
    source: string;
    count: number;
    examples: string[];
  }[];
}

// Mock data
const MOCK_WEDGE: WedgeProfile = {
  id: "1",
  wedge_name: "Construction Permit Automation",
  wedge_score: 8.5,
  detector_source: "pain_signal",
  enterprise_value: "high",
  complexity: "medium",
  mrr_timeline: { to_10k_mrr_months: 6, to_100k_mrr_months: 18 },
  scoring: {
    pain_score: 9.0,
    spend_potential: 8.5,
    growth_rate: 7.8,
    expandability: 8.2,
    distribution_score: 7.5,
    competition_score: 4.0,
    capital_required: 5.0,
    regulatory_friction: 6.0,
  },
  evidence: [
    {
      source: "reddit",
      count: 23,
      examples: [
        "Permit process is completely manual and takes 3-6 months",
        "No software exists that handles the entire workflow",
        "Cities have different requirements making it impossible to automate",
      ],
    },
    {
      source: "job_postings",
      count: 156,
      examples: [
        "Permit coordinator positions across major cities",
        "Manual data entry roles in city planning departments",
      ],
    },
    {
      source: "hackernews",
      count: 8,
      examples: [
        "Why doesn't someone build a permit automation tool?",
        "This is the most broken government process",
      ],
    },
  ],
};

export default function WedgeDetail() {
  const [, params] = useRoute("/wedge/:id");
  const [, navigate] = useLocation();
  const [isSaved, setIsSaved] = useState(false);

  const wedge = MOCK_WEDGE; // Replace with tRPC query using params?.id

  const scoreFactors = [
    { label: "Pain Score", value: wedge.scoring.pain_score, color: "bg-red-500" },
    { label: "Spend Potential", value: wedge.scoring.spend_potential, color: "bg-blue-500" },
    { label: "Growth Rate", value: wedge.scoring.growth_rate, color: "bg-green-500" },
    { label: "Expandability", value: wedge.scoring.expandability, color: "bg-purple-500" },
    { label: "Distribution", value: wedge.scoring.distribution_score, color: "bg-orange-500" },
  ];

  const resistanceFactors = [
    { label: "Competition", value: wedge.scoring.competition_score, color: "bg-slate-500" },
    { label: "Capital Required", value: wedge.scoring.capital_required, color: "bg-slate-500" },
    { label: "Regulatory Friction", value: wedge.scoring.regulatory_friction, color: "bg-slate-500" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/")}
            className="mb-4 gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Button>

          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-slate-900 mb-2">
                {wedge.wedge_name}
              </h1>
              <p className="text-slate-600">
                Detected via <span className="font-semibold">{wedge.detector_source.replace(/_/g, " ")}</span>
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant={isSaved ? "default" : "outline"}
                size="sm"
                onClick={() => setIsSaved(!isSaved)}
                className="gap-2"
              >
                <Heart className={`w-4 h-4 ${isSaved ? "fill-current" : ""}`} />
                {isSaved ? "Saved" : "Save"}
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <Share2 className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <Download className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Wedge Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {wedge.wedge_score.toFixed(1)}/10
              </div>
              <p className="text-xs text-slate-500 mt-1">High potential opportunity</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                To $10k MRR
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {wedge.mrr_timeline.to_10k_mrr_months} months
              </div>
              <p className="text-xs text-slate-500 mt-1">Estimated timeline</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Enterprise Value
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600 capitalize">
                {wedge.enterprise_value}
              </div>
              <p className="text-xs text-slate-500 mt-1">Exit potential</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Complexity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600 capitalize">
                {wedge.complexity}
              </div>
              <p className="text-xs text-slate-500 mt-1">Build difficulty</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="scoring" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="scoring">Scoring Breakdown</TabsTrigger>
            <TabsTrigger value="evidence">Evidence</TabsTrigger>
            <TabsTrigger value="expansion">Expansion Map</TabsTrigger>
          </TabsList>

          {/* Scoring Tab */}
          <TabsContent value="scoring" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Opportunity Factors (Drivers)</CardTitle>
                <CardDescription>
                  Factors that make this wedge attractive
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {scoreFactors.map((factor) => (
                  <div key={factor.label}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-slate-700">
                        {factor.label}
                      </span>
                      <span className="text-sm font-bold text-slate-900">
                        {factor.value.toFixed(1)}/10
                      </span>
                    </div>
                    <Progress value={factor.value * 10} className="h-2" />
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Resistance Factors (Headwinds)</CardTitle>
                <CardDescription>
                  Factors that make this wedge harder to execute
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {resistanceFactors.map((factor) => (
                  <div key={factor.label}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-slate-700">
                        {factor.label}
                      </span>
                      <span className="text-sm font-bold text-slate-900">
                        {factor.value.toFixed(1)}/10
                      </span>
                    </div>
                    <Progress value={factor.value * 10} className="h-2" />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Evidence Tab */}
          <TabsContent value="evidence" className="space-y-4">
            {wedge.evidence.map((evidence, idx) => (
              <Card key={idx}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg capitalize">
                      {evidence.source.replace(/_/g, " ")}
                    </CardTitle>
                    <Badge variant="secondary">{evidence.count} signals</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {evidence.examples.map((example, i) => (
                      <li key={i} className="flex gap-3 text-sm">
                        <span className="text-slate-400 mt-1">•</span>
                        <span className="text-slate-700">{example}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Expansion Map Tab */}
          <TabsContent value="expansion" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Expansion Opportunities</CardTitle>
                <CardDescription>
                  Potential adjacent markets and use cases
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="font-semibold text-blue-900 mb-2">Vertical Expansion</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• Zoning compliance</li>
                      <li>• Environmental reviews</li>
                      <li>• Utility coordination</li>
                    </ul>
                  </div>

                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <h4 className="font-semibold text-green-900 mb-2">Geographic Expansion</h4>
                    <ul className="text-sm text-green-800 space-y-1">
                      <li>• International markets</li>
                      <li>• Regional customization</li>
                      <li>• Multi-language support</li>
                    </ul>
                  </div>

                  <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <h4 className="font-semibold text-purple-900 mb-2">Product Expansion</h4>
                    <ul className="text-sm text-purple-800 space-y-1">
                      <li>• Compliance monitoring</li>
                      <li>• Stakeholder management</li>
                      <li>• Analytics dashboard</li>
                    </ul>
                  </div>

                  <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                    <h4 className="font-semibold text-orange-900 mb-2">Revenue Expansion</h4>
                    <ul className="text-sm text-orange-800 space-y-1">
                      <li>• Consulting services</li>
                      <li>• Training programs</li>
                      <li>• Integration marketplace</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* CTA */}
        <div className="mt-8 bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-slate-900 mb-1">
                Ready to explore this wedge?
              </h3>
              <p className="text-sm text-slate-600">
                Add to your watchlist to track signals and market developments
              </p>
            </div>
            <Button
              size="lg"
              onClick={() => setIsSaved(!isSaved)}
              className="gap-2"
            >
              <Heart className={`w-4 h-4 ${isSaved ? "fill-current" : ""}`} />
              {isSaved ? "Remove from Watchlist" : "Add to Watchlist"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
