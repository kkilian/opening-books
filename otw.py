import json
def load_link_list_from_json(json_filename):
    with open(json_filename) as json_file:
        data = json.load(json_file)
    
    return data['links']
    

def akc(opening_book, board_state, move):
    board_state = board_state.split()
    openinig = board_state + [move]
    for link in opening_book:
        L = link['source']
        R = link['target']
        for i in range(1, len(openinig) + 1):
            p = ''.join(openinig[:i])
            s = ''.join(openinig[i:])
            if p == L and s == R:
                return True
opening_book = load_link_list_from_json("sfre.json")
board_state = "wG1"
print(akc(opening_book, board_state, "bQ1"))