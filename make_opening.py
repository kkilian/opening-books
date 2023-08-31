import random
import numpy as np
from hive_log_processing import get_logs, parse_logs, clean_data, LogParser

class HiveOpeningBookGenerator:
    def __init__(self):
        self.logs = parse_logs(get_logs())
        self.log_parser = LogParser(self.logs)
        self.all_keys, self.white_keys, self.black_keys, self.draw_keys = self.log_parser.parse_logs()

    @staticmethod
    def reverse_sequence(sequence):
        reversed_string = ""
        position_list = sequence.split()
        for pos in position_list:
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

    @staticmethod
    def extract_words(logs, key):
        pieces = []
        rows = logs[key]
        rows_count = len(rows)
        for i, row in enumerate(rows):
            if len(row) == 3:
                pieces.extend(row[1:3])
        return pieces

    @staticmethod
    def extract_words_context(logs, key):
        pieces = []
        rows = logs[key]
        rows_count = len(rows)
        
        for i, row in enumerate(rows):
            if len(row) == 3:
                pieces.append(''.join(row[1:]))
        return pieces

    def analyze_data(self, positive_keys, negative_keys, l, n=10000, player="w", context=False):
        positive_set = set()
        negative_set = set()

        if player == "w":
            
            if context:
                for key in positive_keys:
                    words = self.extract_words_context(self.logs, key)
                    positive_set.add(tuple(words[:])[:l])  
                for key in negative_keys:
                    words = self.extract_words_context(self.logs, key)
                    negative_set.add(tuple(words[:])[:l])  
            else:
                for key in positive_keys:
                    words = self.extract_words(self.logs, key)
                    positive_set.add(tuple(words[::2])[:l])  
                for key in negative_keys:
                    words = self.extract_words(self.logs, key)
                    negative_set.add(tuple(words[::2])[:l])  
        else:

            if context:
                for key in negative_keys:
                    words = self.extract_words_context(self.logs, key)
                    positive_set.add(tuple(words[:])[:l])  
                for key in positive_keys:
                    words = self.extract_words_context(self.logs, key)
                    negative_set.add(tuple(words[:])[:l])  
            else:
                for key in negative_keys:
                    words = self.extract_words(self.logs, key)
                    positive_set.add(tuple(words[::2])[:l])  
                for key in positive_keys:
                    words = self.extract_words(self.logs, key)
                    negative_set.add(tuple(words[::2])[:l])  

        neutral_set = positive_set & negative_set
        name = f"hive_{player}.txt" 
        with open(name, 'w') as final_output:
            for s in positive_set - neutral_set:
                print(f"1 {l} %s" % ' '.join(s), file=final_output)
      
            for s in negative_set | neutral_set:
                print(f"0 {l} %s" % ' '.join(s), file=final_output)
        return positive_set, negative_set

    def make_opening(self, player="w", l=4, context=False):
        self.analyze_data(self.white_keys, self.black_keys, l, player=player, context=context)


