"use client";

import { Evaluation } from "@/lib/types";

import { Separator } from "@/components/ui/separator";

interface EvaluationDisplayProps {
  evaluation: Evaluation | null;
  isVisible: boolean;
}

export default function EvaluationDisplay({
  evaluation,
  isVisible,
}: EvaluationDisplayProps) {
  if (!isVisible) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-muted-foreground text-sm">AI Evaluation Hidden</p>
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-muted-foreground text-sm">
          No AI evaluation available
        </p>
      </div>
    );
  }

  const criteriaOrder = ["typography", "layout_composition", "color"] as const;

  return (
    <div className="">
      {/* Header */}
      <div className="">
        <div className="flex flex-row justify-between items-center px-4 pb-4">
          <div className="flex flex-col">
            <h2 className="text-base font-semibold tracking-tight">
              AI Evaluation
            </h2>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Category: {evaluation.portfolio_category} •{" "}
              {new Date(evaluation.evaluated_at).toLocaleDateString()} •{" "}
              Confidence: {evaluation.overall_confidence.toFixed(1)}
            </p>
          </div>

          <div className="flex items-center gap-6 divide-gray-200 ">
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground">Score</span>
              <span className="text-base font-semibold">
                {evaluation.overall_weighted_score.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        {evaluation.red_flags.length > 0 && (
          <>
            <Separator className="my-2" />
            <div className="space-y-1">
              <p className="text-xs font-medium text-destructive">Red Flags</p>
              <div className="flex flex-wrap gap-1">
                {evaluation.red_flags.map((flag, index) => (
                  <span key={index} className="text-xs text-destructive">
                    {flag.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Content */}
      <div className="space-y-4 px-4">
        {/* Show all criteria at once */}
        {criteriaOrder.map((criterion, index) => (
          <div key={criterion}>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium capitalize">
                  {criterion.replace("_", " ")}
                </h4>
                <div className="flex gap-2 text-sm items-center">
                  <span className="text-xs text-muted-foreground">
                    Confidence {evaluation.criteria[criterion].confidence}
                  </span>
                  <span className="font-semibold">
                    Score: {evaluation.criteria[criterion].score}
                  </span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                {evaluation.criteria[criterion].explanation}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
