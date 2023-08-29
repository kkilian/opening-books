import json

class OpeningBook:
    def __init__(self, book_w_filename, book_b_filename):
        self.opening_book_w = self.load_link_list_from_json(book_w_filename)
        self.opening_book_b = self.load_link_list_from_json(book_b_filename)

    @staticmethod
    def load_link_list_from_json(json_filename):
        with open(json_filename) as json_file:
            data = json.load(json_file)
        return data['links']

    @staticmethod
    def accept(opening_book, board_state, move):
        board_state = board_state.split()
        opening = board_state + [move]
        for link in opening_book:
            L = link['source']
            R = link['target']
            for i in range(1, len(opening) + 1):
                p = ''.join(opening[:i])
                s = ''.join(opening[i:])
                if p == L and s == R:
                    return True

    def graj_niegraj(self, board_state):
        for link in self.opening_book_w:
            if link['source'] == board_state:
                print(link['target'])
        
        for link in self.opening_book_b:
            if link['source'] == board_state:
                print(link['target'])

if __name__ == "__main__":
    opening_book = OpeningBook("book_w.json", "book_b.json")
    board_state = "wS1..."
    opening_book.graj_niegraj(board_state)
