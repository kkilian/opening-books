import json
from Util import get_logs, parse_logs, clean_data, LogParser, load_link_list_from_json, accept, graj_niegraj
from make_opening import OpeningGenerator
from make_book import BookGenerator
"""
opening_book_generator = OpeningGenerator()
opening_book_generator.make_opening(player="w", l=2, context=True)
opening_book_generator.make_opening(player="b", l=2, context=True)

book_generator = BookGenerator()
book_generator.make_book(player="w")
book_generator.make_book(player="b")
opening_book_w, opening_book_b = load_link_list_from_json("book_w.json"), load_link_list_from_json("book_b.json")

"""
board_state1 = "wG1..."
board_state2 = "wG1... bG1"

result1 = graj_niegraj(opening_book_w, opening_book_b, board_state1, "b")
result2 = graj_niegraj(opening_book_w, opening_book_b, board_state2, "w")

print(result1)
print(result2)

