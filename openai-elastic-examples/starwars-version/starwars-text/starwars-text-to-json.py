import re
import json

def parse_book_to_json(input_file, output_file):
    paragraphs = []
    current_paragraph = ""
    current_page = None
    current_paragraph_num = 0

    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()

            # Check if the line contains a page number side 1
            page_match = re.match(r'^STAR WARS (\d+),*?$', line)
            if page_match:
                current_page = int(page_match.group(1))
                current_paragraph_num = 0
                continue

            # Check if the line contains a page number side 2
            page_match = re.match(r'^(\d+) STAR WARS,*?$', line)
            if page_match:
                current_page = int(page_match.group(1))
                current_paragraph_num = 0
                continue

            # Check if the line is a blank indicating a new paragraph
            if re.match(r'^\s+.*', line) or re.match(r'^\n*$', line):
                if current_paragraph:
                    paragraphs.append({"title": "Star Wars", "Author": "George Lucas", "page": current_page, "paragraph_num": current_paragraph_num, "paragraph": current_paragraph})
                    current_paragraph = ""
                    current_paragraph_num = current_paragraph_num + 1
            else:
                if re.match(r'.*[a-zA-Z]+[-] $', current_paragraph):
                    # strip the hyphon at end of line, and join without a space
                    current_paragraph = current_paragraph[:len(current_paragraph)-2]
                    current_paragraph += line
                else:
                    current_paragraph += line + " "

        # Add the last paragraph
        if current_paragraph:
            paragraphs.append({"title": "Star Wars", "Author": "George Lucas", "page": current_page, "paragraph_num": current_paragraph_num, "paragraph": current_paragraph})

    with open(output_file, 'w') as f:
        for paragraph in paragraphs:
            json.dump(paragraph, f)
            f.write('\n')
            #print(paragraph)

if __name__ == "__main__":
    input_file = "starwars.txt"
    output_file = "starwars.json"
    parse_book_to_json(input_file, output_file)
