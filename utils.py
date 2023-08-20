import numpy as np
import requests
import itertools
import os
import glob
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from board import Hive, HiveView, HivePiece
hive = Hive()
hive.setup()
view = HiveView(hive)

def get_logs():
    """
    Fetch logs from a GitHub repository and organize them into a dictionary.
    """
    logs = {}
    i = 1
    
    owner = "kkilian"
    repo = "hive_data"
    path = "Strong Players Only"
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    # Fetch the file list from the repository
    response = requests.get(url)
    if response.status_code == 200:
        try:
            files = response.json()
            for file in files:
                filename = file['name']
                if filename.endswith('.txt') and filename[0] == 'P':
                    logs[i] = filename
                    i += 1
        except ValueError as e:
            print(f"Error decoding response content: {e}")
            print("Response content:")
            print(response.content)
    else:
        print(f"Failed to fetch files from the repository. Status code: {response.status_code}")
    
    return logs

def parse_logs(logs):
    """
    Parse the logs stored in the dictionary and extract the log entries.
    """
    parsed_logs = {}
    for file_number, filename in logs.items():
        file_path = f"/Users/krzysztofkilian/Downloads/{filename}"  
        with open(file_path, 'r') as f:
            parsed_entries = []
            for line in f:
                parts = line.strip().split(' ')
                parsed_entries.append(parts)
            parsed_logs[file_number] = parsed_entries
    return parsed_logs

def process_logs(logs, pmd = []):
    """
    Process logs to extract matches based on specified criteria.
    """
    dictionary = {}
    for i in range(1, len(logs)):
        log_data = logs[i]
        cleaned_data = clean_data(match_patterns(log_data))
        matches = match(cleaned_data, pmd)
        if matches is not None:
            dictionary[i] = matches

    return dictionary

def match_patterns(logs):
    """
    Extract patterns from the logs using regular expressions.
    """
    pattern = re.compile(r'(\d+|[a-zA-Z]+\d*|[\W_]+)')
    matched = []
    for r in logs:
        row = np.array([], dtype=object)
        for example_str in r:
            matches = pattern.findall(example_str)
            if matches != []:
                row = np.append(row, matches)
        matched.append(row)
    return matched

