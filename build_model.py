import sys

import pickle

sys.path.append('/Local-Scratch/PycharmProjects/sport-analytic-markov/')
import json
import sys
import os
from nodes.Node_define_upper import StateNode, StateRefNode
from nodes.Node_define_lower import TransNode, TransRefNode
from nodes.Node_define_Tree import NodeTree, RefNodeTree
from config.soccer_config import select_feature_setting
from model_tools.model_until import switch_mp
from generate_cluster.ap_cluster import APCluster


def init_nodes():
    init_node = StateNode()
    init_node.stateid = 0
    init_ref_node = StateRefNode()
    init_ref_node.obj = init_node

    init_node_tree = NodeTree()
    init_node_tree.info = init_ref_node
    init_ref_node_tree = RefNodeTree()
    init_ref_node_tree.obj = init_node_tree

    return init_node, init_ref_node, init_node_tree, init_ref_node_tree, 1


def build_tree(pre_ref_node, temp_ref_node_tree, hist, context, counterid, goal_home, goal_away, cluster_counter):
    """start building the model"""
    ref_node_tree_found = temp_ref_node_tree.find_tag(hist[0])  # return a refNodeTree
    if ref_node_tree_found is not None:  # if we find them
        # if r == len(hist) - 1:
        target_ref_node = None
        if ref_node_tree_found.obj.info is not None:
            node2find = StateNode()  # create node
            node2find.context = context
            node2find.history = hist
            target_ref_node = ref_node_tree_found.obj.info.Find(node2find)  # find the entire Node bb1
        if target_ref_node:  # if we find the target_ref_node
            # print "target reference node Found"
            pass
        else:
            new_node = StateNode()  # create node
            new_node.stateid = counterid
            counterid += 1
            new_node.context = context
            new_node.history = hist
            new_ref_node = StateRefNode()
            # pvv.obj = vv
            new_ref_node.obj = new_node
            if ref_node_tree_found.obj.info is None:
                ref_node_tree_found.obj.info = new_ref_node
            else:
                ref_node_tree_found.obj.info.Add(new_ref_node)
            target_ref_node = new_ref_node
            # prevRNT = ref_node_tree_found  # refNodeTree we found
            # tempRNT = ref_node_tree_found.obj.child  # temp is the child of pp2's Node
    else:  # if we don't find pp2RNT
        node_tree_new = NodeTree()  # create new Node Tree
        node_tree_new.tag = hist[0]
        ref_node_tree_new = RefNodeTree()
        ref_node_tree_new.obj = node_tree_new  # obj of refNodeTree is NodeTree
        temp_ref_node_tree.add_tree(ref_node_tree_new)  # add more refNodeTree
        new_node = StateNode()
        new_node.stateid = counterid
        counterid += 1  # state number +1
        new_node.context = context
        new_node.history = hist
        new_ref_node = StateRefNode()
        new_ref_node.obj = new_node
        node_tree_new.info = new_ref_node  # the NodeTree's info is pvv, the refNode
        target_ref_node = new_ref_node

    target_ref_node.obj.occ += 1.0  # occ plus one
    if goal_home == 1:
        # print "home goal"
        target_ref_node.obj.home_reward = 1.0  # home team score
    if goal_away == 1:
        # print "away goal"
        target_ref_node.obj.away_reward = 1.0  # away team score
    if pre_ref_node.obj.succ is None:  # the transition is not built before
        new_t_ref_node = TransRefNode()  # create a new transition state RefNode2()
        new_t_node = TransNode()
        new_t_ref_node.obj = new_t_node
        new_t_ref_node.obj.nod = target_ref_node  # connect it to current RefNode()
        pre_ref_node.obj.succ = new_t_ref_node  # connect it to the former RefNode()
    else:
        pFinded = pre_ref_node.obj.succ.Find2(  # TODO: !??
            target_ref_node.obj)  # return RNT2, check if the transitions has been built before
        if pFinded is None:  # if we fail to find
            # print "not bad"
            # p = RefNode2()  # if we fail to find, build a new one
            p = pre_ref_node.obj.succ  # the succ of the Node is a refNode, want to compute Occ(s,a,s')
            while p.obj.nex2 is not None:  # locate the new RN to the end of the nex2
                p = p.obj.nex2
            new_t_ref_node = TransRefNode()
            new_t_node = TransNode()
            new_t_ref_node.obj = new_t_node
            new_t_ref_node.obj.nod = target_ref_node
            p.obj.nex2 = new_t_ref_node
        else:
            # print "really good"
            # ee = RefNode2()
            new_t_ref_node = pFinded
    new_t_ref_node.obj.occ2 += 1.0  # occ2 plus
    # if ee.obj.occ2>1:
    #     print ee.obj.occ2
    new_t_ref_node.obj.eventids.append(cluster_counter - 1)  # new event id

    return target_ref_node


