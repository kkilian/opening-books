import random
import numpy as np
import os
from utils import get_logs, parse_logs, clean_data

def extract_words(logs, key):
    pieces = []
    rows = logs[key]
    rows_count = len(rows)
    for i, row in enumerate(rows):
        if len(row) == 3:
            pieces.extend(row[1:3])
    return pieces

def odczyt(keys1, keys2, n=10000):
    pozytywne = set()
    negatywne = set()
    neutralne = set()

    for key in keys1:
        words = extract_words(logs, key)
        print(words)
        pozytywne.add(tuple(words[::4][:6]))
    for key in keys2:
        words = extract_words(logs, key)
        negatywne.add(tuple(words[::4][:6]))

        
    koncowy = open('hive.txt', 'w')
    neutralne = pozytywne & negatywne  # Calculate neutral states
    for s in pozytywne - neutralne:
        print("1 6 %s" % ' '.join(s), file=koncowy)  

    for s in negatywne | neutralne:
        print("0 6 %s" % ' '.join(s), file=koncowy)  
    return pozytywne, negatywne

if __name__ == "__main__":
    logs = parse_logs(get_logs())

    all_keys = np.array([k for k, v in zip(logs.keys(), logs.values()) if len(v[-1]) > 1])
    white_keys = np.array([k for k, v in zip(logs.keys(), logs.values()) if len(v[-1]) > 1 and v[-1][1][0] == 'w'])
    black_keys = np.array([k for k, v in zip(logs.keys(), logs.values()) if len(v[-1]) > 1 and v[-1][1][0] == 'b'])
    remaining_keys = np.array([k for k in logs.keys() if k not in white_keys and k not in black_keys])
    draw_keys = np.array([k for k in remaining_keys if logs[k][-1] == ['d']])
    white_keys = np.append(white_keys, [k for k in remaining_keys if len(logs[k][-1]) > 1 and logs[k][-1][1][0] == 'r' and logs[k][-2][1][0] == 'w'])
    black_keys = np.append(black_keys, [k for k in remaining_keys if len(logs[k][-1]) > 1 and logs[k][-1][1][0] == 'r' and logs[k][-2][1][0] == 'b'])
    draw_keys = np.append(draw_keys, [k for k in remaining_keys if len(logs[k][-1]) > 1 and logs[k][-1][1][0] == 'a'])

    pozytywne, negatywne = odczyt(white_keys, black_keys)