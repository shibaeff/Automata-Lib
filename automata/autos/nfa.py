#!/usr/bin/env python3
"""Класс для работы с НКА"""

import copy

import automata.exceptions.exceptions as exceptions


class NFA():
    def __init__(self, *, states, alphabet, transition_matrix,
                 inistate, final_states):
        self.states = states.copy()
        self.alphabet = alphabet.copy()
        self.transition_matrix = copy.deepcopy(transition_matrix)
        self.inistate = inistate
        self.final_states = final_states.copy()

    @classmethod
    def from_dfa(cls, dfa):
        """Строим ДКА из НКА"""
        nfa_transition_matrix = {}

        for start_state, paths in dfa.transition_matrix.items():
            nfa_transition_matrix[start_state] = {}
            for input_symbol, end_state in paths.items():
                nfa_transition_matrix[start_state][input_symbol] = {end_state}

        return cls(
            states=dfa.states, alphabet=dfa.alphabet,
            transition_matrix=nfa_transition_matrix, inistate=dfa.inistate,
            final_states=dfa.final_states)

    def read_input(self, input_str):
        """
        Даем на вход строку
        """
        validation_generator = self.read_input_stepwise(input_str)
        for config in validation_generator:
            pass
        return config

    def accepts_input(self, input_str):
        """ПРоверяем, принимает автомат строку"""
        try:
            self.read_input(input_str)
            return True
        except exceptions.RejectionException:
            return False

    def _get_border(self, start_state):
        """
        Получаем замыкание состояния т.е. состония, достижимые по пустым
        переходам
        """
        stack = []
        encountered_states = set()
        stack.append(start_state)

        while stack:
            state = stack.pop()
            if state not in encountered_states:
                encountered_states.add(state)
                if '' in self.transition_matrix[state]:
                    stack.extend(self.transition_matrix[state][''])

        return encountered_states

    def _get_next_current_states(self, current_states, input_symbol):
        """Получаем слудющие состояния для перехода"""
        next_current_states = set()

        for current_state in current_states:
            symbol_end_states = self.transition_matrix[current_state].get(
                input_symbol)
            if symbol_end_states:
                for end_state in symbol_end_states:
                    next_current_states.update(
                        self._get_border(end_state))

        return next_current_states


    def read_input_stepwise(self, input_str):
        """
        Скармливаем строку автомату и получаем результаты шагов через
        генератор
        """
        current_states = self._get_border(self.inistate)

        yield current_states
        for input_symbol in input_str:
            next_current_states = set()

            for current_state in current_states:
                symbol_end_states = self.transition_matrix[current_state].get(
                    input_symbol)
                if symbol_end_states:
                    for end_state in symbol_end_states:
                        next_current_states.update(
                            self._get_border(end_state))
            current_state = next_current_states
            yield current_states

        if not (current_states & self.final_states):
            raise exceptions.RejectionException(
                'НКА остановился на нетерминальных состояниях ({})'.format(
                    ', '.join(current_states)))

    def copy(self):
        return self.__class__(**self.__dict__)
