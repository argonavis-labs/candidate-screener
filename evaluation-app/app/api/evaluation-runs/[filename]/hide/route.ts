import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

const EVALUATION_RESULTS_PATH = path.join(process.cwd(), '..', 'evaluation-results');

interface RouteParams {
  params: {
    filename: string;
  };
}

export async function POST(request: NextRequest, { params }: RouteParams) {
  try {
    const { hideFromDashboard } = await request.json();
    const filename = params.filename;

    if (typeof hideFromDashboard !== 'boolean') {
      return NextResponse.json(
        { error: 'hideFromDashboard must be a boolean' },
        { status: 400 }
      );
    }

    const filePath = path.join(EVALUATION_RESULTS_PATH, filename);
    
    // Check if file exists
    try {
      await fs.access(filePath);
    } catch {
      return NextResponse.json(
        { error: 'Evaluation file not found' },
        { status: 404 }
      );
    }

    // Read, update, and write back the file
    const data = await fs.readFile(filePath, 'utf-8');
    const parsed = JSON.parse(data);
    
    // Ensure evaluation_metadata exists
    if (!parsed.evaluation_metadata) {
      parsed.evaluation_metadata = {};
    }
    
    // Update the hideFromDashboard flag
    parsed.evaluation_metadata.hideFromDashboard = hideFromDashboard;
    
    // Write back to file
    await fs.writeFile(filePath, JSON.stringify(parsed, null, 2), 'utf-8');

    return NextResponse.json({ 
      success: true, 
      hideFromDashboard,
      filename 
    });
  } catch (error) {
    console.error('Error updating hide flag:', error);
    return NextResponse.json(
      { error: 'Failed to update hide flag' },
      { status: 500 }
    );
  }
}
