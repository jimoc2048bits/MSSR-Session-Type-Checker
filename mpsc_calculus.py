import math
from decimal import Decimal
from fractions import Fraction
from typing import Dict, List, Optional, Tuple, Union, Set
import var
import parser

thread_number = 0

class Statement:
    """Commands."""
    def __init__(self):
        pass

    def get_vars(self) -> Set[str]:
        """Returns set of variables in the expression."""
        raise NotImplementedError

    def get_fun_names(self) -> Set[str]:
        """Return set of function names in the expression"""
        return NotImplementedError
    
    def __hash__(self) -> int:
        pass
    

class Basic(Statement):
    def __init__(self, st):
        """A basic type statement."""
        super(Basic, self).__init__()
        self.type = "basic"
        # assert all(isinstance(hp, Statement) for hp in hps)
        self.st = st

    def __repr__(self):
        return "%s;" % self.st

    def __str__(self):
        return "%s;" % self.st
    
    def get_fun_names(self):
        return set()

class Inaction(Statement):
    def __init__(self):
        """hps is a list of hybrid programs."""
        super(Inaction, self).__init__()
        self.type = "inaction"
        # assert all(isinstance(hp, Statement) for hp in hps)
        self.st = 0

    def __repr__(self):
        return "%s;" % self.st

    def __str__(self):
        return "%s;" % self.st
    
    def get_fun_names(self):
        return set()
    
class ExternalChoice(Statement):
    def __init__(self, channel, source, comm_list):
        """hps is a list of hybrid programs."""
        super(ExternalChoice, self).__init__()
        self.type = "external choice"
        self.channel = channel
        self.source = source
        self.comm_list = comm_list
        # A list of comm events, which is a list of 2 elements: a tuple (label, payload), and a continuation statement. 

    def __repr__(self):
        return "[recv: %s, %s, %s]" % (self.channel, self.source, self.comm_list)

    def __str__(self):
        return "[recv: %s, %s, %s]" % (self.channel, self.source, self.comm_list)
    
    def get_fun_names(self):
        return set()
    
class InternalChoice(Statement):
    def __init__(self, channel, target, comm_list):
        """hps is a list of hybrid programs."""
        super(InternalChoice, self).__init__()
        self.type = "internal choice"
        self.channel = channel
        self.target = target
        self.comm_list = comm_list

    def __repr__(self):
        return "[send: %s, %s, %s]" % (self.channel, self.target, self.comm_list)

    def __str__(self):
        return "[send: %s, %s, %s]" % (self.channel, self.target, self.comm_list)
    
    def get_fun_names(self):
        return set()

class MPSCExternalChoice(Statement):
    def __init__(self, channel, comm_list):
        """hps is a list of hybrid programs."""
        super(MPSCExternalChoice, self).__init__()
        self.type = "external choice"
        self.channel = channel
        self.comm_list = comm_list

    def __repr__(self):
        return "[mpscrecv: %s, %s]" % (self.channel, self.comm_list)

    def __str__(self):
        return "[mpscrecv: %s, %s]" % (self.channel, self.comm_list)
    
    def get_fun_names(self):
        return set()
    
class FunctionDef(Statement):
    def __init__(self, name, para_list, func_body, func_ctxt):
        """para_list is a list of AVar, func_body and func_ctxt are Statement."""
        super(FunctionDef, self).__init__()
        self.type = "function definition"
        self.name = name
        self.para_list = para_list
        self.func_body = func_body
        self.func_ctxt = func_ctxt

    def __repr__(self):
        str_list = []
        for para in self.para_list:
            str_list.append(str(para))
        return "def %s(%s) = %s in %s" % (self.name, ', '.join(str_list), self.func_body, self.func_ctxt)

    def __str__(self):
        str_list = []
        for para in self.para_list:
            str_list.append(str(para))
        return "def %s(%s) = %s in %s" % (self.name, ', '.join(str_list), self.func_body, self.func_ctxt)
    
    def get_fun_names(self):
        return set()
    
class FunctionCall(Statement):
    def __init__(self, name, para_list):
        """para_list is a list of AVar, AConst or ChannelRole."""
        super(FunctionCall, self).__init__()
        self.type = "function call"
        self.name = name
        self.para_list = para_list

    def __repr__(self):
        str_list = []
        for para in self.para_list:
            str_list.append(str(para))
        return "%s<%s>" % (self.name, ', '.join(str_list))

    def __str__(self):
        str_list = []
        for para in self.para_list:
            str_list.append(str(para))
        return "%s<%s>" % (self.name, ', '.join(str_list))
    
    def get_fun_names(self):
        return set()
    


# class FunctionCall(Statement):
#     def __init__(self, name, formal_paras, actual_paras, seq):
#         """seq is a Sequence statement."""
#         super(FunctionCall, self).__init__()
#         self.type = "call"
#         self.name = name
#         seq_str = seq
#         assert len(formal_paras) == len(actual_paras)
#         for i in range(0, len(formal_paras)):
#             seq_str = str.replace(seq_str, formal_paras[i], actual_paras[i])
#         self.seq = parser.seq_parser.parse(seq_str)

#     def __repr__(self):
#         return "FunCall_%s(%s)" % (self.name, self.seq)

#     def __str__(self):
#         return " ".join("{" + str(hp) + "}" for hp in self.hps)
    
#     def get_fun_names(self):
#         return set()
    
