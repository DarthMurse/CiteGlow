import os
import pandas as pd
from qwen_agent.agents import Assistant
from PyPDF2 import PdfReader
import json
import re


def get_paper_title(folder):
    """Get the title of the given paper from title.txt"""
    with open(folder + '/title.txt', 'r', encoding='utf-8') as f:
        return f.read().strip()


def pdf_to_text(pdf_path):
    """Convert PDF to text"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None


def find_citation_index(paper_title, paper_text, llm_cfg):
    """Find the citation index of the target paper in the references"""
    
    # Create the assistant agent
    system_instruction = f'''
    You are an expert academic researcher. Your task is to identify the citation index of a specific paper in the reference section of a research paper.
    
    Target paper title: "{paper_title}"
    
    Please follow these steps:
    1. Look for the reference section in the paper text (usually starts with "References" or "Bibliography")
    2. Find the entry that matches the target paper title
    3. Identify the citation index for that entry (e.g., [1], [12], (Smith et al., 2023), etc.)
    
    Respond in the following JSON format:
    {{
        "citation_index": "the citation index found, or null if not found",
        "explanation": "brief explanation of how you found the index or why you couldn't find it"
    }}
    
    If you cannot find the citation, set "citation_index" to null.
    '''
    
    # Create the assistant
    bot = Assistant(
        llm=llm_cfg,
        system_message=system_instruction
    )
    
    # Prepare the message with the paper text
    messages = [{
        'role': 'user', 
        'content': f'Please find the citation index for "{paper_title}" in the following paper text:\n\n{paper_text}'
    }]  # Limiting text length to avoid token limits
    
    try:
        response = []
        for response in bot.run(messages=messages):
            # Get the final response
            pass
        
        # Extract the content from the response
        if response and len(response) > 0:
            content = response[-1]['content']
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # If not JSON, try to extract information manually
                return {
                    "citation_index": None,
                    "explanation": "Could not parse LLM response"
                }
        else:
            return {
                "citation_index": None,
                "explanation": "No response from LLM"
            }
    except Exception as e:
        print(f"Error finding citation index: {e}")
        return {
            "citation_index": None,
            "explanation": f"Error: {e}"
        }


def find_paragraphs_with_citation(paper_text, citation_index, llm_cfg):
    """Find paragraphs that contain the citation index"""
    
    if not citation_index:
        return {
            "paragraphs": [],
            "explanation": "No citation index provided"
        }
    
    # Create the assistant agent
    system_instruction = f'''
    You are an expert academic researcher. Your task is to find paragraphs in a research paper that contain a specific citation.
    
    Target citation: {citation_index}
    
    Please follow these steps:
    1. Look through the main text of the paper (not the references)
    2. Find all paragraphs that contain the citation {citation_index}
    3. Return these paragraphs in a structured format
    
    Respond in the following JSON format:
    {{
        "paragraphs": [
            "paragraph 1 that contains the citation",
            "paragraph 2 that contains the citation"
        ],
        "explanation": "number of paragraphs found and any additional notes"
    }}
    
    If no paragraphs contain the citation, return an empty array for "paragraphs".
    '''
    
    # Create the assistant
    bot = Assistant(
        llm=llm_cfg,
        system_message=system_instruction
    )
    
    # Prepare the message with the paper text
    messages = [{
        'role': 'user', 
        'content': f'Please find paragraphs containing the citation "{citation_index}" in the following paper text:\n\n{paper_text}'
    }]  # Limiting text length to avoid token limits
    
    try:
        response = []
        for response in bot.run(messages=messages):
            # Get the final response
            pass
        
        # Extract the content from the response
        if response and len(response) > 0:
            content = response[-1]['content']
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # If not JSON, try to extract information manually
                return {
                    "paragraphs": [],
                    "explanation": "Could not parse LLM response"
                }
        else:
            return {
                "paragraphs": [],
                "explanation": "No response from LLM"
            }
    except Exception as e:
        print(f"Error finding paragraphs with citation: {e}")
        return {
            "paragraphs": [],
            "explanation": f"Error: {e}"
        }


def analyze_paragraphs_for_positive_comments(paragraphs, citation_index, target_paper_title, llm_cfg):
    """Analyze paragraphs to determine if they contain positive comments about the cited paper"""
    
    if not paragraphs:
        return {
            "has_positive_comments": False,
            "positive_comments": [],
            "explanation": "No paragraphs provided for analysis"
        }
    
    # Create the assistant agent
    system_instruction = f'''
    You are an expert academic researcher. Your task is to analyze paragraphs to determine if they contain positive comments about a specific cited paper.
    
    Target paper: "{target_paper_title}"
    Citation used in text: {citation_index}
    
    Positive comments include expressions like:
    - "... is the first to ..."
    - "... achieves fast inference/good performance ..."
    - Being compared favorably by the author in experiments
    - Other positive evaluations of the cited work
    
    Please follow these steps:
    1. Carefully read each paragraph
    2. Determine if the paragraph contains positive comments about the cited work
    3. Extract the specific sentences that contain positive comments
    
    Respond in the following JSON format:
    {{
        "has_positive_comments": true/false,
        "positive_comments": [
            "sentence 1 containing positive comment",
            "sentence 2 containing positive comment"
        ],
        "explanation": "explanation of your analysis, be simple and don't explain too much"
    }}
    
    If no positive comments are found, set "has_positive_comments" to false and "positive_comments" to an empty array.
    '''
    
    # Create the assistant
    bot = Assistant(
        llm=llm_cfg,
        system_message=system_instruction
    )
    
    # Prepare the message with the paragraphs
    paragraphs_text = "\n\n".join(paragraphs)
    messages = [{
        'role': 'user', 
        'content': f'Please analyze the following paragraphs for positive comments about "{target_paper_title}" (cited as {citation_index}):\n\n{paragraphs_text}'
    }]
    
    try:
        response = []
        for response in bot.run(messages=messages):
            # Get the final response
            pass
        
        # Extract the content from the response
        if response and len(response) > 0:
            content = response[-1]['content']
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # If not JSON, try to extract information manually
                has_positive = "true" in content.lower() or "positive" in content.lower()
                sentences = re.findall(r'"([^"]*?)"', content)
                return {
                    "has_positive_comments": has_positive,
                    "positive_comments": sentences,
                    "explanation": "Extracted from LLM response"
                }
        else:
            return {
                "has_positive_comments": False,
                "positive_comments": [],
                "explanation": "No response from LLM"
            }
    except Exception as e:
        print(f"Error analyzing paragraphs for positive comments: {e}")
        return {
            "has_positive_comments": False,
            "positive_comments": [],
            "explanation": f"Error: {e}"
        }


def process_single_paper(paper_file, target_paper_title, llm_cfg, folder_path):
    """Process a single paper file"""
    print(f"Processing paper: {paper_file}")
    
    # Convert PDF to text
    pdf_path = os.path.join(folder_path, paper_file)
    paper_text = pdf_to_text(pdf_path)
    
    if paper_text is None:
        return None
        
    # Step 1: Find citation index
    print(f"  Finding citation index...")
    citation_result = find_citation_index(target_paper_title, paper_text, llm_cfg)
    citation_index = citation_result.get("citation_index")
    
    if not citation_index:
        print(f"  Citation index not found: {citation_result.get('explanation', 'Unknown reason')}")
        return {
            'paper_title': paper_file,
            'has_positive_comments': False,
            'positive_comments': [],
            'details': f"Citation index not found: {citation_result.get('explanation', 'Unknown reason')}"
        }
    
    print(f"  Found citation index: {citation_index}")
    
    # Step 2: Find paragraphs with citation
    print(f"  Finding paragraphs with citation...")
    paragraphs_result = find_paragraphs_with_citation(paper_text, citation_index, llm_cfg)
    paragraphs = paragraphs_result.get("paragraphs", [])
    
    if not paragraphs:
        print(f"  No paragraphs found with citation: {paragraphs_result.get('explanation', 'Unknown reason')}")
        return {
            'paper_title': paper_file,
            'has_positive_comments': False,
            'positive_comments': [],
            'details': f"No paragraphs found with citation: {paragraphs_result.get('explanation', 'Unknown reason')}"
        }
    
    print(f"  Found {len(paragraphs)} paragraphs with citation")
    
    # Step 3: Analyze paragraphs for positive comments
    print(f"  Analyzing paragraphs for positive comments...")
    analysis_result = analyze_paragraphs_for_positive_comments(
        paragraphs, citation_index, target_paper_title, llm_cfg
    )
    
    has_positive = analysis_result.get("has_positive_comments", False)
    positive_comments = analysis_result.get("positive_comments", [])
    
    print(f"  Positive comments found: {has_positive}")
    if has_positive:
        print(f"  Number of positive comments: {len(positive_comments)}")
    
    return {
        'paper_title': paper_file,
        'has_positive_comments': has_positive,
        'positive_comments': positive_comments
    }


def process_papers(folder, llm_cfg):
    """Main function to process all papers and find those with positive comments"""
    
    # Get the title of the given paper
    target_paper_title = get_paper_title(folder)

    print(f"Target paper title: {target_paper_title}")
    
    # Results to store papers with positive comments
    results = []
    processed_papers = []
    
    # Get all PDF files in the RSNN directory
    with open(folder + '/filtered_papers.json', 'r') as f:
        paper_files = json.load(f)
    
    print(f"Found {len(paper_files)} PDF files to process...")
    
    # Process each paper
    for i, paper in enumerate(paper_files):
        paper_file = paper['file']
        print(f"\n--- Processing paper {i+1}/{len(paper_files)} ---")
        
        try:
            result = process_single_paper(paper_file, target_paper_title, llm_cfg, folder)
            if result:
                processed_papers.append(result)
                
                # If positive comments found, add to results
                if result['has_positive_comments']:
                    results.append({
                        'target_title': target_paper_title,
                        'paper_title': result['paper_title'],
                        'author': paper['author'],
                        'institution': paper['inst'],
                        'publication': paper['pub'],
                        'positive_comments': result['positive_comments']
                    })
                    print(f"✓ Found positive comments in {paper_file}")
                else:
                    print(f"✗ No positive comments found in {paper_file}")
            else:
                print(f"✗ Failed to process {paper_file}")
        except Exception as e:
            print(f"✗ Error processing {paper_file}: {e}")
    
    # Save results to CSV
    if results:
        df = pd.DataFrame(results)
        df.to_csv(folder + '/positive_comments.csv', index=False)
        print(f"\nSaved {len(results)} papers with positive comments to positive_comments.csv")
    else:
        print("\nNo papers with positive comments found.")

def main():
    process_papers("Example")
    '''
    for name in os.listdir():
        if os.path.isdir(name) and '_' in name and os.path.exists(name + '/filtered_papers.json') and not os.path.exists(name + '/positive_comments.csv'):
            process_papers(name)

    df = pd.DataFrame(columns=['index', 'target_title', 'paper_title', 'author', 'institution', 'publication', 'positive_comments'])
    for name in os.listdir():
        if os.path.isdir(name) and '_' in name and os.path.exists(name + '/positive_comments.csv'):
            new_df = pd.read_csv(name + '/positive_comments.csv')
            df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv("final.csv")
    '''

if __name__ == "__main__":
    main()
