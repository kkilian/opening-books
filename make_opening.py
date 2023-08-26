import random
import numpy as np
from hive_log_processing import get_logs, parse_logs, clean_data, LogParser

def reverse_sequence(sequence):
    reversed_string = ""
    position_list = sequence.split()
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

def analyze_data(logs, positive_keys, negative_keys, l, n=10000, player="w", context=False):
    positive_set = set()
    negative_set = set()
    if context:
        for key in positive_keys:
            words = extract_words_context(logs, key)
            positive_set.add(tuple(words[::2])[:l])  
        for key in negative_keys:
            words = extract_words_context(logs, key)
            negative_set.add(tuple(words[::2])[:l])  
    else:
        for key in positive_keys:
            words = extract_words(logs, key)
            positive_set.add(tuple(words[::2])[:l])  
        for key in negative_keys:
            words = extract_words(logs, key)
            negative_set.add(tuple(words[::2])[:l])  

    neutral_set = positive_set & negative_set
    with open('hive.txt', 'w') as final_output:
        for s in positive_set - neutral_set:
            if player == "w":
                print(f"1 {l} %s" % ' '.join(s), file=final_output)
            else:
                print(f"1 {l} %s" % reverse_sequence(' '.join(s)), file=final_output)

        for s in negative_set | neutral_set:
            if player == 'w':
                print(f"0 {l} %s" % ' '.join(s), file=final_output)
            else:
                print(f"0 {l} %s" % reverse_sequence(' '.join(s)), file=final_output)

    final_output.close()

def make_opening(player="w", l=6, context=False):
    logs = parse_logs(get_logs())
    log_parser = LogParser(logs)
    all_keys, white_keys, black_keys, draw_keys = log_parser.parse_logs()
    analyze_data(logs, white_keys, black_keys, l, context=context)

if __name__ == "__main__":
    make_opening(player="w", l=5, context = True)  
    print("Openings written to hive.txt")
