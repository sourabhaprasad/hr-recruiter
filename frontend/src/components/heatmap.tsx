"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface HeatmapData {
  skill: string;
  demand: number;
  supply: number;
  gap: number;
}

interface HeatmapProps {
  jdId?: number;
}

export default function SkillHeatmap({ jdId }: HeatmapProps) {
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHeatmapData();
  }, [jdId]);

  const fetchHeatmapData = async () => {
    try {
      const url = jdId
        ? `http://localhost:8000/dashboard/skills-heatmap?jd_id=${jdId}`
        : "http://localhost:8000/dashboard/skills-heatmap";

      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setHeatmapData(data.skills || []);
      }
    } catch (error) {
      console.error("Error fetching heatmap data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getIntensityColor = (value: number) => {
    // Normalize value between 0 and 1
    const intensity = Math.min(Math.max(value, 0), 1);

    if (intensity < 0.2) return "bg-green-100 text-green-800";
    if (intensity < 0.4) return "bg-yellow-100 text-yellow-800";
    if (intensity < 0.6) return "bg-orange-100 text-orange-800";
    if (intensity < 0.8) return "bg-red-100 text-red-800";
    return "bg-red-200 text-red-900";
  };

  const getGapColor = (gap: number) => {
    if (gap <= 0) return "bg-green-100 text-green-800";
    if (gap < 0.3) return "bg-yellow-100 text-yellow-800";
    if (gap < 0.6) return "bg-orange-100 text-orange-800";
    return "bg-red-100 text-red-800";
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Skills Gap Heatmap</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Skills Gap Heatmap</CardTitle>
        <p className="text-sm text-gray-600">
          Visual representation of skill demand vs supply in candidate pool
        </p>
      </CardHeader>
      <CardContent>
        {heatmapData.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>No skill data available</p>
            <p className="text-sm">
              Upload job descriptions and resumes to see skill gaps
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Legend */}
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-100 rounded"></div>
                <span>Low Gap</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-100 rounded"></div>
                <span>Medium Gap</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-100 rounded"></div>
                <span>High Gap</span>
              </div>
            </div>

            {/* Heatmap Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {heatmapData.map((item, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${getGapColor(
                    item.gap
                  )} transition-all hover:shadow-md`}
                >
                  <div className="font-medium text-sm mb-2">{item.skill}</div>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span>Demand:</span>
                      <span className="font-medium">
                        {Math.round(item.demand * 100)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Supply:</span>
                      <span className="font-medium">
                        {Math.round(item.supply * 100)}%
                      </span>
                    </div>
                    <div className="flex justify-between border-t pt-1">
                      <span>Gap:</span>
                      <span className="font-bold">
                        {Math.round(item.gap * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Summary Stats */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">Summary</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-600">Total Skills</div>
                  <div className="font-bold text-lg">{heatmapData.length}</div>
                </div>
                <div>
                  <div className="text-gray-600">High Gap Skills</div>
                  <div className="font-bold text-lg text-red-600">
                    {heatmapData.filter((item) => item.gap > 0.6).length}
                  </div>
                </div>
                <div>
                  <div className="text-gray-600">Avg Gap</div>
                  <div className="font-bold text-lg">
                    {Math.round(
                      (heatmapData.reduce((sum, item) => sum + item.gap, 0) /
                        heatmapData.length) *
                        100
                    )}
                    %
                  </div>
                </div>
                <div>
                  <div className="text-gray-600">Critical Skills</div>
                  <div className="font-bold text-lg text-orange-600">
                    {heatmapData.filter((item) => item.gap > 0.8).length}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
