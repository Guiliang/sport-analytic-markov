import datetime
import json
import sys
from calibration import Calibration, generate_cali_latex_table

sys.path.append('/Local-Scratch/PycharmProjects/sport-analytic-markov/')
sys.setrecursionlimit(9999)
from config.soccer_config import select_feature_setting
from model_tools.model_until import switch_mp
from generate_cluster.ap_cluster import APCluster
from build_model import run_builder
from player_values_tools import aggregate_player_impact

if __name__ == "__main__":
    counterid = 0
    iter_num = 100
    soccer_data_dir = '/cs/oschulte/soccer-data/sequences_append_goal/'
    test_flag = False
    # sys.setrecursionlimit(20000)
    features_train, features_mean_dic, features_scale_dic, actions = select_feature_setting()
    ap_cluster = APCluster(soccer_data_dir)
    ap_cluster.load_cluster()
    init_node, init_ref_node, init_node_tree, init_ref_node_tree = run_builder(data_dir=soccer_data_dir,
                                                                               cluster=ap_cluster, test_flag=test_flag)

    print 'computing Q-values for home team ...'
    m = 1
    init_ref_node.value_iteration(iter_num, 0.00001, m, 0)

    init_ref_node.reset_nodes()  # set all the vis to 1
    print 'computing Q-values for away team ...'
    init_ref_node.value_iteration(iter_num, 0.00001, m, 1)

    init_ref_node.reset_nodes()
    print 'computing impacts for home team ...'
    init_ref_node.compute_impact(m, 0)

    init_ref_node.reset_nodes()
    print 'computing impacts for away team ...'
    init_ref_node.compute_impact(m, 1)

    player_impact_dict = aggregate_player_impact(init_ref_node_tree=init_ref_node_tree, data_dir=soccer_data_dir,
                                                 cluster=ap_cluster, init_ref_node=init_ref_node,test_flag=test_flag)

    json.dump(player_impact_dict, open('./player_impact/'
                                       'soccer_player_markov_impact-{0}.json'.
                                       format(datetime.date.today().strftime("%Y%B%d")), 'w'))

    calibration_features = ['period', 'score_differential', 'pitch', 'manpower']
    calibration_bins = {'period': {'feature_name': ('sec', 'min'), 'range': (1, 2)},
                        'score_differential': {'feature_name': ('scoreDiff'), 'range': range(-8, 8)},
                        'pitch': {'feature_name': ('x'), 'range': ('left', 'right')},
                        'manpower': {'feature_name': ('manPower'), 'range': (-3, -2, -1, 0, 1, 2, 3)}
                        }
    data_store_dir = "/cs/oschulte/Galen/Soccer-data/"
    data_name = 'markov_values_iter{0}'.format(str(iter_num))

    # soccer_data_store_dir = "/cs/oschulte/Galen/Soccer-data"

    Cali = Calibration(bins=calibration_bins, data_path=soccer_data_dir,
                       calibration_features=calibration_features, cluster=ap_cluster,
                       init_ref_node_tree=init_ref_node_tree, data_store_dir = data_store_dir,
                       focus_actions_list=['shot', 'pass'], data_name=data_name)
    Cali.construct_bin_dicts()
    Cali.aggregate_calibration_values(test_flag=test_flag)
    Cali.compute_distance()
    Cali.__del__()
    generate_cali_latex_table(Cali.save_calibration_dir)
