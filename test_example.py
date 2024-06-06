from typing import Dict, List, Optional, Tuple, Union, Set
from var import Channel, ChannelRole, Expr, AConst, AVar
from mpsc_calculus import Statement, Inaction, InternalChoice, ExternalChoice, MPSCExternalChoice
from comm_event import Event, MobEvent, History, Order, CommContext
from local_type import TypeContext, BType, LType, RecvType, SendType, MultiRecvType, EndLType, mergeLocalType
from global_type import GType, EndGType, CommType, ExistCommType, projection
from type_check import typeCheck
from comm_type_check import commCheck, commTypeInfer, commSafeCheck, commTypeMerge

gType1 = CommType(ChannelRole("p"), ChannelRole("q"), [[tuple(("l2", BType("int"))), EndGType()]])
gType = CommType(ChannelRole("r"), ChannelRole("p"), [[tuple(("l1", BType("str"))), gType1]])
print(str(gType))

ctxt1 = TypeContext()
ctxt1.add({ChannelRole("p")}, projection(gType, {ChannelRole("p")}))
ctxt2 = TypeContext()
ctxt2.add({ChannelRole("q")}, projection(gType, {ChannelRole("q")}))
ctxt2.add({ChannelRole("r")}, projection(gType, {ChannelRole("r")}))
print(str(ctxt1))
print(str(ctxt2))


p1_c = InternalChoice(ChannelRole("p"), ChannelRole("q"), [[tuple(("l2", AConst(1))), Inaction()]])
p1 = ExternalChoice(ChannelRole("p"), ChannelRole("r"), [[tuple(("l1", AVar("x"))), p1_c]])
p2_c = InternalChoice(ChannelRole("r"), ChannelRole("p"), [[tuple(("l1", AConst("test"))), Inaction()]])
p2 = ExternalChoice(ChannelRole("q"), ChannelRole("p"), [[tuple(("l2", AVar("y"))), p2_c]])

ps = [p1, p2]
ctxts = [ctxt1, ctxt2]

print(typeCheck(ps, ctxts))
print(commCheck(ps, ctxts))
