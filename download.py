import os
import re
import arxiv
import semanticscholar as sch
import requests
import json
import pandas as pd
import shutil
from pathlib import Path

def create_paper_folder(title):
    folder_path = sanitize_filename(title)
    os.makedirs(folder_path, exist_ok=True)
    with open(folder_path + "/title.txt", "w") as f:
        f.write(title)
    return folder_path

def sanitize_filename(title, max_length=100):
    title = title.replace(' ', '_')
    
    # Remove or replace invalid characters (keep letters, digits, underscore, hyphen, dot)
    title = re.sub(r'[^a-zA-Z0-9._\-]', '_', title)
    
    # Collapse multiple underscores into one
    title = re.sub(r'_+', '_', title)
    
    # Strip leading/trailing underscores
    title = title.strip('_')
    
    # Limit length (optional, but recommended)
    if len(title) > max_length:
        title = title[:max_length].rstrip('_')

    return title

def download_arxiv_paper(paper_id, filename=None):
    url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    if filename is None:
        filename = f"{paper_id}.pdf"
    
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download. Status code: {response.status_code}")

def search_citing_papers(paper_title, folder_path):
    # Search for papers that cite the given paper using Semantic Scholar
        # Initialize the Semantic Scholar client
    client = sch.SemanticScholar(api_key="I4CUVPi8VS3MR68o8yrYc1MJXbCoIm1G30RPZneL")
    
    # First, find the paper
    search_results = client.search_paper(paper_title, fields=['title'], limit=1)
    if not search_results:
        print("Paper not found on Semantic Scholar.")
        return [], [], []
    
    paper = search_results[0]
    paper_id = paper.paperId
    
    # Get citing papers (citations)
    citing_papers_results = client.get_paper_citations(paper_id, limit=1000)
    
    # Extract titles of citing papers
    citing_paper_titles = []
    unavailable_papers = []
    publish_info = []
    for citation in citing_papers_results:
        citing_paper_titles.append(citation.paper.title)
        try:
            if "ArXiv" in citation.paper.externalIds.keys():
                download_arxiv_paper(citation.paper.externalIds['ArXiv'], folder_path + '/' + sanitize_filename(citation.paper.title) + '.pdf')
            else:
                unavailable_papers.append(citation.paper.title)
        except:
            unavailable_papers.append(citation.paper.title)
        if citation.paper.publicationVenue:
            publish_info.append({"title": citation.paper.title, "publication": citation.paper.publicationVenue.name, "authors": get_author_list(citation.paper.authors), "citationCount": citation.paper.citationCount})
        else:
            publish_info.append({"title": citation.paper.title, "publication": None, "authors": get_author_list(citation.paper.authors), "citationCount": citation.paper.citationCount})
            
    return citing_paper_titles, unavailable_papers, publish_info

def get_author_list(authors):
    result = []
    for a in authors:
        result.append(a.name)
    return result

def single_paper(paper_title):
    # Get paper title from user
    paper_title = paper_title.strip()
    
    if not paper_title:
        print("Paper title cannot be empty.")
        return
    
    # Resume
    if os.path.exists(sanitize_filename(paper_title)):
        return

    # Create folder for the paper       
    folder_path = create_paper_folder(paper_title)
    
    # Search for citing papers
    print(f"Searching for papers that cite the given paper ---- {paper_title}")
    citing_paper_titles, unavailable_papers, publish_info = search_citing_papers(paper_title, folder_path)
    with open(folder_path + "/publish_info.json", "w") as f:
        json.dump(publish_info, f, indent=4)
    
    if not citing_paper_titles:
        print("No citing papers found.")
        return
    
    print(f"Found {len(citing_paper_titles)} papers in total, {len(unavailable_papers)} paper not available.")

    # Write unavailable papers to unavailable.txt
    if unavailable_papers:
        unavailable_file = folder_path + '/' + "unavailable.txt"
        with open(unavailable_file, "w", encoding="utf-8") as f:
            for paper in unavailable_papers:
                f.write(f"{paper}\n")
        print(f"List of unavailable papers saved to {unavailable_file}")
        return False
    
    print(f"Download process completed.")
    return True

def main():
    # single_paper("RSNN: Recurrent Spiking Neural Networks for Dynamic Spatial-Temporal Information Processing")
    paper_list = pd.read_csv("../papers.csv")
    #'''
    not_full_list = []
    for name in os.listdir():
        if os.path.isdir(name) and '_' in name:
            try:
                with open(name + '/publish_info.json') as f:
                    data = json.load(f)
            except:
                data = False
            if not data:
                shutil.rmtree(name)

    for i, item in enumerate(paper_list['文章名字']):
        print(f'--------------------- {i}/{len(paper_list)} ----------------------')
        if not single_paper(item):
            not_full_list.append(item)
    with open("not_full_list.txt", "w") as f:
        f.writelines(not_full_list)
    #'''
    #single_paper(paper_list['文章名字'][11])

def clear():
    for name in os.listdir():
        if os.path.isdir(name) and '_' in name:
            if os.path.exists(name + '/detailed_analysis.csv'):
                os.remove(name + '/detailed_analysis.csv')
            if os.path.exists(name + '/positive_comments.csv'):
                os.remove(name + '/positive_comments.csv')
            if os.path.exists(name + '/filtered_papers.json'):
                os.remove(name + '/filtered_papers.json')

if __name__ == "__main__":
    main()
    #clear()
