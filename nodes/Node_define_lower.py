import copy


class TransRefNode:
    def __init__(self, obj=None):
        if obj is not None:
            obj = None
        self.obj = obj

    def Find2(self, item):
        # p = TransRefNode()
        # p.obj = self.obj
        p = copy.copy(self)
        while p is not None:
            if p.obj.nod.obj.history == item.history and p.obj.nod.obj.context == item.context:
                break
            p = p.obj.nex2
        return p


class TransNode:
    def __init__(self, nod=None, occ2=None, nex2=None, impact_home=None, impact_away=None, eventids=None, vis2=None):
        if nod is not None:
            nod = None
        self.nod = nod
        if occ2 is None:
            occ2 = 0
        self.occ2 = occ2
        if nex2 is not None:
            nex2 = None
        self.nex2 = nex2
        if impact_home is None:
            impact_home = 0
        self.impact_home = impact_home
        if impact_away is None:
            impact_away = 0
        self.impact_away = impact_away
        if eventids is None:
            eventids = []
        self.eventids = eventids
        if vis2 is None:
            vis2 = 1
        self.vis2 = vis2
