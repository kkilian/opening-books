import random
import numpy as np
import os
from utils import get_logs, parse_logs, clean_data, LogParser

def extract_words(logs, key):
    pieces = []
    rows = logs[key]
    rows_count = len(rows)
    for i, row in enumerate(rows):
        if len(row) == 3:
            pieces.extend(row[1:3])
    return pieces

def odczyt(keys1, keys2, n=10000, l=6):
    pozytywne = set()
    negatywne = set()
    neutralne = set()

    for key in keys1:
        words = extract_words(logs, key)
        pozytywne.add(tuple(words[::2][:l]))
    for key in keys2:
        words = extract_words(logs, key)
        negatywne.add(tuple(words[::2][:l]))

        
    koncowy = open('hive.txt', 'w')
    neutralne = pozytywne & negatywne  
    for s in pozytywne - neutralne:
        print(f"1 {l} %s" % ' '.join(s), file=koncowy)  

    for s in negatywne | neutralne:
        print(f"0 {l} %s" % ' '.join(s), file=koncowy)  
    return pozytywne, negatywne

if __name__ == "__main__":
    logs = parse_logs(get_logs()) 
    log_parser = LogParser(logs)
    all_keys, white_keys, black_keys, draw_keys = log_parser.parse_logs()
    pozytywne, negatywne = odczyt(white_keys, black_keys, l=8)