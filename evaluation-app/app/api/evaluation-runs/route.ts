import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const EVALUATION_RESULTS_PATH = path.join(process.cwd(), '..', 'evaluation-results');

export async function GET() {
  try {
    const files = await fs.readdir(EVALUATION_RESULTS_PATH);
    const evaluationFiles = files.filter(file => 
      file.startsWith('evaluation_') && file.endsWith('.json')
    );

    const runs = await Promise.all(
      evaluationFiles.map(async (filename) => {
        try {
          const filePath = path.join(EVALUATION_RESULTS_PATH, filename);
          const data = await fs.readFile(filePath, 'utf-8');
          const parsed = JSON.parse(data);
          
          return {
            filename,
            timestamp: parsed.evaluation_metadata?.timestamp || 'unknown',
            model: parsed.evaluation_metadata?.model_used?.model || 'unknown',
            total_candidates: parsed.evaluation_metadata?.total_candidates_evaluated || 0,
            complete: parsed.evaluation_metadata?.evaluation_complete || false,
          };
        } catch (error) {
          console.error(`Error reading ${filename}:`, error);
          return null;
        }
      })
    );

    // Filter out failed reads and sort by timestamp (most recent first)
    const validRuns = runs
      .filter(run => run !== null)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    return NextResponse.json(validRuns);
  } catch (error) {
    console.error('Error reading evaluation runs:', error);
    return NextResponse.json({ error: 'Failed to read evaluation runs' }, { status: 500 });
  }
}