def run_builder(data_dir, cluster):
    init_node, init_ref_node, init_node_tree, init_ref_node_tree, counterid = init_nodes()

    sys.stdout = sys.__stdout__
    dir_all = os.listdir(data_dir)
    # dir_all = os.listdir('/Users/liu/Desktop/sport-analytic/Hockey-Match-All-data/')

    state_counter = 0
    # cluster = [0]*1519
    # data_dir = '/Users/liu/Desktop/'
    # dir_all = ['919069.json']  # TODO: testing
    for game_dir in dir_all:
        # for i in dir_all[1:11]:
        with open(data_dir + game_dir, 'r') as f:
            game = json.load(f)  # input every game information
        gameId = game['_id']
        events = game['events']
        cluster_counter = 0
        cluster_num_list = cluster.predict_action_cluster(events)

        print 'Processing game %s' % game_dir.split('.')[0]
        # print 'Processing game %s' % gameId[0][0][0]

        home_id = game['homeTeamId']  # home ID
        away_id = game['awayTeamId']
        # con = [0, 1, 0]
        context = {'score_difference': 0, 'period': 1, 'manpower': 0}
        # first place: number of goal in a game? home team +1 but route team -1 | second place: period? | third place: manpower situation
        # prevPossession = 0
        pre_ref_node = init_ref_node  # pre_ref_node is initialized to the root node, a refNode
        goal_home = 0
        goal_away = 0  # set home/away team score to 0
        # pre_ref_node = init_ref_node
        temp_ref_node_tree = init_ref_node_tree
        for event_index in range(0, len(events)):  # the number of event
            eve = events[event_index]
            teamId = eve['teamId']
            state_counter += 1
            # zone = eve['zone']  # zone name
            # judge if it is home
            if teamId == home_id:
                home = 1
            else:
                home = 0
            # currentPossession = ((((eve['currentPossession'])[0])[0])[0])[0]  # current possession
            event_action = eve['action']
            event_type = eve['label']
            period = 1 if eve['min'] <= 45 else 2
            context['period'] = period
            context['score_difference'] = eve['scoreDiff']

            mp = eve['manPower']  # man power situation
            context['manpower'] = mp

            # if make score or a certain type of shot
            if event_action == 'goal':
                if home:  # home goal
                    goal_home = 1
                else:  # away goal
                    goal_away = 1
            else:
                [goal_away, goal_home] = [0, 0]

            home_away_str = 'away' if not home else "home"

            nameInfo = event_action + '-' + home_away_str + '-cluster' + str(
                cluster_num_list[cluster_counter])  # pass-home-cluster3'
            cluster_counter += 1
            hist = [str(nameInfo)]  # history ignored, so len(hist)=1
            # print hist
            target_ref_node = build_tree(pre_ref_node, temp_ref_node_tree, hist, context,
                                         counterid, goal_home, goal_away,
                                         cluster_counter)

            if event_index == (len(events) - 1):  # update prevxx, if it's the end of a game
                pre_ref_node = init_ref_node
            else:
                pre_ref_node = target_ref_node
        # break

    print 'number of states is %i' % state_counter
    print 'states_id is %i' % counterid
    return init_ref_node_tree


# def save_model(model):
#     model
#     sys.setrecursionlimit(1500)
#     pickle.dump(model, open('./saved_model/markov_model', 'w'))


if __name__ == "__main__":
    counterid = 0
    soccer_data_dir = '/cs/oschulte/soccer-data/sequences_append_goal/'
    # sys.setrecursionlimit(20000)
    features_train, features_mean_dic, features_scale_dic, actions = select_feature_setting()
    soccer_data_dir = '/cs/oschulte/soccer-data/sequences_append_goal/'
    ap_cluster = APCluster(soccer_data_dir)
    ap_cluster.load_cluster()
    init_ref_node_tree = run_builder(data_dir=soccer_data_dir, cluster=ap_cluster)


    print 'computing Q-values for home team ...'
    m = 1
    markov_model.value_iteration(5, 0.00001, m, 0)

    markov_model.reset_nodes()  # set all the vis to 1
    print 'computing Q-values for away team ...'
    markov_model.value_iteration(5, 0.00001, m, 1)

    markov_model.reset_nodes()
    print 'computing impacts for home team ...'
    markov_model.compute_impact(m, 0)

    markov_model.reset_nodes()
    print 'computing impacts for away team ...'
    markov_model.compute_impact(m, 1)

    # save_model(init_ref_node_tree)
    # game1 = scipy.io.loadmat('./dataset/gamesInfo.mat')
    # gamesInfo = game1['gamesInfo']

    # cluster = scipy.io.loadmat('./dataset/cluster.mat')
    # cluster = cluster['cluster']
    # cluster = cluster[0]  # 9 clusters in total, 1359377 values

    # numcluster = scipy.io.loadmat('./dataset/numcluster.mat')
    # numcluster = numcluster['numcluster']
    # numcluster = numcluster[0]  # [5, 8, 7, 3, 3, 1, 6, 3, 7, 7, 6, 4, 3], 13 numbers in total

    # pl = scipy.io.loadmat('./dataset/pl.mat')
    # pl = pl['pl']
    # pl = pl[0]
