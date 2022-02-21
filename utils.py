# module containing utility functions


def get_legal_houses(player, board):
    legal_houses = [h_index for h_index, house in enumerate(board[player][:-1]) if house > 0]
    return legal_houses


def get_nr_of_houses(board):
    return len(board[0]) - 1


def get_total_nr_of_pits(board):
    return len(board[0]) + len(board[1])


def change_player(player):
    return (player+1) % 2


def capture_seeds(player, board, end_house, end_side):
    # 4 conditions have to be satisfied to capture seeds:
    # the last seeds lands in a previously empty pit, that is on the player's side of the board,
    # and that is not the store, while the opposite pit is not empty
    nr_of_houses = get_nr_of_houses(board)
    if player == end_side and board[player][end_house] == 1 and end_house < nr_of_houses:
        opposite_house = nr_of_houses - 1 - end_house
        opponent = change_player(player)
        if board[opponent][opposite_house] > 0:
            board[player][nr_of_houses] += board[opponent][opposite_house] + 1
            board[player][end_house] = 0
            board[opponent][opposite_house] = 0
    return board


def determine_player(end_pit, nr_of_houses, player):
    if end_pit == nr_of_houses:
        new_player = player
    else:
        new_player = change_player(player)
    return new_player


def is_game_over(board, is_move_finished=True):
    # is_move_finished is only given in the GUI variant, otherwise it is set to true
    if is_move_finished and min(sum(board[0][:-1]), sum(board[1][:-1])) == 0:
        return True
    else:
        return False


def end_the_game(board):
    nr_of_houses = get_nr_of_houses(board)
    board = [[0]*nr_of_houses + [sum(board[0])], [0]*nr_of_houses + [sum(board[1])]]
    return board


def remove_seeds(board, side, house):
    active_seeds = board[side][house]
    board[side][house] = 0
    return board, active_seeds


def add_seed(board, side, house):
    board[side][house] += 1
    return board


def get_next_house(player, side, house, nr_of_houses):
    # return the side and house that the next seed will fall into
    if side == player:
        if house == nr_of_houses:
            side = change_player(side)
            house = 0
        else:
            house += 1
    else:
        if house + 1 == nr_of_houses:
            side = change_player(side)
            house = 0
        else:
            house += 1
    return side, house


def compute_state_stepwise(player, board, side, house, active_seeds, has_move_started):
    """
    compute the new state stepwise (i.e. one seed at a time). This is used for the GUI
    :param player: boolean indicating which player's turn it is
    :param board: list of lists indicating the current board
    :param side: boolean indicating the side that the currently focused on house is located on
    :param house: integer indicating the currently focused on house
    :param active_seeds: integer indicating the number of seeds that have yet to be distributed
    :param has_move_started: boolean indicating whether the seeds from the selected house have been picked up yet
    :return:
        list of lists indicating the new board
        boolean indicating the side that the subsequently focused on house is located on
        integer indicating the subsequently focused on house
        integer indicating the number of seeds that will yet have to be distributed
        boolean indicating whether the seeds from the selected house have been picked up yet
        boolean indicating whether the full move has been finished yet
    """
    is_move_finished = False
    nr_of_houses = get_nr_of_houses(board)
    if not has_move_started:
        board, active_seeds = remove_seeds(board, side, house)
        has_move_started = True
    elif active_seeds == 0:
        board = capture_seeds(player, board, house, side)
        player = determine_player(house, nr_of_houses, player)
        is_move_finished = True
    else:
        board = add_seed(board, side, house)
        active_seeds -= 1
    if active_seeds > 0:
        side, house = get_next_house(player, side, house, nr_of_houses)
    return board, side, house, player, active_seeds, has_move_started, is_move_finished


def compute_state(player, old_board, house):
    """
    compute the new state directly. This is used for the Monte Carlo Tree Search
    :param player: boolean indicating which player's turn it is
    :param old_board: list of lists indicating the current board
    :param house: integer indicating the selected house
    :return: boolean indicating which player's turn it will be next, list of lists indicating the new board
    """
    board = [old_board[0].copy(), old_board[1].copy()]
    nr_of_houses = get_nr_of_houses(board)
    total_nr_of_pits = get_total_nr_of_pits(board)
    opponent = change_player(player)
    active_seeds = board[player][house]
    board[player][house] = 0
    end_pit = (house + active_seeds) % (total_nr_of_pits-1)
    # this is relative to the current player (i.e. 0 corresponds to the current player's first house)
    if end_pit % total_nr_of_pits <= nr_of_houses:
        end_side = player
    else:
        end_side = opponent
    new_player = determine_player(end_pit, nr_of_houses, player)
    # determine how many "rounds" the seeds do ->
    # "rounds" many seeds are added to each pit (except the opponent's store)
    rounds = active_seeds // total_nr_of_pits
    board[player] = [s+rounds for s in board[player]]
    board[opponent][:-1] = [s + rounds for s in board[opponent][:-1]]
    if end_side == player:
        if end_pit > house:
            board[player][house+1: end_pit+1] = [board[player][i] + 1 for i in range(house+1, end_pit+1)]
        else:
            board[player] = [s + 1 if i <= end_pit or i > house else s for i, s in enumerate(board[player])]
            board[opponent][:-1] = [s + 1 for s in board[opponent][:-1]]
    else:
        board[player][house + 1:nr_of_houses+1] = [s + 1 for s in board[player][house + 1:nr_of_houses+1]]
        board[opponent][:end_pit - nr_of_houses] = [s + 1 for s in board[opponent][:end_pit - nr_of_houses]]
    end_house = end_pit % (nr_of_houses+1)
    board = capture_seeds(player, board, end_house, end_side)
    return new_player, board


# just for easier debugging
def print_board(board):
    nr_of_houses = get_nr_of_houses(board)
    opposite_side_reversed = board[1][0:nr_of_houses]
    opposite_side_reversed.reverse()
    middle_spaces = (3*nr_of_houses-4)*" "
    print(" ", opposite_side_reversed)
    print(board[1][nr_of_houses:nr_of_houses+1], middle_spaces, board[0][nr_of_houses:nr_of_houses+1])
    print(" ", board[0][0:nr_of_houses])

