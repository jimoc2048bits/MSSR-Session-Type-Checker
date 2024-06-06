import mpsc_calculus
from typing import Dict, List, Optional, Tuple, Union, Set
from var import Channel, ChannelRole, Expr, AVar, AConst

class BType:
    """Type of payload. The type is int, bool, real, string and LType."""
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return str(self.type)
    
    def __repr__(self):
        return str(self.type)
    
    def __eq__(self, other) -> bool:
        return self.type == other.type

    def __hash__(self) -> int:
        return hash(str(self))
    

class LType(BType):
    """Local type."""
    def __init__(self):
        self.type = None

    def get_vars(self) -> Set[str]:
        raise NotImplementedError

    def get_fun_names(self) -> Set[str]:
        return NotImplementedError


class SendType(LType):
    def __init__(self, target, comm_set):
        """comm_set is a set of ((label, type), cont)."""
        super(SendType, self).__init__()
        self.type = "send type"
        self.thread = 0
        self.target = target
        self.comm_set = set()
        self.comm_dict = dict()
        for comm in comm_set:
            assert isinstance(comm[0][1], BType)
            assert isinstance(comm[1], LType)
            assert comm[0] not in self.comm_set
            self.comm_set.add(comm[0])
            self.comm_dict[comm[0]] = comm[1]


    def __repr__(self):
        return "[send type:%s, %s, (%s)];" % (self.thread, self.target, self.comm_dict)
    
    def __eq__(self, other) -> bool:
        return self.type == other.type and self.thread == other.thread and self.target == other.target and self.comm_dict == other.comm_dict

    def __str__(self):
        return "[send type:%s, %s, (%s)];" % (self.thread, self.target, self.comm_dict)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def get_fun_names(self):
        return set()

class RecvType(LType):
    def __init__(self, source, comm_set):
        """comm_set is a set of ((label, type), cont)."""
        super(RecvType, self).__init__()
        self.type = "recv type"
        self.thread = 0
        self.source = source
        self.comm_set = set()
        self.comm_dict = dict()
        for comm in comm_set:
            assert isinstance(comm[0][1], BType)
            assert isinstance(comm[1], LType)
            assert comm[0] not in self.comm_set
            self.comm_set.add(comm[0])
            self.comm_dict[comm[0]] = comm[1]

    def __repr__(self):
        return "[recv type:%s, %s, (%s)];" % (self.thread, self.source, self.comm_dict)
    
    def __eq__(self, other) -> bool:
        return self.type == other.type and self.thread == other.thread and self.source == other.source and self.comm_dict == other.comm_dict

    def __str__(self):
        return "[recv type:%s, %s, (%s)];" % (self.thread, self.source, self.comm_dict)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def get_fun_names(self):
        return set()
    
class MultiRecvType(LType):
    def __init__(self, comm_set):
        """comm_set is a set of ((source, label, type), cont)."""
        super(MultiRecvType, self).__init__()
        self.type = "multi recv type"
        self.thread = 0
        self.source = set()
        self.comm_set = set()
        self.comm_dict = dict()
        for comm in comm_set:
            assert isinstance(comm[0][2], BType)
            assert isinstance(comm[1], LType)
            assert comm[0] not in self.comm_set
            self.source.add(comm[0][0])
            self.comm_set.add(comm[0])
            self.comm_dict[comm[0]] = comm[1]

    def __repr__(self):
        return "[multi recv type:%s, (%s)];" % (self.thread, self.comm_dict)
    
    def __eq__(self, other) -> bool:
        return self.type == other.type and self.thread == other.thread and self.comm_dict == other.comm_dict

    def __str__(self):
        return "[multi recv type:%s, (%s)];" % (self.thread, self.comm_dict)
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def get_fun_names(self):
        return set()
    
