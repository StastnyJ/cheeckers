from enum import Enum
from AI_base import *


class StoneTypes(Enum):
    Basic = 0
    Queen = 1


class PlayerType(Enum):
    Player = 0
    AI = 1


class MovementDirection(Enum):
    Up = 0
    Down = 1


class Game:
    def __init__(self, player0_type, player1_type, player0_AI = None, player1_AI = None):
        self.player0 = Player(0, player0_type, player0_AI)
        self.player1 = Player(1, player1_type, player1_AI)
        self.playground = [[None] * 8 for _ in range(8)]
        self.player_on_move = self.player0
        self.selected_stone = None
        self.possible_moves = None
        self.force_move = False
        self.highlighted_move = []
        self.highlighted_removed = []
        self.is_AI_simulation = player0_type == PlayerType.AI and player1_type == PlayerType.AI

        for _, stone in self.player0.stones.items():
            col, row = stone.position
            self.playground[col][row] = stone
        for _, stone in self.player1.stones.items():
            col, row = stone.position
            self.playground[col][row] = stone
        
        if self.is_AI_simulation:
            self._play_automatic_turn()

    def click_event(self, position):
        if self.is_AI_simulation:
            self._play_automatic_turn()
            return
        col, row = position
        if self._is_click_on_my_stone(position) and not self.force_move:
            self._select_stone(self.playground[col][row])
        else:
            if self._is_move_click(position):
                move = self._get_move_object(position)
                became_queen = self._move_stone(move)
                if move.removed_stone is not None and not became_queen and self._can_jump(move.end):
                    self._select_stone(self.playground[move.end[0]][move.end[1]])
                    self.force_move = True
                else:
                    return self._end_turn()
            elif not self.force_move:
                self._remove_selected_stone()
        return False

    def _can_jump(self, pos):
        moves = self._possible_moves(pos) if self.playground[pos[0]][pos[1]].type == StoneTypes.Basic else self._queen_possible_moves(pos)
        for m in moves:
            if m.is_jump():
                return True
        return False

    def _move_stone(self, move):
        self.playground[self.selected_stone.position[0]][self.selected_stone.position[1]] = None
        self.selected_stone.position = move.end
        self.playground[self.selected_stone.position[0]][self.selected_stone.position[1]] = self.selected_stone
        if move.is_jump():
            self._remove_stone(move.removed_stone)
        if self.selected_stone.position[1] in [0, 7]:
            self.selected_stone.type = StoneTypes.Queen
            return True
        return False

    def _remove_stone(self, stone):
        self.playground[stone.position[0]][stone.position[1]] = None
        del stone.owner.stones[stone.id]

    def _end_turn(self):
        self._remove_selected_stone()
        self.force_move = False
        if self.player_on_move.id == 0:
            self.player_on_move = self.player1
        else:
            self.player_on_move = self.player0
        if len(self._get_all_possible_moves()) <= 0:
            return True
        if self.player_on_move.type == PlayerType.AI and not self.is_AI_simulation:
            return self._play_automatic_turn()
        return False

    def _play_automatic_turn(self):
        rotate = self.player_on_move.direction == MovementDirection.Up
        move = self.player_on_move.AI.make_move(self.playground, self.player_on_move.id, rotate)
        moving_stone = self.playground[move.start[0]][move.start[1]]
        self.playground[move.start[0]][move.start[1]] = None
        moving_stone.position = move.end
        self.playground[move.end[0]][move.end[1]] = moving_stone
        self.highlighted_move = [move.start, move.end]
        self.highlighted_removed = move.removed
        if moving_stone.position[1] in [0, 7]:
            moving_stone.type = StoneTypes.Queen
        for pos in move.removed:
            self._remove_stone(self.playground[pos[0]][pos[1]])
        return self._end_turn()
        
    def _is_click_on_my_stone(self, position):
        col, row = position
        stone = self.playground[col][row]
        if stone is None or stone.owner.id != self.player_on_move.id:
            return False
        return True

    def _remove_selected_stone(self):
        self.selected_stone = None
        self.possible_moves = None

    def _select_stone(self, stone):
        self.selected_stone = stone
        self.possible_moves = self._get_possible_moves()

    def _get_possible_moves(self):
        moves = []
        if self.selected_stone.type == StoneTypes.Queen:
            moves = self._queen_possible_moves(self.selected_stone.position)
        else:
            moves = self._possible_moves(self.selected_stone.position)
        moves = self._filter_possible_moves(moves)
        return moves

    def _possible_moves(self, start):
        result = []
        new_row = start[1]
        new_row += 1 if self.player_on_move.direction == MovementDirection.Down else -1
        if new_row < 0 or new_row > 7:
            return []
        adepts = [(start[0] - 1, new_row), (start[0] + 1, new_row)]
        for col, row in adepts:
            if col < 0 or col > 7:
                continue
            if self.playground[col][row] is None:
                result.append(Move((col, row), None))
            elif self.playground[col][row].owner.id == self.player_on_move.id:
                continue
            else:
                moves = self._create_jump_moves((col, row), start)
                for m in moves:
                    result.append(m)
        return result

    def _queen_possible_moves(self, start):
        result = []
        for a in [-1, 1]:
            for b in [-1, 1]:
                pos = start
                stone = None
                while True:
                    new_col = pos[0] + a
                    new_row = pos[1] + b
                    pos = (new_col, new_row)
                    if new_col < 0 or new_row < 0 or new_col > 7 or new_row > 7:
                        break
                    if self.playground[new_col][new_row] is None:
                        result.append(Move((new_col, new_row), stone))
                        continue
                    if self.playground[new_col][new_row].owner.id == self.player_on_move.id:
                        break
                    if stone is None:
                        stone = self.playground[new_col][new_row]
                    else:
                        break
        return result               

    def _create_jump_moves(self, target, start):
        col, row = target
        new_col = 2 * col - start[0]
        new_row = 2 * row - start[1]
        if new_col < 0 or new_col > 7:
            return []
        if new_row < 0 or new_row > 7:
            return []
        result = []
        if self.playground[new_col][new_row] is None:
            result.append(Move((new_col, new_row), self.playground[col][row]))
        return result

    def _is_move_click(self, position):
        if self.possible_moves is None:
            return False
        for move in self.possible_moves:
            if position == move.end:
                return True
        return False

    def _get_move_object(self, position):
        for move in self.possible_moves:
            if position == move.end:
                return move
        return None

    def _can_someone_jump(self):
        moves = self._get_all_possible_moves()
        for m in moves:
            if m.is_jump():
                return True
        return False

    def _can_queen_jump(self):
        moves = self._get_all_queens_possible_moves()
        for m in moves:
            if m.is_jump():
                return True
        return False

    def _get_all_possible_moves(self):
        result = []
        for _, stone in self.player_on_move.stones.items():
            if stone.type == StoneTypes.Queen:
                result += self._queen_possible_moves(stone.position)
            else:
                result += self._possible_moves(stone.position)
        return result

    def _get_all_queens_possible_moves(self):
        result = []
        for _, stone in self.player_on_move.stones.items():
            if stone.type == StoneTypes.Queen:
                result += self._queen_possible_moves(stone.position)
        return result

    def _filter_possible_moves(self, moves):
        res = []
        if self._can_queen_jump():
            if self.selected_stone == StoneTypes.Basic:
                return []
            for m in moves:
                if m.is_jump():
                    res.append(m)
            return res

        if self._can_someone_jump():
            for m in moves:
                if m.is_jump():
                    res.append(m)
            return res

        return moves


class Stone:
    def __init__(self, id, position, player):
        self.id = id
        self.position = position
        self.owner = player
        self.type = StoneTypes.Basic


class Player:
    def __init__(self, id, type, AI_Algorithm = None):
        self.id = id
        self.type = type
        self.stones = self._generate_stones()
        self.direction = MovementDirection.Up if id == 0 else MovementDirection.Down
        self.AI = AI_Algorithm

    def _generate_stones(self):
        stones = {}
        stone_id = self.id
        for _ in range(12):
            actual_stone = Stone(stone_id, self._get_init_stone_position(stone_id), self)
            stones[stone_id] = actual_stone
            stone_id += 2
        return stones

    def _get_init_stone_position(self, stone_id):
        modified_id = stone_id // 2
        row = modified_id // 4
        col = (modified_id % 4) * 2 + (row % 2)
        if stone_id % 2 == 0:
            row = 7 - row
            col = 7 - col
        return col, row


class Move:
    def __init__(self, end, removed_stone):
        self.end = end
        self.removed_stone = removed_stone

    def is_jump(self):
        return self.removed_stone is not None
