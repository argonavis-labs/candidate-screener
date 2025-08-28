import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { Ratings, HumanRatings } from '@/lib/types';

const AI_RATINGS_PATH = path.join(process.cwd(), '..', 'ai-ratings.json');
const HUMAN_RATINGS_PATH = path.join(process.cwd(), '..', 'human-ratings.json');

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const type = searchParams.get('type') || 'ai';
    
    const filePath = type === 'ai' ? AI_RATINGS_PATH : HUMAN_RATINGS_PATH;
    
    try {
      const data = await fs.readFile(filePath, 'utf-8');
      const parsed = JSON.parse(data);
      
      // Handle the new AI ratings format which has ratings nested under 'candidate_ratings'
      if (type === 'ai' && parsed.candidate_ratings) {
        return NextResponse.json(parsed.candidate_ratings);
      }
      
      return NextResponse.json(parsed);
    } catch (error: any) {
      // If file doesn't exist, return empty object
      if (error.code === 'ENOENT') {
        return NextResponse.json({});
      }
      console.error(`Error reading ${type} ratings:`, error);
      return NextResponse.json({});
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
