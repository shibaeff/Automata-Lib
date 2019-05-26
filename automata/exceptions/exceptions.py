#!/usr/bin/env python3


class AutomataError(Exception):
    """В автомате возникла ошибка."""

    pass


class UnknownState(AutomataError):
    """Некорректное состояние"""

    pass


class UnknownCharacter(AutomataError):
    """Некорректный символ"""

    pass


class StateGapError(AutomataError):
    """Пропущено состояние при инициализации автомата"""

    pass


class SymbolGapError(AutomataError):
    """Пропущен символ при иницаилизации автомата"""

    pass


class IniStateError(AutomataError):
    """Некорректное начальное состояние"""

    pass


class FinalStateError(AutomataError):
    """Ошибка конечного состояния"""

    pass


class RejectionException(AutomataError):
    """Автомат отверг ввод"""

    pass
