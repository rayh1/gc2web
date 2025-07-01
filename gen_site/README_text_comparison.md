# Text Comparison Tool

A Python program that computes text comparison metrics between a reference file and one or more candidate files.

## Features

The program calculates three key metrics for text comparison:

1. **Character Error Rate (CER)** - The percentage of character-level errors (insertions, deletions, substitutions) relative to the reference text
2. **Word Error Rate (WER)** - The percentage of word-level errors relative to the reference text
3. **Levenshtein Distance / Edit Distance** - The minimum number of single-character edits needed to transform the candidate text into the reference text

### Preprocessing

The program includes a preprocessing phase that normalizes all text files before comparison:
- **Case normalization**: Converts all text to lowercase
- **Whitespace normalization**: Replaces multiple whitespace characters (spaces, tabs, newlines) with single spaces
- **Trimming**: Removes leading and trailing whitespace

This ensures that comparisons focus on content differences rather than formatting variations.

## Usage

```bash
python3 text_comparison.py reference_file candidate_file1 [candidate_file2 ...]
```

### Options

- `-o, --output FILE` - Save the results to a markdown file instead of printing to stdout
- `-h, --help` - Show help message

### Examples

Compare a single candidate file against a reference:
```bash
python3 text_comparison.py reference.txt candidate.txt
```

Compare multiple candidate files:
```bash
python3 text_comparison.py reference.txt file1.txt file2.txt file3.txt
```

Save results to a file:
```bash
python3 text_comparison.py reference.txt candidate.txt -o results.md
```

## Output Format

The program outputs a markdown table with:
- Rows representing each candidate file
- Columns showing the computed metrics (CER, WER, Levenshtein Distance)

Example output:
```markdown
| File | CER (%) | WER (%) | Levenshtein Distance |
|------|---------|---------|---------------------|
| candidate1.txt | 0.00 | 0.00 | 0 |
| candidate2.txt | 2.27 | 6.90 | 4 |
```

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only standard library)

## Error Handling

- The program handles file encoding issues by trying UTF-8 first, then falling back to Latin-1
- If a candidate file cannot be processed, it will show "ERROR" in the results for that file
- Missing files will cause the program to exit with an error message

## Algorithm Details

### Character Error Rate (CER)
CER = (Character-level Levenshtein Distance / Length of Reference Text) × 100

### Word Error Rate (WER)  
WER = (Word-level Levenshtein Distance / Number of Words in Reference Text) × 100

### Levenshtein Distance
Calculated using dynamic programming to find the minimum number of edits (insertions, deletions, substitutions) needed to transform one string into another.
