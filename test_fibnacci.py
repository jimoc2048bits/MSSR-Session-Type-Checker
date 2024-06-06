from typing import Dict, List, Optional, Tuple, Union, Set
from var import Channel, ChannelRole, Expr, AConst, AVar
from mpsc_calculus import Statement, Inaction, InternalChoice, ExternalChoice, MPSCExternalChoice, FunctionCall, FunctionDef
from comm_event import Event, MobEvent, History, Order, CommContext
from local_type import TypeContext, BType, LType, RecvType, SendType, MultiRecvType, EndLType, RecCallLType, RecLType, mergeLocalType
from global_type import GType, EndGType, CommType, ExistCommType, RecGType, RecCallGType, projection
from type_check import typeCheck
from comm_type_check import commCheck, commTypeInfer, commSafeCheck, commTypeMerge

gType3 = CommType(ChannelRole("p"), ChannelRole("u"), [[tuple(("lc", BType("int"))), RecCallGType("t")]])
gType2 = CommType(ChannelRole("r"), ChannelRole("p"), [[tuple(("lk", BType("int"))), gType3]])
gType1 = CommType(ChannelRole("q"), ChannelRole("p"), [[tuple(("ld", BType("int"))), gType2]])
gType = RecGType("t", gType1)
print(str(gType))

ctxt1 = TypeContext()
ctxt1.add({ChannelRole("q")}, projection(gType, {ChannelRole("q")}))
ctxt2 = TypeContext()
ctxt2.add({ChannelRole("r")}, projection(gType, {ChannelRole("r")}))
ctxt3 = TypeContext()
ctxt3.add({ChannelRole("p")}, projection(gType, {ChannelRole("p")}))
ctxt4 = TypeContext()
ctxt4.add({ChannelRole("u")}, projection(gType, {ChannelRole("u")}))
print(str(ctxt1))
print(str(ctxt2))
print(str(ctxt3))
print(str(ctxt4))


p_data = FunctionDef("D", [AVar("d"), AVar("x")], InternalChoice(AVar("d"), ChannelRole("p"), [[tuple(("ld", AVar("x"))), FunctionCall("D", [AVar("d"), AVar("x")])]]), FunctionCall("D", [ChannelRole("q"), AConst(1)]))
p_key = FunctionDef("Ke", [AVar("k"), AVar("y")], InternalChoice(AVar("k"), ChannelRole("p"), [[tuple(("lk", AVar("y"))), FunctionCall("Ke", [AVar("k"), AVar("y")])]]), FunctionCall("Ke", [ChannelRole("r"), AConst(3)]))
p_kernel_2 = InternalChoice(AVar("d"), ChannelRole("u"), [[tuple(("lc", AVar("x"))), FunctionCall("K", [AVar("d")])]])
p_kernel_1 = ExternalChoice(AVar("d"), ChannelRole("r"), [[tuple(("lk", AVar("y"))), p_kernel_2]])
p_kernel = FunctionDef("K", [AVar("d")], ExternalChoice(AVar("d"), ChannelRole("q"), [[tuple(("ld", AVar("x"))), p_kernel_1]]), FunctionCall("K", [ChannelRole("p")]))
p_consumer = FunctionDef("C", [AVar("c")], ExternalChoice(AVar("c"), ChannelRole("p"), [[tuple(("lc", AVar("z"))), FunctionCall("C", [AVar("c")])]]), FunctionCall("C", [ChannelRole("u")]))


ps = [p_data, p_key, p_kernel, p_consumer]
ctxts = [ctxt1, ctxt2, ctxt3, ctxt4]

print(typeCheck(ps, ctxts))
# print(commCheck(ps, ctxts))
