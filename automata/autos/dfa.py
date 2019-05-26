#!/usr/bin/env python3
"""Класс для работы с ДКА"""

import copy
import itertools
import queue

import automata.exceptions.exceptions as exceptions


class DFA():
    def __init__(self, *, states, alphabet, transition_matrix,
                 inistate, final_states):
        self.states = states.copy()
        self.alphabet = alphabet.copy()
        self.transition_matrix = copy.deepcopy(transition_matrix)
        self.inistate = inistate
        self.final_states = final_states.copy()

    def _get_next_current_state(self, current_state, input_symbol):
        """
        Получаем следующие состояния
        """
        if input_symbol in self.transition_matrix[current_state]:
            return self.transition_matrix[current_state][input_symbol]
        else:
            raise exceptions.RejectionException(
                'Встречен некорректный символ {}'.format(input_symbol))

    def _rejection_check(self, current_state):
        """Проверка на прерывание"""
        if current_state not in self.final_states:
            raise exceptions.RejectionException(
                'Останов в нетерминальном состоянии({})'.format(
                    current_state))

    def read_input(self, input_str):
        """Передаем строку в автомат"""
        validation_generator = self.read_input_stepwise(input_str)
        for config in validation_generator:
            pass
        return config

    def copy(self):
        """Глубокое копирование автомата"""
        return self.__class__(**self.__dict__)

    def accepts_input(self, input_str):
        """Проверяем входную строку"""
        try:
            self.read_input(input_str)
            return True
        except exceptions.RejectionException:
            return False

    def read_input_stepwise(self, input_str):
        """
        Пошаговая проверка
        """
        current_state = self.inistate

        yield current_state
        for input_symbol in input_str:
            current_state = self._get_next_current_state(
                current_state, input_symbol)
            yield current_state

        self._rejection_check(current_state)

    def minimize(self):
        """
        Создаем минимальный ДКА
        """
        new_dfa = self.copy()
        new_dfa._comb_unreachable()
        states_table = new_dfa._create_markable_states_table()
        new_dfa._mark_final(states_table)
        new_dfa._mark_additoinal(states_table)
        new_dfa._merge_marked(states_table)
        return new_dfa

    def _comb_unreachable(self):
        """Ищем недостижимые состояния"""
        reachable_states = self._det_reachable()
        unreachable_states = self.states - reachable_states
        for state in unreachable_states:
            self.states.remove(state)
            del self.transition_matrix[state]

    def _det_reachable(self):
        """Определяем достижимые состояния"""
        reachable_states = set()
        states_to_check = queue.Queue()
        states_checked = set()
        states_to_check.put(self.inistate)
        while not states_to_check.empty():
            state = states_to_check.get()
            reachable_states.add(state)
            for symbol, dst_state in self.transition_matrix[state].items():
                if dst_state not in states_checked:
                    states_to_check.put(dst_state)
            states_checked.add(state)
        return reachable_states

    def _create_markable_states_table(self):
        """
        Создаем табличку с комбиациями состояний
        """
        table = {
            frozenset(c): False
            for c in itertools.combinations(self.states, 2)
        }
        return table

    def _mark_final(self, table):
        """Помечаем пару состояний, если хотя бы одно из них - терминальное"""
        for s in table.keys():
            if any((x in self.final_states for x in s)):
                if any((x not in self.final_states for x in s)):
                    table[s] = True

    def _mark_additoinal(self, table):
        """
        Помечаем состояния, если есть переход из уже помеченных
        """
        changed = True
        while changed:
            changed = False
            for s in filter(lambda s: not table[s], table.keys()):
                s_ = tuple(s)
                for a in self.alphabet:
                    s2 = frozenset({
                        self._get_next_current_state(s_[0], a),
                        self._get_next_current_state(s_[1], a)
                    })
                    if s2 in table and table[s2]:
                        table[s] = True
                        changed = True
                        break

    def _merge_marked(self, table):
        """Объединение непомеченных пар состояний в одно состояние
        """
        non_marked_states = set(filter(lambda s: not table[s], table.keys()))
        changed = True
        while changed:
            changed = False
            for s, s2 in itertools.combinations(non_marked_states, 2):
                if s2.isdisjoint(s):
                    continue
                # слияние
                s3 = s.union(s2)
                # удаляем старые
                non_marked_states.remove(s)
                non_marked_states.remove(s2)
                # добаляем новое
                non_marked_states.add(s3)
                # выставляяем флаг на изменение
                changed = True
                break
        # меняем ДКА
        for s in non_marked_states:
            stringified = DFA._embed_to_braces(s)
            # добаляем новое
            self.states.add(stringified)
            self.transition_matrix[stringified] = self.transition_matrix[tuple(s)[0]]
            # удаляем вхождения старых состояний
            for state in s:
                self.states.remove(state)
                del self.transition_matrix[state]
                for src_state, transition in self.transition_matrix.items():
                    for symbol in transition.keys():
                        if transition[symbol] == state:
                            transition[symbol] = stringified
                if state in self.final_states:
                    self.final_states.add(stringified)
                    self.final_states.remove(state)
                if state == self.inistate:
                    self.inistate = stringified

    @staticmethod
    def _embed_to_braces(states):
        """Создаем имя для нового состояния"""
        if isinstance(states, (set, frozenset)):
            states = sorted(states)
        return '{{{}}}'.format(','.join(states))

    @classmethod
    def _nfa_queue_extract(cls, nfa, current_states,
                           current_state_name, dfa_states,
                           dfa_transition_matrix, dfa_final_states):
        """ДОбавляем состояния из НКА в ДКА"""
        dfa_states.add(current_state_name)
        dfa_transition_matrix[current_state_name] = {}
        if (current_states & nfa.final_states):
            dfa_final_states.add(current_state_name)

    @classmethod
    def _nfa_enqueue(cls, nfa, current_states,
                     current_state_name, state_queue,
                     dfa_transition_matrix):
        """Следующая очередь состояний из НКА"""
        for input_symbol in nfa.alphabet:
            next_current_states = nfa._get_next_current_states(
                current_states, input_symbol)
            dfa_transition_matrix[current_state_name][input_symbol] = (
                cls._embed_to_braces(next_current_states))
            state_queue.put(next_current_states)

    @classmethod
    def from_nfa(cls, nfa):
        """Строим ДКА по НКА"""
        dfa_states = set()
        dfa_symbols = nfa.alphabet
        dfa_transition_matrix = {}
        nfa_inistates = nfa._get_border(nfa.inistate)
        dfa_inistate = cls._embed_to_braces(nfa_inistates)
        dfa_final_states = set()

        state_queue = queue.Queue()
        state_queue.put(nfa_inistates)
        while not state_queue.empty():

            current_states = state_queue.get()
            current_state_name = cls._embed_to_braces(current_states)
            if current_state_name in dfa_states:
                continue
            cls._nfa_queue_extract(nfa, current_states,
                                   current_state_name, dfa_states,
                                   dfa_transition_matrix, dfa_final_states)
            cls._nfa_enqueue(
                nfa, current_states, current_state_name, state_queue,
                dfa_transition_matrix)

        return cls(
            states=dfa_states, alphabet=dfa_symbols,
            transition_matrix=dfa_transition_matrix, inistate=dfa_inistate,
            final_states=dfa_final_states)
