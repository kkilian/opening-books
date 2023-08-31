import numpy as np

class Board(object):
    """
    Class representing a game board.
    """
    def __init__(self):
        self.board = [[[]]]
        self.ref0x = 0
        self.ref0y = 0

    def _add_row(self, before=False):
        newRow = []
        rowSize = len(self.board[0])
        for i in range(rowSize):
            newRow.append([])
        if not before:
            self.board.append(newRow)
        else:
            self.ref0y += 1
            self.board.insert(0, newRow)

    def _add_column(self, before=False):
        if before:
            self.ref0x += 1
        for row in self.board:
            if not before:
                row.append([])
            else:
                row.insert(0, [])

    def resize(self, position):

        (x, y) = position
        xx = self.ref0x + x
        yy = self.ref0y + y

        while xx < 0:
            self._add_column(before=True)
            xx += 1
        while xx >= len(self.board[0]):
            self._add_column()
        while yy < 0:
            self._add_row(before=True)
            yy += 1
        while yy >= len(self.board):
            self._add_row()
        return (xx, yy)
    
    def get_boundaries(self):
        firstCol = -self.ref0x
        firstRow = -self.ref0y
        lastCol = len(self.board[0]) + firstCol - 1
        lastRow = len(self.board) + firstRow - 1
        return firstCol, firstRow, lastCol, lastRow
    
    def get_surrounding(self, position):
        (x, y) = position
        return [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]
    
    def get_w_xy(self, position):
        (x, y) = position
        return (x-1, y)


    def get_e_xy(self, position):

        (x, y) = position
        return (x+1, y)

class HexBoard(Board):
    """
    Class representing a hexagonal game board, inheriting from the Board class.
    """

    HX_O = 0   # same/on-top(żuki -,-)
    HX_W = 1   # W
    HX_NW = 2  # NW
    HX_NE = 3  # NE
    HX_E = 4   # E
    HX_SE = 5  # SE
    HX_SW = 6  # SW
    
    def __init__(self):
        super(HexBoard, self).__init__()
        self.dir2func = {
            0: lambda x: x,
            1: self.get_w_xy,
            2: self.get_nw_xy,
            3: self.get_ne_xy,
            4: self.get_e_xy,
            5: self.get_se_xy,
            6: self.get_sw_xy
        }
    def get_surrounding(self, position):

        res = super(HexBoard, self).get_surrounding(position)
        (x, y) = position
        p = y % 2
        if p == 0:
            res.insert(1, (x-1, y-1))
            res.insert(5, (x-1, y+1))
        else:
            res.insert(2, (x+1, y-1))
            res.insert(4, (x+1, y+1))
        return res


    def get_dir_cell(self, cell, direction):
            return self.dir2func[direction](cell)


    def get_nw_xy(self, position):
      
        (x, y) = position
        p = y % 2
        nx = x - 1 + p
        ny = y - 1
        return (nx, ny)


    def get_ne_xy(self, position):
       
        (x, y) = position
        p = y % 2
        nx = x + p
        ny = y - 1
        return (nx, ny)


    def get_sw_xy(self, position):
        
        (x, y) = position
        p = y % 2
        nx = x - 1 + p
        ny = y + 1
        return (nx, ny)


    def get_se_xy(self, position):
        
        (x, y) = position
        p = y % 2
        nx = x + p
        ny = y + 1
        return (nx, ny)


    def get_w_xy(self, position):
        
        (x, y) = position
        return (x-1, y)


    def get_e_xy(self, position):
        
        (x, y) = position
        return (x+1, y)


    def get_line_dir(self, cell0, cell1):
        
        (sx, sy) = cell0
        (ex, ey) = cell1
        dx = ex - sx
        dy = ey - sy
        p = sy % 2  

        if dx == dy == 0:
            return self.HX_O

        moveDir = None
        if dy == 0:
            if dx < 0:
                moveDir = self.HX_W
            else:
                moveDir = self.HX_E

        else:

            nx = int((abs(dy) + (1 - p)) / 2)
            if abs(dx) != abs(nx):
                return None

            if dx < 0:
                if dy < 0:
                    moveDir = self.HX_NW
                else:
                    moveDir = self.HX_SW
            else:
                if dy < 0:
                    moveDir = self.HX_NE
                else:
                    moveDir = self.HX_SE

        return moveDir

    
class HivePiece(object):
    """
    Class representing a piece in the game.
    """

    def __init__(self, color, kind, number):
        self.color = color     
        self.kind = kind        
        self.number = number    


    def __repr__(self):
        return "%s%s%s" % (self.color, self.kind, self.number)

class HiveException(Exception):
    pass

