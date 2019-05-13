import sys
sys.path.append('/Local-Scratch/PycharmProjects/sport-analytic-markov/')
from ap_cluster import APCluster


if __name__ == "__main__":
    soccer_data_dir = '/cs/oschulte/soccer-data/sequences_append_goal/'
    ap_cluster = APCluster(soccer_data_dir)
    ap_cluster.generate_cluster_data()
    ap_cluster.train_cluster()

