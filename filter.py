import os
import json
import re
from qwen_agent.agents import Assistant
from PyPDF2 import PdfReader


# Define influential journals
INFLUENTIAL_JOURNALS = [
    "Cell", "Nature", "Science", 
    "Nature Machine Intelligence", "Nature Communications",
    "Cell Reports", "iScience", "Joule", "Matter"
]

# Define influential institutions
INFLUENTIAL_INSTITUTIONS = [
    "NASA", "Nvidia", "Openai", "OpenAI", "IBM", "Intel", 
    "Google", "Meta", "Microsoft", "Facebook"
]

# Define universities to exclude
EXCLUDED_UNIVERSITIES = ["Zhejiang University"]

# Define names to exclude
EXCLUDED_NAMES = ["Gang Pan", "Pan Gang"]


def pdf_to_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None


def process_pdf_name(folder_path, publish_info, llm_cfg=None):
    """
    Process PDF file names to ensure they match the title format with underscores.
    Uses an LLM agent to read the actual title from each PDF file.
    
    Args:
        folder_path (str): Path to the folder containing PDF files
        publish_info (list): List of paper information dictionaries with 'title' keys
        llm_cfg (dict): Configuration for the LLM agent
    
    Returns:
        dict: Mapping of original file names to new file names (if changed)
    """
    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    # Track renamed files
    renamed_files = {}
    
    # Process each PDF file directly using LLM to extract title
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        
        # Extract text from PDF
        pdf_text = pdf_to_text(pdf_path)
        if not pdf_text:
            print(f"Could not extract text from {pdf_file}")
            continue
            
        # Use LLM to extract the title if configuration is provided
        if llm_cfg:
            extracted_title = extract_title_with_llm(pdf_text, llm_cfg)
            if extracted_title:
                # Create the expected file name (title with spaces replaced by underscores)
                # Also remove any characters that might be problematic in file names
                expected_name = extracted_title.replace(" ", "_").replace(":", "") + ".pdf"
                print(expected_name)
                
                # Rename the file if it doesn't match the expected name
                if pdf_file != expected_name:
                    old_path = os.path.join(folder_path, pdf_file)
                    new_path = os.path.join(folder_path, expected_name)
                    
                    # Check if a file with the expected name already exists
                    if os.path.exists(new_path):
                        print(f"Warning: File {expected_name} already exists. Skipping rename of {pdf_file}")
                        continue
                        
                    try:
                        os.rename(old_path, new_path)
                        renamed_files[pdf_file] = expected_name
                        print(f"Renamed '{pdf_file}' to '{expected_name}'")
                    except Exception as e:
                        print(f"Error renaming {pdf_file} to {expected_name}: {e}")
            else:
                print(f"Could not extract title from {pdf_file} using LLM")
        else:
            # Fallback to matching with publish_info if no LLM config
            # Process each paper in publish_info
            for paper_info in publish_info:
                title = paper_info.get("title", "")
                if not title:
                    continue
                    
                # Create the expected file name (title with spaces replaced by underscores)
                # Also remove any characters that might be problematic in file names
                expected_name = re.sub(r'[^\\w\\-_\\. ]', '', title)  # Remove special characters
                expected_name = expected_name.replace(" ", "_").replace(":", "") + ".pdf"
                
                # Find the corresponding PDF file
                if title.lower().replace(" ", "_").replace(":", "") in pdf_file.lower().replace(" ", "_").replace(":", ""):
                    # Rename the file if it doesn't match the expected name
                    if pdf_file != expected_name:
                        old_path = os.path.join(folder_path, pdf_file)
                        new_path = os.path.join(folder_path, expected_name)
                        
                        # Check if a file with the expected name already exists
                        if os.path.exists(new_path):
                            print(f"Warning: File {expected_name} already exists. Skipping rename of {pdf_file}")
                            continue
                            
                        try:
                            os.rename(old_path, new_path)
                            renamed_files[pdf_file] = expected_name
                            print(f"Renamed '{pdf_file}' to '{expected_name}'")
                        except Exception as e:
                            print(f"Error renaming {pdf_file} to {expected_name}: {e}")
                    break
    
    return renamed_files