class Sequence(Statement):
    def __init__(self, *hps):
        """hps is a list of hybrid programs."""
        super(Sequence, self).__init__()
        self.type = "sequence"
        # assert all(isinstance(hp, Statement) for hp in hps)
        # assert len(hps) >= 1
        self.hps: List[Statement] = []
        for hp in hps:
            if isinstance(hp, Sequence):
                self.hps.extend(hp.hps)
            else:
                self.hps.append(hp)
        self.hps = tuple(self.hps)

    def __repr__(self):
        return "Seq(%s)" % ", ".join(repr(hp) for hp in self.hps)

    def __str__(self):
        return " ".join("{" + str(hp) + "}" for hp in self.hps)
    
    def get_fun_names(self):
        return set()
    

# class ITE(Statement):
#     def __init__(self, if_hps, else_hp=None):
#         super(ITE, self).__init__()
#         # assert all(isinstance(cond, expr.Expr) and isinstance(hp, Statement) for cond, hp in if_hps)
#         assert len(if_hps) > 0, "ITE: must have at least one if branch"
#         # assert else_hp is None or isinstance(else_hp, Statement)
#         self.type = "ite"
#         self.if_hps: List[Tuple[expr.Expr, Statement]] = list(tuple(p) for p in if_hps)
#         self.else_hp: Optional[Statement] = else_hp

#     def __repr__(self):
#         if_hps_strs = ", ".join("%s, %s" % (cond, repr(hp)) for cond, hp in self.if_hps)
#         return "ITE(%s, %s)" % (if_hps_strs, repr(self.else_hp))

#     def __str__(self):
#         res = "if (%s) { %s " % (self.if_hps[0][0], self.if_hps[0][1])
#         for cond, hp in self.if_hps[1:]:
#             res += "} else if (%s) { %s " % (cond, hp)
#         if self.else_hp is None:
#             res += "}"
#         else:
#             res += "} else { %s }" % self.else_hp
#         return res

#     def __eq__(self, other):
#         return self.type == other.type and self.if_hps == other.if_hps and self.else_hp == other.else_hp
    
#     def get_fun_names(self):
#         return set()
    
class Lock(Sequence):
    def __init__(self, name, var):
        super(Lock, self).__init__()
        self.type = "lock"
        global thread_number
        self.thread = thread_number
        self.name = name
        self.hps: List[Statement] = []
        comm_list1 = [("l_" + str(thread_number), None)]
        comm_list2 = [("lock", None)]
        comm_list3 = [("ok", var)]
        self.hps.append(InternalChoice(channel=self.name, target="lockserver_"+self.name, comm_list= comm_list1))
        self.hps.append(InternalChoice(channel=self.name, target="lockserver_"+self.name, comm_list= comm_list2))
        self.hps.append(ExternalChoice(channel=self.name, source="lockserver_"+self.name, comm_list= comm_list3))

class TryLock(Sequence):
    def __init__(self, name, var):
        super(TryLock, self).__init__()
        self.type = "try lock"
        global thread_number
        self.thread = thread_number
        self.name = name
        self.hps: List[Statement] = []
        comm_list1 = [("l_" + str(thread_number), None)]
        comm_list2 = [("try_lock", None)]
        comm_list3 = [("ok", var), ("block", None)]
        self.hps.append(InternalChoice(channel=self.name, target="lockserver_"+self.name, comm_list= comm_list1))
        self.hps.append(InternalChoice(channel=self.name, target="lockserver_"+self.name, comm_list= comm_list2))
        self.hps.append(ExternalChoice(channel=self.name, source="lockserver_"+self.name, comm_list= comm_list3))

class Unlock(Sequence):
    def __init__(self, name, var):
        super(Unlock, self).__init__()
        self.type = "unlock"
        global thread_number
        self.thread = thread_number
        self.name = name
        self.hps: List[Statement] = []
        comm_list1 = [("l_" + str(thread_number), None)]
        comm_list2 = [("unlock", var)]
        self.hps.append(InternalChoice(channel=self.name, target="lockserver_"+self.name, comm_list= comm_list1))
        self.hps.append(InternalChoice(channel=self.name, target="lockserver_"+self.name, comm_list= comm_list2))

    
class Send(Sequence):
    def __init__(self, name, payload):
        super(Send, self).__init__()
        self.name = name
        self.payload = payload

    def __repr__(self):
        return "Send(%s, %s)" % (self.name, self.payload)

    def __str__(self):
        return "<thread, %s, num, !>" % self.name

    def __hash__(self):
        return hash(("Send", self.name))
    
    def get_fun_names(self):
        return set()


class Recv(Sequence):
    def __init__(self, name, payload):
        super(Recv, self).__init__()
        self.name = name
        self.payload = payload

    def __repr__(self):
        return "Recv(%s, %s)" % (self.name, self.payload)

    def __str__(self):
        return "<thread, %s, num, ?>" % self.name

    def __hash__(self):
        return hash(("Recv", self.name))
    
    def get_fun_names(self):
        return set()
    

class ParaStatement:
    def __init__(self, statement):
        super(ParaStatement, self).__init__()
        self.states = list()
        self.states.append(statement)

    def __init__(self, a, b):
        super(ParaStatement, self).__init__()
        assert isinstance(a, ParaStatement) and isinstance(b, ParaStatement)
        self.states = a.states.extend(b.states)

    def __repr__(self):
        ret_str = ""
        for state in self.states:
            if ret_str != "":
                ret_str += " || "
            ret_str += str(self.states)
        return ret_str

    def __str__(self):
        ret_str = ""
        for state in self.states:
            if ret_str != "":
                ret_str += " || "
            ret_str += str(self.states)
        return ret_str

    def __hash__(self):
        return hash(str(self))
    
    def get_fun_names(self):
        return set()