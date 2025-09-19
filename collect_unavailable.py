import os
import pandas as pd

def collect_list():
    result = []
    for name in os.listdir():
        if len(name) > 30 and os.path.exists(name + '/unavailable.txt'):
            with open(name + '/title.txt', 'r') as f:
                cited_title = f.readline()
            with open(name + '/unavailable.txt', 'r') as f:
                titles = f.readlines()
            for title in titles:
                result.append({'cited_title': cited_title, 'title': title})
    return result

def main():
    papers = collect_list()
    df = pd.DataFrame(columns=['cited_title', 'title'])
    for paper in papers:
        df = pd.concat([df, pd.DataFrame([paper])], ignore_index=True)
    df.to_csv('unavailable.csv')

if __name__ == "__main__":
    main()

