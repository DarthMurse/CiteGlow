# CiteGlow
When you're applying for academic awards or fundings, do you find searching for positive comments by other influential scholars about your work tedious and labor-intensive? Well, CiteGlow is meant to save you from hours of tedious work of searching for author information and positive comments in papers that cite your work. CiteGlow use LLM agents to automatically find influential authors and positive comments in papers that cite your work. All you have to do is download the papers that cite your work, and provide the title of your paper, CiteGlow will do the rest. Currently, CiteGlow suuports the following features:

+ Find papers with influential authors
+ Find positive comments of your work in papers
+ Exclude self citations
+ Export found positive comments of your paper to csv file
+ Custom definition of influential authors in natural language

Enjoy the power of LLMs!

## Installation
Clone the repository, then create a python environment with python version 3.12 and install the dependencies.
```
git clone https://github.com/DarthMurse/CiteGlow.git
cd CiteGlow

# install python environment
conda create -n citeglow python=3.12
conda activate citeglow
pip install -r requirements.txt
```

## Usage
Before using CiteGlow, you should provide a list of your papers that you want to find positive citing papers in `papers.txt`, each line containing the title of your paper. And you should also download papers that cite your paper in seperate folders, each folder containing a `title.txt` file which contains the title of your paper. In short, you file structure should be like this:

```
root folder
|--- ... (all the source files in the repo)
|--- papers.txt
|--- paper1 (folder name could be anything)
    |--- title.txt (title of your paper1)
    |--- cite_paper1.pdf (pdf name could be anything)
    |--- cite_paper2.pdf (pdf name could be anything)
|--- paper2 (folder name could be anything)
    |--- title.txt (title of your paper2)
    |--- cite_paper1.pdf (pdf name could be anything)
    |--- cite_paper2.pdf (pdf name could be anything)
|--- ...
```

To define your custom criterion for other influential scholars, you could edit the `author_standar` string in `main.py`, and because we use LLMs, you will need to specify your api_key and other other configurations in the `main.py`. For detailed explanation of the LLM configuration, please refer to [qwen-agent](https://github.com/QwenLM/Qwen-Agent#:~:text=llm_cfg%20%3D%20%7B,%3A%200.8%0A%20%20%20%20%7D%0A%7D).

After setting up all the configurations in `main.py`, you can run CiteGlow with 
```
python3 main.py
```
And wait for the final outcome in `final.csv`
