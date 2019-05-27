import sys
sys.path.append('/Local-Scratch/PycharmProjects/sport-analytic-markov/')
sys.setrecursionlimit(9999)
from config.soccer_config import select_feature_setting
from model_tools.model_until import switch_mp
from generate_cluster.ap_cluster import APCluster
from build_model import run_builder
from aggregate_player_values import aggregate_player_impact

if __name__ == "__main__":
    counterid = 0
    soccer_data_dir = '/cs/oschulte/soccer-data/sequences_append_goal/'
    # sys.setrecursionlimit(20000)
    features_train, features_mean_dic, features_scale_dic, actions = select_feature_setting()
    soccer_data_dir = '/cs/oschulte/soccer-data/sequences_append_goal/'
    ap_cluster = APCluster(soccer_data_dir)
    ap_cluster.load_cluster()
    init_node, init_ref_node, init_node_tree, init_ref_node_tree = run_builder(data_dir=soccer_data_dir, cluster=ap_cluster)

    print 'computing Q-values for home team ...'
    m = 1
    init_ref_node.value_iteration(5, 0.00001, m, 0)

    init_ref_node.reset_nodes()  # set all the vis to 1
    print 'computing Q-values for away team ...'
    init_ref_node.value_iteration(5, 0.00001, m, 1)

    init_ref_node.reset_nodes()
    print 'computing impacts for home team ...'
    init_ref_node.compute_impact(m, 0)

    init_ref_node.reset_nodes()
    print 'computing impacts for away team ...'
    init_ref_node.compute_impact(m, 1)

    aggregate_player_impact(init_ref_node_tree=init_ref_node_tree, data_dir=soccer_data_dir, cluster=ap_cluster, init_ref_node=init_ref_node)

