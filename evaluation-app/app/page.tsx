"use client";

import { useState, useEffect, useMemo } from "react";
import { Ratings, HumanRatings, HumanEvaluation, Rubric } from "@/lib/types";
import EvaluationDisplay from "@/components/EvaluationDisplay";
import HumanEvaluationForm from "@/components/HumanEvaluationForm";
import Analytics from "@/components/Analytics";
import {
  ChevronLeft,
  ChevronRight,
  Eye,
  EyeOff,
  Search,
  BarChart,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface EvaluationRun {
  filename: string;
  timestamp: string;
  model: string;
  total_candidates: number;
  complete: boolean;
  hideFromDashboard: boolean;
}

export default function Home() {
  const [currentCandidateIndex, setCurrentCandidateIndex] = useState(0);
  const [aiRatings, setAiRatings] = useState<Ratings>({});
  const [humanRatings, setHumanRatings] = useState<HumanRatings>({});
  const [rubric, setRubric] = useState<Rubric | null>(null);
  const [showAiEvaluation, setShowAiEvaluation] = useState(true);
  const [jumpToCandidate, setJumpToCandidate] = useState("");
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("evaluation");

  // New state for evaluation runs
  const [evaluationRuns, setEvaluationRuns] = useState<EvaluationRun[]>([]);
  const [allAiRatings, setAllAiRatings] = useState<Record<string, Ratings>>({});
  
  // Sorting state
  const [sortMode, setSortMode] = useState<"numerical" | "gap">("numerical");
  
  // Analytics controls
  const [showHiddenRuns, setShowHiddenRuns] = useState(false);
  const [sortByGap, setSortByGap] = useState(false);

  // Generate sorted list of candidates based on sort mode
  const candidateIds = useMemo(() => {
    const allCandidates = Array.from({ length: 54 }, (_, i) => String(i + 1));
    
    if (sortMode === "numerical") {
      return allCandidates.sort((a, b) => parseInt(a) - parseInt(b));
    } else if (sortMode === "gap") {
      // Sort by gap size (largest first), then by candidate ID
      return allCandidates.sort((a, b) => {
        const humanA = humanRatings[a];
        const aiA = aiRatings[a];
        const humanB = humanRatings[b];
        const aiB = aiRatings[b];
        
        // Calculate gaps, only for candidates with both ratings
        const gapA = (humanA && aiA) 
          ? Math.abs((humanA.overall_weighted_score || 0) - (aiA.overall_weighted_score || 0))
          : -1; // Put candidates without both ratings at the end
        
        const gapB = (humanB && aiB)
          ? Math.abs((humanB.overall_weighted_score || 0) - (aiB.overall_weighted_score || 0))
          : -1;
        
        // Sort by gap (largest first), then by candidate ID
        if (gapA !== gapB) {
          return gapB - gapA; // Larger gaps first
        }
        return parseInt(a) - parseInt(b); // Then by candidate ID
      });
    }
    return allCandidates;
  }, [sortMode, humanRatings, aiRatings]);
  
  const currentCandidateId = candidateIds[currentCandidateIndex];
  const currentImageFilename = `candidate_${currentCandidateId}.jpg`;

  // Load evaluation runs on mount
  useEffect(() => {
    const loadEvaluationRuns = async () => {
      try {
        const response = await fetch("/api/evaluation-runs");
        const runs = await response.json();
        setEvaluationRuns(runs);
        // No need to set selected run since we load all runs
      } catch (error) {
        console.error("Error loading evaluation runs:", error);
      }
    };
    loadEvaluationRuns();
  }, []);

  // Load data for all evaluation runs
  useEffect(() => {
    if (evaluationRuns.length === 0) return;

    const loadAllRunData = async () => {
      try {
        // Load human ratings and rubric
        const [humanRes, rubricRes] = await Promise.all([
          fetch("/api/ratings?type=human"),
          fetch("/api/rubric"),
        ]);

        const [humanData, rubricData] = await Promise.all([
          humanRes.json(),
          rubricRes.json(),
        ]);

        setHumanRatings(humanData);
        setRubric(rubricData);

        // Load AI ratings for all runs
        const aiRatingsPromises = evaluationRuns.map(run =>
          fetch(`/api/ratings?type=ai&filename=${run.filename}`).then(res => res.json())
        );

        const aiRatingsData = await Promise.all(aiRatingsPromises);

        const allRatings: Record<string, Ratings> = {};
        evaluationRuns.forEach((run, index) => {
          allRatings[run.filename] = aiRatingsData[index] || {};
        });

        setAllAiRatings(allRatings);

        // Set the current AI ratings to the most recent run for evaluation tab
        if (evaluationRuns.length > 0) {
          setAiRatings(aiRatingsData[0] || {});
        }
      } catch (error) {
        console.error("Error loading data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadAllRunData();
  }, [evaluationRuns]);

  // Reset to first candidate when sort mode changes
  useEffect(() => {
    setCurrentCandidateIndex(0);
  }, [sortMode]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Only handle arrow keys on evaluation tab
      if (activeTab !== "evaluation") return;

      // Don't trigger if user is typing in an input/textarea
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        event.target instanceof HTMLSelectElement
      ) {
        return;
      }

      if (event.key === "ArrowLeft") {
        event.preventDefault();
        if (currentCandidateIndex > 0) {
          navigateToCandidate(currentCandidateIndex - 1);
        }
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        if (currentCandidateIndex < candidateIds.length - 1) {
          navigateToCandidate(currentCandidateIndex + 1);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeTab, currentCandidateIndex, candidateIds.length]);

  const handleSaveHumanEvaluation = async (evaluation: HumanEvaluation) => {
    try {
      const response = await fetch("/api/ratings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidateId: currentCandidateId,
          evaluation,
        }),
      });

      if (response.ok) {
        setHumanRatings((prev) => ({
          ...prev,
          [currentCandidateId]: evaluation,
        }));
      }
    } catch (error) {
      console.error("Error saving evaluation:", error);
    }
  };

  const navigateToCandidate = (index: number) => {
    if (index >= 0 && index < candidateIds.length) {
      setCurrentCandidateIndex(index);
    }
  };

  const handleJumpToCandidate = () => {
    const candidateNum = parseInt(jumpToCandidate);
    if (candidateNum >= 1 && candidateNum <= 54) {
      setCurrentCandidateIndex(candidateNum - 1);
      setJumpToCandidate("");
    }
  };

  const evaluatedCount = Object.keys(humanRatings).length;
  const hasHumanEvaluation = currentCandidateId in humanRatings;
  const progressPercentage = (evaluatedCount / candidateIds.length) * 100;



  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-2">
          <div className="text-lg font-medium">Loading evaluation data...</div>
          <Progress value={33} className="w-48" />
        </div>
      </div>
    );
  }

  return (
    <Tabs
      value={activeTab}
      onValueChange={setActiveTab}
      className="h-screen flex flex-col bg-background"
    >
      {/* Header */}
      <header className="py-2 border-b border-stone-100">
        <div className="flex items-center justify-between px-8">
          <div className="flex items-center gap-6">
            {/* Tabs in header */}
            <TabsList className="h-9">
              <TabsTrigger value="evaluation">Evaluation</TabsTrigger>
              <TabsTrigger value="analytics">
                <BarChart className="h-4 w-4 mr-1" />
                Analytics
              </TabsTrigger>
            </TabsList>
            <h1 className="text-sm leading-normal font-medium">
              {activeTab === "evaluation"
                ? `Candidate ${currentCandidateId} (${currentCandidateIndex + 1}/${candidateIds.length}${sortMode === "gap" ? " - sorted by gap" : ""})`
                : "Analytics Dashboard"}
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {activeTab === "evaluation" && (
              <>
                {/* Sort dropdown */}
                <div className="flex items-center gap-2">
                  <Select value={sortMode} onValueChange={(value: "numerical" | "gap") => setSortMode(value)}>
                    <SelectTrigger className="w-32 h-8">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="numerical">Numerical</SelectItem>
                      <SelectItem value="gap">By Gap</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Jump to candidate */}
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    min="1"
                    max="54"
                    value={jumpToCandidate}
                    onChange={(e) => setJumpToCandidate(e.target.value)}
                    onKeyPress={(e) =>
                      e.key === "Enter" && handleJumpToCandidate()
                    }
                    placeholder="Jump to..."
                    className="w-24"
                  />
                  <Button
                    onClick={handleJumpToCandidate}
                    size="sm"
                    variant="outline"
                  >
                    <Search className="h-3 w-3" />
                  </Button>
                </div>
              </>
            )}

            {activeTab === "analytics" && (
              <>
                {/* Show hidden runs toggle */}
                <div className="flex items-center space-x-2">
                  <Switch
                    id="show-hidden-runs"
                    checked={showHiddenRuns}
                    onCheckedChange={setShowHiddenRuns}
                  />
                  <Label htmlFor="show-hidden-runs" className="text-sm">
                    Show hidden runs
                  </Label>
                  {showHiddenRuns && (
                    <div className="text-sm text-muted-foreground ml-2">
                      ({evaluationRuns.filter(r => r.hideFromDashboard).length} hidden)
                    </div>
                  )}
                </div>

                {/* Sort by gap toggle */}
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
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      {/* Evaluation Tab */}
      <TabsContent value="evaluation" className="flex-1 overflow-hidden">
        <div className="flex h-full overflow-hidden">
          {/* Left side - Image viewer (75%) */}
          <div className="w-3/4 h-full overflow-hidden">
            <ScrollArea className="h-full w-full">
              <img
                src={`/api/image/${currentImageFilename}`}
                alt={`Candidate ${currentCandidateId}`}
                className="w-full h-auto block"
              />
            </ScrollArea>
          </div>

          {/* Right side - Evaluations (25%) */}
          <div className="w-1/4 h-full border-l border-stone-100 overflow-y-auto">
            <div className="space-y-4">
              {/* Navigation Controls */}
              <div className="space-y-4  border-b border-stone-100 py-3 px-4">
                {/* Navigation Row: Previous/Next Buttons + AI Toggle */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center divide-x divide-stone-100">
                    <Button
                      onClick={() =>
                        navigateToCandidate(currentCandidateIndex - 1)
                      }
                      disabled={currentCandidateIndex === 0}
                      variant="ghost"
                      size="sm"
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Previous
                    </Button>

                    <Button
                      onClick={() =>
                        navigateToCandidate(currentCandidateIndex + 1)
                      }
                      disabled={
                        currentCandidateIndex === candidateIds.length - 1
                      }
                      variant="ghost"
                      size="sm"
                    >
                      Next
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                  {/* AI Evaluation Toggle */}
                  <div className="flex items-center gap-2">
                    <Switch
                      id="ai-toggle"
                      checked={showAiEvaluation}
                      onCheckedChange={setShowAiEvaluation}
                    />
                    <Label
                      htmlFor="ai-toggle"
                      className="text-xs cursor-pointer"
                    >
                      {showAiEvaluation ? (
                        <Eye className="h-4 w-4" />
                      ) : (
                        <EyeOff className="h-4 w-4" />
                      )}
                    </Label>
                  </div>
                </div>

                {/* Progress Indicators */}
                {/* <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Progress</span>
                      <span className="font-medium">
                        {evaluatedCount}/{candidateIds.length}
                      </span>
                    </div>
                    <Progress value={progressPercentage} className="w-full" />
                  </div> */}

                {/* Candidate Dots */}
                {/* <div className="max-h-32 overflow-y-auto">
                    <div className="flex flex-wrap gap-1.5">
                      {candidateIds.map((id, index) => (
                        <button
                          key={id}
                          onClick={() => navigateToCandidate(index)}
                          className={cn(
                            "w-2 h-2 rounded-full transition-all",
                            "hover:scale-125",
                            index === currentCandidateIndex
                              ? "w-6 bg-primary"
                              : humanRatings[id]
                              ? "bg-green-500"
                              : "bg-muted-foreground/30"
                          )}
                          title={`Candidate ${id}${
                            humanRatings[id] ? " (Evaluated)" : ""
                          }`}
                        />
                      ))}
                    </div>
                  </div> */}
              </div>

              {/* AI Evaluation */}
              <EvaluationDisplay
                evaluation={aiRatings[currentCandidateId] || null}
                isVisible={showAiEvaluation}
              />

              {/* Human Evaluation Form */}
              <HumanEvaluationForm
                candidateId={currentCandidateId}
                imageFilename={currentImageFilename}
                existingEvaluation={humanRatings[currentCandidateId] || null}
                rubric={rubric}
                onSave={handleSaveHumanEvaluation}
              />
            </div>
          </div>
        </div>
      </TabsContent>

      {/* Analytics Tab */}
      <TabsContent value="analytics" className="flex-1 overflow-hidden">
        <div className="w-full px-8 py-5 h-full overflow-y-auto">
          <Analytics
            humanRatings={humanRatings}
            allAiRatings={allAiRatings}
            evaluationRuns={evaluationRuns}
            showHiddenRuns={showHiddenRuns}
            sortByGap={sortByGap}
          />
        </div>
      </TabsContent>
    </Tabs>
  );
}