class Hive(object):


    # Directions
    O = HexBoard.HX_O    # origin/on-top
    W = HexBoard.HX_W    # west
    NW = HexBoard.HX_NW  # north-west
    NE = HexBoard.HX_NE  # north-east
    E = HexBoard.HX_E    # east
    SE = HexBoard.HX_SE  # south-east
    SW = HexBoard.HX_SW  # south-west

    def __init__(self):
        self.turn = 0
        self.activePlayer = 0
        self.players = ['w', 'b']
        self.board = HexBoard()
        self.playedPieces = {}
        self.piecesInCell = {}
        self.unplayedPieces = {}

    def setup(self):

        self.unplayedPieces['w'] = self._piece_set('w')
        self.unplayedPieces['b'] = self._piece_set('b')
        self.turn = 1


    def action(self, actionType, action):

        if (actionType == 'play'):
            if (isinstance(action, tuple)):
                (actPiece, refPiece, direction) = action
            else:
                (actPiece, refPiece, direction) = (action, None, None)

            player = self.get_active_player()
            piece = self.unplayedPieces[player].get(actPiece, None)
            if piece is not None:
                self.place_piece(piece, refPiece, direction)

                del self.unplayedPieces[player][actPiece]
            else:
                ppiece = self.playedPieces.get(actPiece, None)
                if ppiece is None:
                    return False
                else:
                    self.move_piece(ppiece['piece'], refPiece, direction)

        elif (actionType == 'non_play' and action == 'pass'):
            pass

        self.turn += 1
        self.activePlayer ^= 1 
        return True

    def get_unplayed_pieces(self, player):
        return self.unplayedPieces[player]


    def get_active_player(self):
        if self.turn <= 0:
            return None

        return self.players[self.activePlayer]

    def get_board_boundaries(self):
        return self.board.get_boundaries()


    def get_pieces(self, cell):
        return self.piecesInCell.get(cell, [])


    def locate(self, pieceName):

        pp = self.playedPieces.get(pieceName)
        if pp is not None:
            res = pp['cell']

        return res


    def move_piece(self, piece, refPiece, refDirection):

        pieceName = str(piece)
        targetCell = self._poc2cell(refPiece, refDirection)

        pp = self.playedPieces[pieceName]
        startingCell = pp['cell']

        self.piecesInCell[startingCell].remove(pieceName)

        self.board.resize(targetCell)
        pp['cell'] = targetCell
        pic = self.piecesInCell.setdefault(targetCell, [])
        pic.append(str(piece))

        return targetCell


    def place_piece(self, piece, refPieceName=None, refDirection=None):

        if refPieceName is None and self.turn == 1:
            targetCell = (0, 0)
        else:
            targetCell = self._poc2cell(refPieceName, refDirection)


        self.board.resize(targetCell)
        self.playedPieces[str(piece)] = {'piece': piece, 'cell': targetCell}
        pic = self.piecesInCell.setdefault(targetCell, [])
        pic.append(str(piece))

        return targetCell



    def _occupied_surroundings(self, cell):

        surroundings = self.board.get_surrounding(cell)
        return [c for c in surroundings if not self._is_cell_free(c)]


    def _poc2cell(self, refPiece, pointOfContact):

        refCell = self.locate(refPiece)
        return self.board.get_dir_cell(refCell, pointOfContact)



    def _piece_set(self, color):

        pieceSet = {}
        for i in range(3):
            ant = HivePiece(color, 'A', i+1)
            pieceSet[str(ant)] = ant
            grasshopper = HivePiece(color, 'G', i+1)
            pieceSet[str(grasshopper)] = grasshopper
        for i in range(2):
            spider = HivePiece(color, 'S', i+1)
            pieceSet[str(spider)] = spider
            beetle = HivePiece(color, 'B', i+1)
            pieceSet[str(beetle)] = beetle
        queen = HivePiece(color, 'Q', 1)
        pieceSet[str(queen)] = queen
        return pieceSet
    
    def encode_piece_set(self, piece_set):
        piece_names = list(piece_set.keys())

        num_pieces = len(piece_names)
        encoding_array = np.zeros((num_pieces,), dtype=np.int)

        for i, piece_name in enumerate(piece_names):
            piece = piece_set[piece_name]
            color = piece.color
            kind = piece.kind
            number = piece.number

            if color == 'w':
                encoding_array[i * 11] = 1
            elif color == 'b':
                encoding_array[i * 11 + 1] = 1

            if kind == 'A':
                encoding_array[i * 11 + 2] = 1
            elif kind == 'G':
                encoding_array[i * 11 + 3] = 1
            elif kind == 'S':
                encoding_array[i * 11 + 4] = 1
            elif kind == 'B':
                encoding_array[i * 11 + 5] = 1
            elif kind == 'Q':
                encoding_array[i * 11 + 6] = 1

            if number == 1:
                encoding_array[i * 11 + 7] = 1
            elif number == 2:
                encoding_array[i * 11 + 8] = 1
            elif number == 3:
                encoding_array[i * 11 + 9] = 1

        encoding_dict = dict(zip(piece_names, encoding_array))

        return encoding_dict


class HiveView(object):
    def __init__(self, game):
        self.game = game

    def __repr__(self):
        firstCol, firstRow, lastCol, lastRow = self.game.get_board_boundaries()
        res = "\n"
        for i in range(firstRow, lastRow + 1):
            p = i % 2
            if i > firstRow:
                res += " \\" * p
            else:
                res += "  " * p
            for j in range(firstCol, lastCol + 1):
                res += " / \\"
            if i > firstRow and p == 0:
                res += " /"
            res += "\n"
            res += "  " * p
            for j in range(firstCol, lastCol + 1):
                pieces = self.game.get_pieces((j, i))
                if len(pieces) != 0:
                    pieceName = str(pieces[-1])[:3]
                else:
                    pieceName = "   "

                res += "|" + pieceName
            res += "|\n"
        p = (lastRow) % 2
        res += "  " * p
        for j in range(firstCol, lastCol + 1):
            res += " \\ /"
        res += "\n"

        return res


class GameStatus(object):
    def __init__(self, game):
        self.game = game
        self.view = HiveView(game)

    def __repr__(self, moves, data):
        self.moves = len(data)
        view_str = ""
        for i in range(1, moves + 1):
            if i == 1:
                self.game.action('play', (data[i][0]))
            else:
                if isinstance(data[i][1], str):
                    self.game.action('play', (data[i][0], data[i][1], data[i][2]))
                elif isinstance(data[i][2], str):
                    self.game.action('play', (data[i][0], data[i][2], data[i][1]))

        view_str += f"Move {moves}:\n"
        last_move_piece_name = str(data[moves][0])
        formatted_last_move_piece_name = f"\033[1;4m{last_move_piece_name}\033[0m"
        view_str += str(self.view).replace(last_move_piece_name, formatted_last_move_piece_name) + "\n"

        return view_str



