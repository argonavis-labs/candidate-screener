import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { Ratings, HumanRatings } from '@/lib/types';

const EVALUATION_RESULTS_PATH = path.join(process.cwd(), '..', 'evaluation-results');
const HUMAN_RATINGS_PATH = path.join(process.cwd(), '..', 'human-ratings.json');

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const type = searchParams.get('type') || 'ai';
    const filename = searchParams.get('filename'); // For AI ratings from specific run
    
    if (type === 'ai') {
      if (!filename) {
        // Return most recent evaluation by default
        try {
          const files = await fs.readdir(EVALUATION_RESULTS_PATH);
          const evaluationFiles = files.filter(file => 
            file.startsWith('evaluation_') && file.endsWith('.json')
          ).sort().reverse(); // Most recent first
          
          if (evaluationFiles.length === 0) {
            return NextResponse.json({});
          }
          
          const mostRecentFile = evaluationFiles[0];
          const filePath = path.join(EVALUATION_RESULTS_PATH, mostRecentFile);
          const data = await fs.readFile(filePath, 'utf-8');
          const parsed = JSON.parse(data);
          
          // Add metadata to each candidate rating
          const candidateRatings = parsed.candidate_ratings || {};
          const metadata = parsed.evaluation_metadata;
          
          // Attach metadata to each evaluation
          Object.keys(candidateRatings).forEach(candidateId => {
            candidateRatings[candidateId].evaluation_metadata = metadata;
          });
          
          return NextResponse.json(candidateRatings);
        } catch (error: any) {
          console.error('Error reading most recent AI ratings:', error);
          return NextResponse.json({});
        }
      } else {
        // Return specific evaluation run
        try {
          const filePath = path.join(EVALUATION_RESULTS_PATH, filename);
          const data = await fs.readFile(filePath, 'utf-8');
          const parsed = JSON.parse(data);
          
          // Add metadata to each candidate rating
          const candidateRatings = parsed.candidate_ratings || {};
          const metadata = parsed.evaluation_metadata;
          
          // Attach metadata to each evaluation
          Object.keys(candidateRatings).forEach(candidateId => {
            candidateRatings[candidateId].evaluation_metadata = metadata;
          });
          
          return NextResponse.json(candidateRatings);
        } catch (error: any) {
          console.error(`Error reading AI ratings from ${filename}:`, error);
          return NextResponse.json({});
        }
      }
    } else {
      // Human ratings
      try {
        const data = await fs.readFile(HUMAN_RATINGS_PATH, 'utf-8');
        return NextResponse.json(JSON.parse(data));
      } catch (error: any) {
        if (error.code === 'ENOENT') {
          return NextResponse.json({});
        }
        console.error('Error reading human ratings:', error);
        return NextResponse.json({});
      }
    }
  } catch (error) {
    console.error('Error in GET /api/ratings:', error);
    return NextResponse.json({ error: 'Failed to read ratings' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { candidateId, evaluation } = await request.json();
    
    // Read existing human ratings
    let humanRatings: HumanRatings = {};
    try {
      const data = await fs.readFile(HUMAN_RATINGS_PATH, 'utf-8');
      humanRatings = JSON.parse(data);
    } catch (error: any) {
      // File doesn't exist, start with empty object
      if (error.code !== 'ENOENT') {
        console.error('Error reading human ratings:', error);
      }
    }
    
    // Update with new evaluation
    humanRatings[candidateId] = evaluation;
    
    // Write back to file
    await fs.writeFile(
      HUMAN_RATINGS_PATH, 
      JSON.stringify(humanRatings, null, 2),
      'utf-8'
    );
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error saving human rating:', error);
    return NextResponse.json({ error: 'Failed to save rating' }, { status: 500 });
  }
}
