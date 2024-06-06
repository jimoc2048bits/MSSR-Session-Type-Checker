from typing import Dict, List, Optional, Tuple, Union, Set
from var import Channel, ChannelRole, Expr, AVar, AConst
from mpsc_calculus import Statement, Inaction, InternalChoice, ExternalChoice, MPSCExternalChoice
from comm_event import Event, MobEvent, History, Order, CommContext

def commTypeMerge(context_1: CommContext, context_2 : CommContext) -> CommContext:
    new_context = CommContext()
    new_context.setU.update(context_1.setU, context_2.setU)
    new_context.setM.update(context_1.setM, context_2.setM)
    new_context.setR.update(context_1.setR, context_2.setR)

    # Unify
    while True:
        if not new_context.unify():
            break
    return new_context

# def commInaction(statement:Statement) -> CommContext:
#     return CommContext()

def commSelect(statement:InternalChoice, ch_vars: set) -> CommContext:
    assert (len(statement.comm_list) == 1)
    comm = statement.comm_list[0]
    cont_context = commTypeInfer(comm[1], ch_vars)
    ret_context = CommContext()
    new_event = Event(Channel(statement.channel, statement.target), comm[0][0], 1)
    ret_context.setU.add(new_event)
    ret_context.setM.update(cont_context.setM)
    ret_context.incMEnd(Channel(statement.channel, statement.target), 1)
    if isinstance(comm[0][1], ChannelRole) or (isinstance(comm[0][1], AVar) and comm[0][1] in ch_vars):
        new_mob_event = MobEvent(new_event, comm[0][1], History())
        ret_context.setM.add(new_mob_event)
    ret_context.setR.update(cont_context.setR)
    ret_context.incREnd(Channel(statement.channel, statement.target), 1)
    for event in cont_context.setU:
        if new_event.channel != event.channel:
            ret_context.setR.add(Order(new_event, event))
    return ret_context
    

def commBranch(statement:ExternalChoice, ch_vars: set) -> CommContext:
    ret_context = CommContext()
    for comm in statement.comm_list:
        cont_context = commTypeInfer(comm[1], ch_vars)
        new_event = Event(Channel(statement.channel, statement.source), comm[0][0], 1)
        ret_context.setU.add(new_event)
        ret_context.setM.update(cont_context.setM)
        ret_context.incMEnd(Channel(statement.channel, statement.source), 1)
        if isinstance(comm[0][1], AVar) and comm[0][1] in ch_vars:
            new_mob_event = MobEvent(new_event, comm[0][1], History())
            ret_context.setM.add(new_mob_event)
        ret_context.setR.update(cont_context.setR)
        ret_context.incREnd(Channel(statement.channel, statement.source), 1)
        for event in cont_context.setU:
            if new_event.channel != event.channel:
                ret_context.setR.add(Order(new_event, event))
    return ret_context

def commExist(statement:MPSCExternalChoice, ch_vars: set) -> CommContext:
    ret_context = CommContext()
    for comm in statement.comm_list:
        cont_context = commTypeInfer(comm[1], ch_vars)
        new_event = Event(Channel(statement.channel, comm[0][0]), comm[0][1], 1)
        ret_context.setU.add(new_event)
        ret_context.setM.update(cont_context.setM)
        ret_context.incMEnd(Channel(statement.channel, comm[0][0]), 1)
        if isinstance(comm[0][2], AVar) and comm[0][2] in ch_vars:
            new_mob_event = MobEvent(new_event, comm[0][2], History())
            ret_context.setM.add(new_mob_event)
        ret_context.setR.update(cont_context.setR)
        ret_context.incREnd(Channel(statement.channel, comm[0][0]), 1)
        for event in cont_context.setU:
            if new_event.channel != event.channel:
                ret_context.setR.add(Order(new_event, event))
    return ret_context

def commTypeInfer(statement:Statement, ch_vars: set) -> CommContext:
    assert isinstance(statement, Statement)
    if isinstance(statement, Inaction):
        return CommContext()
    elif isinstance(statement, ExternalChoice):
        return commBranch(statement, ch_vars)
    elif isinstance(statement, InternalChoice):
        return commSelect(statement, ch_vars)
    elif isinstance(statement, MPSCExternalChoice):
        return commExist(statement, ch_vars)
    else:
        raise NotImplementedError


def commSafeCheck(context : CommContext) -> bool:
    prefix_events = set()
    preds = dict()
    succs = dict()
    for order in context.setR:
        stan_left = order.left.getStandard()
        stan_right = order.right.getStandard()
        if stan_right not in preds:
            preds[stan_right] = set()
        preds[stan_right].add(stan_left)
        if stan_left not in succs:
            succs[stan_left] = set()
        succs[stan_left].add(stan_right)
        if stan_left not in preds:
            prefix_events.add(stan_left)
        prefix_events.discard(stan_right)

    while True:
        if len(prefix_events) == 0:
            if len(preds) == 0 and len(succs) == 0:
                return True
            else:
                for key in preds:
                    print(key)
                return False
        event = prefix_events.pop()
        if event in succs:
            for succ in succs[event]:
                preds[succ].remove(event)
                if len(preds[succ]) == 0:
                    prefix_events.add(succ)
                    preds.pop(succ)
            succs.pop(event)


def commCheck(stt_list, ctxt_list):
    assert isinstance(stt_list, list) and isinstance(ctxt_list, list)
    assert len(stt_list) == len(ctxt_list)
    mcomm = CommContext()
    for i in range(0, len(stt_list)):
        comm = commTypeInfer(stt_list[i], ctxt_list[i].get_ch_vars())
        mcomm = commTypeMerge(mcomm, comm)
    return commSafeCheck(mcomm)