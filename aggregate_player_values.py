import sys
import json
import os
from nodes.Node_define_upper import StateNode, StateRefNode


def find_impact(hist, init_ref_node_tree, context, pre_ref_node):
    ref_node_tree_found = init_ref_node_tree.find_tag(hist[0])  # return a refNodeTree
    assert ref_node_tree_found.obj.info is not None
    node2find = StateNode()  # create node
    node2find.context = context
    node2find.history = hist
    target_ref_node = ref_node_tree_found.obj.info.Find(node2find)
    assert target_ref_node is not None

    pFinded = pre_ref_node.obj.succ.Find2(  # TODO: !??
        target_ref_node.obj)

    return pFinded.obj.impact_home, pFinded.obj.impact_away, target_ref_node


def aggregate_player_impact(init_ref_node_tree, data_dir, cluster, init_ref_node):
    player_impact_dict = {}
    pre_ref_node = init_ref_node
    dir_all = os.listdir(data_dir)
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
        # pre_ref_node = init_ref_node  # pre_ref_node is initialized to the root node, a refNode
        # goal_home = 0
        # goal_away = 0  # set home/away team score to 0
        # pre_ref_node = init_ref_node
        # temp_ref_node_tree = init_ref_node_tree
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
            playerId = eve['playerId']
            # if make score or a certain type of shot
            # if event_action == 'goal':
            #     if home:  # home goal
            #         goal_home = 1
            #     else:  # away goal
            #         goal_away = 1
            # else:
            #     [goal_away, goal_home] = [0, 0]

            home_away_str = 'away' if not home else "home"

            nameInfo = event_action + '-' + home_away_str + '-cluster' + str(
                cluster_num_list[cluster_counter])  # pass-home-cluster3'
            cluster_counter += 1
            hist = [str(nameInfo)]  # history ignored, so len(hist)=1
            # print hist
            impact_home, impact_away, target_ref_node = find_impact(hist, init_ref_node_tree, context, pre_ref_node)
            pre_ref_node = target_ref_node
            try:
                player_impact_sum = player_impact_dict[playerId]
                if home:
                    player_impact_sum += impact_home
                else:
                    player_impact_sum += impact_away
            except:
                if home:
                    player_impact_sum = impact_home
                else:
                    player_impact_sum = impact_away
            player_impact_dict[playerId] = player_impact_sum

    print player_impact_dict
    return player_impact_dict


