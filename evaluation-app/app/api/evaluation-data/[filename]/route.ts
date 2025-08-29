import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const EVALUATION_RESULTS_PATH = path.join(process.cwd(), '..', 'evaluation-results');

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const { filename } = await params;
    const filePath = path.join(EVALUATION_RESULTS_PATH, filename);
    
    const data = await fs.readFile(filePath, 'utf-8');
    const parsed = JSON.parse(data);
    
    // Return just the candidate ratings for consistency with existing API
    return NextResponse.json(parsed.candidate_ratings || {});
  } catch (error: any) {
    console.error(`Error loading evaluation data ${await params.then(p => p.filename)}:`, error);
    if (error.code === 'ENOENT') {
      return NextResponse.json({ error: 'Evaluation data not found' }, { status: 404 });
    }
    return NextResponse.json({ error: 'Failed to load evaluation data' }, { status: 500 });
  }
}