def clean_data(data):
    """
    Clean the input data by performing various data cleaning operations.
    """
    df = pd.DataFrame(data).copy()
    df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce').astype('Int32')
    df = df.drop(columns=1)
    df = df[df.iloc[:, 1].notna() & (df.iloc[:, 1] != 'https')]
    df = df.replace({'wQ': 'wQ1', 'bQ': 'bQ1'}).fillna(0)
    last = df.iloc[-1, 1][0]
    first = df.iloc[0, 1][0]
    if first == 'w':
        df.insert(0, 'w_index', (df.index // 2) )
        df.loc[df.index % 2 != 0, 'w_index'] = ''

        df.insert(0, 'b_index', (df.index // 2) )
        df.loc[df.index % 2  != 1, 'b_index'] = ''
    else: 
        df.insert(0, 'w_index', (df.index // 2) )
        df.loc[df.index % 2 != 1, 'w_index'] = ''

        df.insert(0, 'b_index', (df.index // 2) )
        df.loc[df.index % 2  != 0, 'b_index'] = ''
        
    return df.iloc[:,:6]

def game_dict(data):
    """
    Convert DataFrame into a dictionary with modified values.
    """
    game_dict = {}
    for index, row in data.iterrows():
        key = row[0]
        value1 = row[2]
        value2 = row[3]
        value3 = row[4]

        game_dict[key] = (value1, value2, value3)

    # Modify values based on specific conditions
    for key, value in game_dict.items():
        if value[1] == "-":
            new_value = hive.W
            game_dict[key] = (value[0], new_value, value[2])
        if value[1] == "/":
            new_value = hive.NW
            game_dict[key] = (value[0], new_value, value[2])
        if value[1] == "\\":
            new_value = hive.NW
            game_dict[key] = (value[0], new_value, value[2])
        if value[2] == '0':
            new_value = hive.O
            game_dict[key] = (value[0], value[1], new_value)
        if value[2] == "-":
            new_value = hive.E
            game_dict[key] = (value[0], value[1], new_value)
        if value[2] == "/":
            new_value = hive.NE
            game_dict[key] = (value[0], value[1], new_value)
        if value[2] == "\\":
            new_value = hive.SE
            game_dict[key] = (value[0], value[1], new_value)

    return game_dict

def num_dir(num):
    """
    Translate a number to a corresponding direction.
    """
    translation_dict = {
        0: 'O',
        1: 'W',
        2: 'NW',
        3: 'NE',
        4: 'E',
        5: 'SE',
        6: 'SW'
    }
    return translation_dict.get(num)


def dir_num(direction):
    """
    Translate a direction to a corresponding number.
    """
    translation_dict = {
        'O': 0,
        'W': 1,
        'NW': 2,
        'NE': 3,
        'E': 4,
        'SE': 5,
        'SW': 6
    }
    return translation_dict.get(direction)

def match(data, pmd=[]):
    """
    Filter and match data based on specified pieces, moves, and directions.
    """
    dictionary = game_dict(data)

    column1 = data.iloc[:, 0].tolist()
    column2 = data.iloc[:, 1].tolist()

    combined_list = [val1 if val1 else val2 for val1, val2 in zip(column1, column2) if val1 or val2]
    appended_dictionary = {key: (num,) + value for (key, value), num in zip(dictionary.items(), combined_list)}
    data = pd.DataFrame.from_dict(appended_dictionary, orient='index')
    pmd_mask = []

    for i in range(len(pmd)):
        pmd_i = pmd[i]
        direction_num = dir_num(pmd_i[2]) if pmd_i[2] else None
        mask1 = data.iloc[:, 0] == pmd_i[1] if pmd_i[1] else True
        mask2 = data.iloc[:, 1] == pmd_i[0] if pmd_i[0] else True
        mask3 = data.iloc[:, 2] == direction_num if pmd_i[2] else data.iloc[:, 2]
        mask4 = data.iloc[:, 3] == direction_num if pmd_i[2] else data.iloc[:, 3]
        pmd_mask.append(mask1 & mask2 & mask3)
        
    if not data[pmd_mask[0]].empty:
        return data
import numpy as np

class LogParser:
    def __init__(self, logs):
        self.logs = logs

    def parse_all_keys(self):
        return np.array([k for k, v in self.logs.items() if len(v[-1]) > 1])

    def parse_white_keys(self):
        return np.array([k for k, v in self.logs.items() if len(v[-1]) > 1 and v[-1][1][0] == 'w'])

    def parse_black_keys(self):
        return np.array([k for k, v in self.logs.items() if len(v[-1]) > 1 and v[-1][1][0] == 'b'])

    def parse_remaining_keys(self):
        all_keys = set(self.logs.keys())
        white_keys = set(self.parse_white_keys())
        black_keys = set(self.parse_black_keys())
        return np.array(list(all_keys - white_keys - black_keys))

    def parse_draw_keys(self):
        remaining_keys = set(self.parse_remaining_keys())
        return np.array([k for k in remaining_keys if self.logs[k][-1] == ['d']])

    def process_remaining_keys(self, color):
        prev_color = 'w' if color == 'b' else 'b'
        remaining_keys = set(self.parse_remaining_keys())
        processed_keys = [k for k in remaining_keys if len(self.logs[k][-1]) > 1 and self.logs[k][-1][1][0] == 'r' and self.logs[k][-2][1][0] == prev_color]
        return np.array(processed_keys)

    def parse_and_append(self, keys, condition_color):
        return np.append(keys, self.process_remaining_keys(condition_color))

    def parse_logs(self):
        all_keys = self.parse_all_keys()
        white_keys = self.parse_and_append(self.parse_white_keys(), 'w')
        black_keys = self.parse_and_append(self.parse_black_keys(), 'b')
        draw_keys = self.parse_and_append(self.parse_draw_keys(), 'a')
        return all_keys, white_keys, black_keys, draw_keys
