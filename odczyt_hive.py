import random
import numpy as np
import os
from utils import get_logs, parse_logs, clean_data, LogParser

def reverse_sequence(r):
    reversed_string = ""
    position_list = r.split()
    for pos in reversed(position_list):
        new_pos = ""
        for char in pos:
            if char == 'w':
                new_pos += 'b'
            elif char == 'b':
                new_pos += 'w'
            else:
                new_pos += char
        reversed_string += new_pos + ' '
    return reversed_string.strip()

def extract_words(logs, key):
    pieces = []
    rows = logs[key]
    rows_count = len(rows)
    for i, row in enumerate(rows):
        if len(row) == 3:
            pieces.extend(row[1:3])
    return pieces

def extract_words_context(logs, key):
    pieces = []
    rows = logs[key]
    rows_count = len(rows)
    
    for i, row in enumerate(rows):
        if len(row) == 3:
            pieces.append(''.join(row[1:]))
    return pieces

def odczyt(keys1, keys2, n=10000, player="w", l=6):
    pozytywne = set()
    negatywne = set()
    for key in keys1:
        words = extract_words_context(logs, key)
        pozytywne.add(tuple(words[::2][:l]))
    for key in keys2:
        words = extract_words_context(logs, key)
        negatywne.add(tuple(words[::2][:l]))

    koncowy = open('hive.txt', 'w')
    neutralne = pozytywne & negatywne
    for s in pozytywne - neutralne:
        if player == "w":
            print(f"1 {l} %s" % ' '.join(s), file=koncowy)
        else:
            print(f"1 {l} %s" % reverse_sequence(' '.join(s)), file=koncowy)

    for s in negatywne | neutralne:
        if player == 'w':
            print(f"0 {l} %s" % ' '.join(s), file=koncowy)
        else:
            print(f"0 {l} %s" % reverse_sequence(' '.join(s)), file=koncowy)
    return pozytywne, negatywne

if __name__ == "__main__":
    logs = parse_logs(get_logs())
    log_parser = LogParser(logs)
    all_keys, white_keys, black_keys, draw_keys = log_parser.parse_logs()
    pozytywne, negatywne = odczyt(white_keys, black_keys, l=4)
