'use client';

import { useState, useEffect } from 'react';
import { HumanEvaluation, Rubric } from '@/lib/types';
import { Save } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

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
const SCORE_LABELS = ['Terrible', 'Below average', 'Average', 'Above average', 'Fantastic'];

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
      portfolio_category: 'Minimal',
      image_filename: imageFilename,
      evaluated_at: new Date().toISOString(),
      criteria: {
        typography: { score: 3, explanation: '', confidence: 3 },
        layout_composition: { score: 3, explanation: '', confidence: 3 },
        color: { score: 3, explanation: '', confidence: 3 },
      },
      overall_weighted_score: 3,
      overall_confidence: 3,
      red_flags: [],
    };
  });

  const [saving, setSaving] = useState(false);

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
        portfolio_category: 'Minimal',
        image_filename: imageFilename,
        evaluated_at: new Date().toISOString(),
        criteria: {
          typography: { score: 3, explanation: '', confidence: 3 },
          layout_composition: { score: 3, explanation: '', confidence: 3 },
          color: { score: 3, explanation: '', confidence: 3 },
        },
        overall_weighted_score: 3,
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

      const typographyScore = evaluation.criteria.typography?.score ?? 3;
      const layoutScore = evaluation.criteria.layout_composition?.score ?? 3;
      const colorScore = evaluation.criteria.color?.score ?? 3;

      const baseScore = 
        typographyScore * weights.typography +
        layoutScore * weights.layout_composition +
        colorScore * weights.color;

      // Apply red flag penalties
      const penaltyWeights: Record<string, number> = {
        'template_scent_high': 0.5,
        'sloppy_images': 0.3,
        'process_soup': 0.2,
      };
      
      const totalPenalty = evaluation.red_flags.reduce((sum, flag) => {
        return sum + (penaltyWeights[flag] || 0);
      }, 0);
      
      const weightedScore = baseScore - totalPenalty;  // Allow scores to go below 0

      const typographyConfidence = evaluation.criteria.typography?.confidence ?? 3;
      const layoutConfidence = evaluation.criteria.layout_composition?.confidence ?? 3;
      const colorConfidence = evaluation.criteria.color?.confidence ?? 3;

      const avgConfidence = 
        (typographyConfidence + layoutConfidence + colorConfidence) / 3;

      setEvaluation(prev => ({
        ...prev,
        base_weighted_score: parseFloat(baseScore.toFixed(2)),
        penalty_applied: totalPenalty,
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
    evaluation.red_flags,
    rubric,
  ]);

  const handleSave = async () => {
    setSaving(true);
    try {
      // Set all confidence scores to 5 for human evaluations (max confidence)
      const evaluationWithConfidence = {
        ...evaluation,
        evaluated_at: new Date().toISOString(),
        criteria: {
          typography: { ...evaluation.criteria.typography, confidence: 5 },
          layout_composition: { ...evaluation.criteria.layout_composition, confidence: 5 },
          color: { ...evaluation.criteria.color, confidence: 5 },
        },
        overall_confidence: 5,
      };
      
      await onSave(evaluationWithConfidence);
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



  return (
    <div className="border-t border-stone-100 pt-4">
      {/* Header */}
      <div className="">
        <div className="flex flex-row justify-between items-center px-4 pb-4">
          <div className="flex flex-col">
            <h2 className="text-base font-semibold tracking-tight">Human Evaluation</h2>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Category: {evaluation.portfolio_category} • {new Date().toLocaleDateString()}
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground">Score</span>
              <span className="text-base font-semibold">
                {(evaluation.overall_weighted_score ?? 0).toFixed(2)}
                {evaluation.penalty_applied && evaluation.penalty_applied > 0 && (
                  <span className="text-xs text-orange-600 ml-1">
                    (-{evaluation.penalty_applied.toFixed(1)})
                  </span>
                )}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-4 px-4">
        {/* Show all criteria at once - no collapsing */}
        {(['typography', 'layout_composition', 'color'] as const).map((criterion, index) => (
          <div key={criterion} className="space-y-2">
            {/* Single row: criterion name + 1-4 toggle */}
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium capitalize">
                {criterion.replace('_', ' ')}
              </h4>
              
              <RadioGroup
                value={evaluation.criteria[criterion].score.toString()}
                onValueChange={(value) => updateCriterion(criterion, 'score', value)}
                className="flex gap-1"
              >
                {[1, 2, 3, 4, 5].map(score => (
                  <div key={score} className="flex items-center">
                    <RadioGroupItem 
                      value={score.toString()} 
                      id={`${criterion}-${score}`}
                      className="peer sr-only"
                    />
                    <Label
                      htmlFor={`${criterion}-${score}`}
                      className={cn(
                        "flex items-center justify-center w-6 h-6 text-xs rounded-md cursor-pointer transition-all",
                        "hover:bg-accent",
                        " peer-data-[state=checked]:bg-primary peer-data-[state=checked]:text-primary-foreground"
                      )}
                    >
                      <span className="font-bold">{score}</span>
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>

            {/* Explanation */}
            <div>
              <Textarea
                value={evaluation.criteria[criterion].explanation}
                onChange={(e) => updateCriterion(criterion, 'explanation', e.target.value)}
                className="min-h-[60px] text-xs"
                placeholder={`Explain your ${criterion.replace('_', ' ')} score...`}
              />
            </div>
          </div>
        ))}

        {/* Red Flags */}
        <div className="space-y-2 pt-2">
          <h4 className="text-sm font-medium">Red Flags</h4>
          <div className="space-y-2">
            {rubric?.rubric?.red_flags?.map((flag) => {
              const [flagKey, flagDescription] = flag.split(': ');
              return (
                <div key={flagKey} className="flex items-start space-x-2">
                  <Checkbox
                    id={flagKey}
                    checked={evaluation.red_flags.includes(flagKey)}
                    onCheckedChange={() => toggleRedFlag(flagKey)}
                    className="mt-0.5"
                  />
                  <div className="flex-1">
                    <Label
                      htmlFor={flagKey}
                      className="text-xs font-medium cursor-pointer"
                    >
                      {flagKey.replace(/_/g, ' ')}
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      {flagDescription}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
          {evaluation.red_flags.length > 0 && (
            <div className="text-xs text-orange-600 font-medium">
              Penalty: -{evaluation.red_flags.map((flag): number => 
                flag === 'template_scent_high' ? 0.5 : 
                flag === 'sloppy_images' ? 0.3 : 
                flag === 'process_soup' ? 0.2 : 0
              ).reduce((a: number, b: number) => a + b, 0).toFixed(1)} points
            </div>
          )}
        </div>

        {/* Save Button */}
        <div className="pt-4 flex items-center gap-2">
          <Select
            value={evaluation.portfolio_category}
            onValueChange={(value) => setEvaluation(prev => ({ ...prev, portfolio_category: value }))}
          >
            <SelectTrigger id="category" className="h-9 w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PORTFOLIO_CATEGORIES.map(cat => (
                <SelectItem key={cat} value={cat}>{cat}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={handleSave} disabled={saving} className="flex-1 gap-2">
            <Save className="h-4 w-4" />
            {saving ? 'Saving...' : 'Save Evaluation'}
          </Button>
        </div>
      </div>
    </div>
  );
}