#!/usr/bin/env python3
"""
Text Comparison Tool

This program computes text comparison metrics between a reference file and candidate files:
- Character Error Rate (CER)
- Word Error Rate (WER) 
- Levenshtein Distance / Edit Distance

The program includes a preprocessing phase that normalizes text by:
- Converting to lowercase
- Removing extra whitespace (multiple spaces, tabs, newlines become single spaces)

Usage:
    python text_comparison.py reference.txt candidate1.txt [candidate2.txt ...]
"""

import argparse
import sys
import re
from pathlib import Path
from typing import List, Tuple


def normalize_text(text: str) -> str:
    """
    Normalize text by converting to lowercase and removing extra whitespace.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text with lowercase and single spaces
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace multiple whitespace characters (spaces, tabs, newlines) with single spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading and trailing whitespace
    text = text.strip()
    
    return text


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        The minimum number of single-character edits (insertions, deletions, substitutions)
        required to change s1 into s2
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, and substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def calculate_cer(reference: str, candidate: str) -> float:
    """
    Calculate Character Error Rate (CER).
    
    CER = (S + D + I) / N
    where S is substitutions, D is deletions, I is insertions, N is number of characters in reference
    
    Args:
        reference: Reference text
        candidate: Candidate text
        
    Returns:
        Character Error Rate as a percentage
    """
    if not reference:
        return 100.0 if candidate else 0.0
    
    distance = levenshtein_distance(reference, candidate)
    cer = (distance / len(reference)) * 100
    return cer


def calculate_wer(reference: str, candidate: str) -> float:
    """
    Calculate Word Error Rate (WER).
    
    WER = (S + D + I) / N
    where S is substitutions, D is deletions, I is insertions, N is number of words in reference
    
    Args:
        reference: Reference text
        candidate: Candidate text
        
    Returns:
        Word Error Rate as a percentage
    """
    ref_words = reference.split()
    cand_words = candidate.split()
    
    if not ref_words:
        return 100.0 if cand_words else 0.0
    
    distance = levenshtein_distance(' '.join(ref_words), ' '.join(cand_words))
    # For WER, we need to calculate based on word-level operations
    word_distance = levenshtein_distance_words(ref_words, cand_words)
    wer = (word_distance / len(ref_words)) * 100
    return wer


def levenshtein_distance_words(words1: List[str], words2: List[str]) -> int:
    """
    Calculate Levenshtein distance at word level.
    
    Args:
        words1: List of words from first text
        words2: List of words from second text
        
    Returns:
        Word-level Levenshtein distance
    """
    if len(words1) < len(words2):
        return levenshtein_distance_words(words2, words1)

    if len(words2) == 0:
        return len(words1)

    previous_row = list(range(len(words2) + 1))
    for i, w1 in enumerate(words1):
        current_row = [i + 1]
        for j, w2 in enumerate(words2):
            # Cost of insertions, deletions, and substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (w1 != w2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def read_file_safely(filepath: Path) -> str:
    """
    Read a file safely with error handling.
    
    Args:
        filepath: Path to the file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file can't be decoded as UTF-8
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(filepath, 'r', encoding='latin-1') as f:
            return f.read().strip()


def process_files(reference_file: Path, candidate_files: List[Path]) -> List[Tuple[str, float, float, int]]:
    """
    Process all files and calculate metrics.
    
    Args:
        reference_file: Path to reference file
        candidate_files: List of paths to candidate files
        
    Returns:
        List of tuples containing (filename, CER, WER, Levenshtein Distance)
    """
    try:
        reference_text = read_file_safely(reference_file)
        # Normalize reference text once
        reference_text = normalize_text(reference_text)
    except Exception as e:
        print(f"Error reading reference file {reference_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    results = []
    
    for candidate_file in candidate_files:
        try:
            candidate_text = read_file_safely(candidate_file)
            # Normalize candidate text
            candidate_text = normalize_text(candidate_text)
            
            # Calculate metrics
            cer = calculate_cer(reference_text, candidate_text)
            wer = calculate_wer(reference_text, candidate_text)
            levenshtein_dist = levenshtein_distance(reference_text, candidate_text)
            
            results.append((candidate_file.name, cer, wer, levenshtein_dist))
            
        except Exception as e:
            print(f"Error processing candidate file {candidate_file}: {e}", file=sys.stderr)
            results.append((candidate_file.name, float('inf'), float('inf'), float('inf')))
    
    return results


def generate_markdown_table(results: List[Tuple[str, float, float, int]]) -> str:
    """
    Generate a markdown table from the results.
    
    Args:
        results: List of tuples containing (filename, CER, WER, Levenshtein Distance)
        
    Returns:
        Markdown formatted table as string
    """
    if not results:
        return "No results to display."
    
    # Create header with metrics as columns
    header = "| File | CER (%) | WER (%) | Levenshtein Distance |"
    separator = "|------|---------|---------|---------------------|"
    
    # Create rows for each candidate file
    rows = []
    for filename, cer, wer, levenshtein_dist in results:
        if cer == float('inf'):
            row = f"| {filename} | ERROR | ERROR | ERROR |"
        else:
            row = f"| {filename} | {cer:.2f} | {wer:.2f} | {levenshtein_dist} |"
        rows.append(row)
    
    return f"{header}\n{separator}\n" + "\n".join(rows)


def main():
    """Main function to handle command line arguments and orchestrate the comparison."""
    parser = argparse.ArgumentParser(
        description="Compare text files and calculate CER, WER, and Levenshtein Distance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python text_comparison.py reference.txt candidate.txt
    python text_comparison.py reference.txt file1.txt file2.txt file3.txt
        """
    )
    
    parser.add_argument(
        'reference_file',
        type=Path,
        help='Reference text file'
    )
    
    parser.add_argument(
        'candidate_files',
        type=Path,
        nargs='+',
        help='One or more candidate text files to compare against the reference'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file for the markdown table (default: print to stdout)'
    )
    
    args = parser.parse_args()
    
    # Validate that reference file exists
    if not args.reference_file.exists():
        print(f"Error: Reference file '{args.reference_file}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Validate that candidate files exist
    for candidate_file in args.candidate_files:
        if not candidate_file.exists():
            print(f"Error: Candidate file '{candidate_file}' does not exist.", file=sys.stderr)
            sys.exit(1)
    
    # Process files and calculate metrics
    print("Processing files...", file=sys.stderr)
    results = process_files(args.reference_file, args.candidate_files)
    
    # Generate markdown table
    markdown_table = generate_markdown_table(results)
    
    # Output results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(markdown_table)
            print(f"Results written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(markdown_table)


if __name__ == "__main__":
    main()
