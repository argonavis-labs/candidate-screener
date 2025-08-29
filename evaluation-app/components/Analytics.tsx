'use client';

import { useState, useEffect, useMemo } from 'react';


import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart';
import { Scatter, ScatterChart, XAxis, YAxis, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { HumanRatings, Ratings } from '@/lib/types';

interface AnalyticsProps {
  humanRatings: HumanRatings;
  aiRatings: Ratings;
  selectedRun: string;
}

export default function Analytics({ humanRatings, aiRatings, selectedRun }: AnalyticsProps) {
  const [sortByGap, setSortByGap] = useState(false);
  const analytics = useMemo(() => {
    const candidateIds = [...new Set([
      ...Object.keys(humanRatings),
      ...Object.keys(aiRatings)
    ])].sort((a, b) => parseInt(a) - parseInt(b));

    // Calculate gaps and prepare data
    const comparisonData = candidateIds.map(id => {
      const human = humanRatings[id];
      const ai = aiRatings[id];
      
      if (!human || !ai) {
        return {
          candidateId: id,
          humanScore: human?.overall_weighted_score || null,
          aiScore: ai?.overall_weighted_score || null,
          gap: null,
          hasHuman: !!human,
          hasAi: !!ai,
        };
      }

      const gap = Math.abs((human.overall_weighted_score || 0) - (ai.overall_weighted_score || 0));
      
      return {
        candidateId: id,
        humanScore: human.overall_weighted_score || 0,
        aiScore: ai.overall_weighted_score || 0,
        gap: gap,
        hasHuman: true,
        hasAi: true,
        // Individual dimension scores for detailed analysis
        typography: {
          human: human.criteria?.typography?.score || 0,
          ai: ai.criteria?.typography?.score || 0,
          gap: Math.abs((human.criteria?.typography?.score || 0) - (ai.criteria?.typography?.score || 0))
        },
        layout: {
          human: human.criteria?.layout_composition?.score || 0,
          ai: ai.criteria?.layout_composition?.score || 0,
          gap: Math.abs((human.criteria?.layout_composition?.score || 0) - (ai.criteria?.layout_composition?.score || 0))
        },
        color: {
          human: human.criteria?.color?.score || 0,
          ai: ai.criteria?.color?.score || 0,
          gap: Math.abs((human.criteria?.color?.score || 0) - (ai.criteria?.color?.score || 0))
        }
      };
    });

    // Calculate statistics
    const validComparisons = comparisonData.filter(d => d.hasHuman && d.hasAi);
    const averageGap = validComparisons.length > 0
      ? validComparisons.reduce((sum, d) => sum + (d.gap || 0), 0) / validComparisons.length
      : 0;

    // Calculate correlation
    const humanScores = validComparisons.map(d => d.humanScore ?? 0);
    const aiScores = validComparisons.map(d => d.aiScore ?? 0);
    const correlation = calculateCorrelation(humanScores, aiScores);

    // Calculate bias (does AI consistently rate higher or lower?)
    const bias = validComparisons.length > 0
      ? validComparisons.reduce((sum, d) => sum + ((d.aiScore || 0) - (d.humanScore || 0)), 0) / validComparisons.length
      : 0;

    // Calculate accuracy within threshold
    const threshold = 0.5;
    const accurateWithinThreshold = validComparisons.filter(d => (d.gap || 0) <= threshold).length;
    const accuracyRate = validComparisons.length > 0
      ? (accurateWithinThreshold / validComparisons.length) * 100
      : 0;

    return {
      comparisonData,
      validComparisons,
      averageGap,
      correlation,
      bias,
      accuracyRate,
      totalCandidates: candidateIds.length,
      evaluatedByBoth: validComparisons.length,
    };
  }, [humanRatings, aiRatings]);

  // Prepare scatter plot data - separate datasets for human and AI
  const scatterPlotData = useMemo(() => {
    let dataToUse = analytics.comparisonData;
    let sortedCandidateIds: string[] = [];
    
    if (sortByGap) {
      // Sort by gap (smallest to largest), but only include candidates with both ratings
      const sortedData = analytics.validComparisons
        .sort((a, b) => (a.gap || 0) - (b.gap || 0));
      
      sortedCandidateIds = sortedData.map(d => d.candidateId);
      
      dataToUse = sortedData.map((d, index) => ({ ...d, sortIndex: index + 1 }));
    } else {
      // For normal view, ensure we have all candidates 1-54
      const allCandidateIds = Array.from({ length: 54 }, (_, i) => String(i + 1));
      dataToUse = allCandidateIds.map(id => {
        const existingData = analytics.comparisonData.find(d => d.candidateId === id);
        if (existingData) {
          return existingData;
        }
        // Create placeholder data for candidates without ratings
        return {
          candidateId: id,
          humanScore: null,
          aiScore: null,
          gap: null,
          hasHuman: false,
          hasAi: false,
        };
      });
    }
    
    const scatterDataHuman = dataToUse
      .filter(d => d.hasHuman && d.humanScore !== null)
      .map(d => ({
        x: sortByGap ? (d as any).sortIndex || parseInt(d.candidateId) : parseInt(d.candidateId),
        y: d.humanScore,
        candidate: d.candidateId,
        type: 'Human',
        gap: d.gap
      }));

    const scatterDataAI = dataToUse
      .filter(d => d.hasAi && d.aiScore !== null)
      .map(d => ({
        x: sortByGap ? (d as any).sortIndex || parseInt(d.candidateId) : parseInt(d.candidateId),
        y: d.aiScore,
        candidate: d.candidateId,
        type: 'AI',
        gap: d.gap
      }));
      
    return { 
      scatterDataHuman, 
      scatterDataAI, 
      maxX: sortByGap ? analytics.validComparisons.length : 54,
      sortedCandidateIds
    };
  }, [analytics.comparisonData, analytics.validComparisons, sortByGap]);

  return (
    <div className="space-y-6">
      {/* Summary Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-6 bg-card">
          <div className="pb-1">
            <p className="text-sm text-muted-foreground leading-tight">Average Gap</p>
            <h3 className="text-2xl font-semibold tracking-tight">
              {analytics.averageGap.toFixed(2)}
            </h3>
          </div>
        </div>
        <div className="p-6 bg-card">
          <div className="pb-1">
            <p className="text-sm text-muted-foreground leading-tight">Correlation</p>
            <h3 className="text-2xl font-semibold tracking-tight">
              {analytics.correlation.toFixed(3)}
            </h3>
          </div>
        </div>
        <div className="p-6 bg-card">
          <div className="pb-1">
            <p className="text-sm text-muted-foreground leading-tight">AI Bias</p>
            <h3 className="text-2xl font-semibold tracking-tight">
              {analytics.bias > 0 ? '+' : ''}{analytics.bias.toFixed(2)}
            </h3>
          </div>
        </div>
        <div className="p-6 bg-card">
          <div className="pb-1">
            <p className="text-sm text-muted-foreground leading-tight">Within ±0.5</p>
            <h3 className="text-2xl font-semibold tracking-tight">
              {analytics.accuracyRate.toFixed(0)}%
            </h3>
          </div>
        </div>
      </div>

      <Tabs defaultValue="chart" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chart">Scatter Plot</TabsTrigger>
          <TabsTrigger value="table">Comparison Table</TabsTrigger>
          <TabsTrigger value="dimensions">Per-Dimension Analysis</TabsTrigger>
        </TabsList>

        {/* Scatter Plot */}
        <TabsContent value="chart">
          <div className="p-6 bg-card">
            <div className="pb-4 flex justify-between items-start">
              <div>
                <h3 className="text-lg font-semibold tracking-tight">Candidate Ratings Comparison</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Human and AI ratings for each candidate. {sortByGap ? 'Sorted by agreement (smallest to largest gap).' : 'X-axis shows candidate IDs, Y-axis shows ratings.'}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="sort-by-gap"
                  checked={sortByGap}
                  onCheckedChange={setSortByGap}
                />
                <Label htmlFor="sort-by-gap" className="text-sm">
                  Sort by gap
                </Label>
              </div>
            </div>
            <div>
              <div className="h-[500px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="x" 
                      type="number" 
                      domain={[1, scatterPlotData.maxX]} 
                      name={sortByGap ? "Ranking by Gap" : "Candidate"}
                      label={{ value: sortByGap ? 'Ranking by Gap (Low → High)' : 'Candidate', position: 'insideBottom', offset: -10 }}
                      tickFormatter={(value) => {
                        if (sortByGap) {
                          const candidateId = scatterPlotData.sortedCandidateIds[value - 1];
                          return candidateId ? `C${candidateId}` : `${value}`;
                        }
                        return `C${value}`;
                      }}
                      ticks={Array.from({ length: scatterPlotData.maxX }, (_, i) => i + 1)}
                      interval={0}
                    />
                    <YAxis 
                      dataKey="y" 
                      type="number" 
                      domain={[1, 4]} 
                      name="Rating"
                      label={{ value: 'Rating', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      content={({ active, payload }) => {
                        if (active && payload && payload.length > 0) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-background rounded p-2 shadow-lg border">
                              <p className="font-semibold">Candidate {data.candidate}</p>
                              <p className="text-sm">{data.type}: {data.y.toFixed(2)}</p>
                              {sortByGap && data.gap !== null && (
                                <p className="text-sm text-muted-foreground">Gap: {data.gap.toFixed(2)}</p>
                              )}
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Legend />
                    <Scatter 
                      name="Human Ratings" 
                      data={scatterPlotData.scatterDataHuman} 
                      fill="#3b82f6"
                    />
                    <Scatter 
                      name="AI Ratings" 
                      data={scatterPlotData.scatterDataAI} 
                      fill="#ef4444"
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Comparison Table */}
        <TabsContent value="table">
          <div className="p-6 bg-card">
            <div className="pb-4">
              <h3 className="text-lg font-semibold">Detailed Comparison - {selectedRun}</h3>
              <p className="text-sm text-muted-foreground">
                Comparison table with candidates as columns and evaluation types as rows
              </p>
            </div>
            <div className="overflow-auto max-h-[600px]">
              <div className="min-w-max">
                <table className="border-collapse" style={{ minWidth: `${120 + (analytics.comparisonData.length * 80)}px` }}>
                    <thead>
                      <tr>
                        <th className="sticky left-0 bg-background border border-border p-3 text-left font-medium min-w-[120px]">
                          Evaluation Type
                        </th>
                        {analytics.comparisonData.map(candidate => (
                          <th key={candidate.candidateId} className="border border-border p-2 text-center font-medium min-w-[80px]">
                            C{candidate.candidateId}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {/* Human Ratings Row */}
                      <tr>
                        <td className="sticky left-0 bg-background border border-border p-3 font-medium">
                          Human Rating
                        </td>
                        {analytics.comparisonData.map(candidate => (
                          <td key={candidate.candidateId} className="border border-border p-2 text-center">
                            {candidate.hasHuman ? (
                              <span className="text-sm font-medium text-primary">
                                {candidate.humanScore?.toFixed(2)}
                              </span>
                            ) : (
                              <span className="text-xs text-muted-foreground">-</span>
                            )}
                          </td>
                        ))}
                      </tr>
                      
                      {/* AI Ratings Row */}
                      <tr>
                        <td className="sticky left-0 bg-background border border-border p-3 font-medium">
                          AI Rating
                        </td>
                        {analytics.comparisonData.map(candidate => (
                          <td key={candidate.candidateId} className="border border-border p-2 text-center">
                            {candidate.hasAi ? (
                              <span className="text-sm font-medium">
                                {candidate.aiScore?.toFixed(2)}
                              </span>
                            ) : (
                              <span className="text-xs text-muted-foreground">-</span>
                            )}
                          </td>
                        ))}
                      </tr>
                      
                      {/* Difference Row */}
                      <tr>
                        <td className="sticky left-0 bg-background border border-border p-3 font-medium">
                          Difference (|Human - AI|)
                        </td>
                        {analytics.comparisonData.map(candidate => (
                          <td key={candidate.candidateId} className="border border-border p-2 text-center">
                            {candidate.gap !== null ? (
                              <span className={`text-sm font-medium ${
                                candidate.gap <= 0.5 
                                  ? 'text-green-600' 
                                  : candidate.gap <= 1.0 
                                    ? 'text-yellow-600' 
                                    : 'text-red-600'
                              }`}>
                                {candidate.gap.toFixed(2)}
                              </span>
                            ) : (
                              <span className="text-xs text-muted-foreground">-</span>
                            )}
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
          </div>
        </TabsContent>

        {/* Per-Dimension Analysis */}
        <TabsContent value="dimensions">
          <div className="p-6 bg-card">
            <div className="pb-4">
              <h3 className="text-lg font-semibold">Per-Dimension Analysis</h3>
              <p className="text-sm text-muted-foreground">
                Breaking down the comparison by evaluation criteria
              </p>
            </div>
            <div>
              <div className="space-y-4">
                {(['typography', 'layout', 'color'] as const).map(dimension => {
                  const dimData = analytics.validComparisons
                    .filter(d => d[dimension as 'typography' | 'layout' | 'color'])
                    .map(d => d[dimension as 'typography' | 'layout' | 'color']!);
                  
                  const avgGap = dimData.length > 0
                    ? dimData.reduce((sum, d) => sum + d.gap, 0) / dimData.length
                    : 0;

                  return (
                    <div key={dimension} className="space-y-2">
                      <h4 className="font-medium capitalize">{dimension.replace('_', ' ')}</h4>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Average Gap</p>
                          <p className="text-xl font-semibold">{avgGap.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Max Gap</p>
                          <p className="text-xl font-semibold">
                            {dimData.length > 0 ? Math.max(...dimData.map(d => d.gap)).toFixed(2) : '0.00'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Perfect Matches</p>
                          <p className="text-xl font-semibold">
                            {dimData.filter(d => d.gap === 0).length}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Helper function to calculate Pearson correlation coefficient
function calculateCorrelation(x: number[], y: number[]): number {
  const n = x.length;
  if (n === 0) return 0;
  
  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
  const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
  const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
  
  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
  
  return denominator === 0 ? 0 : numerator / denominator;
}
