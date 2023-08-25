import difflib

def calculate_similarity_percentage(diff_string):
    lines = diff_string.split('\n')
    total_lines = len(lines)
    same_lines = sum(1 for line in lines if line.startswith('  '))  # Lines starting with '  ' are the same
    
    similarity_percentage = (same_lines / total_lines) * 100 if total_lines > 0 else 0
    return similarity_percentage

# Example documents
document1 = "This is the first document."
document2 = "This document is the second document."

# Calculate textual differences using difflib
differ = difflib.Differ()
diff = differ.compare(document1.split(), document2.split())
diff_string = '\n'.join(diff)

print("Difference String:\n", diff_string)

# Calculate and print similarity percentage
similarity_percentage = calculate_similarity_percentage(diff_string)
print(f"Similarity Percentage: {similarity_percentage:.2f}%")
