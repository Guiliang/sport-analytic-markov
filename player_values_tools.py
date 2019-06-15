import sys
import json
import os

from nodes.Node_define_upper import StateNode, StateRefNode


def read_feature_within_events(directory, data_path, feature_name):
    with open(data_path + str(directory)) as f:
        data = json.load(f)
    events = data.get('events')
    features_all = []
    for event in events:
        try:
            value = str(event.get(feature_name).encode('utf-8'))
        except:
            value = event.get(feature_name)
        features_all.append(value)

    return features_all


def read_features_within_events(directory, data_path, feature_name_list):
    with open(data_path + str(directory)) as f:
        data = json.load(f)
    events = data.get('events')
    features_all = []
    for event in events:
        feature_values = {}
        for feature_name in feature_name_list:
            try:
                value = str(event.get(feature_name).encode('utf-8'))
            except:
                value = event.get(feature_name)
            feature_values.update({feature_name: value})
        features_all.append(feature_values)

    return features_all


def find_Qs(hist, init_ref_node_tree, context):
    ref_node_tree_found = init_ref_node_tree.find_tag(hist[0])  # return a refNodeTree
    print hist[0]
    assert ref_node_tree_found.obj.info is not None
    node2find = StateNode()  # create node
    node2find.context = context
    node2find.history = hist
    target_ref_node = ref_node_tree_found.obj.info.Find(node2find)
    assert target_ref_node is not None

    return target_ref_node.obj.q, target_ref_node.obj.q1


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
    if pFinded is not None:
        return pFinded.obj.impact_home, pFinded.obj.impact_away, target_ref_node
    else:
        print 'pFinded is None'
        return 0, 0, target_ref_node


def aggregate_player_impact(init_ref_node_tree, data_dir, cluster, init_ref_node, data_store_dir, test_flag=False):
    player_impact_dict = {}
    if test_flag:
        data_dir = '/Users/liu/Desktop/'
        dir_all = ['919069.json']  # TODO: testing
    else:
        dir_all = os.listdir(data_dir)
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
        # first place: number of goal in a game? home team +1 but route team -1 | second place: period? | third place: manpower situation
        # prevPossession = 0
        # pre_ref_node = init_ref_node  # pre_ref_node is initialized to the root node, a refNode
        # goal_home = 0
        # goal_away = 0  # set home/away team score to 0
        # pre_ref_node = init_ref_node
        # temp_ref_node_tree = init_ref_node_tree
        pre_ref_node = init_ref_node
        markov_impact_all = {}
        for event_index in range(0, len(events)):  # the number of event
            eve = events[event_index]
            teamId = eve['teamId']
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
            context = {'period': period, 'score_difference': eve['scoreDiff'], 'manpower': eve['manPower']}
            try:
                playerId = eve['playerId']
            except:
                print eve
                playerId = 'Unknown'

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
            markov_impact_all.update({event_index: {'home': impact_home, 'away': impact_away, 'end': 0}})
            pre_ref_node = target_ref_node

            player_impact_sum = player_impact_dict[playerId]
            if player_impact_sum is not None:
                if home:
                    player_impact_sum += impact_home
                else:
                    player_impact_sum += impact_away
            else:
                if home:
                    player_impact_sum = impact_home
                else:
                    player_impact_sum = impact_away
            player_impact_dict[playerId] = player_impact_sum

        with open(data_store_dir + game_dir.split('.')[0]+'/markov_impact_values.json', 'w')as f:
            json.dump(obj=markov_impact_all, fp=f)

    print player_impact_dict
    return player_impact_dict
