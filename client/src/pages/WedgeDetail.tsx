import { useRoute } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Heart, Share2, Download } from "lucide-react";
import { useState } from "react";
import { trpc } from "@/lib/trpc";

export default function WedgeDetail() {
  const [, params] = useRoute("/wedge/:id");
  const [isSaved, setIsSaved] = useState(false);

  const { data: wedge, isLoading } = trpc.wedges.get.useQuery(
    { wedge_id: params?.id || "" },
    { enabled: !!params?.id }
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-600">Loading wedge details...</p>
        </div>
      </div>
    );
  }

  if (!wedge) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-600">Wedge not found</p>
        </div>
      </div>
    );
  }

  const scoreFactors = [
    { label: "Pain Score", value: 0.8, color: "bg-red-500" },
    { label: "Spend Potential", value: 0.7, color: "bg-blue-500" },
    { label: "Growth Rate", value: 0.85, color: "bg-green-500" },
    { label: "Expandability", value: 0.75, color: "bg-purple-500" },
    { label: "Distribution", value: 0.6, color: "bg-orange-500" },
  ];

  const resistanceFactors = [
    { label: "Competition", value: 0.5, color: "bg-slate-500" },
    { label: "Capital Required", value: 0.4, color: "bg-slate-500" },
    { label: "Regulatory Friction", value: 0.3, color: "bg-slate-500" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <Button
            variant="ghost"
            className="mb-4 gap-2"
            onClick={() => window.history.back()}
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>

          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-slate-900 mb-2">
                {wedge.name}
              </h1>
              <p className="text-slate-600">
                Detected via <span className="font-semibold">{wedge.detector?.replace(/_/g, " ") || "Unknown"}</span>
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
              <div className="text-3xl font-bold text-slate-900">{wedge.score?.toFixed(1) || "N/A"}</div>
              <p className="text-xs text-slate-500 mt-1">Out of 100</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                To $10k MRR
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">{wedge.to_10k_mrr_months || "N/A"}mo</div>
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
              <div className="text-xl font-bold text-slate-900 capitalize">
                {wedge.enterprise_value || "N/A"}
              </div>
              <p className="text-xs text-slate-500 mt-1">Market potential</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Complexity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-xl font-bold text-slate-900 capitalize">
                {wedge.complexity || "N/A"}
              </div>
              <p className="text-xs text-slate-500 mt-1">Implementation difficulty</p>
            </CardContent>
          </Card>
        </div>

        {/* Score Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Driving Factors</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {scoreFactors.map((factor) => (
                <div key={factor.label}>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700">{factor.label}</span>
                    <span className="text-sm font-semibold text-slate-900">{(factor.value * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className={`${factor.color} h-2 rounded-full transition-all`}
                      style={{ width: `${factor.value * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Resistance Factors</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {resistanceFactors.map((factor) => (
                <div key={factor.label}>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700">{factor.label}</span>
                    <span className="text-sm font-semibold text-slate-900">{(factor.value * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className={`${factor.color} h-2 rounded-full transition-all`}
                      style={{ width: `${factor.value * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Evidence Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Evidence & Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {wedge.evidence && Object.entries(wedge.evidence).length > 0 ? (
                Object.entries(wedge.evidence).map(([key, value]: any) => (
                  <div key={key} className="border-l-4 border-blue-500 pl-4 py-2">
                    <h4 className="font-semibold text-slate-900 capitalize">{key.replace(/_/g, " ")}</h4>
                    <p className="text-sm text-slate-600 mt-1">{String(value)}</p>
                  </div>
                ))
              ) : (
                <p className="text-slate-600">No evidence data available</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