class RecLType(LType):
    def __init__(self, flag, cont):
        """flag is a string conrresponding to rec call."""
        super(RecLType, self).__init__()
        assert isinstance(flag, str)
        assert isinstance(cont, LType)
        self.type = "recursive type"
        self.flag = flag
        self.cont = cont

    def __repr__(self):
        return "#%s.%s" % (self.flag, self.cont)
       
    def __eq__(self, other) -> bool:
        return self.flag == other.flag and self.cont == other.cont

    def __str__(self):
        return "#%s.%s" % (self.flag, self.cont)
    
    def get_fun_names(self):
        return set()
    
class RecCallLType(LType):
    def __init__(self, flag):
        """flag is a string conrresponding to rec call."""
        super(RecCallLType, self).__init__()
        assert isinstance(flag, str)
        self.type = "recursive call type"
        self.flag = flag

    def __repr__(self):
        return "%s" % self.flag
       
    def __eq__(self, other) -> bool:
        return self.flag == other.flag

    def __str__(self):
        return "%s" % self.flag
    
    def get_fun_names(self):
        return set()
    
class EndLType(LType):
    def __init__(self):
        super(EndLType, self).__init__()
        self.type = "local end type"

    def __repr__(self):
        return "[end type];"
    
    def __eq__(self, other) -> bool:
        return self.type == other.type

    def __str__(self):
        return "[end type];"
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def get_fun_names(self):
        return set()
    
def mergeLocalType(lType1, lType2) -> LType:
    assert isinstance(lType1, LType) and isinstance(lType2, LType) 
    assert lType1.type == lType2.type
    if isinstance(lType1, SendType):
        assert lType1 == lType2
        return lType1
    elif isinstance(lType1, RecvType):
        assert isinstance(lType2, RecvType)
        assert lType1.source == lType2.source
        set1 = lType1.comm_set
        set2 = lType2.comm_set
        set_intersection = set1 & set2
        set_12 = set1 - set2
        set_21 = set2 - set1
        new_comm_set = set()
        for comm in set_intersection:
            new_comm_set.add((comm, mergeLocalType(lType1.comm_dict[comm], lType2.comm_dict[comm])))
        for comm in set_12:
            new_comm_set.add((comm, lType1.comm_dict[comm]))
        for comm in set_21:
            new_comm_set.add((comm, lType2.comm_dict[comm]))
        return RecvType(lType1.source, new_comm_set)
    elif isinstance(lType1, MultiRecvType):
        assert isinstance(lType2, MultiRecvType)
        set1 = lType1.comm_set
        set2 = lType2.comm_set
        set_intersection = set1 & set2
        set_12 = set1 - set2
        set_21 = set2 - set1
        new_comm_set = set()
        for comm in set_intersection:
            new_comm_set.add((comm, mergeLocalType(lType1.comm_dict[comm], lType2.comm_dict[comm])))
        for comm in set_12:
            new_comm_set.add((comm, lType1.comm_dict[comm]))
        for comm in set_21:
            new_comm_set.add((comm, lType2.comm_dict[comm]))
        return MultiRecvType(new_comm_set)
    elif isinstance(lType1, RecLType):
        assert isinstance(lType2, RecLType)
        assert lType1.flag == lType2.flag
        return RecLType(lType1.flag, mergeLocalType(lType1.cont, lType2.cont))
    elif isinstance(lType1, RecCallLType):
        assert isinstance(lType2, RecCallLType)
        assert lType1.flag == lType2.flag
        return RecCallLType(lType1.flag)
    elif isinstance(lType1, EndLType):
        return EndLType()
    
