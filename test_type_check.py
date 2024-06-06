import math
from decimal import Decimal
from fractions import Fraction
from typing import Dict, List, Optional, Tuple, Union, Set
import expr
import parser
import mpsc_calculus
import local_type
from type_check import typeSeqCheck

# send

test_ctxt = local_type.TypeContext()
test_lType = local_type.SendType("b", [[tuple(("l", local_type.BType("Real"))), local_type.EndLType()]])
test_ctxt.add("a", test_lType)

test_stt0 = mpsc_calculus.InternalChoice("a", "b", [[tuple(("l", 1)), mpsc_calculus.Inaction()]])
print(typeSeqCheck(test_ctxt, test_stt0))

test_ctxt = local_type.TypeContext()
test_set = set()
test_set.add("a")
test_lType = local_type.SendType("b", [[tuple(("l", local_type.BType("Real"))), local_type.EndLType()]])
test_ctxt.add(test_set, test_lType)

test_stt1 = mpsc_calculus.InternalChoice(test_set, "c", [[tuple(("l", 1)), mpsc_calculus.Inaction()]])
print(typeSeqCheck(test_ctxt, test_stt1))

test_ctxt = local_type.TypeContext()
test_set = set()
test_set.add("a")
test_lType = local_type.SendType("b", [[tuple(("l", local_type.BType("Real"))), local_type.EndLType()]])
test_ctxt.add(test_set, test_lType)

test_stt2 = mpsc_calculus.InternalChoice(test_set, "b", [[tuple(("l", 1)), test_stt0]])
print(typeSeqCheck(test_ctxt, test_stt2))

test_ctxt = local_type.TypeContext()
test_set = set()
test_set.add("a")
test_lType = local_type.SendType("b", [[tuple(("l", local_type.BType("Real"))), local_type.EndLType()]])
test_ctxt.add(test_set, test_lType)

test_stt3 = mpsc_calculus.InternalChoice(test_set, "b", [[tuple(("l1", 1)), mpsc_calculus.Inaction()]])
print(typeSeqCheck(test_ctxt, test_stt3))

# receive

test_ctxt = local_type.TypeContext()
test_set = set()
test_set.add("a")
test_lType = local_type.RecvType("b", [[tuple(("l", local_type.BType("Real"))), local_type.EndLType()], [tuple(("l2", local_type.BType("Real"))), local_type.EndLType()]])
test_ctxt.add(test_set, test_lType)

test_stt0 = mpsc_calculus.ExternalChoice(test_set, "b", [[tuple(("l", 1)), mpsc_calculus.Inaction()], [tuple(("l2", 1)), mpsc_calculus.Inaction()]])
print(typeSeqCheck(test_ctxt, test_stt0))

test_ctxt = local_type.TypeContext()
test_set = set()
test_set.add("a")
test_lType = local_type.RecvType("b", [[tuple(("l", local_type.BType("Real"))), local_type.EndLType()], [tuple(("l2", local_type.BType("Real"))), local_type.EndLType()]])
test_ctxt.add(test_set, test_lType)


test_stt1 = mpsc_calculus.ExternalChoice(test_set, "b", [[tuple(("l2", 1)), mpsc_calculus.Inaction()]])
print(typeSeqCheck(test_ctxt, test_stt1))

test_ctxt = local_type.TypeContext()
test_set = set()
test_set.add("a")
test_lType = local_type.RecvType("b", [[tuple(("l", local_type.BType("Real"))), local_type.EndLType()], [tuple(("l2", local_type.BType("Real"))), local_type.EndLType()]])
test_ctxt.add(test_set, test_lType)


test_stt2 = mpsc_calculus.ExternalChoice(test_set, "b", [[tuple(("l", 1)), mpsc_calculus.Inaction()], [tuple(("l2", 1)), mpsc_calculus.Inaction()], [tuple(("l3", 1)), mpsc_calculus.Inaction()]])
print(typeSeqCheck(test_ctxt, test_stt2))

test_ctxt = local_type.TypeContext()
test_set = set()
test_set.add("a")
test_lType = local_type.MultiRecvType([[tuple(("b", "l", local_type.BType("Real"))), local_type.EndLType()], [tuple(("c", "l2", local_type.BType("Real"))), local_type.EndLType()]])
test_ctxt.add(test_set, test_lType)


test_stt0 = mpsc_calculus.MPSCExternalChoice(test_set, [[tuple(("b", "l", 1)), mpsc_calculus.Inaction()], [tuple(("c", "l2", 1)), mpsc_calculus.Inaction()], [tuple(("d", "l3", 1)), mpsc_calculus.Inaction()]])
print(typeSeqCheck(test_ctxt, test_stt0))