from typing import Dict, List, Optional, Tuple, Union, Set
from var import Channel, ChannelRole, Expr, AConst, AVar
from mpsc_calculus import Statement, Inaction, InternalChoice, ExternalChoice, MPSCExternalChoice
from comm_event import Event, MobEvent, History, Order, CommContext
from local_type import TypeContext, BType, LType, RecvType, SendType, MultiRecvType, EndLType, mergeLocalType
from global_type import GType, EndGType, CommType, ExistCommType, projection
from type_check import typeCheck
from comm_type_check import commCheck, commTypeInfer, commSafeCheck, commTypeMerge

gType3 = CommType(ChannelRole("b"), ChannelRole("a"), [[tuple(("l3", BType("int"))), EndGType()]])
gType2 = CommType(ChannelRole("d"), ChannelRole("c"), [[tuple(("l2", SendType(ChannelRole("a"), [[tuple(("l3", BType("int"))), EndLType()]]))), gType3]])
gType1 = CommType(ChannelRole("b"), ChannelRole("a"), [[tuple(("l1", BType("int"))), gType2]])
print(str(gType1))

ctxt1 = TypeContext()
ctxt1.add({ChannelRole("b")}, projection(gType1, {ChannelRole("b")}))
ctxt1.add({ChannelRole("d")}, projection(gType1, {ChannelRole("d")}))
ctxt2 = TypeContext()
ctxt2.add({ChannelRole("c")}, projection(gType1, {ChannelRole("c")}))
ctxt3 = TypeContext()
ctxt3.add({ChannelRole("a")}, projection(gType1, {ChannelRole("a")}))
print(str(ctxt1))
print(str(ctxt2))
print(str(ctxt3))

stt1_c = InternalChoice(ChannelRole("d"), ChannelRole("c"), [[tuple(("l2", ChannelRole("b"))), Inaction()]])
stt1 = InternalChoice(ChannelRole("b"), ChannelRole("a"), [[tuple(("l1", AConst(1))), stt1_c]])
stt2_c = InternalChoice(AVar("e"), ChannelRole("a"), [[tuple(("l3", AConst(2))), Inaction()]])
stt2 = ExternalChoice(ChannelRole("c"), ChannelRole("d"), [[tuple(("l2", AVar("e"))), stt2_c]])
stt3_c = ExternalChoice(ChannelRole("a"), ChannelRole("b"), [[tuple(("l3", AVar("y"))), Inaction()]])
stt3 = ExternalChoice(ChannelRole("a"), ChannelRole("b"), [[tuple(("l1", AVar("x"))), stt3_c]])

stts = [stt1, stt2, stt3]
ctxts = [ctxt1, ctxt2, ctxt3]
print(typeCheck(stts, ctxts))
print(commCheck(stts, ctxts))


