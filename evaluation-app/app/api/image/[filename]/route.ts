import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const { filename } = await params;
    const imagePath = path.join(process.cwd(), '..', 'candidate-images', filename);
    
    const imageBuffer = await fs.readFile(imagePath);
    
    return new NextResponse(imageBuffer as unknown as BodyInit, {
      headers: {
        'Content-Type': 'image/jpeg',
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    });
  } catch (error: any) {
    console.error('Error loading image:', error);
    if (error.code === 'ENOENT') {
      return NextResponse.json({ error: 'Image not found' }, { status: 404 });
    }
    return NextResponse.json({ error: 'Failed to load image' }, { status: 500 });
  }
}
