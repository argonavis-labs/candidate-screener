#!/usr/bin/env python3
"""
Token counter for HTML files - estimates tokens for LLM context
Uses tiktoken for accurate OpenAI token counting
"""

import sys
import os

def estimate_tokens(text):
    """
    Estimate token count using various methods
    Returns dict with different estimates
    """
    
    # Method 1: Character-based estimation
    # Rule of thumb: ~4 characters per token for English/HTML
    char_estimate = len(text) // 4
    
    # Method 2: Word-based estimation  
    # Rule of thumb: ~1.3 tokens per word
    words = len(text.split())
    word_estimate = int(words * 1.3)
    
    # Method 3: Byte-based estimation
    # UTF-8 bytes divided by ~3.5 (HTML/code tends to be more token-dense)
    byte_estimate = len(text.encode('utf-8')) // 3
    
    # Try tiktoken if available for accurate GPT token counting
    tiktoken_estimate = None
    try:
        import tiktoken
        # Use cl100k_base encoding (GPT-4/GPT-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        tiktoken_estimate = len(tokens)
    except ImportError:
        pass
    
    return {
        'char_estimate': char_estimate,
        'word_estimate': word_estimate, 
        'byte_estimate': byte_estimate,
        'tiktoken_gpt4': tiktoken_estimate,
        'best_estimate': tiktoken_estimate or byte_estimate
    }

def analyze_file(filepath):
    """Analyze token usage for a file"""
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_size_kb = len(content) // 1024
    estimates = estimate_tokens(content)
    
    print(f"\n=== Token Analysis for {os.path.basename(filepath)} ===")
    print(f"File size: {file_size_kb} KB ({len(content):,} characters)")
    print(f"\nToken Estimates:")
    print(f"  Character-based (~4 chars/token): {estimates['char_estimate']:,} tokens")
    print(f"  Word-based (~1.3 tokens/word): {estimates['word_estimate']:,} tokens")
    print(f"  Byte-based (~3 bytes/token): {estimates['byte_estimate']:,} tokens")
    
    if estimates['tiktoken_gpt4']:
        print(f"  **Actual GPT-4 tokens: {estimates['tiktoken_gpt4']:,} tokens**")
    
    # Best estimate
    best = estimates['best_estimate']
    print(f"\nBest estimate: ~{best:,} tokens")
    print(f"Token density: ~{best / file_size_kb:.0f} tokens per KB")
    
    # Context window calculations
    print(f"\n=== Context Window Capacity ===")
    
    models = [
        ("GPT-4 Turbo", 128000),
        ("Claude 3 Opus", 200000),
        ("GPT-4o", 128000),
        ("Claude 3.5 Sonnet", 200000),
        ("Gemini 1.5 Pro", 1000000),
        ("GPT-5 (rumored)", 256000)  # Speculative
    ]
    
    for model_name, context_size in models:
        # Reserve 20% for system prompt, output, and safety margin
        usable_context = int(context_size * 0.8)
        files_that_fit = usable_context // best
        print(f"  {model_name} ({context_size:,} tokens):")
        print(f"    → Can fit ~{files_that_fit} files @ {best:,} tokens each")
        print(f"    → With 80% utilization ({usable_context:,} usable tokens)")
    
    # RAG considerations
    print(f"\n=== RAG System Recommendations ===")
    print(f"For a 200KB compressed HTML file (~{best:,} tokens):")
    print(f"• Chunk size: Consider 2-4KB chunks (~{best // 100}-{best // 50} tokens)")
    print(f"• Overlap: 10-20% overlap between chunks")
    print(f"• Embedding: Can embed full pages if using modern embedding models")
    print(f"• Retrieval: Retrieve 3-5 most relevant pages per query")
    
    return estimates

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Default to Sally Wang compressed file if it exists
        filepath = "Sally_Wang_fonts_compressed.html"
    
    analyze_file(filepath)
