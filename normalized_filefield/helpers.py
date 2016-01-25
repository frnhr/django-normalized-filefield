from collections import namedtuple


def make_choices(name, choices_str, start_from=0):
    """
    A pattern for Django choices.
    Uses integers for choice values and named things in code.

    Usage:
    >>> STATE = make_choices("State", "empty selected current update clear")
    >>> STATE
    State(empty=0, selected=1, current=2, update=3, clear=4)
    >>> STATE.empty
    0
    >>> STATE.current
    2
    >>> STATE._name(1)
    'selected'
    >>> OPTIONS = make_choices("Options", "good bad ugly", start_from=101)
    >>> OPTIONS
    Options(good=101, bad=102, ugly=103)
    >>> OPTIONS._name(102)
    'bad'

    :param name: string, name of the class
    :param choices_str: string, space-separated names of possible choices
    :param start_from: int
    :return: namedtuple instance
    """
    choices_class = namedtuple(name, choices_str)
    choices_class._choices_str = choices_str
    choices_class._start_from = start_from
    choices_class._name = lambda self, i: self._choices_str.split()[i - self._start_from]
    choices_count = len(choices_str.split())
    choices = choices_class._make(range(start_from, choices_count + start_from))
    return choices
