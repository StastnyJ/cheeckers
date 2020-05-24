from enum import Enum
from random import randint
from math import *

class Directions(Enum):
    lu = 0
    ru = 1
    ld = 2
    rd = 3


class AIMove:
    def __init__(self, start, end, removed):
        self.start = start
        self.end = end
        self.removed = removed 


class AIBase:
    def _format_input(self, playground, my_id, rotate):
        enemy_stones = set()
        my_stones = set()
        queens = set()
        for row in playground:
            for pos in row:
                if pos is None:
                    continue
                if pos.owner.id == my_id:
                    my_stones.add(self._coords_to_num(pos.position, rotate))
                else:
                    enemy_stones.add(self._coords_to_num(pos.position, rotate))
                if pos.type.value == 1:
                    queens.add(self._coords_to_num(pos.position, rotate))
        return (my_stones, enemy_stones, queens)

    def _coords_to_num(self, coords, rotate):
        col, row = coords
        return 4 * row + col // 2 if not rotate else 31 - (4 * row + col // 2)

    def _num_to_coords(self, num, rotate):
        if rotate:
            num = 31 - num
        return (2 * (num % 4) + (num // 4 ) % 2, num // 4)

    def _format_output(self, start_position, end_position, rotate):
        my_start, enemy_start, _ = start_position
        my_end, enemy_end, _ = end_position
        for m in my_start.symmetric_difference(my_end):
            if m in my_start:
                start = self._num_to_coords(m, rotate)
            else:
                end = self._num_to_coords(m, rotate)
        removed = []
        for r in enemy_start - enemy_end:
            removed.append(self._num_to_coords(r, rotate))
        return AIMove(start, end, removed)

    def _get_neighbor_positions(self, pos):
        left_moved = (pos // 4) % 2 == 0
        if left_moved:
            lu = None if pos % 4 == 0 else pos - 5
            ru = pos - 4
            ld = None if pos % 4 == 0 else pos + 3
            rd = pos + 4
        else:
            lu = pos - 4
            ru = None if pos % 4 == 3 else pos - 3
            ld = pos + 4
            rd = None if pos % 4 == 3 else pos + 5
        if pos < 4:
            lu = None
            ru = None
        if pos > 27:
            ld = None
            rd = None
        return lu, ru, ld, rd

    def _get_neighbor_position(self, pos, direction):
        return self._get_neighbor_positions(pos)[direction.value]

    def make_move(self, playground, my_id, rotate = False):
        start_position = self._format_input(playground, my_id, rotate)
        end_position = self._solve_problem(start_position)
        return self._format_output(start_position, end_position, rotate)

    def _solve_problem(self, start):
        print("AIBase")
        return start


class MovementTreeStrategy(AIBase):
    def __init__(self):
        self._tmp_results = {}
        self._tmp_enemy_results = {}

    def _generate_all_possible_moves(self, my_stones, enemy_stones, queens):
        jump_moves = []
        normal_moves = []
        key = hash((tuple(my_stones), tuple(enemy_stones), tuple(queens)))
        if key in self._tmp_results:
            return self._tmp_results[key]
        for stone in my_stones:
            if stone in queens:
                act, act_jump = self._generate_possible_queen_moves(my_stones, enemy_stones, queens, stone)
            else:
                act, act_jump = self._generate_possible_moves(my_stones, enemy_stones, queens, stone)
            jump_moves += act_jump
            if len(jump_moves) == 0:
                normal_moves += act
        self._tmp_results[key] = jump_moves if len(jump_moves) > 0 else normal_moves
        return jump_moves if len(jump_moves) > 0 else normal_moves

    def _generate_possible_queen_moves(self, my_stones, enemy_stones, queens, actual_stone):
        res_normal = []
        res_jump = []
        normal, jump = self._generate_possible_queen_moves_in_one_direction(my_stones, enemy_stones, queens, actual_stone, Directions.lu)
        res_normal += normal
        res_jump += jump
        normal, jump = self._generate_possible_queen_moves_in_one_direction(my_stones, enemy_stones, queens, actual_stone, Directions.ru)
        res_normal += normal
        res_jump += jump
        normal, jump = self._generate_possible_queen_moves_in_one_direction(my_stones, enemy_stones, queens, actual_stone, Directions.ld)
        res_normal += normal
        res_jump += jump
        normal, jump = self._generate_possible_queen_moves_in_one_direction(my_stones, enemy_stones, queens, actual_stone, Directions.rd)
        res_normal += normal
        res_jump += jump
        return (res_normal, res_jump)

    def _generate_possible_queen_moves_in_one_direction(self, my_stones, enemy_stones, queens, actual_stone, direction):
        target = actual_stone
        res_normal = []
        res_jump = []
        jumped_stone = None
        while True:
            target = self._get_neighbor_position(target, direction)
            if target is None or target in my_stones:
                break
            if target in enemy_stones:
                if jumped_stone is not None:
                    break
                jumped_stone = target
                continue
            new_my = set(my_stones)
            new_queen = set(queens)
            new_my.remove(actual_stone)
            new_my.add(target)
            new_queen.remove(actual_stone)
            new_queen.add(target)
            if jumped_stone is None:
                res_normal.append((new_my, enemy_stones, new_queen))
            else:
                new_enemy = set(enemy_stones)
                new_enemy.remove(jumped_stone)
                _, moves = self._generate_possible_queen_moves(new_my, new_enemy, new_queen, target)
                if len(moves) > 0:
                    res_jump += moves
                else:
                    res_jump.append((new_my, new_enemy, new_queen))
        return (res_normal, res_jump)
            
    def _generate_possible_moves(self, my_stones, enemy_stones, queens, actual_stone):
        _, _, ld, rd = self._get_neighbor_positions(actual_stone)
        res_normal = []
        res_jump = []
        normal, jump = self._generate_moves(my_stones, enemy_stones, actual_stone, queens, ld, Directions.ld)
        res_normal += normal
        res_jump += jump
        normal, jump = self._generate_moves(my_stones, enemy_stones, actual_stone, queens, rd, Directions.rd)
        res_normal += normal
        res_jump += jump
        return (res_normal, res_jump)
    
    def _generate_moves(self, my_stones, enemy_stones, actual_stone, queens, target, direction):
        if target is None:
            return ([], [])
        if target in my_stones:
            return ([], [])
        if target in enemy_stones:
            new_pos = self._get_neighbor_position(target, direction)
            if new_pos is None or new_pos in my_stones or new_pos in enemy_stones:
                return ([], [])
            new_my = set(my_stones)
            new_enemy = set(enemy_stones)
            new_enemy.remove(target)
            new_queens = set(queens)
            if target in queens:
                new_queens.remove(target)
            new_my.remove(actual_stone)
            new_my.add(new_pos)
            _, moves = self._generate_possible_moves(new_my, new_enemy, new_queens, new_pos)
            if len(moves) > 0:
                return ([], moves)
            return ([], [(new_my, new_enemy, new_queens)])
        new_my = set(my_stones)
        new_my.remove(actual_stone)
        new_my.add(target)
        new_queens = set(queens)
        if target > 27:
            new_queens.add(target)
        return ([(new_my, enemy_stones, new_queens)], [])
        
    def _generate_all_possible_enemy_moves(self, my_stones, enemy_stones, queens):
        jump_moves = []
        normal_moves = []
        key = hash((tuple(my_stones), tuple(enemy_stones), tuple(queens)))
        if key in self._tmp_enemy_results:
            return self._tmp_enemy_results[key]

        for stone in enemy_stones:
            if stone in queens:
                act, act_jump = self._generate_possible_queen_moves(enemy_stones, my_stones, queens, stone)
            else:
                act, act_jump = self._generate_possible_enemy_moves(enemy_stones, my_stones, queens, stone)
            jump_moves += act_jump
            if len(jump_moves) == 0:
                normal_moves += act
        self._tmp_enemy_results[key] = jump_moves if len(jump_moves) > 0 else normal_moves
        return jump_moves if len(jump_moves) > 0 else normal_moves

    def _generate_possible_enemy_moves(self, my_stones, enemy_stones, queens, stone):
        lu, ru, _, _ = self._get_neighbor_positions(stone)
        res_normal = []
        res_jump = []
        normal, jump = self._generate_enemy_moves(my_stones, enemy_stones, stone, queens, lu, Directions.lu)
        res_normal += normal
        res_jump += jump
        normal, jump = self._generate_enemy_moves(my_stones, enemy_stones, stone, queens, ru, Directions.ru)
        res_normal += normal
        res_jump += jump
        return (res_normal, res_jump)

    def _generate_enemy_moves(self, my_stones, enemy_stones, actual_stone, queens, target, direction):
        if target is None:
            return ([], [])
        if target in my_stones:
            return ([], [])
        if target in enemy_stones:
            new_pos = self._get_neighbor_position(target, direction)
            if new_pos is None or new_pos in my_stones or new_pos in enemy_stones:
                return ([], [])
            new_my = set(my_stones)
            new_enemy = set(enemy_stones)
            new_enemy.remove(target)
            new_queens = set(queens)
            if target in queens:
                new_queens.remove(target)
            new_my.remove(actual_stone)
            new_my.add(new_pos)
            _, moves = self._generate_possible_enemy_moves(new_my, new_enemy, new_queens, new_pos)
            if len(moves) > 0:
                return ([], moves)
            return ([], [(new_my, new_enemy, new_queens)])
        new_my = set(my_stones)
        new_my.remove(actual_stone)
        new_my.add(target)
        new_queens = set(queens)
        if target > 27:
            new_queens.add(target)
        return ([(new_my, enemy_stones, new_queens)], [])

class RandomStrategy(MovementTreeStrategy):
    def _solve_problem(self, start):
        possible_moves = self._generate_all_possible_moves(start[0], start[1], start[2])
        print(len(possible_moves))
        return possible_moves[randint(0, len(possible_moves) - 1)]


class MinMaxStrategy(MovementTreeStrategy):
    def __init__(self, max_deep):
        self.max_deep = max_deep
        super(MinMaxStrategy, self).__init__()

    def _solve_problem(self, start):
        return self._get_max(start[0], start[1], start[2])[1]

    def _get_max(self, my_stones, enemy_stones, queens, act_deep = 0):
        moves = self._generate_all_possible_moves(my_stones, enemy_stones, queens)
        best = -inf
        best_move = None
        if act_deep >= self.max_deep:
            for move in moves:
                score = self._value_position(move)
                if score >= best:
                    best = score
                    best_move = move
            return (best, best_move)
        for move in moves:
            act, _ = self._get_min(move[0], move[1], move[2], act_deep + 1)
            if act >= best:
                best = act
                best_move = move
        if act_deep == 0 and best_move is None:
            a = 1
        return (best, best_move)

    def _get_min(self, my_stones, enemy_stones, queens, act_deep = 0):
        moves = self._generate_all_possible_enemy_moves(my_stones, enemy_stones, queens)
        best = inf
        best_move = None
        for move in moves:
            act, _ = self._get_max(move[1], move[0], move[2], act_deep + 1)
            if act <= best:
                best = act
                best_move = move
        return (best, best_move)

    def _value_position(self, position):
        my_stones, enemy_stones, queens = position
        score = len(my_stones) - len(enemy_stones)
        for q in queens:
            if q in my_stones:
                score += 10
            else:
                score -= 10
        return score



class MinMaxRandomStrategy(MovementTreeStrategy):
    def __init__(self, max_deep):
        self.max_deep = max_deep
        super(MinMaxStrategy, self).__init__()

    def _solve_problem(self, start):
        return self._get_max(start[0], start[1], start[2])[1]

    def _get_max(self, my_stones, enemy_stones, queens, act_deep = 0):
        moves = self._generate_all_possible_moves(my_stones, enemy_stones, queens)
        valued_moves = []
        for move in moves:
            if act_deep >= self.max_deep:
                score = self._value_position(move)
            else
                score, _ = self._get_min(move[0], move[1], move[2], act_deep + 1)
            valued_moves.append((score, move))
        # Select_best
        return (best, best_move)

    def _get_min(self, my_stones, enemy_stones, queens, act_deep = 0):
        moves = self._generate_all_possible_enemy_moves(my_stones, enemy_stones, queens)
        best = inf
        best_move = None
        for move in moves:
            act, _ = self._get_max(move[1], move[0], move[2], act_deep + 1)
            if act <= best:
                best = act
                best_move = move
        return (best, best_move)

    def _value_position(self, position):
        my_stones, enemy_stones, queens = position
        score = len(my_stones) - len(enemy_stones)
        for q in queens:
            if q in my_stones:
                score += 10
            else:
                score -= 10
        return score


class MinMaxFlexibleDeepStrategy(MinMaxStrategy):
    def _get_max_deep_downgread(self, moves, act_deep):
        return int(log(moves + 1, act_deep + 2))

    def _get_max(self, my_stones, enemy_stones, queens, act_deep = 0, max_deep = 8):
        moves = self._generate_all_possible_moves(my_stones, enemy_stones, queens)
        best = -inf
        best_move = None
        max_deep -= self._get_max_deep_downgread(len(moves), act_deep)
        if act_deep >= max_deep:
            for move in moves:
                score = self._value_position(move)
                if score >= best:
                    best = score
                    best_move = move
            return (best, best_move)
        for move in moves:
            act, _ = self._get_min(move[0], move[1], move[2], act_deep + 1, max_deep)
            if act >= best:
                best = act
                best_move = move
        if act_deep == 0 and best_move is None:
            a = 1
        return (best, best_move)

    def _get_min(self, my_stones, enemy_stones, queens, act_deep = 0, max_deep = 8):
        moves = self._generate_all_possible_enemy_moves(my_stones, enemy_stones, queens)
        best = inf
        best_move = None
        max_deep -= self._get_max_deep_downgread(len(moves), act_deep)
        for move in moves:
            act, _ = self._get_max(move[1], move[0], move[2], act_deep + 1, max_deep)
            if act <= best:
                best = act
                best_move = move
        return (best, best_move)