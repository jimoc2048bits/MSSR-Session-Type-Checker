import math
from decimal import Decimal
from fractions import Fraction
from typing import Dict, List, Optional, Tuple, Union, Set
import expr
import parser
from var import AConst, AVar, Expr, ChannelRole, Channel
import mpsc_calculus
import local_type

def select(context, statement) -> bool:
    assert isinstance(context, local_type.TypeContext)
    if not (isinstance(statement, mpsc_calculus.InternalChoice) and context.find(statement.channel)):
        return False
    lType = context.get(statement.channel)
    while isinstance(lType, local_type.RecLType):
        lType = local_type.recExpand(lType.cont, lType.flag, local_type.RecLType(lType.flag, lType.cont))
    if not (isinstance(lType, local_type.SendType) and lType.target == statement.target):
        return False
    assert (len(statement.comm_list) == 1)
    comm = statement.comm_list[0]
    key = None
    for lComm in lType.comm_set:
        if lComm[0] == comm[0][0]:
            key = lComm
            break
    if key == None:
        return False
    # Now key is a tuple(l_k, B_k).
    assert isinstance(key, tuple)
    assert isinstance(key[1], local_type.BType)
    if context.get(comm[0][1]) != key[1]:
        print(type(context.get(comm[0][1])))
        print(type(key[1]))
        return False
    elif isinstance(comm[0][1], AVar) or isinstance(comm[0][1], ChannelRole):
        if comm[0][1] in context.get_ch_vars():
            context.delete(comm[0][1])
    # if isinstance(key[1].type, local_type.LType):
    #     if not context.find(comm[0][1]):
    #         return False
    #     else:
    #         context.delete(comm[0][1])

    # print(comm[1])
    # print(key)
    # print(lType.comm_dict)
    context.add(statement.channel, lType.comm_dict[key])
    # print(context.dic)
    return typeSeqCheck(context, comm[1])    

def selectExist(context, statement) -> bool:
    assert isinstance(context, local_type.TypeContext)
    return False
def branch(context, statement) -> bool:
    assert isinstance(context, local_type.TypeContext)
    if not (isinstance(statement, mpsc_calculus.ExternalChoice) and context.find(statement.channel)):
        return False
    lType = context.get(statement.channel)
    while isinstance(lType, local_type.RecLType):
        lType = local_type.recExpand(lType.cont, lType.flag, local_type.RecLType(lType.flag, lType.cont))
    if not (isinstance(lType, local_type.RecvType) and lType.source == statement.source):
        return False
    assert (len(statement.comm_list) >= 1)
    for lComm in lType.comm_set:
        key = None
        for comm in statement.comm_list:
            if lComm[0] == comm[0][0]:
                key = comm
                break
        if key == None:
            return False
        # Now key is a tuple(l_k, B_k). incorrect
        assert isinstance(lComm, tuple)
        assert isinstance(lComm[1], local_type.BType)
        assert isinstance(comm[0][1], AVar)
        context_new = context
        context_new.add(statement.channel, lType.comm_dict[lComm])
        context_new.add(comm[0][1], lComm[1])
        if not typeSeqCheck(context_new, key[1]):
            return False
    return True
def exist(context, statement) -> bool:
    assert isinstance(context, local_type.TypeContext)
    if not (isinstance(statement, mpsc_calculus.MPSCExternalChoice) and context.find(statement.channel)):
        return False
    lType = context.get(statement.channel)
    while isinstance(lType, local_type.RecLType):
        lType = local_type.recExpand(lType.cont, lType.flag, local_type.RecLType(lType.flag, lType.cont))
    if not (isinstance(lType, local_type.MultiRecvType)):
        return False
    assert (len(statement.comm_list) >= 1)
    for lComm in lType.comm_set:
        key = None
        for comm in statement.comm_list:
            if lComm[0] == comm[0][0] and lComm[1] == comm[0][1]:
                key = comm
                break
        if key == None:
            return False
        # Now key is a tuple(l_k, B_k). incorrect
        assert isinstance(lComm, tuple)
        assert isinstance(lComm[2], local_type.BType)
        assert isinstance(comm[0][2], AVar)

        context_new = context
        context_new.add(statement.channel, lType.comm_dict[lComm])
        context_new.add(comm[0][2], lComm[2])
        if not typeSeqCheck(context_new, key[1]):
            return False
    return True
def inaction(context, statement) -> bool:
    assert isinstance(context, local_type.TypeContext)
    if not isinstance(statement, mpsc_calculus.Inaction):
        return False
    if len(context.dic) == 0:
        return True
    for key in context.dic:
        if isinstance(context.dic[key], local_type.LType) and not isinstance(context.dic[key], local_type.EndLType):
            print(context.dic[key])
            return False
    return True
def funcDef(context, statement) -> bool:
    assert isinstance(context, local_type.TypeContext)
    if not isinstance(statement, mpsc_calculus.FunctionDef):
        return False
    if not typeSeqCheck(context, statement.func_ctxt):
        return False
    func_ctxt = local_type.TypeContext()
    func_ctxt.func_paras = context.func_paras.copy()
    para_type = func_ctxt.get_func_paras(statement.name)
    assert len(para_type) == len(statement.para_list)
    for i in range(0, len(para_type)):
        func_ctxt.add(statement.para_list[i], para_type[i])
    if not typeSeqCheck(func_ctxt, statement.func_body):
        return False
    return True
def funcCall(context, statement) -> bool:
    assert isinstance(context, local_type.TypeContext)
    if not isinstance(statement, mpsc_calculus.FunctionCall):
        return False
    type_list = []
    for i in range(0, len(statement.para_list)):
        if isinstance(statement.para_list[i], (AVar, ChannelRole)) and not context.find(statement.para_list[i]):
            print(statement.para_list[i])
            print(context)
            return False
        else:
            type_list.append(context.get(statement.para_list[i]))
    context.add_func_paras(statement.name, type_list)
    return True
def typeSeqCheck(context, statement) -> bool:
    assert isinstance(context, local_type.TypeContext)
    assert isinstance(statement, mpsc_calculus.Statement)
    if isinstance(statement, mpsc_calculus.FunctionDef):
        return funcDef(context, statement)
    elif isinstance(statement, mpsc_calculus.FunctionCall):
        return funcCall(context, statement)
    elif isinstance(statement, mpsc_calculus.Inaction):
        return inaction(context, statement)
    elif isinstance(statement, mpsc_calculus.ExternalChoice):
        return branch(context, statement)
    elif isinstance(statement, mpsc_calculus.InternalChoice):
        return select(context, statement) or selectExist(context, statement)
    elif isinstance(statement, mpsc_calculus.MPSCExternalChoice):
        return exist(context, statement)
    else:
        return False 

def typeCheck(stt_list, ctxt_list):
    assert isinstance(stt_list, list) and isinstance(ctxt_list, list)
    assert len(stt_list) == len(ctxt_list)
    for i in range(0, len(stt_list)):
        if not typeSeqCheck(ctxt_list[i], stt_list[i]):
            print(stt_list[i])
            return False
    return True
