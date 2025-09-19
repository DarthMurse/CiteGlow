from filter import one_folder
from filter_comment import process_papers
import os
import pandas as pd

# LLM configuration, please refer to the README of qwen-agent
llm_cfg = {
        'model': 'your local model name',
        'model_server': 'your local model address',
        # 'api_key': 'YOUR_DASHSCOPE_API_KEY',  # Will use DASHSCOPE_API_KEY environment variable
        'generate_cfg': {
            'max_input_tokens': 100000,
            'temperature': 0.7
            }
}
# Your name
exclude_author = "Your name"
# Criterion for a influential author, stated in a list
author_standard = '''
    1. A fellow of the national academy of science or engineering in China, US, Europe or Singapore
    (or)2. The leader of a famous lab in US, Europe or Singapore
'''
# Criterion for a influential institution, stated in a list
inst_standard = '''
    1. Big tech companies like Google, Nvidia, Openai, Meta, Microsoft, etc.
    (and)2. Do not consider universities as influential institutions
'''
# Criterion for a influential publication, stated in a list
pub_standard = '''
    1. Nature, Science and Cell
'''

def main():
    for name in os.listdir():
        if os.path.isdir(name) and os.path.exists(name + "/title.txt"):
            # save filtered_paper.json to name folder
            one_folder(name, llm_cfg, exclude_author, author_standard, inst_standard, pub_standard)
    for name in os.listdir():
        if os.path.isdir(name) and os.path.exists(name + "/filtered_papers.json"):
            # save positive_comments.csv to name folder
            process_papers(name, llm_cfg) 

    # Merge all the positve comments
    df = pd.DataFrame(columns=['index', 'target_title', 'paper_title', 'author', 'institution', 'publication', 'positive_comments'])
    for name in os.listdir():
        if os.path.isdir(name) and os.path.exists(name + '/positive_comments.csv'):
            new_df = pd.read_csv(name + '/positive_comments.csv')
            df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv("final.csv")

if __name__ == "__main__":
    main()

