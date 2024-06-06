import itertools
import mpsc_calculus
import local_type
from typing import Dict, List, Optional, Tuple, Union, Set
from var import Channel, ChannelRole, Expr

class Event:
    """communacating events."""
    def __init__(self, channel, label, index):
        self.channel = channel
        self.label = label
        self.index = index

    def __str__(self) -> str:
        return "(%s, %s, %s)" % (self.channel, self.label, self.index)
    
    def __repr__(self) -> str:
        return "(%s, %s, %s)" % (self.channel, self.label, self.index)
    
    def __eq__(self, value: object) -> bool:
        return (self.channel == value.channel and self.label == value.label and self.index == value.index)

    def __hash__(self) -> int:
        return hash(str(self))
    
    def indexInc(self, channel, num):
        if channel == self.channel:
            self.index += num

    def substituteRole(self, value, var):
        if self.channel.__role__ == var:
            self.channel.__role__ = value
        elif self.channel.__oppo__ == var:
            self.channel.__oppo__ = value

    def getStandard(self):
        return "(%s, %s, %s)" % (self.channel.getStandard(), self.label, self.index)

class Order:
    """Order between communacating events. Left occurs before right."""
    def __init__(self, left, right):
        assert isinstance(left, Event) and isinstance(right, Event) 
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return str(self.left) + "<" + str(self.right) 
    
    def __repr__(self) -> str:
        return str(self.left) + "<" + str(self.right) 
    
    def __eq__(self, value: object) -> bool:
        return (self.left == value.left and self.right == value.right)

    def __hash__(self) -> int:
        return hash(str(self))
    
    def indexInc(self, channel, num):
        self.left.indexInc(channel, num)
        self.right.indexInc(channel, num)

    def indexIncHis(self, history):
        assert isinstance(history, History)
        if self.left.channel in history:
            self.left.indexInc(self.left.channel, history.get(self.left.channel))
        if self.right.channel in history:
            self.right.indexInc(self.right.channel, history.get(self.right.channel)) 

    def substituteRole(self, value, var):
        self.left.substituteRole(value, var)
        self.right.substituteRole(value, var)
    
class History:
    """Dictionary, key -> channel, value -> times of events on this channel before moved."""
    def __init__(self):
        self.dic = dict()

    def indexInc(self, channel, num):
        if channel in self.dic:
            self.dic[channel] += num
        else:
            self.dic[channel] = num

    def __str__(self) -> str:
        return str(self.dic)
    
    def __repr__(self) -> str:
        return str(self.dic)
    
    def __eq__(self, value: object) -> bool:
        return self.dic == value.dic
    
    def __contains__(self, item):
        for key, value in self.dic.items():
            if key == item:
                return True
        return False
    
    def get(self, item):
        for key, value in self.dic.items():
            if key == item:
                return value
    
    def copy(self):
        ret = History()
        for key in self.dic:
            ret.dic[key.copy()] = self.dic[key]
        return ret    

    def substituteRole(self, value, var):
        new_dic = self.dic.copy()
        for ch in new_dic:
            if ch.__role__ == var:
                ch.__role__ = value
            elif ch.__oppo__ == var:
                ch.__oppo__ = value
        self.dic = new_dic

        # if var in new_dic:
        #     new_dic[value] = self.dic[var]
        #     print(new_dic)
        #     print(1)
        #     del new_dic[var]
        #     print(new_dic)
        #     self.dic = new_dic
    
class MobEvent:
    """communacating events with mobility."""
    def __init__(self, event, mChannel, history):
        self.event = event
        self.mChannel = mChannel
        self.history = history

    def __str__(self) -> str:
        return "m(%s, %s, %s)" % (self.event, self.mChannel, self.history)
    
    def __repr__(self) -> str:
        return "m(%s, %s, %s)" % (self.event, self.mChannel, self.history)
    
    def __eq__(self, value: object) -> bool:
        return (self.event == value.event and self.mChannel == value.mChannel and self.history == value.history)

    def __hash__(self) -> int:
        return hash(str(self))

    def indexInc(self, channel, num):
        if channel == self.event.channel:
            self.event.indexInc(channel, num)
        elif self.mChannel == channel.__role__:
            self.history.indexInc(channel, num)

    def substituteRole(self, value, var):
        self.event.substituteRole(value, var)
        if self.mChannel == var:
            self.mChannel = value
        self.history.substituteRole(value, var)


class CommContext:
    def __init__(self):
        self.setU = set()
        self.setM = set()
        self.setR = set()

    def __str__(self) -> str:
        return "Context[U = %s, M = %s, R = %s]" % (self.setU, self.setM, self.setR)
    
    def __repr__(self) -> str:
        return "Context[U = %s, M = %s, R = %s]" % (self.setU, self.setM, self.setR)
    
    def __eq__(self, value: object) -> bool:
        return (self.setU == value.setU and self.setM == value.setM and self.setR == value.setR)

    def __hash__(self) -> int:
        return hash(str(self))

    def incREnd(self, channel, num):
        for rel in self.setR:
            rel.indexInc(channel, num)

    def incRHis(self, history):
        for rel in self.setR:
            rel.indexIncHis(history)

    def incMEnd(self, channel, num):
        for mEvent in self.setM:
            mEvent.indexInc(channel, num)

    def incMHis(self, history):
        for channel, index in history.dic.items():
            self.incMEnd(channel, index)

    def substituteRole(self, value, var):
        for mEvent in self.setM:
            mEvent.substituteRole(value, var)
        for rel in self.setR:
            rel.substituteRole(value, var)

    def unify(self) -> bool:
        if len(self.setM) == 0:
            return False
        
        for me1 in self.setM:
            for me2 in self.setM:
                if me1 != me2 and me1.event.getStandard() == me2.event.getStandard() and (isinstance(me1.mChannel, ChannelRole) or isinstance(me2.mChannel, ChannelRole)):
                    new_setM = set()
                    for me in self.setM:
                        if me != me1 and me != me2:
                            new_setM.add(me)
                    self.setM = new_setM
                    if isinstance(me1.mChannel, ChannelRole):
                        mR = me1
                        mV = me2
                    else:
                        mV = me1
                        mR = me2

                    hisA = mR.history
                    hisB = hisA.copy()
                    hisB.substituteRole(mV.mChannel, mR.mChannel)
                    self.incMHis(hisB)
                    self.incRHis(hisB)
                    self.substituteRole(mR.mChannel, mV.mChannel)
                    return True

        # for com in itertools.combinations(self.setM, 2):
        #     if com[0].event.getStandard() == com[1].event.getStandard() and (isinstance(com[0].mChannel, ChannelRole) or isinstance(com[1].mChannel, ChannelRole)):
        #         print(com)
        #         print(self.setM)
        #         self.setM.discard(com[0])
        #         print(com)
        #         print(self.setM)
        #         print(com[1] == self.setM.pop())
        #         self.setM.discard(com[1])
        #         print(com)
        #         print(self.setM)
        #         if isinstance(com[0].mChannel, ChannelRole):
        #             mR = com[0]
        #             mV = com[1]
        #         else:
        #             mV = com[0]
        #             mR = com[1]

        #         self.substituteRole(mR.mChannel, mV.mChannel)
        #         print(mR.history)
        #         self.incMHis(mR.history)
        #         self.incRHis(mR.history)
        #         return True
        return False



