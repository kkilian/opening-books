import sys
import networkx as nx
from networkx.readwrite import json_graph
import random
from parse import parse
from pipetools import pipe
import datetime
import json

class BookGenerator:
    def __init__(self):
        self.random_seed = None
        self.filename = None
        self.sfre_graph = None

    @staticmethod
    def read_words(lines):
        X = set()
        Y = set()
        for line in lines:
            r = parse("{flag} {length} {word}", line)
            word = r['word']
            if r['flag'] == '1':
                if 'Q' in word:
                    word = word.replace('Q', 'Q1')
                    word = word.replace('.', '...')
                    X.add(word)
            else:
                if 'Q' in word:
                    word = word.replace('Q', 'Q1')
                    word = word.replace('.', '...')
                Y.add(word)
        if not X.isdisjoint(Y):
            sys.exit()
        return (Y, X)

    @staticmethod
    def concatenation(U, Y):
        X = set()
        for u in U:
            for y in Y:
                X.add(u + y)
        return X

    @staticmethod
    def split_from_clique(k):
        L = set()
        R = set()
        for (a, b) in k:
            L.add(a)
            R.add(b)
        return (L, R)

    def sfre_from_cliques(self, cliques):
        result = []
        for i, k in enumerate(cliques):
            (L, R) = self.split_from_clique(k)  
            result.append((L, R))
        return result

    @staticmethod
    def build_graph(S):
        Sm, Sp = S[0], S[1]
        V = []
        G = nx.Graph()
        for x in Sp:
            x = x.split()
            for i in range(1, len(x) + 1):
                move_sequence = ' '.join(x[:i])
                remaining_moves = ' '.join(x[i:])
                V.append((move_sequence, remaining_moves))
                G.add_node((move_sequence, remaining_moves))
        for i in range(len(V) - 1):
            for j in range(i + 1, len(V)):
                w1 = V[i][0] + V[j][1]
                w2 = V[j][0] + V[i][1]
                if (w1 not in Sm) and (w2 not in Sm):
                    G.add_edge(V[i], V[j])
        return G

    @staticmethod
    def N(G, S):
        T = set(G.nodes())
        for s in S:
            s > pipe | G.neighbors | set | T.intersection_update
        return T - S

    def find_cliques(self, G):
        V = set(G.nodes())
        C = set()
        while C != V:
            v = random.choice(list(V - C))
            S = {v}
            while True:
                U = self.N(G, S)  
                if U:
                    v = random.choice(list(U))
                    S.add(v)
                else:
                    C.update(S)
                    yield S
                    break

    @staticmethod
    def accepts(e, x):
        for (p, s) in ((x[:i], x[i:]) for i in range(1, len(x))):
            for (L, R) in e:
                if p in L and s in R:
                    return True
        return False


    def make_book(self, player):
        if player not in ['w', 'b']:
            print("Invalid player color. Use 'w' for white or 'b' for black.")
            return
        
        self.random_seed = random.seed()
        self.filename = f"hive_{player}.txt"
        
        sfre = self.read_words(open(self.filename, "r").readlines()) > (pipe
            | self.build_graph
            | self.find_cliques
            | self.sfre_from_cliques)

        self.sfre_graph = nx.Graph()
        for (L, R) in sfre:
            self.sfre_graph.add_nodes_from(L)
            self.sfre_graph.add_nodes_from(R)
            for u in L:
                for v in R:
                    self.sfre_graph.add_edge(u, v)
        book_name = f"book_{player}.json"
        with open(book_name, 'w') as file:
            source_target = {}
            sfre_graph_data = json_graph.node_link_data(self.sfre_graph)
            for n, link in enumerate( sfre_graph_data['nodes']):
                source_target[link['id']] = n
            json.dump(source_target, file)


