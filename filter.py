import os
import json
import re
from qwen_agent.agents import Assistant
from PyPDF2 import PdfReader

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


def process_pdf_name(folder_path, llm_cfg):
    """
    Process PDF file names to ensure they match the title format with underscores.
    Uses an LLM agent to read the actual title from each PDF file.
    
    Args:
        folder_path (str): Path to the folder containing PDF files
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

def check(pdf_text, llm_cfg, exclude_author, author_standard=None, inst_standard=None, pub_standard=None):   
    if not author_standard:
        author_standard = '''
        1. A fellow of the national academy of science or engineering in China, US, Europe or Singapore
        (or)2. The leader of a famous lab in US, Europe or Singapore
        '''

    if not inst_standard:
        inst_standard = '''
        1. Big tech companies like Google, Nvidia, Openai, Meta, Microsoft, etc.
        (and)2. Do not consider universities as influential institutions
        '''

    if not pub_standard:
        pub_standard = '''
        1. Nature, Science and Cell
        '''
    # Create the assistant agent
    system_instruction = f'''
    You are an expert researcher. Your task is to determine if a paper is influential.
    
    An influential paper is defined as:
    1. Do not have {exclude_author} in the authors list
    (and)2. Published on influential journals or written by influential authors or written by authors from influential institutions

    An influential journal is defined to be:
    {pub_standard}

    An influential author is defined to be:
    {author_standard}
    Only check if the last three authors in the author list is influential

    An influential institution is defined to be:
    {inst_standard}
    
    DO NOT judge influence by citation count. If you're not sure about something, please check online.
    
    Respond in the following JSON format:
    {{
        "is_influential": true/false,
        "author": "the name of the influential author",
        "pub": "the publication place of the paper"
        "inst": "the institution which the author belongs to",
        "explanation": "brief explanation"
    }}
    '''
    
    # Create the assistant
    bot = Assistant(
        llm=llm_cfg,
        system_message=system_instruction
    )
    
    # Prepare the message
    messages = [{
        'role': 'user', 
        'content': f'Paper text:\n{pdf_text}' 
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


def should_include_paper(pdf_path, llm_cfg, exclude_author, author_standard=None, inst_standard=None, pub_standard=None):   
    print(f"Processing paper: {pdf_path}")
    
    # For the remaining checks, we need to read the PDF
    pdf_text = pdf_to_text(pdf_path)
    if not pdf_text:
        print(f"  -> Excluded: Could not read PDF")
        return False
    
    # Check if paper is influential
    result = check(pdf_text, llm_cfg, exclude_author, author_standard, inst_standard, pub_standard)
    try:
        if result['is_influential']:
            print(f"  -> Included: paper is influential")
            return {"inst": result["inst"], "author": result["author"], "pub": result["pub"]}
        else:
            print(f"  -> Excluded: paper is not influential")
            return False
    except:
        print(f"   -> Excluded: parsing error.")
        return False

def filter_papers(folder_path, llm_cfg, exclude_author, author_standard=None, inst_standard=None, pub_standard=None):        
    # Results to store filtered papers
    filtered_papers = []
    
    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Process each paper
    for i, pdf_file in enumerate(pdf_files):
        print(f"\n--- Processing paper {i+1}/{len(pdf_files)} ---")
                
        pdf_path = os.path.join(folder_path, pdf_file)
        
        # Check if paper should be included
        out = should_include_paper(pdf_path, llm_cfg, exclude_author, author_standard, inst_standard, pub_standard)
        if out:
            filtered_papers.append({'file': pdf_file} | out)
    
    return filtered_papers


def one_folder(folder_path, llm_cfg, exclude_author, author_standard=None, inst_standard=None, pub_standard=None):        
    # Process PDF names to ensure they match title format
    renamed_files = process_pdf_name(folder_path, llm_cfg)
    if renamed_files:
        print(f"Renamed {len(renamed_files)} PDF files to match title format")
        print("Renamed files:")
        for old_name, new_name in renamed_files.items():
            print(f"  {old_name} -> {new_name}")
    
    # Filter papers
    filtered_papers = filter_papers(folder_path, llm_cfg, exclude_author, author_standard=None, inst_standard=None, pub_standard=None)
    
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
    '''
    for name in os.listdir():
        if os.path.isdir(name) and "_" in name and not os.path.exists(name + "/filtered_papers.json"):
            print(f"----------------- Processing {name} ---------------------")
            one_folder(name)
    '''

    llm_cfg = {
        'model': './Qwen3-Next-80B-A3B-Instruct',
        'model_server': 'http://10.202.236.93:8000/v1',
        # 'api_key': 'YOUR_DASHSCOPE_API_KEY',  # Will use DASHSCOPE_API_KEY environment variable
        'generate_cfg': {
            'max_input_tokens': 100000,
            'temperature': 1.0
            }
    }
    exclude_author = "Gang Pan"
    author_standard = '''
        1. A fellow of the national academy of science or engineering in China, US, Europe or Singapore
        (or)2. The leader of a famous lab in US, Europe or Singapore
    '''
    inst_standard = '''
        1. Big tech companies like Google, Nvidia, Openai, Meta, Microsoft, etc.
        (and)2. Do not consider universities as influential institutions
    '''
    pub_standard = '''
        1. Nature, Science and Cell
    '''
    one_folder('Example', llm_cfg, exclude_author, author_standard, inst_standard, pub_standard)

if __name__ == "__main__":
    main()
