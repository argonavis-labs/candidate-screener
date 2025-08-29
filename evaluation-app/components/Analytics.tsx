'use client';

import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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

  // Prepare scatter plot data
  const scatterData = analytics.validComparisons.map(d => ({
    x: d.humanScore,
    y: d.aiScore,
    candidate: d.candidateId,
  }));

  return (
    <div className="space-y-6">
      {/* Summary Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-1">
            <CardDescription className="leading-tight">Average Gap</CardDescription>
            <CardTitle className="text-2xl tracking-tight">
              {analytics.averageGap.toFixed(2)}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardDescription className="leading-tight">Correlation</CardDescription>
            <CardTitle className="text-2xl tracking-tight">
              {analytics.correlation.toFixed(3)}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardDescription className="leading-tight">AI Bias</CardDescription>
            <CardTitle className="text-2xl tracking-tight">
              {analytics.bias > 0 ? '+' : ''}{analytics.bias.toFixed(2)}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardDescription className="leading-tight">Within ±0.5</CardDescription>
            <CardTitle className="text-2xl tracking-tight">
              {analytics.accuracyRate.toFixed(0)}%
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Tabs defaultValue="chart" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chart">Scatter Plot</TabsTrigger>
          <TabsTrigger value="table">Comparison Table</TabsTrigger>
          <TabsTrigger value="dimensions">Per-Dimension Analysis</TabsTrigger>
        </TabsList>

        {/* Scatter Plot */}
        <TabsContent value="chart">
          <Card>
            <CardHeader>
              <CardTitle className="tracking-tight">Human vs AI Scores</CardTitle>
              <CardDescription className="leading-relaxed">
                Each point represents a candidate. Points on the diagonal line indicate perfect agreement.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="x" 
                      type="number" 
                      domain={[1, 4]} 
                      name="Human Score"
                      label={{ value: 'Human Score', position: 'insideBottom', offset: -10 }}
                    />
                    <YAxis 
                      dataKey="y" 
                      type="number" 
                      domain={[1, 4]} 
                      name="AI Score"
                      label={{ value: 'AI Score', angle: -90, position: 'insideLeft' }}
                    />
                    <ReferenceLine 
                      x={1} 
                      y={1} 
                      stroke="hsl(var(--muted-foreground))" 
                      strokeDasharray="5 5"
                      segment={[{ x: 1, y: 1 }, { x: 4, y: 4 }]}
                    />
                    <Tooltip 
                      content={({ active, payload }) => {
                        if (active && payload && payload.length > 0) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-background rounded p-2 shadow-lg">
                              <p className="font-semibold">Candidate {data.candidate}</p>
                              <p className="text-sm">Human: {data.x.toFixed(2)}</p>
                              <p className="text-sm">AI: {data.y.toFixed(2)}</p>
                              <p className="text-sm">Gap: {Math.abs(data.x - data.y).toFixed(2)}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Scatter 
                      name="Candidates" 
                      data={scatterData} 
                      fill="hsl(var(--primary))"
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Comparison Table */}
        <TabsContent value="table">
          <Card>
            <CardHeader>
              <CardTitle>Detailed Comparison</CardTitle>
              <CardDescription>
                All candidates with their human and AI scores
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <table className="w-full">
                  <thead>
                    <tr>
                      <th className="text-left p-2">Candidate</th>
                      <th className="text-center p-2">Human Score</th>
                      <th className="text-center p-2">AI Score</th>
                      <th className="text-center p-2">Gap</th>
                      <th className="text-center p-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.comparisonData.map(row => (
                      <tr key={row.candidateId}>
                        <td className="p-2">{row.candidateId}</td>
                        <td className="text-center p-2">
                          {row.hasHuman ? row.humanScore?.toFixed(2) : '-'}
                        </td>
                        <td className="text-center p-2">
                          {row.hasAi ? row.aiScore?.toFixed(2) : '-'}
                        </td>
                        <td className="text-center p-2">
                          {row.gap !== null ? (
                            <Badge variant={row.gap <= 0.5 ? 'default' : row.gap <= 1 ? 'secondary' : 'destructive'}>
                              {row.gap.toFixed(2)}
                            </Badge>
                          ) : '-'}
                        </td>
                        <td className="text-center p-2">
                          {!row.hasHuman ? (
                            <Badge variant="outline">No Human</Badge>
                          ) : !row.hasAi ? (
                            <Badge variant="outline">No AI</Badge>
                          ) : (
                            <Badge variant="default">Complete</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Per-Dimension Analysis */}
        <TabsContent value="dimensions">
          <Card>
            <CardHeader>
              <CardTitle>Per-Dimension Analysis</CardTitle>
              <CardDescription>
                Breaking down the comparison by evaluation criteria
              </CardDescription>
            </CardHeader>
            <CardContent>
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
            </CardContent>
          </Card>
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