def recExpand(lType, flag, rType) -> LType:
    # assert isinstance(lType, LType) and isinstance(rType, RecLType)
    assert isinstance(lType, LType)
    assert isinstance(rType, RecLType)
    if isinstance(lType, SendType):
        new_comm_set = []
        for comm in lType.comm_set:
            new_comm = []
            new_comm.append(comm)
            new_comm.append(recExpand(lType.comm_dict[comm], flag, rType))
            new_comm_set.append(new_comm)
        return SendType(lType.target, new_comm_set)
    elif isinstance(lType, RecvType):
        new_comm_set = []
        for comm in lType.comm_set:
            new_comm = []
            new_comm.append(comm)
            new_comm.append(recExpand(lType.comm_dict[comm], flag, rType))
            new_comm_set.append(new_comm)
        return RecvType(lType.source, new_comm_set)
    elif isinstance(lType, MultiRecvType):
        new_comm_set = []
        for comm in lType.comm_set:
            new_comm = []
            new_comm.append(comm)
            new_comm.append(recExpand(lType.comm_dict[comm], flag, rType))
            new_comm_set.append(new_comm)
        return MultiRecvType(new_comm_set)
    elif isinstance(lType, RecLType):
        return RecLType(lType.flag, recExpand(lType.cont, flag, rType))
    elif isinstance(lType, RecCallLType):
        if lType.flag == flag:
            return rType
        else:
            return RecCallLType(lType.flag)
    elif isinstance(lType, EndLType):
        return EndLType()
    
    
class TypeContext:
    """Context of local types. 
    dic: a dictionary between role(s) or variable and its BType. 
    ch_vars: variables which types are LType.
    func_paras: a dictionary between function name and list of its paramaters' types.
    """
    def __init__(self):
        self.dic = dict()
        self.ch_vars = set()
        self.func_paras = dict()

    def __str__(self):
        return "Dict:" + str(self.dic) + "\nChannel Vars:" + str(self.ch_vars) + "\nFunctions:" + str(self.func_paras)
    
    def __repr__(self):
        return "Dict:" + str(self.dic) + "\nChannel Vars:" + str(self.ch_vars) + "\nFunctions:" + str(self.func_paras)
    
    def add(self, key, value):
        assert isinstance(key, set) or isinstance(key, AVar) or isinstance(key, ChannelRole)
        if isinstance(key, AVar):
            key_set = set()
            key_set.add(key)
            if isinstance(value, LType):
                self.ch_vars.add(key)
        elif isinstance(key, ChannelRole):
            key_set = set()
            key_set.add(key)
        else:
            key_set = key
        key_tuple = tuple(key_set)
        assert isinstance(value, BType)
        self.dic[key_tuple] = value

    def delete(self, key) -> bool:
        assert isinstance(key, set) or isinstance(key, AVar) or isinstance(key, ChannelRole)
        if isinstance(key, AVar):
            key_set = set()
            key_set.add(key)
        elif isinstance(key, ChannelRole):
            key_set = set()
            key_set.add(key)
        else:
            key_set = key
        key_tuple = tuple(key_set)
        if key_tuple in self.dic:
            del self.dic[key_tuple]
            return True
        else:
            return False
        
    def find(self, key) -> bool:
        assert isinstance(key, set) or isinstance(key, AVar) or isinstance(key, ChannelRole)
        if isinstance(key, AVar):
            key_set = set()
            key_set.add(key)
        elif isinstance(key, ChannelRole):
            key_set = set()
            key_set.add(key)
        else:
            key_set = key
        key_tuple = tuple(key_set)
        if key_tuple in self.dic:
            return True
        else:
            return False
        
    def get(self, key):
        assert isinstance(key, set) or isinstance(key, Expr)
        if isinstance(key, AConst):
            type_str = str(type(key.value))
            words = type_str.split('\'')
            return BType(words[1])
        elif isinstance(key, AVar):
            key_set = set()
            key_set.add(key)
        elif isinstance(key, ChannelRole):
            key_set = set()
            key_set.add(key)
        else:
            key_set = key
        key_tuple = tuple(key_set)
        return self.dic[key_tuple]
    
    def get_ch_vars(self):
        return self.ch_vars
    
    def add_func_paras(self, name, type_list):
        if name not in self.func_paras:
            self.func_paras[name] = type_list
        else:
            assert self.func_paras[name] == type_list

    def get_func_paras(self, name):
        assert name in self.func_paras
        return self.func_paras[name]