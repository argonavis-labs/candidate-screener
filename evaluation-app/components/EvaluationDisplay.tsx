'use client';

import { Evaluation } from '@/lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';

interface EvaluationDisplayProps {
  evaluation: Evaluation | null;
  isVisible: boolean;
}

export default function EvaluationDisplay({ evaluation, isVisible }: EvaluationDisplayProps) {
  if (!isVisible) {
    return (
      <Card className="h-full">
        <CardContent className="h-full flex items-center justify-center">
          <p className="text-muted-foreground text-sm">AI Evaluation Hidden</p>
        </CardContent>
      </Card>
    );
  }

  if (!evaluation) {
    return (
      <Card className="h-full">
        <CardContent className="h-full flex items-center justify-center">
          <p className="text-muted-foreground text-sm">No AI evaluation available</p>
        </CardContent>
      </Card>
    );
  }

  const getScoreBadgeVariant = (score: number): "default" | "secondary" | "destructive" | "outline" => {
    if (score >= 3.5) return 'default';
    if (score >= 2.5) return 'secondary';
    if (score >= 1.5) return 'outline';
    return 'destructive';
  };

  const criteriaOrder = ['typography', 'layout_composition', 'color'] as const;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="space-y-1">
          <CardTitle className="text-lg">AI Evaluation</CardTitle>
          <CardDescription className="text-xs">
            {evaluation.portfolio_category} • {new Date(evaluation.evaluated_at).toLocaleDateString()}
          </CardDescription>
        </div>
        
        <div className="flex items-center gap-3 pt-2">
          <div className="flex flex-col">
            <span className="text-xs text-muted-foreground">Score</span>
            <Badge variant={getScoreBadgeVariant(evaluation.overall_weighted_score)} className="mt-1">
              {evaluation.overall_weighted_score.toFixed(2)}
            </Badge>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-muted-foreground">Confidence</span>
            <Badge variant="outline" className="mt-1">
              {evaluation.overall_confidence.toFixed(1)}
            </Badge>
          </div>
        </div>

        {evaluation.red_flags.length > 0 && (
          <>
            <Separator className="my-2" />
            <div className="space-y-1">
              <p className="text-xs font-medium text-destructive">Red Flags</p>
              <div className="flex flex-wrap gap-1">
                {evaluation.red_flags.map((flag, index) => (
                  <Badge key={index} variant="destructive" className="text-xs py-0">
                    {flag.replace(/_/g, ' ')}
                  </Badge>
                ))}
              </div>
            </div>
          </>
        )}
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden pb-3">
        <Tabs defaultValue="typography" className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-3 h-8">
            {criteriaOrder.map(criterion => (
              <TabsTrigger key={criterion} value={criterion} className="text-xs py-1">
                <span className="hidden sm:inline">{criterion.replace('_', ' ')}</span>
                <span className="sm:hidden">{criterion.charAt(0).toUpperCase()}</span>
                <Badge variant={getScoreBadgeVariant(evaluation.criteria[criterion].score)} className="ml-1 h-4 px-1 text-xs">
                  {evaluation.criteria[criterion].score}
                </Badge>
              </TabsTrigger>
            ))}
          </TabsList>

          <ScrollArea className="flex-1 mt-3">
            {criteriaOrder.map(criterion => (
              <TabsContent key={criterion} value={criterion} className="mt-0 space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium capitalize">
                      {criterion.replace('_', ' ')}
                    </h4>
                    <div className="flex gap-2">
                      <Badge variant={getScoreBadgeVariant(evaluation.criteria[criterion].score)}>
                        Score: {evaluation.criteria[criterion].score}
                      </Badge>
                      <Badge variant="outline">
                        Conf: {evaluation.criteria[criterion].confidence}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {evaluation.criteria[criterion].explanation}
                  </p>
                </div>
              </TabsContent>
            ))}
          </ScrollArea>
        </Tabs>
      </CardContent>
    </Card>
  );
}