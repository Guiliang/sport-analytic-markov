import json
import os

import pickle

from config.soccer_config import select_feature_setting
from sklearn.cluster import AffinityPropagation


class APCluster(object):
    def __init__(self, soccer_data_dir):
        self.model_save_dir = './cluster_models/ap_cluster_'
        self.soccer_data_dir = soccer_data_dir
        _, _, _, actions = select_feature_setting()
        self.actions = actions
        self.action_data_dict = {}
        for action in self.actions:
            self.action_data_dict.update({action: {'data': [], 'largest_x': 0, 'largest_y': 0,
                                                   'smallest_x': 100, 'smallest_y': 100}})

    def generate_cluster_data(self, ):
        dir_all = os.listdir(self.soccer_data_dir)
        # self.soccer_data_dir = '/Users/liu/Desktop/'
        # dir_all = ['919069.json']
        for game_dir in dir_all:
            # for i in dir_all[1:11]:

            with open(self.soccer_data_dir + game_dir, 'r') as f:
                game = json.load(f)  # input every game information
            gameId = game['_id']
            events = game['events']

            for event in events:
                event_action = event['action']
                event_x = event['x']
                event_y = event['y']
                action_info = self.action_data_dict.get(event_action)
                action_info.get('data').append([event_x, event_y])
                if event_x > action_info.get('largest_x'):
                    action_info.update({'largest_x': event_x})
                if event_y > action_info.get('largest_y'):
                    action_info.update({'largest_y': event_y})
                if event_x < action_info.get('smallest_x'):
                    action_info.update({'smallest_x': event_x})
                if event_y < action_info.get('smallest_y'):
                    action_info.update({'smallest_y': event_y})
                self.action_data_dict.update({event_action: action_info})

    def train_cluster(self):
        for action in self.actions:
            action_info = self.action_data_dict.get(action)
            action_data = action_info.get('data')
            # if action == 'simple-pass':
            #     print 'test'
            if len(action_data) < 2:
                print 'number of cluster for action {0} is 0'.format(action)
                continue
            preference = -1 * ((action_info.get('largest_x')-action_info.get('smallest_x'))**2 +
                               (action_info.get('largest_y')-action_info.get('smallest_y'))**2)
            af = AffinityPropagation(preference=preference).fit(action_data)
            cluster_centers_indices = af.cluster_centers_indices_
            print 'number of cluster for action {0} is {1}'.format(action, len(cluster_centers_indices))
            with open(self.model_save_dir + action, 'w') as f:
                pickle.dump(af, f)
