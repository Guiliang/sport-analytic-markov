import copy


class RefNodeTree:
    def __init__(self, obj=None):
        if obj is not None:
            obj = None
        self.obj = obj

    def add_tree(self, itemTree):
        """
        add the new RefNodeTree
        :param itemTree: a new RefNodeTree
        :return: nothing
        """
        # p = RefNodeTree()
        if self.obj is None:
            self.obj = itemTree.obj

        else:
            # p.obj = self.obj
            p = self
            while p.obj.nex is not None:
                p = p.obj.nex
            p.obj.nex = itemTree

    def find_tag(self, tag2):
        """
        find the RefNodeTree according to the tag2
        :param tag2: form like "pass-home-cluster3"
        :return: the RefNodeTree
        """
        # p = RefNodeTree()
        # p.obj = self.obj
        p = copy.copy(self)
        if p.obj is None:
            return None
        while p is not None:
            if p.obj.tag == tag2:
                return p
            p = p.obj.nex
        return None


class NodeTree:
    def __init__(self, tag=None, info=None, nex=None):
        """
        
        :param tag: action-team-cluster
        :param info: ref_node
        :param nex: the next ref_node_tree
        """
        if tag is None:
            tag = 0
        self.tag = tag
        self.info = info
        # self.child = child  # TODO: what it is?
        self.nex = None
