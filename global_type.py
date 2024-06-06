import mpsc_calculus
import local_type
from typing import Dict, List, Optional, Tuple, Union, Set

class GType:
    """Type."""
    def __init__(self):
        self.type = None

    def get_vars(self) -> Set[str]:
        raise NotImplementedError

    def get_fun_names(self) -> Set[str]:
        return NotImplementedError

class CommType(GType):
    def __init__(self, source, target, comm_list):
        """comm_list is a set of (label, type, cont)."""
        super(CommType, self).__init__()
        self.type = "comm type"
        self.source = source
        self.target = target
        self.comm_set = set()
        self.comm_dict = dict()

        for comm in comm_list:
            assert isinstance(comm[0][1], local_type.BType)
            assert isinstance(comm[1], GType)
            assert comm[0] not in self.comm_set
            self.comm_set.add(comm[0])
            self.comm_dict[comm[0]] = comm[1]

    def __repr__(self):
        cont_str = ""
        for comm in self.comm_set:
            if cont_str != "":
                cont_str += ","
            cont_str += "%s(%s).%s" % (comm[0], comm[1], self.comm_dict[comm])
        return "%s -> %s:{ %s }" % (self.source, self.target, cont_str)
    
    def __eq__(self, other) -> bool:
        return self.type == other.type and self.source == other.source and self.target == other.target and self.comm_set == other.comm_set

    def __str__(self):
        cont_str = ""
        for comm in self.comm_set:
            if cont_str != "":
                cont_str += ","
            cont_str += "%s(%s).%s" % (comm[0], comm[1], self.comm_dict[comm])
        return "%s -> %s:{ %s }" % (self.source, self.target, cont_str)
    
    def get_fun_names(self):
        return set()

class ExistCommType(GType):
    def __init__(self, target, comm_list):
        """comm_list is a set of (source, label, type, cont)."""
        super(ExistCommType, self).__init__()
        self.type = "multi recv type"
        self.source = set()
        self.target = target
        self.comm_set = set()
        self.comm_dict = dict()

        for comm in comm_list:
            assert isinstance(comm[0][2], local_type.BType)
            assert isinstance(comm[1], GType)
            assert comm[0] not in self.comm_set
            self.source.add(comm[0])
            self.comm_set.add(comm[0])
            self.comm_dict[comm[0]] = comm[1]

    def __repr__(self):
        return "[exist comm type:%s, (%s)];" % (self.target, self.comm_set)
    
    def __eq__(self, other) -> bool:
        return self.type == other.type and self.target == other.target and self.comm_set == other.comm_set

    def __str__(self):
        return "[exist comm type:%s, (%s)];" % (self.target, self.comm_set)
    
    def get_fun_names(self):
        return set()
    
class RecGType(GType):
    def __init__(self, flag, cont):
        """flag is a string conrresponding to rec call."""
        super(RecGType, self).__init__()
        assert isinstance(flag, str)
        assert isinstance(cont, GType)
        self.type = "recursive global type"
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
    
class RecCallGType(GType):
    def __init__(self, flag):
        """flag is a string conrresponding to rec call."""
        super(RecCallGType, self).__init__()
        assert isinstance(flag, str)
        self.type = "recursive call global type"
        self.flag = flag

    def __repr__(self):
        return "%s" % self.flag
       
    def __eq__(self, other) -> bool:
        return self.flag == other.flag

    def __str__(self):
        return "%s" % self.flag
    
    def get_fun_names(self):
        return set()
    
class EndGType(GType):
    def __init__(self):
        super(EndGType, self).__init__()
        self.type = "global end type"

    def __repr__(self):
        return "[end]"
    
    def __eq__(self, other) -> bool:
        return self.type == other.type

    def __str__(self):
        return "[end]"
    
    def get_fun_names(self):
        return set()
    
def projection(gType, roles) -> local_type.LType:
    assert isinstance(gType, GType) and isinstance(roles, Set)
    if isinstance(gType, CommType):
        if len(roles) == 1 and gType.source in roles:
            comm_list = []
            for comm in gType.comm_set:
                comm_list.append([comm, projection(gType.comm_dict[comm], roles)])
            return local_type.SendType(gType.target, comm_list)
        elif len(roles) == 1 and gType.target in roles:
            comm_list = []
            for comm in gType.comm_set:
                comm_list.append((comm, projection(gType.comm_dict[comm], roles)))
            return local_type.RecvType(gType.source, comm_list)
        else:
            merge_type = None
            for comm in gType.comm_set:
                if merge_type == None:
                    merge_type = projection(gType.comm_dict[comm], roles)
                else:
                    merge_type = local_type.mergeLocalType(merge_type, projection(gType.comm_dict[comm], roles)) 
            return merge_type
    elif isinstance(gType, ExistCommType):
        if roles == gType.source:
            comm_list = []
            for comm in gType.comm_set:
                comm_list.append((comm, projection(gType.comm_dict[comm], roles)))
            return local_type.SendType(gType.target, comm_list)
        elif len(roles) == 1 and gType.target in roles:
            comm_list = []
            for comm in gType.comm_set:
                comm_list.append((comm, projection(gType.comm_dict[comm], roles)))
            return local_type.MultiRecvType(comm_list)
        else:
            merge_type = None
            for comm in gType.comm_set:
                if merge_type == None:
                    merge_type = projection(gType.comm_dict[comm], roles)
                else:
                    merge_type = local_type.mergeLocalType(merge_type, projection(gType.comm_dict[comm], roles)) 
            return merge_type
    elif isinstance(gType, RecGType):
        return local_type.RecLType(gType.flag, projection(gType.cont, roles))
    elif isinstance(gType, RecCallGType):
        return local_type.RecCallLType(gType.flag)
    elif isinstance(gType, EndGType):
        return local_type.EndLType()
    

# test_type_1 = CommType("a", "b", [[tuple(("l1", local_type.BType("Real"))), EndGType()]])
# test_type_2 = CommType("a", "b", [[tuple(("l2", local_type.BType("Real"))), test_type_1]])

# print(test_type_2)
# role_a = set()
# role_a.add("a")
# test_local_a = projection(test_type_2, role_a)
# print(test_local_a)

# test_type_3 = ExistCommType("a", [[tuple(("b", "l2", local_type.BType("Real"))), EndGType()], [tuple(("c", "l1", local_type.BType("Real"))), EndGType()]])

# print(test_type_3)
# test_local_a = projection(test_type_3, role_a)
# print(test_local_a)