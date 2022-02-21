# module for the implementation of the Monte Carlo Tree Search

from time import time
import random
from utils import *
from math import log, sqrt, inf
import networkx as nx
import numpy as np


def ucb1(attributes, nr_of_parent_visits, parent_player, player0, constant=sqrt(2)):
    """
    compute the ucb1 value of a node. The formula balances exploration and exploitation, i.e., nodes that
        haven't been visited a lot or have provided good results yield high ucb1 values
    :param attributes: list containing attributes the node
    :param nr_of_parent_visits: integer indicating the number of times the parent node has been visited
    :param parent_player: boolean indicating which player's turn it currently it was in the parent node
    :param player0: boolean indicating from which player's point of view the node values should be interpreted
    :param constant: float indicating the "exploration parameter"
    :return: float indicating the ucb1 value of the node
    """
    nr_of_visits = attributes['nr of visits']
    total_wins = attributes['total wins']
    if nr_of_visits == 0:
        return inf
    else:
        # the value is from the point of view of the original player. So if it is the opponent's turn, he will
        # prefer to enter states that have low values
        if parent_player == player0:
            return total_wins/nr_of_visits + constant * sqrt(log(nr_of_parent_visits)/nr_of_visits)
        else:
            return 1-total_wins/nr_of_visits + constant * sqrt(log(nr_of_parent_visits)/nr_of_visits)


def get_value(player0, board):
    """
    compute the victory value and the score difference of a terminal state
    :param player0: boolean indicating from which player's point of view the result should be interpreted
    :param board: list of lists indicating the final board
    :return: a float indicating if the game resulted in a win (1), loss (0) or a tie (0.5); an integer indicating the
        final score differential (own points - opponent's points) of the game
    """
    opponent = change_player(player0)
    player0_score = sum(board[player0])
    opponent_score = sum(board[opponent])
    if player0_score > opponent_score:
        return 1, player0_score - opponent_score
    elif player0_score < opponent_score:
        return 0, player0_score - opponent_score
    else:
        return 0.5, player0_score - opponent_score


def get_best_house(G, node_attributes):
    """
    determine the house that hos the the highest projected win percentage.
    In case of ties the house that provided the best score differential is returned.
    This is done by adding the score differentials multiplied with a small factor  to the win percentages;
    the factor is chosen sufficiently small such the score differentials only start to matter when 2 houses have equal
    win percentages
    :param G: networkx graph of the game tree
    :param node_attributes: dictionary containing relevant information for each discovered node of the the game tree
    :return: integer indicating the house that maximizes the projected win probability
    """
    parent_attributes = node_attributes[0]
    total_nr_of_seeds = sum(parent_attributes['board'][0]) + sum(parent_attributes['board'][1])
    factor = 1 / (parent_attributes['nr of visits'] ** 2 * total_nr_of_seeds)
    best_node_index = np.argmax([(node_attributes[node]['total wins'] +
                                  factor * node_attributes[node]['total score differential']) /
                                 node_attributes[node]['nr of visits']
                                 for node in G.adj[0]])
    return node_attributes[list(G.adj[0])[best_node_index]]['selected house']


def traverse(G, node_attributes, player0):
    """
    traverse the discovered part of the game tree by always choosing the child node that maximizes the ucb1
    :param G: networkx graph of the discovered portion of the game tree
    :param node_attributes: dictionary containing relevant information for each discovered node of the the game tree
    :param player0: boolean indicating from which player's point of view the node values should be interpreted
    :return: updated networkx graph of the discovered portion of the game tree;
        integer indicating the subsequently considered node;
        updated dictionary containing relevant information for each discovered node of the the game tree
        updated list containing the traversed nodes
    """
    current_node = 0
    traversed_nodes = [0]
    child_nodes = G.adj[current_node]
    while child_nodes:
        nr_of_parent_visits = node_attributes[current_node]['nr of visits']
        parent_player = node_attributes[current_node]['player']
        current_node = list(child_nodes)[np.argmax([ucb1(node_attributes[node], nr_of_parent_visits, parent_player,
                                                         player0)
                                                    for node in child_nodes])]
        traversed_nodes.append(current_node)
        child_nodes = G.adj[current_node]
    return G, current_node, node_attributes, traversed_nodes


