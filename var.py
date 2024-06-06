import math
from decimal import Decimal
from fractions import Fraction
from typing import Dict, Set
    
class Expr:
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "Expr[%s]" % self.expr

    def __repr__(self):
        return "Expr[%s]" % self.expr

    def __hash__(self):
        return hash(("Expr", self.expr))

    def __eq__(self, other):
        return self.expr == other.expr

class ChannelRole(Expr):
    def __init__(self, role):
        self.role = role
        self.type = "role"

    def __str__(self):
        return "role_%s" % self.role

    def __repr__(self):
        return "role_%s" % self.role

    def __hash__(self):
        return hash(("CHANNELROLE", self.role))

    def __eq__(self, other):
        return isinstance(other, ChannelRole) and self.role == other.role
    
    def copy(self):
        ret = ChannelRole(self.role[:])
        return ret
    
class Channel:
    def __init__(self, role, oppo):
        self.__role__ = role
        self.__oppo__ = oppo
        # role is a ChannleRole or AVar,  oppo is a ChannleRole

    def __str__(self):
        return "channel[%s][%s]" % (self.__role__, self.__oppo__)

    def __repr__(self):
        return "channel[%s][%s]" % (self.__role__, self.__oppo__)

    def __hash__(self):
        return hash(("CHANNEL", self.__role__, self.__oppo__))

    def __eq__(self, other):
        return isinstance(other, Channel) and self.__role__ == other.__role__ and self.__oppo__ == other.__oppo__
    
    def copy(self):
        return Channel(self.__role__.copy(), self.__oppo__.copy())
    
    def getStandard(self):
        if str(self.__role__) < str(self.__oppo__):
            return str(self)
        else:
            return str(Channel(self.__oppo__, self.__role__))

class AVar(Expr):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Var[%s]" % self.name

    def __repr__(self):
        return "Var[%s]" % self.name

    def __hash__(self):
        return hash(("Var", self.name))

    def __eq__(self, other):
        return isinstance(other, AVar) and self.name == other.name
    
    def copy(self):
        return AVar(self.name[:])
    
class AConst(Expr):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Const[%s]" % self.value

    def __repr__(self):
        return "Const[%s]" % self.value

    def __hash__(self):
        return hash(("Const", self.value))

    def __eq__(self, other):
        return isinstance(other, AConst) and self.value == other.value