def extract_title_with_llm(pdf_text, llm_cfg):
    """
    Use an LLM agent to extract the title from PDF text.
    
    Args:
        pdf_text (str): Text extracted from PDF
        llm_cfg (dict): Configuration for the LLM agent
    
    Returns:
        str: Extracted title or None if failed
    """
    try:
        # Create the assistant agent
        system_instruction = '''
        You are an expert researcher. Your task is to extract the exact title of a research paper from the provided text.
        
        Please extract only the title of the paper and respond in the following JSON format:
        {
            "title": "exact paper title here"
        }
        
        Do not include any other text in your response.
        '''
        
        # Create the assistant
        bot = Assistant(
            llm=llm_cfg,
            system_message=system_instruction
        )
        
        # Prepare the message with first 4000 characters (to avoid token limits)
        messages = [{
            'role': 'user', 
            'content': f'Paper text:\\n{pdf_text[:4000]}'
        }]
        
        response = []
        for response in bot.run(messages=messages):
            pass
        
        if response and len(response) > 0:
            content = response[-1]['content']
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return result.get("title", None)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract title from plain text
                lines = content.strip().split('\n')
                for line in lines:
                    if '"title":' in line:
                        # Extract title from JSON-like string
                        title_match = re.search(r'"title":\\s*"([^"]+)"', line)
                        if title_match:
                            return title_match.group(1)
                return None
    except Exception as e:
        print(f"Error extracting title with LLM: {e}")
        return None


def check_influential_journal(publication):
    if not publication:
        return False
    
    for journal in INFLUENTIAL_JOURNALS:
        if journal.lower() in publication.lower():
            return True
    return False


def check_excluded_names(authors):
    if not authors:
        return False
    
    for author in authors:
        for name in EXCLUDED_NAMES:
            if name.lower() in author.lower():
                return True
    return False


def check_excluded_universities(authors):
    if not authors:
        return False
    
    # For this implementation, we'll need to use LLM to check affiliations
    # Since we don't have affiliation information in the JSON, we'll skip this for now
    # In a real implementation, you would check author affiliations
    return False


def check_influential_institution(authors, pdf_text, llm_cfg):
    if not authors or not pdf_text:
        return False
    
    # Create the assistant agent
    system_instruction = '''
    You are an expert researcher. Your task is to determine if the authors of a paper belong to influential institutions.
    
    Influential institutions include: NASA, Nvidia, OpenAI, IBM, Intel, Google, Meta, Microsoft, Facebook, Alphabet.
    
    Please analyze the paper text and determine if any of the authors are affiliated with these institutions.
    Do not consider universities as influential institutions.
    
    Respond in the following JSON format:
    {
        "has_influential_institution_author": true/false,
        "name": "name of the last author in the institution",
        "institution": "name of the institution, no matter influential or not",
        "explanation": "brief explanation"
    }
    '''
    
    # Create the assistant
    bot = Assistant(
        llm=llm_cfg,
        system_message=system_instruction
    )
    
    # Prepare the message
    authors_str = ", ".join(authors)
    messages = [{
        'role': 'user', 
        'content': f'Authors: {authors_str}\n\nPaper text:\n{pdf_text}'  # Limit text length
    }]
    
    try:
        response = []
        for response in bot.run(messages=messages):
            pass
        
        if response and len(response) > 0:
            content = response[-1]['content']
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                return False
    except Exception as e:
        print(f"Error checking influential institution: {e}")
        return False


def check_influential_authors(authors, pdf_text, llm_cfg):
    if not authors or not pdf_text:
        return False
    
    # Create the assistant agent
    system_instruction = '''
    You are an expert researcher. Your task is to determine if there are any influential authors in the author list.
    
    An influential author is defined as:
    1. A member of national (China, US, Europe or Singapore) academy of science or engineering
    2. The leader of a famous lab or department
    
    DO NOT judge influence by citation count. DO NOT include authors from Zhejiang University.
    
    Respond in the following JSON format:
    {
        "has_influential_author": true/false,
        "name": "the name of the influential author, leave empty if none",
        "institution": "the institution which the author belongs to",
        "explanation": "brief explanation"
    }
    '''
    
    # Create the assistant
    bot = Assistant(
        llm=llm_cfg,
        system_message=system_instruction
    )
    
    # Prepare the message
    authors_str = ", ".join(authors)
    messages = [{
        'role': 'user', 
        'content': f'Authors: {authors_str}\n\nPaper text:\n{pdf_text}'  # Limit text length
    }]
    
    try:
        response = []
        for response in bot.run(messages=messages):
            pass
        
        if response and len(response) > 0:
            content = response[-1]['content']
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                return False
    except Exception as e:
        print(f"Error checking influential authors: {e}")
        return False


