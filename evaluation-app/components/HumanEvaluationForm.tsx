'use client';

import { useState, useEffect } from 'react';
import { HumanEvaluation, Rubric } from '@/lib/types';
import { Save, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

interface HumanEvaluationFormProps {
  candidateId: string;
  imageFilename: string;
  existingEvaluation: HumanEvaluation | null;
  rubric: Rubric | null;
  onSave: (evaluation: HumanEvaluation) => Promise<void>;
}

const PORTFOLIO_CATEGORIES = ['Unknown', 'Minimal', 'Standard', 'Elaborate'];
const SCORE_LABELS = ['Very bad', 'Below average', 'Above average', 'Great'];

export default function HumanEvaluationForm({
  candidateId,
  imageFilename,
  existingEvaluation,
  rubric,
  onSave,
}: HumanEvaluationFormProps) {
  const [evaluation, setEvaluation] = useState<HumanEvaluation>(() => {
    return existingEvaluation || {
      candidate_id: candidateId,
      portfolio_category: 'Unknown',
      image_filename: imageFilename,
      evaluated_at: new Date().toISOString(),
      criteria: {
        typography: { score: 2.5, explanation: '', confidence: 3 },
        layout_composition: { score: 2.5, explanation: '', confidence: 3 },
        color: { score: 2.5, explanation: '', confidence: 3 },
      },
      overall_weighted_score: 2.5,
      overall_confidence: 3,
      red_flags: [],
    };
  });

  const [saving, setSaving] = useState(false);
  const [expandedCriteria, setExpandedCriteria] = useState<Record<string, boolean>>({
    typography: false,
    layout_composition: false,
    color: false,
  });

  // Update evaluation when candidateId changes
  useEffect(() => {
    setEvaluation(prev => ({
      ...prev,
      candidate_id: candidateId,
      image_filename: imageFilename,
    }));
  }, [candidateId, imageFilename]);

  // Update evaluation when existingEvaluation changes
  useEffect(() => {
    if (existingEvaluation) {
      // Ensure all fields are defined when loading existing evaluation
      setEvaluation({
        ...existingEvaluation,
        overall_weighted_score: existingEvaluation.overall_weighted_score ?? 2.5,
        overall_confidence: existingEvaluation.overall_confidence ?? 3,
        criteria: {
          typography: {
            score: existingEvaluation.criteria?.typography?.score ?? 2.5,
            explanation: existingEvaluation.criteria?.typography?.explanation ?? '',
            confidence: existingEvaluation.criteria?.typography?.confidence ?? 3,
          },
          layout_composition: {
            score: existingEvaluation.criteria?.layout_composition?.score ?? 2.5,
            explanation: existingEvaluation.criteria?.layout_composition?.explanation ?? '',
            confidence: existingEvaluation.criteria?.layout_composition?.confidence ?? 3,
          },
          color: {
            score: existingEvaluation.criteria?.color?.score ?? 2.5,
            explanation: existingEvaluation.criteria?.color?.explanation ?? '',
            confidence: existingEvaluation.criteria?.color?.confidence ?? 3,
          },
        },
        red_flags: existingEvaluation.red_flags || [],
      });
    } else {
      // Reset to default for new candidate
      setEvaluation({
        candidate_id: candidateId,
        portfolio_category: 'Unknown',
        image_filename: imageFilename,
        evaluated_at: new Date().toISOString(),
        criteria: {
          typography: { score: 2.5, explanation: '', confidence: 3 },
          layout_composition: { score: 2.5, explanation: '', confidence: 3 },
          color: { score: 2.5, explanation: '', confidence: 3 },
        },
        overall_weighted_score: 2.5,
        overall_confidence: 3,
        red_flags: [],
      });
    }
  }, [existingEvaluation, candidateId, imageFilename]);

  // Calculate weighted score whenever criteria scores change
  useEffect(() => {
    if (rubric && evaluation.criteria) {
      const weights = {
        typography: 0.35,
        layout_composition: 0.35,
        color: 0.3,
      };

      const typographyScore = evaluation.criteria.typography?.score ?? 2.5;
      const layoutScore = evaluation.criteria.layout_composition?.score ?? 2.5;
      const colorScore = evaluation.criteria.color?.score ?? 2.5;

      const weightedScore = 
        typographyScore * weights.typography +
        layoutScore * weights.layout_composition +
        colorScore * weights.color;

      const typographyConfidence = evaluation.criteria.typography?.confidence ?? 3;
      const layoutConfidence = evaluation.criteria.layout_composition?.confidence ?? 3;
      const colorConfidence = evaluation.criteria.color?.confidence ?? 3;

      const avgConfidence = 
        (typographyConfidence + layoutConfidence + colorConfidence) / 3;

      setEvaluation(prev => ({
        ...prev,
        overall_weighted_score: parseFloat(weightedScore.toFixed(2)),
        overall_confidence: parseFloat(avgConfidence.toFixed(2)),
      }));
    }
  }, [
    evaluation.criteria?.typography?.score,
    evaluation.criteria?.typography?.confidence,
    evaluation.criteria?.layout_composition?.score,
    evaluation.criteria?.layout_composition?.confidence,
    evaluation.criteria?.color?.score,
    evaluation.criteria?.color?.confidence,
    rubric,
  ]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave({
        ...evaluation,
        evaluated_at: new Date().toISOString(),
      });
    } finally {
      setSaving(false);
    }
  };

  const updateCriterion = (
    criterion: 'typography' | 'layout_composition' | 'color',
    field: 'score' | 'explanation' | 'confidence',
    value: string | number
  ) => {
    setEvaluation(prev => ({
      ...prev,
      criteria: {
        ...prev.criteria,
        [criterion]: {
          ...prev.criteria[criterion],
          [field]: field === 'explanation' ? value : parseFloat(value as string),
        },
      },
    }));
  };

  const toggleRedFlag = (flag: string) => {
    setEvaluation(prev => ({
      ...prev,
      red_flags: prev.red_flags.includes(flag)
        ? prev.red_flags.filter(f => f !== flag)
        : [...prev.red_flags, flag],
    }));
  };

  const getScoreBadgeVariant = (score: number): "default" | "secondary" | "destructive" | "outline" => {
    if (score >= 3.5) return 'default';
    if (score >= 2.5) return 'secondary';
    if (score >= 1.5) return 'outline';
    return 'destructive';
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-base tracking-tight">Human Evaluation</CardTitle>
            <CardDescription className="text-xs leading-relaxed">
              Score: {(evaluation.overall_weighted_score ?? 0).toFixed(2)} • Confidence: {(evaluation.overall_confidence ?? 0).toFixed(1)}
            </CardDescription>
          </div>
          <Button onClick={handleSave} disabled={saving} size="sm" className="gap-1">
            <Save className="h-3 w-3" />
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </div>

        <div className="pt-2">
          <Label htmlFor="category" className="text-xs">Portfolio Category</Label>
          <Select
            value={evaluation.portfolio_category}
            onValueChange={(value) => setEvaluation(prev => ({ ...prev, portfolio_category: value }))}
          >
            <SelectTrigger id="category" className="h-8 mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PORTFOLIO_CATEGORIES.map(cat => (
                <SelectItem key={cat} value={cat}>{cat}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden pb-3">
        <ScrollArea className="h-full pr-3">
          <div className="space-y-3">
            {/* Criteria Evaluations */}
            {(['typography', 'layout_composition', 'color'] as const).map(criterion => (
              <div key={criterion} className="space-y-2">
                <div 
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setExpandedCriteria(prev => ({ ...prev, [criterion]: !prev[criterion] }))}
                >
                  <h4 className="text-sm font-medium capitalize tracking-tight">
                    {criterion.replace('_', ' ')}
                  </h4>
                  <div className="flex items-center gap-2">
                    <Badge variant={getScoreBadgeVariant(evaluation.criteria[criterion].score)}>
                      {evaluation.criteria[criterion].score}
                    </Badge>
                    {expandedCriteria[criterion] ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                  </div>
                </div>

                {expandedCriteria[criterion] && (
                  <div className="space-y-3 pl-2">
                    {/* Score */}
                    <div className="space-y-1">
                      <Label className="text-xs">Score</Label>
                      <RadioGroup
                        value={evaluation.criteria[criterion].score.toString()}
                        onValueChange={(value) => updateCriterion(criterion, 'score', value)}
                      >
                        <div className="grid grid-cols-4 gap-1">
                          {[1, 2, 3, 4].map(score => (
                            <div key={score} className="flex items-center">
                              <RadioGroupItem 
                                value={score.toString()} 
                                id={`${criterion}-${score}`}
                                className="peer sr-only"
                              />
                              <Label
                                htmlFor={`${criterion}-${score}`}
                                className={cn(
                                  "flex flex-col items-center justify-center w-full p-2 text-xs rounded-md cursor-pointer transition-all",
                                  "hover:bg-accent",
                                  " peer-data-[state=checked]:bg-primary peer-data-[state=checked]:text-primary-foreground"
                                )}
                              >
                                <span className="font-bold">{score}</span>
                                <span className="text-[10px] leading-tight opacity-70">{SCORE_LABELS[score - 1].split(' ')[0]}</span>
                              </Label>
                            </div>
                          ))}
                        </div>
                      </RadioGroup>
                    </div>

                    {/* Confidence */}
                    <div className="space-y-1">
                      <Label className="text-xs">Confidence</Label>
                      <RadioGroup
                        value={evaluation.criteria[criterion].confidence.toString()}
                        onValueChange={(value) => updateCriterion(criterion, 'confidence', value)}
                      >
                        <div className="grid grid-cols-4 gap-1">
                          {[1, 2, 3, 4].map(conf => (
                            <div key={conf} className="flex items-center">
                              <RadioGroupItem 
                                value={conf.toString()} 
                                id={`${criterion}-conf-${conf}`}
                                className="peer sr-only"
                              />
                              <Label
                                htmlFor={`${criterion}-conf-${conf}`}
                                className={cn(
                                  "flex items-center justify-center w-full p-1.5 text-xs rounded-md cursor-pointer transition-all",
                                  "hover:bg-accent",
                                  " peer-data-[state=checked]:bg-primary peer-data-[state=checked]:text-primary-foreground"
                                )}
                              >
                                {conf}
                              </Label>
                            </div>
                          ))}
                        </div>
                      </RadioGroup>
                    </div>

                    {/* Explanation */}
                    <div className="space-y-1">
                      <Label className="text-xs">Explanation</Label>
                      <Textarea
                        value={evaluation.criteria[criterion].explanation}
                        onChange={(e) => updateCriterion(criterion, 'explanation', e.target.value)}
                        className="min-h-[60px] text-xs"
                        placeholder="Add your reasoning..."
                      />
                    </div>

                    {/* Rubric Hints */}
                    {rubric && (
                      <div className="text-xs space-y-1 bg-muted/30 p-2 rounded">
                        <details className="cursor-pointer">
                          <summary className="font-medium text-green-700 dark:text-green-400">Good indicators</summary>
                          <ul className="mt-1 space-y-0.5 text-muted-foreground">
                            {rubric.rubric.dimensions.find(d => d.id === criterion)?.good_anchor.slice(0, 2).map((item, i) => (
                              <li key={i} className="pl-3">• {item}</li>
                            ))}
                          </ul>
                        </details>
                        <details className="cursor-pointer">
                          <summary className="font-medium text-red-700 dark:text-red-400">Weak indicators</summary>
                          <ul className="mt-1 space-y-0.5 text-muted-foreground">
                            {rubric.rubric.dimensions.find(d => d.id === criterion)?.weak_anchor.slice(0, 2).map((item, i) => (
                              <li key={i} className="pl-3">• {item}</li>
                            ))}
                          </ul>
                        </details>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}

            <Separator />

            {/* Red Flags */}
            {rubric && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Red Flags</h4>
                <div className="space-y-2">
                  {rubric.rubric.red_flags.map(flag => (
                    <div key={flag} className="flex items-start space-x-2">
                      <Checkbox
                        id={flag}
                        checked={evaluation.red_flags.includes(flag)}
                        onCheckedChange={() => toggleRedFlag(flag)}
                      />
                      <Label 
                        htmlFor={flag}
                        className="text-xs cursor-pointer leading-relaxed"
                      >
                        {flag.replace(/_/g, ' ')}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}