"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import {
  ArrowLeft,
  Users,
  AlertTriangle,
  TrendingUp,
  RefreshCw,
  Eye,
  UserCheck,
  BarChart3,
  PieChart,
  Activity,
} from "lucide-react";
import Link from "next/link";
import AIChat from "@/components/ai-chat";
import SkillHeatmap from "@/components/heatmap";

interface Candidate {
  id: number;
  name: string;
  email: string;
  overall_score: number;
  skills_match_score: number;
  experience_match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  skill_gaps: any[];
  experience_years: number;
  education: string;
  gender: string;
  status: string;
  is_shortlisted: boolean;
  jd_title: string;
  jd_id?: number;
}

interface BiasAlert {
  type: string;
  description: string;
  severity: string;
}

interface DiversityMetrics {
  gender_distribution: Record<string, number>;
  experience_distribution: Record<string, number>;
  education_distribution: Record<string, number>;
}

interface Insights {
  total_candidates: number;
  shortlisted_candidates: number;
  average_score: number;
  bias_alerts: BiasAlert[];
  diversity_metrics: DiversityMetrics;
  risk_heatmap: Record<string, number>;
  diversity_score: number;
  sentiment_data: Record<string, number>;
}

export default function DashboardPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [selectedCandidates, setSelectedCandidates] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [shortlistLoading, setShortlistLoading] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(
    null
  );

  const updateCandidateStatus = async (candidateId: number, status: string) => {
    try {
      const response = await fetch("http://localhost:8000/candidate/status", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          candidate_id: candidateId,
          status: status,
        }),
      });
      
      if (response.ok) {
        // Immediately update the local state to reflect the change
        setCandidates(prevCandidates => 
          prevCandidates.map(candidate => 
            candidate.id === candidateId 
              ? { ...candidate, status: status, is_shortlisted: status === "shortlisted" }
              : candidate
          )
        );

        // Update insights to reflect the new shortlisted count
        if (insights) {
          const oldCandidate = candidates.find(c => c.id === candidateId);
          const wasShortlisted = oldCandidate?.status === "shortlisted";
          const isNowShortlisted = status === "shortlisted";
          
          if (!wasShortlisted && isNowShortlisted) {
            // Candidate was just shortlisted
            setInsights(prevInsights => ({
              ...prevInsights!,
              shortlisted_candidates: prevInsights!.shortlisted_candidates + 1
            }));
          } else if (wasShortlisted && !isNowShortlisted) {
            // Candidate was un-shortlisted
            setInsights(prevInsights => ({
              ...prevInsights!,
              shortlisted_candidates: Math.max(0, prevInsights!.shortlisted_candidates - 1)
            }));
          }
        }

        // Also refresh data to ensure consistency
        fetchData();
      } else {
        const errorText = await response.text();
        console.error("API error:", response.status, errorText);
      }
    } catch (error) {
      console.error("Error updating candidate status:", error);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [candidatesRes, insightsRes] = await Promise.all([
        fetch("http://localhost:8000/dashboard/candidates"),
        fetch("http://localhost:8000/dashboard/insights"),
      ]);

      const candidatesData = await candidatesRes.json();
      const insightsData = await insightsRes.json();

      setCandidates(candidatesData);
      setInsights(insightsData);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleCandidateSelect = (candidateId: number, checked: boolean) => {
    if (checked) {
      setSelectedCandidates([...selectedCandidates, candidateId]);
    } else {
      setSelectedCandidates(
        selectedCandidates.filter((id) => id !== candidateId)
      );
    }
  };

  const handleShortlist = async () => {
    if (selectedCandidates.length === 0) return;

    setShortlistLoading(true);
    try {
      // Assuming we're working with the first JD for now
      const response = await fetch(
        "http://localhost:8000/dashboard/shortlist",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            candidate_ids: selectedCandidates,
            jd_id: 1, // This should be dynamic based on selected JD
          }),
        }
      );

      if (response.ok) {
        // Immediately update local state for selected candidates
        setCandidates(prevCandidates => 
          prevCandidates.map(candidate => 
            selectedCandidates.includes(candidate.id)
              ? { ...candidate, status: "shortlisted", is_shortlisted: true }
              : candidate
          )
        );

        // Update insights to reflect the new shortlisted count
        if (insights) {
          const newlyShortlistedCount = selectedCandidates.filter(id => {
            const candidate = candidates.find(c => c.id === id);
            return candidate?.status !== "shortlisted";
          }).length;

          setInsights(prevInsights => ({
            ...prevInsights!,
            shortlisted_candidates: prevInsights!.shortlisted_candidates + newlyShortlistedCount
          }));
        }

        setSelectedCandidates([]);
        alert("Candidates shortlisted successfully!");
        
        // Also refresh data to ensure consistency
        await fetchData();
      }
    } catch (error) {
      console.error("Error shortlisting candidates:", error);
      alert("Error shortlisting candidates");
    } finally {
      setShortlistLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-yellow-600" />
          <p>
            No data available. Please upload job descriptions and resumes first.
          </p>
          <Link href="/" className="text-blue-600 hover:underline mt-2 block">
            Go to Homepage
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Link>
            <h1 className="text-3xl font-bold">HR Dashboard</h1>
          </div>
          <div className="flex gap-2">
            <Button onClick={fetchData} variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
            {selectedCandidates.length > 0 && (
              <Button
                onClick={handleShortlist}
                disabled={shortlistLoading}
                className="bg-green-600 hover:bg-green-700"
              >
                <UserCheck className="mr-2 h-4 w-4" />
                Shortlist {selectedCandidates.length} Candidate
                {selectedCandidates.length !== 1 ? "s" : ""}
              </Button>
            )}
          </div>
        </div>

        {/* Key Metrics */}
        {insights && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Total Candidates
                    </p>
                    <p className="text-2xl font-bold">
                      {insights.total_candidates}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Shortlisted
                    </p>
                    <p className="text-2xl font-bold">
                      {insights.shortlisted_candidates}
                    </p>
                  </div>
                  <UserCheck className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Average Score
                    </p>
                    <p className="text-2xl font-bold">
                      {insights.average_score}
                    </p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Diversity Score
                    </p>
                    <p className="text-2xl font-bold">
                      {insights.diversity_score}%
                    </p>
                  </div>
                  <PieChart className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Bias Alerts */}
        {insights?.bias_alerts && insights.bias_alerts.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="h-5 w-5" />
                Bias Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {insights.bias_alerts.map((alert, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-md border ${getSeverityColor(
                      alert.severity
                    )}`}
                  >
                    <p className="font-medium">
                      {alert.type.toUpperCase()} BIAS DETECTED
                    </p>
                    <p className="text-sm">{alert.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Risk Heatmap */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {insights?.risk_heatmap ? (
                Object.entries(insights.risk_heatmap).map(
                  ([department, risk]) => (
                    <div key={department} className="p-3 rounded-lg border">
                      <div className="text-sm font-medium">{department}</div>
                      <div
                        className={`text-lg font-bold ${
                          risk > 25
                            ? "text-red-600"
                            : risk > 15
                            ? "text-yellow-600"
                            : "text-green-600"
                        }`}
                      >
                        {risk}%
                      </div>
                    </div>
                  )
                )
              ) : (
                <p className="text-sm text-gray-500 col-span-full">
                  No risk data available
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Candidate Ranking Table */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Candidate Ranking
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">
                      <Checkbox
                        checked={
                          selectedCandidates.length === candidates.length &&
                          candidates.length > 0
                        }
                        onCheckedChange={(checked: boolean) => {
                          if (checked) {
                            setSelectedCandidates(candidates.map((c) => c.id));
                          } else {
                            setSelectedCandidates([]);
                          }
                        }}
                      />
                    </th>
                    <th className="text-left py-3 px-4">Name</th>
                    <th className="text-left py-3 px-4">Overall Score</th>
                    <th className="text-left py-3 px-4">Skills Match</th>
                    <th className="text-left py-3 px-4">Experience</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.map((candidate, index) => (
                    <tr
                      key={`${candidate.id}-${candidate.jd_id}-${index}`}
                      className="border-b hover:bg-gray-50"
                    >
                      <td className="py-3 px-4">
                        <Checkbox
                          checked={selectedCandidates.includes(candidate.id)}
                          onCheckedChange={(checked: boolean) =>
                            handleCandidateSelect(candidate.id, checked)
                          }
                        />
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <p className="font-medium">{candidate.name}</p>
                          <p className="text-sm text-gray-600">
                            {candidate.email}
                          </p>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span
                            className={`font-bold ${getScoreColor(
                              candidate.overall_score
                            )}`}
                          >
                            {(candidate.overall_score * 100).toFixed(0)}%
                          </span>
                          <Progress
                            value={candidate.overall_score * 100}
                            className="w-16 h-2"
                          />
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={getScoreColor(
                            candidate.skills_match_score
                          )}
                        >
                          {(candidate.skills_match_score * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {candidate.experience_years
                          ? `${candidate.experience_years} years`
                          : "N/A"}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Badge
                            className={
                              candidate.status === "shortlisted"
                                ? "bg-green-100 text-green-800"
                                : candidate.status === "rejected"
                                ? "bg-red-100 text-red-800"
                                : candidate.status === "accepted"
                                ? "bg-blue-100 text-blue-800"
                                : "bg-gray-100 text-gray-800"
                            }
                          >
                            {candidate.status || "pending"}
                          </Badge>
                          <select
                            value={candidate.status || "pending"}
                            onChange={(e) =>
                              updateCandidateStatus(candidate.id, e.target.value)
                            }
                            className="text-xs border border-gray-300 rounded px-1 py-0.5 ml-2"
                          >
                            <option value="pending">Pending</option>
                            <option value="shortlisted">Shortlisted</option>
                            <option value="rejected">Rejected</option>
                            <option value="accepted">Accepted</option>
                          </select>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setSelectedCandidate(candidate)}
                            >
                              <Eye className="mr-1 h-3 w-3" />
                              Details
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>
                                {candidate.name} - Match Details
                              </DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <p className="text-sm font-medium">
                                    Overall Score
                                  </p>
                                  <p className="text-2xl font-bold text-blue-600">
                                    {(candidate.overall_score * 100).toFixed(0)}
                                    %
                                  </p>
                                </div>
                                <div>
                                  <p className="text-sm font-medium">
                                    Job Position
                                  </p>
                                  <p className="font-medium">
                                    {candidate.jd_title}
                                  </p>
                                </div>
                              </div>

                              <div>
                                <p className="text-sm font-medium mb-2">
                                  Matched Skills
                                </p>
                                <div className="flex flex-wrap gap-1">
                                  {candidate.matched_skills?.map(
                                    (skill, index) => (
                                      <Badge
                                        key={index}
                                        className="bg-green-100 text-green-800"
                                      >
                                        {skill}
                                      </Badge>
                                    )
                                  )}
                                </div>
                              </div>

                              <div>
                                <p className="text-sm font-medium mb-2">
                                  Missing Skills
                                </p>
                                <div className="flex flex-wrap gap-1">
                                  {candidate.missing_skills?.map(
                                    (skill, index) => (
                                      <Badge
                                        key={index}
                                        className="bg-red-100 text-red-800"
                                      >
                                        {skill}
                                      </Badge>
                                    )
                                  )}
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <p>
                                    <strong>Experience:</strong>{" "}
                                    {candidate.experience_years || "N/A"} years
                                  </p>
                                  <p>
                                    <strong>Education:</strong>{" "}
                                    {candidate.education || "N/A"}
                                  </p>
                                </div>
                                <div>
                                  <p>
                                    <strong>Skills Match:</strong>{" "}
                                    {(
                                      candidate.skills_match_score * 100
                                    ).toFixed(0)}
                                    %
                                  </p>
                                  <p>
                                    <strong>Experience Match:</strong>{" "}
                                    {(
                                      candidate.experience_match_score * 100
                                    ).toFixed(0)}
                                    %
                                  </p>
                                </div>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Diversity Metrics */}
        {insights?.diversity_metrics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Gender Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {insights?.diversity_metrics?.gender_distribution ? (
                    Object.entries(
                      insights.diversity_metrics.gender_distribution
                    ).map(([gender, percentage]) => (
                      <div
                        key={gender}
                        className="flex justify-between items-center"
                      >
                        <span className="capitalize text-sm">{gender}</span>
                        <span className="font-medium">{percentage}%</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">
                      No gender data available
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">
                  Experience Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {insights?.diversity_metrics?.experience_distribution ? (
                    Object.entries(
                      insights.diversity_metrics.experience_distribution
                    ).map(([range, percentage]) => (
                      <div
                        key={range}
                        className="flex justify-between items-center"
                      >
                        <span className="text-sm">{range} years</span>
                        <span className="font-medium">{percentage}%</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">
                      No experience data available
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">
                  Education Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {insights?.diversity_metrics?.education_distribution ? (
                    Object.entries(
                      insights.diversity_metrics.education_distribution
                    ).map(([education, percentage]) => (
                      <div
                        key={education}
                        className="flex justify-between items-center"
                      >
                        <span className="text-sm">{education}</span>
                        <span className="font-medium">{percentage}%</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">
                      No education data available
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Skills Heatmap */}
        <div className="mt-6">
          <SkillHeatmap />
        </div>

        {/* AI Assistant */}
        <div className="mt-6">
          <AIChat />
        </div>
      </div>
    </div>
  );
}
