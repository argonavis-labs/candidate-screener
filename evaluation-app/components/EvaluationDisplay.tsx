"use client";

import { Evaluation } from "@/lib/types";

import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, AlertCircle, Info } from "lucide-react";

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
                {evaluation.penalty_applied &&
                  evaluation.penalty_applied > 0 && (
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
      {/* red flags */}
      {evaluation.red_flags.length > 0 && (
        <>
          <div className="space-y-2 px-4 mt-4">
            <div className="flex flex-wrap gap-1.5">
              {evaluation.red_flags.map((flag, index) => {
                // Get penalty amount and severity
                const getPenaltyInfo = (flag: string) => {
                  switch (flag) {
                    case "template_scent_high":
                      return {
                        penalty: 0.5,
                        label: "Template-like",
                        variant: "destructive" as const,
                        icon: AlertTriangle,
                        description: "Site feels like a template",
                      };
                    case "sloppy_images":
                      return {
                        penalty: 0.3,
                        label: "Sloppy Images",
                        variant: "secondary" as const,
                        icon: AlertCircle,
                        description: "Poor image layout/quality",
                      };
                    case "process_soup":
                      return {
                        penalty: 0.2,
                        label: "Process Heavy",
                        variant: "outline" as const,
                        icon: Info,
                        description: "Too much process content",
                      };
                    default:
                      return {
                        penalty: 0,
                        label: flag.replace(/_/g, " "),
                        variant: "outline" as const,
                        icon: Info,
                        description: "",
                      };
                  }
                };

                const flagInfo = getPenaltyInfo(flag);
                const Icon = flagInfo.icon;

                return (
                  <Badge
                    key={index}
                    variant={flagInfo.variant}
                    className="text-xs py-0.5 px-2"
                    title={flagInfo.description}
                  >
                    <Icon className="h-3 w-3" />
                    <span>{flagInfo.label}</span>
                    <span className="ml-1 font-bold">-{flagInfo.penalty}</span>
                  </Badge>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
