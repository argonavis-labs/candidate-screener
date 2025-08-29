'use client';

import { useState, useEffect } from 'react';
import { Ratings, HumanRatings, HumanEvaluation, Rubric } from '@/lib/types';
import EvaluationDisplay from '@/components/EvaluationDisplay';
import HumanEvaluationForm from '@/components/HumanEvaluationForm';
import Analytics from '@/components/Analytics';
import { ChevronLeft, ChevronRight, Eye, EyeOff, Search, BarChart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from '@/lib/utils';

interface EvaluationRun {
  filename: string;
  timestamp: string;
  model: string;
  total_candidates: number;
  complete: boolean;
}

export default function Home() {
  const [currentCandidateIndex, setCurrentCandidateIndex] = useState(0);
  const [aiRatings, setAiRatings] = useState<Ratings>({});
  const [humanRatings, setHumanRatings] = useState<HumanRatings>({});
  const [rubric, setRubric] = useState<Rubric | null>(null);
  const [showAiEvaluation, setShowAiEvaluation] = useState(true);
  const [jumpToCandidate, setJumpToCandidate] = useState('');
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('evaluation');
  
  // New state for evaluation runs
  const [evaluationRuns, setEvaluationRuns] = useState<EvaluationRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<string>('');

  // Generate list of all candidates (1-54)
  const candidateIds = Array.from({ length: 54 }, (_, i) => String(i + 1));
  const currentCandidateId = candidateIds[currentCandidateIndex];
  const currentImageFilename = `candidate_${currentCandidateId}.jpg`;

  // Load evaluation runs on mount
  useEffect(() => {
    const loadEvaluationRuns = async () => {
      try {
        const response = await fetch('/api/evaluation-runs');
        const runs = await response.json();
        setEvaluationRuns(runs);
        if (runs.length > 0) {
          setSelectedRun(runs[0].filename); // Default to most recent
        }
      } catch (error) {
        console.error('Error loading evaluation runs:', error);
      }
    };
    loadEvaluationRuns();
  }, []);

  // Load data when selected run changes
  useEffect(() => {
    if (!selectedRun) return;
    
    const loadData = async () => {
      try {
        const [aiRes, humanRes, rubricRes] = await Promise.all([
          fetch(`/api/ratings?type=ai&filename=${selectedRun}`),
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
  }, [selectedRun]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Only handle arrow keys on evaluation tab
      if (activeTab !== 'evaluation') return;
      
      // Don't trigger if user is typing in an input/textarea
      if (event.target instanceof HTMLInputElement || 
          event.target instanceof HTMLTextAreaElement ||
          event.target instanceof HTMLSelectElement) {
        return;
      }

      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        if (currentCandidateIndex > 0) {
          navigateToCandidate(currentCandidateIndex - 1);
        }
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        if (currentCandidateIndex < candidateIds.length - 1) {
          navigateToCandidate(currentCandidateIndex + 1);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, currentCandidateIndex, candidateIds.length]);

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

  const currentRun = evaluationRuns.find(run => run.filename === selectedRun);

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
    <Tabs value={activeTab} onValueChange={setActiveTab} className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="py-4 px-8 border-b border-stone-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div>
              <h1 className="text-xl font-semibold tracking-tight">Portfolio Evaluation</h1>
              <p className="text-sm text-muted-foreground leading-normal">
                {activeTab === 'evaluation' 
                  ? `Candidate ${currentCandidateId} of ${candidateIds.length}`
                  : 'Analytics Dashboard'
                }
              </p>
            </div>

            {/* Tabs in header */}
            <TabsList className="h-9">
              <TabsTrigger value="evaluation">Evaluation</TabsTrigger>
              <TabsTrigger value="analytics">
                <BarChart className="h-4 w-4 mr-1" />
                Analytics
              </TabsTrigger>
            </TabsList>


          </div>

          <div className="flex items-center gap-4">
            {/* AI Run Selector */}
            {evaluationRuns.length > 0 && (
              <div className="flex items-center gap-2">
                <Label htmlFor="run-selector" className="text-sm">AI Run:</Label>
                <Select value={selectedRun} onValueChange={setSelectedRun}>
                  <SelectTrigger id="run-selector" className="w-56 h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {evaluationRuns.map(run => (
                      <SelectItem key={run.filename} value={run.filename}>
                        <div className="flex flex-col">
                          <span className="text-sm leading-tight">{run.model}</span>
                          <span className="text-xs text-muted-foreground leading-tight">
                            {new Date(run.timestamp).toLocaleDateString()}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {activeTab === 'evaluation' && (
              <>
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
                    className="w-24"
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
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      {/* Evaluation Tab */}
      <TabsContent value="evaluation" className="flex-1 overflow-hidden">
          <div className="flex h-full overflow-hidden px-8">
            {/* Left side - Image viewer (75%) */}
            <div className="w-3/4 py-5 pr-6 overflow-hidden">
              <ScrollArea className="h-full w-full">
                <img
                  src={`/api/image/${currentImageFilename}`}
                  alt={`Candidate ${currentCandidateId}`}
                  className="w-full h-auto block"
                />
              </ScrollArea>
            </div>

            {/* Right side - Evaluations (25%) */}
            <div className="w-1/4 p-6 flex flex-col gap-4 h-full border-l border-stone-100">
              {/* Navigation Controls */}
              <div className="flex flex-col gap-4 pb-4">
                {/* Previous/Next Buttons */}
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

                {/* Progress Indicators */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Progress</span>
                    <span className="font-medium">{evaluatedCount}/{candidateIds.length}</span>
                  </div>
                  <Progress value={progressPercentage} className="w-full" />
                </div>

                {/* Candidate Dots */}
                <ScrollArea className="max-h-32">
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
                        title={`Candidate ${id}${humanRatings[id] ? ' (Evaluated)' : ''}`}
                      />
                    ))}
                  </div>
                </ScrollArea>
              </div>

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
      </TabsContent>

      {/* Analytics Tab */}
      <TabsContent value="analytics" className="flex-1 overflow-hidden">
        <div className="container py-5 h-full overflow-y-auto">
          <Analytics 
            humanRatings={humanRatings}
            aiRatings={aiRatings}
            selectedRun={selectedRun}
          />
        </div>
      </TabsContent>


    </Tabs>
  );
}