def should_include_paper(paper_info, pdf_path, llm_cfg):
    title = paper_info.get("title", "")
    publication = paper_info.get("publication")
    authors = paper_info.get("authors", [])
    
    print(f"Processing paper: {title}")

    # Rule 2: Check if should be excluded based on author names
    if check_excluded_names(authors):
        print(f"  -> Excluded: Contains excluded author names")
        return False
    
    # Rule 3: Check if should be excluded based on university
    if check_excluded_universities(authors):
        print(f"  -> Excluded: Affiliated with excluded university")
        return False
    
    # For the remaining checks, we need to read the PDF
    pdf_text = pdf_to_text(pdf_path)
    if not pdf_text:
        print(f"  -> Excluded: Could not read PDF")
        return False
    
    # Rule 1: Check if published in influential journal
    if check_influential_journal(publication):
        print(f"  -> Included: Published in influential journal")
        return {"institution": "not known", "name": authors[-1], "publication": publication}

    # Rule 4: Check if authors belong to influential institutions
    inst = check_influential_institution(authors, pdf_text, llm_cfg)
    if inst and inst["has_influential_institution_author"]:
        print(f"  -> Included: Has influential institution author")
        return {"institution": inst["institution"], "name": inst["name"], "publication": publication}
    
    # Rule 5: Check if there are influential authors
    inst = check_influential_authors(authors, pdf_text, llm_cfg)
    if inst and inst["has_influential_author"]:
        print(f"  -> Included: Has influential author")
        return {"institution": inst["institution"], "name": inst["name"], "publication": publication}
    
    print(f"  -> Excluded: Does not meet inclusion criteria")
    return False


def filter_papers(folder_path, publish_info_path, llm_cfg=None):
    # Configure LLM if not provided
    if llm_cfg is None:
        llm_cfg = {
            'model': './Qwen3-Next-80B-A3B-Instruct',
            'model_server': 'http://10.202.236.93:8000/v1',
            # 'api_key': 'YOUR_DASHSCOPE_API_KEY',  # Will use DASHSCOPE_API_KEY environment variable
            'generate_cfg': {
                'max_input_tokens': 150000,
                'temperature': 1.0
                }
        }
    
    # Read publish info
    with open(publish_info_path, 'r', encoding='utf-8') as f:
        publish_info = json.load(f)
    
    # Results to store filtered papers
    filtered_papers = []
    
    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDF files and {len(publish_info)} entries in publish_info.json")
    
    # Process each paper
    for i, paper_info in enumerate(publish_info):
        title = paper_info.get("title", "")
        print(f"\n--- Processing paper {i+1}/{len(publish_info)} ---")
        
        # Find corresponding PDF file (match by title)
        pdf_file = None
        for pdf in pdf_files:
            # Try to match PDF filename with title
            if title.lower().replace(" ", "_").replace(":", "") in pdf.lower().replace(" ", "_").replace(":", ""):
                pdf_file = pdf
                break
            # Also try exact match with expected format
            expected_name = title.replace(" ", "_").replace(":", "") + ".pdf"
            if pdf == expected_name:
                pdf_file = pdf
                break
        
        if not pdf_file:
            print(f"  -> Excluded: Could not find PDF file for '{title}'")
            continue
        
        pdf_path = os.path.join(folder_path, pdf_file)
        
        # Check if paper should be included
        out = should_include_paper(paper_info, pdf_path, llm_cfg)
        if out:
            filtered_papers.append({'file': pdf_file} | out)
    
    return filtered_papers


def one_folder(folder_path):
    publish_info_path = os.path.join(folder_path, "publish_info.json")
    
    if not os.path.exists(publish_info_path):
        print(f"Publish info file not found: {publish_info_path}")
        return
    
    # Read publish info
    with open(publish_info_path, 'r', encoding='utf-8') as f:
        publish_info = json.load(f)
    
    # Configure LLM
    llm_cfg = {
        'model': './Qwen3-Next-80B-A3B-Instruct',
        'model_server': 'http://10.202.236.93:8000/v1',
        # 'api_key': 'YOUR_DASHSCOPE_API_KEY',  # Will use DASHSCOPE_API_KEY environment variable
        'generate_cfg': {
            'max_input_tokens': 150000,
            'temperature': 0.7
            }
    }
    
    # Process PDF names to ensure they match title format
    renamed_files = process_pdf_name(folder_path, publish_info, llm_cfg)
    if renamed_files:
        print(f"Renamed {len(renamed_files)} PDF files to match title format")
        print("Renamed files:")
        for old_name, new_name in renamed_files.items():
            print(f"  {old_name} -> {new_name}")
    
    # Filter papers
    filtered_papers = filter_papers(folder_path, publish_info_path, llm_cfg)
    
    # Save results to a txt file
    if filtered_papers:
        output_file = folder_path + "/filtered_papers.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(filtered_papers, f, indent=4)
    
    print(f"\nFiltered {len(filtered_papers)} papers out of {len([f for f in os.listdir(folder_path) if f.endswith('.pdf')])} total papers")
    
    # Also print the results
    print("\nFiltered papers:")
    for paper in filtered_papers:
        print(f"  - {paper}")

def main():
    for name in os.listdir():
        if os.path.isdir(name) and "_" in name and not os.path.exists(name + "/filtered_papers.json"):
            print(f"----------------- Processing {name} ---------------------")
            one_folder(name)

if __name__ == "__main__":
    main()