def expand(G, current_node, node_attributes, traversed_nodes, node_counter):
    """
    expand the current node and traverse a child node. If possible the traversed node is a node that implies an extra
    move for the current player. In that case, this node is expanded and one of its child nodes is traversed as well.
    This process is continued until it is the opponent's turn again.
    :param G: networkx graph of the discovered portion of the game tree
    :param current_node: integer indicating the currently considered node
    :param node_attributes: dictionary containing relevant information for each discovered node of the the game tree
    :param traversed_nodes: list containing the traversed nodes
    :param node_counter: integer indicating the number of nodes in the tree below the root
    :return: updated networkx graph of the discovered portion of the game tree;
        integer indicating the subsequently considered node;
        updated dictionary containing relevant information for each discovered node of the the game tree
        updated list containing the traversed nodes
        integer indicating the updated number of nodes in the tree below the root
    """
    is_expanding_stopped = False
    while not is_expanding_stopped:
        is_expanding_stopped = True
        current_node_attributes = node_attributes[current_node]
        parent_node = current_node
        player = current_node_attributes['player']
        board = current_node_attributes['board']
        legal_houses = get_legal_houses(player, board)
        for i in range(len(legal_houses)):
            house = legal_houses[-1-i]
            new_player, new_board = compute_state(player, board, house)
            G.add_edge(parent_node, node_counter)
            node_attributes[node_counter] = \
                {'nr of visits': 0, 'total wins': 0, 'total score differential': 0, 'board': new_board,
                 'selected house': house, 'player': new_player, 'game over': is_game_over(new_board)}
            if new_player == player:
                current_node = node_counter
                traversed_nodes.append(current_node)
                is_expanding_stopped = False
                node_counter += 1
                break
            node_counter += 1
        if is_expanding_stopped:
            current_node = node_counter - 1
            traversed_nodes.append(current_node)

    return G, current_node, node_attributes, traversed_nodes, node_counter


def rollout(player, board, player0):
    """
    simulate the game to the end
    :param player: boolean indicating which player's turn it currently is
    :param board: list of lists indicating the current board
    :param player0: boolean indicating from which player's point of view the result should be interpreted
    :return: a float indicating if the game resulted in a win (1), loss (0) or a tie (0.5); an integer indicating the
        final score differential (own points - opponent's points) of the game
    """
    while not is_game_over(board):
        legal_houses = get_legal_houses(player, board)
        house = random.choice(legal_houses)
        player, board = compute_state(player, board, house)
    return get_value(player0, board)


def backpropagate(node_attributes, traversed_nodes, win, score_differential):
    """
    update the total number of wins, the total score differential and the number of visits of the traversed nodes
    :param node_attributes: dictionary containing relevant information for each discovered node of the the game tree
    :param traversed_nodes: list containing the traversed nodes
    :param win: float indicating if the game resulted in a win (1), loss (0) or a tie (0.5)
    :param score_differential: integer indicating the score differential (own points - opponent's points) of the game
    :return: an updated dictionary containing relevant information for each discovered node of the the game tree
    """
    for node in traversed_nodes:
        node_attributes[node]['total wins'] += win
        node_attributes[node]['total score differential'] += score_differential
        node_attributes[node]['nr of visits'] += 1
    return node_attributes


def get_ai_house(player0, board0, time_limit):
    """
    compute the AI's choice given the current board by doing Monte Carlo Tree Search
    :param player0: binary variable indicating which side of the board the AI plays on
    :param board0: list of lists indicating the current board
    :param time_limit: float indicating time limit for the AI in seconds
    :return: integer indicating the house selected by the AI
    """
    # initialize
    start = time()
    G = nx.DiGraph()
    G.add_node(0)
    node_counter = 1
    node_attributes = {0: {'nr of visits': 0, 'total wins': 0, 'total score differential': 0, 'board': board0,
                           'selected house': None, 'player': player0, 'game over': False}}

    while time() - start < time_limit:
        # traverse
        G, current_node, node_attributes, traversed_nodes = traverse(G, node_attributes, player0)
        current_node_attributes = node_attributes[current_node]

        if current_node_attributes['nr of visits'] > 0 and not current_node_attributes['game over']:
            # expand
            G, current_node, node_attributes, traversed_nodes, node_counter = \
                expand(G, current_node, node_attributes, traversed_nodes, node_counter)

        # rollout
        player = current_node_attributes['player']
        board = current_node_attributes['board']
        win, score_differential = rollout(player, board, player0)

        # back propagate
        node_attributes = backpropagate(node_attributes, traversed_nodes, win, score_differential)

    return get_best_house(G, node_attributes)
