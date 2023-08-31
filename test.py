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

    return data['links']

def accept(opening_book, board_state):
    opening = board_state.split(' ')
    accepted = []
    for link in opening_book:
        L = link['source'].split(' ')
        R = link['target'].split(' ')


        for i in range(1, len(opening) + 1):
            p = opening[:i]
            s = opening[i:]
            print(L, p)
            if p == L and s == R:  
                accepted.append(R)

            if len(accepted) != 0:    
                return True, accepted

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
                print("Move accepted in the first opening book. Winning moves:", target_move)
                return target_move
            else:
                print("Move accepted in the second opening book. Loosing moves:", target_move)
                return target_move  # Remove this line if you don't want to return on second book match
    return None  # Move was not accepted in any of the opening books
            



        

opening_book_w = load_link_list_from_json("book_w.json")
opening_book_b = load_link_list_from_json("book_b.json")

board_state = "wG1... bG1wG1- wA1-wG1"

print(graj_niegraj(opening_book_w, opening_book_b, board_state, "w"))


transformed_dict = {}

for link in opening_book_w:
    source = link['source']
    target = link['target']
    
    # Skip empty target values
    if target:
        transformed_dict[source] = target

# Print the transformed dictionary
print(json.dumps(transformed_dict, indent=4))