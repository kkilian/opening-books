import json
from make_opening import HiveOpeningBookGenerator
from make_book import BookGenerator

"""opening_book_generator = HiveOpeningBookGenerator()
opening_book_generator.make_opening(player="w", l=5,context=True)
opening_book_generator.make_opening(player="b", l=5,context=True)

book_generator = BookGenerator()
book_generator.make_book("w")
book_generator.make_book("b")"""

def load_link_list_from_json(json_filename):
    with open(json_filename) as json_file:
        data = json.load(json_file)
    return data

def accept(opening_book, board_state):
    opening = board_state.split(' ')
    cd = {}

    for L, R in opening_book.items():
        L = L.split(' ')
        for i in range(1, len(L) + 1):
            p = L[:i]
            s = L[i:]

            if opening == p:
                if len(s) > 0:  
                    cd[s[0]] = opening[0]  

    if len(cd) != 0:
        return True, cd
    else:
        return False, None



def graj_niegraj(opening_book_w, opening_book_b, board_state, player):
    if player == "w":
        books_to_search = [opening_book_w, opening_book_b]
    else:
        books_to_search = [opening_book_b, opening_book_w]

    for book_index, book in enumerate(books_to_search):
        accepted, target_move = accept(book, board_state)
        if accepted:
            if book_index == 0:  
                return 1, target_move.keys()
            else:
                return 0, target_move.keys()  
    return None  
            



        

opening_book_w = load_link_list_from_json("book_w.json")
opening_book_b = load_link_list_from_json("book_b.json")

board_state1 = "wB1... bG1wB1- wQ1/wB1"
board_state2 = "wG1... bG1-wG1"

print(graj_niegraj(opening_book_w, opening_book_b, board_state1, "b"))
print(graj_niegraj(opening_book_w, opening_book_b, board_state2, "w"))
