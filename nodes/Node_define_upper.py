import scipy
import copy
from Node_define_lower import TransRefNode


class StateRefNode:
    """
    class static variables
    """
    allEvents = []  # TODO: it is ugly, remove
    allHome = []
    cluster = []

    def __init__(self, obj=None):
        if obj is not None:
            obj = None
        self.obj = obj

        # # record the eventId
        # self.allEvents = []
        # # record if it's a home team
        # self.allHome = []
        # self.m = 1
        # cluster = scipy.io.loadmat('../dataset/cluster.mat')
        # cluster = cluster['cluster']
        # self.cluster = cluster[0]

        # record the eventId
        # self.allEvents = allEvents
        # record if it's a home team
        # self.allHome = allHome
        self.m = 1
        # self.cluster = cluster

    def compute_impact(self, m, t, if_probability=False):
        """
        compute the impact,
        impact is defined in the transition node
        :param m: visit indicator
        :param t: team 1/0
        :return: nothing
        """
        if if_probability:
            print 'applying probability'
        if self.obj.vis == m:
            self.obj.vis = -m
            # print self.obj.history
            # p = TransRefNode()
            p = copy.copy(self.obj.succ)  # p is refNode2
            if t == 0:  # home team
                while p is not None:
                    if if_probability:
                        q_front = p.obj.nod.obj.q / (p.obj.nod.obj.q + p.obj.nod.obj.q1) if (
                                                                                            p.obj.nod.obj.q + p.obj.nod.obj.q1) > 0 else 0
                        q_back = self.obj.q / (self.obj.q + self.obj.q1) if (self.obj.q + self.obj.q1) > 0 else 0
                        p.obj.impact_home = q_front - q_back
                    else:
                        p.obj.impact_home = p.obj.nod.obj.q - self.obj.q  # impact is difference between two q values between nodes
                    print 'impact', p.obj.impact_home
                    p = p.obj.nex2
            else:  # away team
                while p is not None:
                    if if_probability:
                        q1_front = p.obj.nod.obj.q1 / (p.obj.nod.obj.q + p.obj.nod.obj.q1) if (
                                                                                            p.obj.nod.obj.q + p.obj.nod.obj.q1) > 0 else 0
                        q1_back = self.obj.q1 / (self.obj.q + self.obj.q1) if (self.obj.q + self.obj.q1) > 0 else 0
                        p.obj.impact_away = q1_front - q1_back
                    else:
                        p.obj.impact_away = p.obj.nod.obj.q1 - self.obj.q1
                    print 'impact_away', p.obj.impact_away
                    p = p.obj.nex2
            p = self.obj.succ
            while p is not None:
                p.obj.nod.compute_impact(m, t)
                p = p.obj.nex2

    def impact_calculate_v0(self, m):
        if self.obj.vis == m:
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ  # TODO: could be a mistake
            while p is not None:
                print 'impact_away %f' % (p.obj.impact_away)
                print 'impact_home %f' % (p.obj.impact_home)
                p.obj.nod.impact_calculate_v0(m)
                p = p.obj.nex2

    def impact_calculate_v1(self, m, t):
        """
        The same structure as visit(),  but iterable
        :param m: visit indicator
        :param t: team 1/0
        :return: nothing
        """
        if self.obj.vis == m:  # if not visited, visited it
            self.obj.vis = -m
            # print self.obj.history
            # p = refNode2()
            p = self.obj.succ  # TODO: could be a mistake
            if t == 0:
                while p is not None:
                    p.obj.impact_home = p.obj.nod.obj.q - self.obj.q  # Q(s,a) - V(s),
                    print 'impact_home', p.obj.impact_home
                    p = p.obj.nex2
            else:
                while p is not None:
                    p.obj.impact_away = p.obj.nod.obj.q1 - self.obj.q1
                    print 'impact_away', p.obj.impact_away
                    p = p.obj.nex2
            p = self.obj.succ
            while p is not None:
                p.obj.nod.impact_calculate_v1(m, t)
                p = p.obj.nex2

    def impact_calculate_v2(self, m, ev, cl, t):
        sum0 = 0.0
        count = 0.0
        if self.obj.vis == m:
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ  # TODO: could be a mistake
            while p is not None:
                eventIds = p.obj.eventids
                for i in eventIds:
                    if i > 0:
                        temp = self.allEvents[i]
                        if temp['name'] == ev and self.cluster[i] == cl and t == 0:
                            sum0 = sum0 + p.obj.impact_home
                        if temp['name'] == ev and self.cluster[i] == cl and t == 1:
                            sum0 = sum0 + p.obj.impact_away
                        count += 1
                p = p.obj.nex2
            p = self.obj.succ
            while (p != None):
                (sum1, count1) = p.obj.nod.visit1(m, ev, cl, t)
                sum0 = sum1 + sum0
                count = count1 + count
                p = p.obj.nex2
        return sum0, count

    def impact_calculate_v3(self, m, player):
        sum0 = 0.0
        count = 0.0
        if self.obj.vis == m:
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ  # TODO: could be a mistake
            while p is not None:
                evIds = p.obj.eventids
                for i in evIds:
                    if i > 0:
                        # temp = self.allevents[i]
                        temp = self.allEvents[i]
                        # if (temp['playerId'] == player and self.allhome[i] == 1):
                        if temp['playerId'] == player and self.allHome[i] == 1:
                            sum0 = sum0 + p.obj.impact_home
                            count += 1.0
                        # if (temp['playerId'] == player and self.allhome[i] == 0):
                        if temp['playerId'] == player and self.allHome[i] == 0:
                            sum0 = sum0 + p.obj.impact_away
                            count += 1.0

                p = p.obj.nex2
            p = self.obj.succ
            while p is not None:
                (sum1, count1) = p.obj.nod.impact_calculate_v3(m, player)
                sum0 = sum1 + sum0
                count = count1 + count
                p = p.obj.nex2
        return sum0, count

    def impact_calculate_v4(self):
        """
        output all the states information
        :return: notrhing
        """
        if self.obj.vis == self.m:
            self.obj.vis = -self.m
            # p = refNode2()
            p = self.obj.succ  # TODO: could be a mistake
            print "id:%06d" % self.obj.stateid, ' context:[goal differential:%i' % self.obj.context[0], 'period:%i' % \
                                                                                                        self.obj.context[
                                                                                                            1], 'manpower:',
            if self.obj.context[2] == 0:
                print 'evenStrength]',
            if self.obj.context[2] == 1:
                print 'shortHanded]',
            if self.obj.context[2] == -1:
                print 'powerPlay]',
            if self.obj.context[2] == 2:
                print 'none]',
            if self.obj.history is not None:
                print ' history:%s' % self.obj.history,
            else:
                print ' history:none',
            print ' q_home:%.5f' % self.obj.q, ' q_away:%.5f' % self.obj.q1, ' r_home:%i' % self.obj.reward, ' r_away:%i' % self.obj.rewardAway, ' occurrence:%i' % self.obj.occ, ' \n    next nodes:'
            while p is not None:
                print "        id:%06d" % p.obj.nod.obj.stateid,
                eventIds = p.obj.eventids
                evid = eventIds[0]

                # temp = self.allevents[evid]
                temp = StateRefNode.allEvents[evid]
                temp = temp['name']

                rr = str(temp[0][0][0])
                # if self.allhome[evid] == 1:
                if StateRefNode.allHome[evid] == 1:
                    rr += '-home'
                else:
                    rr += '-away'
                # rr = rr + '-cluster' + str(self.cluster[evid])
                rr = rr + '-cluster' + str(StateRefNode.cluster[evid])
                print ' event:%s' % rr,

                print ' transition_occurrence:%i' % p.obj.occ2, ' impact_home:%.5f' % p.obj.impact_home, ' impact_away:%.5f' % p.obj.impact_away,
                p = p.obj.nex2
                print ''
            p = self.obj.succ
            while p is not None:
                p.obj.nod.impact_calculate_v4()
                p = p.obj.nex2

    def visit1(self, m, ev, cl, t):
        sum0 = 0.0
        count = 0.0
        if self.obj.vis == m:
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ  # TODO: could be a mistake
            while p is not None:
                evids = p.obj.eventids
                for i in evids:
                    if i > 0:
                        temp = self.allEvents[i]
                        if temp['name'] == ev and self.cluster[i] == cl and t == 0:
                            sum0 = sum0 + p.obj.impact_home
                        if temp['name'] == ev and self.cluster[i] == cl and t == 1:
                            sum0 = sum0 + p.obj.impact_away
                        count += 1
                p = p.obj.nex2
            p = self.obj.succ
            while (p != None):
                (sum1, count1) = p.obj.nod.visit1(m, ev, cl, t)
                sum0 = sum1 + sum0
                count = count1 + count
                p = p.obj.nex2
        return (sum0, count)

    def visit4(self, m, ev, cl):
        sum0 = 0.0
        count = 0.0
        if (self.obj.vis == m):
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ  # TODO: could be a mistake
            while (p != None):
                evids = p.obj.eventids
                for i in evids:
                    if (i > 0):
                        temp = self.allEvents[i]
                        if (temp['name'] == ev and self.cluster[i] == cl):
                            if (self.allHome[i] == 1):
                                sum0 = sum0 + p.obj.nod.obj.q
                                # sum0 = sum0 + p.obj.nod.obj.q * p.obj.occ2
                            else:
                                sum0 = sum0 + p.obj.nod.obj.q1
                                # sum0 = sum0 + p.obj.nod.obj.q1 * p.obj.occ2
                            count = count + 1

                p = p.obj.nex2
            p = self.obj.succ
            while (p != None):
                (sum1, count1) = p.obj.nod.visit4(m, ev, cl)
                sum0 = sum1 + sum0
                count = count1 + count
                p = p.obj.nex2
        return (sum0, count)

    def visit5(self, m, player):
        sum0 = 0.0
        count = 0.0
        if (self.obj.vis == m):
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ  # TODO: could be a mistake
            while (p != None):
                evids = p.obj.eventids
                for i in evids:
                    if (i > 0):
                        temp = self.allEvents[i]
                        if (temp['playerId'] == player and self.allHome[i] == 1):
                            sum0 = sum0 + p.obj.impact_home
                            count = count + 1.0
                        if (temp['playerId'] == player and self.allHome[i] == 0):
                            sum0 = sum0 + p.obj.impact_away
                            count = count + 1.0

                p = p.obj.nex2
            p = self.obj.succ
            while (p != None):
                (sum1, count1) = p.obj.nod.impact_calculate_v3(m, player)
                sum0 = sum1 + sum0
                count = count1 + count
                p = p.obj.nex2
        return (sum0, count)

    def value_iteration(self, number, c, m, team):  # c is the threshold of the error
        cv = 0.0  # current value?
        lv = 0.0  # last value?
        for i in range(number):  # number of iterations
            cv = self.dynamic_programming(m, cv, team, 0, scale=1.2)
            er = (cv - lv) / cv  # calculate the error, current value - last value?
            print 'cv is' + str(cv)
            print 'iteration %i' % (i + 1), 'value %.10f' % lv, 'error %.12f' % er
            # print 'iteration %i' % (i + 1), 'value %.10f' % lv

            if er < c:
                break
            lv = cv
            cv = 0.0
            m = -m

    def reset_nodes(self):
        """
        set the all the visited Node to unvisited
        :return: nothing
        """
        if self.obj.vis == -1:
            self.obj.vis = 1
            # p = refNode2()
            p = self.obj.succ
            while p is not None:
                p.obj.nod.reset_nodes()
                p = p.obj.nex2

    def visit6(self, m=1):
        """
        output all the state information
        :param m: visit indicator
        :return: nothing
        """
        if self.obj.vis == m:
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ
            print "id:%06d" % self.obj.stateid, ' context:[goal differential:%i' % self.obj.context[0], 'period:%i' % \
                                                                                                        self.obj.context[
                                                                                                            1], 'manpower:',
            if self.obj.context[2] == 0:
                print 'evenStrength]',
            if self.obj.context[2] == 1:
                print 'shortHanded]',
            if self.obj.context[2] == -1:
                print 'powerPlay]',
            if self.obj.context[2] == 2:
                print 'none]',
            if None != self.obj.history:
                print ' history:%s' % self.obj.history,
            else:
                print ' history:none',
            print ' q_home:%.5f' % self.obj.q, ' q_away:%.5f' % self.obj.q1, ' r_home:%i' % self.obj.reward, ' r_away:%i' % self.obj.rewardAway, ' occurrence:%i' % self.obj.occ, ' \n    next nodes:'
            while p is not None:
                print "        id:%06d" % p.obj.nod.obj.stateid,
                evids = p.obj.eventids
                evid = evids[0]

                # temp = self.allEvents[evid]
                temp = StateRefNode.allEvents[evid]
                temp = temp['name']

                rr = str(temp[0][0][0])
                # if self.allHome[evid] == 1:
                if StateRefNode.allHome[evid] == 1:
                    rr += '-home'
                else:
                    rr += '-away'
                # rr = rr + '-cluster' + str(self.cluster[evid])
                rr = rr + '-cluster' + str(StateRefNode.cluster[evid])
                print ' event:%s' % rr,

                print ' transition_occurrence:%i' % p.obj.occ2, ' impact_home:%.5f' % p.obj.impact, ' impact_away:%.5f' % p.obj.impact_away,
                p = p.obj.nex2
                print ''
            p = self.obj.succ
            while p is not None:
                p.obj.nod.impact_calculate_v4()
                p = p.obj.nex2

    def visit7(self, m=1):
        if self.obj.vis == m:
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ
            while (p != None):
                for i in p.obj.eventids:
                    print "%06d,%06d,%d" % (self.obj.stateid, p.obj.nod.obj.stateid, i)
                p = p.obj.nex2
            p = self.obj.succ
            while (p != None):
                p.obj.nod.visit7()
                p = p.obj.nex2

    def visit0(self, m):
        if (self.obj.vis == m):
            self.obj.vis = -m
            # p = refNode2()
            p = self.obj.succ
            while (p is not None):
                print 'impact_away %f' % (p.obj.impact_away)
                print 'impact_home %f' % (p.obj.impact_home)
                p.obj.nod.impact_calculate_v0(m)
                p = p.obj.nex2

    def dynamic_programming(self, m, cv, t, r_c, scale=1.0):  # cv is current value?
        """
        search all the relevant states to compute the cv(accumulate values), complete a step of value iteration
        The only function has reward
        :type scale: object
        :param m:
        :param cv:
        :param t:
        :param t: recursive count
        :return:
        """

        if self.obj.vis == m:  # if it is not visited, set it to visited
            self.obj.vis = -m
            if (self.obj.home_reward == 1 and t == 0) or (  # if the node represent score
                            self.obj.away_reward == 1 and t == 1):  # r is reward?, r for the home team and r1 for the remote team

                if t == 0:
                    # print "reward home is 1"
                    self.obj.q = 1.0  # q is q value? if reward is 1, set q to 1
                else:
                    # print "reward home is 1"
                    self.obj.q1 = 1.0
                cv += 1
            else:
                cc = 0.0
                u = self.obj.succ  # what's the difference between the succ and nex2? ans: succ point to refNode2 while nex point to refNode
                local_count = 0
                while u is not None:
                    local_count += 1
                    if t == 0:
                        cc = (u.obj.nod.obj.q) * (u.obj.occ2) + cc  # calculate the occurrence Occ(s,a,s')*V(s')
                    else:
                        cc = (u.obj.nod.obj.q1) * (u.obj.occ2) + cc
                    u = u.obj.nex2
                # print local_count
                if t == 0:
                    # compute the v for each state, here q is value
                    self.obj.q = self.obj.home_reward + scale * cc / self.obj.occ  # calculate R(s,a)+ sum(s,a,s') Occ(s,a,s')*Value(s')/Occ(s,a)
                    cv = cv + abs(self.obj.q)

                else:
                    self.obj.q1 = self.obj.away_reward + scale * cc / self.obj.occ
                    cv = cv + abs(self.obj.q1)

            u = self.obj.succ
            while u is not None:  # if the model has more state, go on
                r_c += 1
                # print 'r_c' + str(r_c)
                cv = u.obj.nod.dynamic_programming(m, cv, t, r_c, scale)
                u = u.obj.nex2
        return (cv)

    def Add(self, item):
        if self.obj is None:
            self.obj = item.obj
            return
        else:
            p = StateRefNode()
            p.obj = self.obj
            while p.obj.nex is not None:
                p = p.obj.nex
            p.obj.nex = item

    def Find(self, item):
        # p = RefNode()
        p = copy.copy(self)
        while p is not None:
            if p.obj.history == item.history and p.obj.context == item.context:
                break
            p = p.obj.nex
        return p


class StateNode:
    def __init__(self, history=None, context=None, succ=None, occ=None, reward=None, q=None, rewardAway=None, q1=None,
                 nex=None,
                 vis=None, stateid=None):
        # global counterid
        # if stateid == None:
        # stateid = counterid
        # counterid = counterid + 1
        if stateid is None:
            stateid = -1

        if history is not None:
            history = None
        if context is None:
            context = None
        if nex is not None:
            nex = None
        if vis is None:
            vis = 1
        if succ is not None:
            succ = None
        if occ is None:
            occ = 0
        if reward is None:
            reward = 0
        if q is None:
            q = 0.0
        if rewardAway is None:
            rewardAway = 0
        if q1 is None:
            q1 = 0.0

        self.stateid = stateid

        self.history = history
        self.context = context
        self.succ = succ
        self.occ = occ
        self.home_reward = reward
        self.q = q
        self.away_reward = rewardAway
        self.q1 = q1
        self.nex = nex
        self.vis = vis
