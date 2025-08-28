import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const RUBRIC_PATH = path.join(process.cwd(), '..', 'rubric.json');

export async function GET() {
  try {
    const data = await fs.readFile(RUBRIC_PATH, 'utf-8');
    return NextResponse.json(JSON.parse(data));
  } catch (error: any) {
    console.error('Error reading rubric:', error);
    if (error.code === 'ENOENT') {
      return NextResponse.json({ error: 'Rubric file not found' }, { status: 404 });
    }
    return NextResponse.json({ error: 'Failed to read rubric' }, { status: 500 });
  }
}
