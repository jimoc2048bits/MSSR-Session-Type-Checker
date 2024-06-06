import math
from decimal import Decimal
from fractions import Fraction
from typing import Dict, Set

class Channel:
    def __init__(self, name: str, type: str, buffer: int):
        self.name = name
        self.type = type
        self.buffer = buffer

    def __str__(self):
        return "channel<%s>(%s)%s" % (self.type, self.buffer, self.name)

    def __repr__(self):
        return "channel<%s>(%s)%s" % (self.type, self.buffer, self.name)

    def __hash__(self):
        return hash(("CHANNEL", self.name, self.type, self.buffer))

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type and self.buffer == other.type

class Expr:
    """Expressions."""
    def __init__(self):
        pass

    def get_vars(self) -> Set[str]:
        """Returns set of variables in the expression."""
        raise NotImplementedError

    def get_fun_names(self) -> Set[str]:
        """Return set of function names in the expression"""
        return NotImplementedError

class AVar(Expr):
    def __init__(self, name):
        super(AVar, self).__init__()
        assert isinstance(name, str)
        self.name = name

    def __repr__(self):
        return "AVar(%s)" % self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, AVar) and self.name == other.name

    def __hash__(self):
        return hash(("AVar", self.name))
    
    def get_fun_names(self):
        return set()
    
class AStr(Expr):
    def __init__(self, name):
        super(AStr, self).__init__()
        assert isinstance(name, str)
        self.name = name

    def __repr__(self):
        return "AStr(%s)" % self.name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(("AStr", self.name))
    
    def get_fun_names(self):
        return set()
    
class AConst(Expr):
    def __init__(self, name):
        super(AConst, self).__init__()
        assert isinstance(name, str)
        self.name = name

    def __repr__(self):
        return "AConst(%s)" % self.name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(("AConst", self.name))
    
    def get_fun_names(self):
        return set()