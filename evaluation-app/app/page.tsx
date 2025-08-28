'use client';

import { useState, useEffect } from 'react';
import { Ratings, HumanRatings, HumanEvaluation, Rubric } from '@/lib/types';
import EvaluationDisplay from '@/components/EvaluationDisplay';
import HumanEvaluationForm from '@/components/HumanEvaluationForm';
import { ChevronLeft, ChevronRight, Eye, EyeOff, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

export default function Home() {
  const [currentCandidateIndex, setCurrentCandidateIndex] = useState(0);
  const [aiRatings, setAiRatings] = useState<Ratings>({});
  const [humanRatings, setHumanRatings] = useState<HumanRatings>({});
  const [rubric, setRubric] = useState<Rubric | null>(null);
  const [showAiEvaluation, setShowAiEvaluation] = useState(true);
  const [jumpToCandidate, setJumpToCandidate] = useState('');
  const [loading, setLoading] = useState(true);

  // Generate list of all candidates (1-54)
  const candidateIds = Array.from({ length: 54 }, (_, i) => String(i + 1));
  const currentCandidateId = candidateIds[currentCandidateIndex];
  const currentImageFilename = `candidate_${currentCandidateId}.jpg`;

  // Load all data on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [aiRes, humanRes, rubricRes] = await Promise.all([
          fetch('/api/ratings?type=ai'),
          fetch('/api/ratings?type=human'),
          fetch('/api/rubric'),
        ]);

        const [aiData, humanData, rubricData] = await Promise.all([
          aiRes.json(),
          humanRes.json(),
          rubricRes.json(),
        ]);

        setAiRatings(aiData);
        setHumanRatings(humanData);
        setRubric(rubricData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleSaveHumanEvaluation = async (evaluation: HumanEvaluation) => {
    try {
      const response = await fetch('/api/ratings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidateId: currentCandidateId,
          evaluation,
        }),
      });

      if (response.ok) {
        setHumanRatings(prev => ({
          ...prev,
          [currentCandidateId]: evaluation,
        }));
      }
    } catch (error) {
      console.error('Error saving evaluation:', error);
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
      setJumpToCandidate('');
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
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div>
              <h1 className="text-xl font-semibold">Portfolio Evaluation</h1>
              <p className="text-sm text-muted-foreground">Candidate {currentCandidateId} of {candidateIds.length}</p>
            </div>

            {/* Progress */}
            <div className="flex items-center gap-3">
              <Progress value={progressPercentage} className="w-32" />
              <span className="text-sm font-medium">{evaluatedCount}/{candidateIds.length}</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Jump to candidate */}
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min="1"
                max="54"
                value={jumpToCandidate}
                onChange={(e) => setJumpToCandidate(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleJumpToCandidate()}
                placeholder="Jump to..."
                className="w-24 h-8"
              />
              <Button onClick={handleJumpToCandidate} size="sm" variant="outline">
                <Search className="h-3 w-3" />
              </Button>
            </div>

            {/* Toggle AI evaluation */}
            <div className="flex items-center gap-2">
              <Switch
                id="ai-toggle"
                checked={showAiEvaluation}
                onCheckedChange={setShowAiEvaluation}
              />
              <Label htmlFor="ai-toggle" className="text-sm cursor-pointer">
                {showAiEvaluation ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
              </Label>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left side - Image viewer (75%) */}
        <div className="w-3/4 p-6">
          <div className="h-full bg-muted/20 rounded-lg border overflow-hidden">
            <ScrollArea className="h-full">
              <img
                src={`/api/image/${currentImageFilename}`}
                alt={`Candidate ${currentCandidateId}`}
                className="w-full h-auto"
              />
            </ScrollArea>
          </div>
        </div>

        {/* Right side - Evaluations (25%) */}
        <div className="w-1/4 p-6 pl-0 flex flex-col gap-4">
          {/* AI Evaluation */}
          <div className="flex-1 min-h-0">
            <EvaluationDisplay
              evaluation={aiRatings[currentCandidateId] || null}
              isVisible={showAiEvaluation}
            />
          </div>

          {/* Human Evaluation Form */}
          <div className="flex-1 min-h-0">
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

      {/* Footer - Navigation */}
      <footer className="border-t px-6 py-3">
        <div className="flex items-center justify-between">
          <Button
            onClick={() => navigateToCandidate(currentCandidateIndex - 1)}
            disabled={currentCandidateIndex === 0}
            variant="outline"
            size="sm"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>

          {/* Candidate dots */}
          <ScrollArea className="max-w-xl">
            <div className="flex items-center gap-1.5 px-4">
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
                  title={`Candidate ${id}${humanRatings[id] ? ' (Evaluated)' : ''}`}
                />
              ))}
            </div>
          </ScrollArea>

          <Button
            onClick={() => navigateToCandidate(currentCandidateIndex + 1)}
            disabled={currentCandidateIndex === candidateIds.length - 1}
            variant="outline"
            size="sm"
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </footer>
    </div>
  );
}