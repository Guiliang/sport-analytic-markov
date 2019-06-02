import os
from player_values_tools import read_features_within_events, read_feature_within_events, find_Qs
import json
import math
import datetime


class Calibration:
    def __init__(self, bins, data_path, calibration_features, cluster,
                 init_ref_node_tree, data_store_dir, data_name, focus_actions_list=[]):
        self.bins = bins
        # self.bins_names = bins.keys()
        self.data_path = data_path
        self.calibration_features = calibration_features
        self.calibration_values_all_dict = {}
        # self.soccer_data_store_dir = soccer_data_store_dir
        self.focus_actions_list = focus_actions_list
        self.save_calibration_dir = './calibration_results/calibration-markov-{0}-{1}.txt'. \
            format(str(self.focus_actions_list), datetime.date.today().strftime("%Y%B%d"))
        self.save_calibration_file = open(self.save_calibration_dir, 'w')
        self.teams = ['home', 'away', 'end']
        self.cluster = cluster
        self.init_ref_node_tree = init_ref_node_tree
        self.data_store_dir = data_store_dir
        self.data_name = data_name
        # learning_rate = tt_lstm_config.learn.learning_rate
        # pass

    def __del__(self):
        print 'ending calibration'
        print self.save_calibration_file.close()

    def recursive2construct(self, store_dict_str, depth):
        feature_number = len(self.calibration_features)
        if depth >= feature_number:
            self.calibration_values_all_dict.update({store_dict_str: {'cali_sum': [0, 0, 0],
                                                                      'model_sum': [0, 0, 0],
                                                                      'number': 0}})
            return
        calibration_feature = self.calibration_features[depth]
        feature_range = self.bins.get(calibration_feature).get('range')
        for value in feature_range:
            # store_dict_str = '-' + store_dict_str if len(store_dict_str) > 0 else store_dict_str
            store_dict_str_update = store_dict_str + calibration_feature + '_' + str(value) + '-'
            self.recursive2construct(store_dict_str_update, depth + 1)

    def construct_bin_dicts(self):
        """create calibration dict"""
        self.recursive2construct('', 0)

    def compute_calibration_values(self, actions_team_all):
        """ground truth value for each game"""
        pre_index = 0
        cali_home = [0] * len(actions_team_all)
        cali_away = [0] * len(actions_team_all)
        cali_end = [0] * len(actions_team_all)
        for index in range(0, len(actions_team_all)):
            actions_team = actions_team_all[index]
            if actions_team['action'] == 'goal':
                if actions_team['home_away'] == 'H':
                    cali_home[pre_index:index] = [1] * (index - pre_index)
                elif actions_team['home_away'] == 'A':
                    cali_away[pre_index:index] = [1] * (index - pre_index)
                pre_index = index
            if index == len(actions_team_all) - 1:
                cali_end[pre_index:index] = [1] * (index - pre_index)
        return zip(cali_home, cali_away, cali_end)

    def aggregate_calibration_values(self, test_flag=False):
        """update calibration dict by each game"""
        if test_flag:
            self.data_path = '/Users/liu/Desktop/'
            dir_all = ['919069.json']  # TODO: testing
        else:
            dir_all = os.listdir(self.data_path)

        for json_dir in dir_all:
            features_all = []
            for calibration_feature in self.calibration_features:
                features = self.bins.get(calibration_feature).get('feature_name')
                if isinstance(features, str):
                    features_all.append(features)
                else:
                    for feature in features:
                        features_all.append(feature)
            # model_values = [[1, 0, 0]] * 1519  # TODO: test
            actions_team_all = read_features_within_events(feature_name_list=['action', 'home_away'],
                                                           data_path=self.data_path, directory=json_dir)
            calibration_values = self.compute_calibration_values(actions_team_all)

            features_values_dict_all = read_features_within_events(feature_name_list=features_all,
                                                                   data_path=self.data_path,
                                                                   directory=json_dir)

            with open(self.data_path + str(json_dir)) as f:
                data = json.load(f)
            events = data['events']
            home_id = data['homeTeamId']
            cluster_counter = 0
            cluster_num_list = self.cluster.predict_action_cluster(events)

            v_game_dict = {}

            for index in range(0, len(features_values_dict_all)):
                action = actions_team_all[index]['action']  # find the action we focus
                continue_flag = False if len(self.focus_actions_list) == 0 else True
                for f_action in self.focus_actions_list:
                    if f_action in action:
                        print action
                        continue_flag = False
                if continue_flag:
                    cluster_counter += 1
                    continue

                features_values_dict = features_values_dict_all[index]
                cali_dict_str = ''
                for calibration_feature in self.calibration_features:
                    if calibration_feature == 'period':
                        min = features_values_dict.get('min')
                        sec = features_values_dict.get('sec')
                        if min <= 45:
                            value = 1
                        else:
                            value = 2
                        cali_dict_str = cali_dict_str + calibration_feature + '_' + str(value) + '-'
                    elif calibration_feature == 'score_differential':
                        value = features_values_dict.get('scoreDiff')
                        cali_dict_str = cali_dict_str + calibration_feature + '_' + str(value) + '-'
                    elif calibration_feature == 'pitch':
                        xccord = features_values_dict.get('x')
                        if xccord <= 50:
                            value = 'left'
                        else:
                            value = 'right'
                        cali_dict_str = cali_dict_str + calibration_feature + '_' + value + '-'

                    elif calibration_feature == 'manpower':
                        value = features_values_dict.get('manPower')
                        cali_dict_str = cali_dict_str + calibration_feature + '_' + str(value) + '-'
                    else:
                        raise ValueError('unknown feature' + calibration_feature)

                calibration_value = calibration_values[index]
                cali_bin_info = self.calibration_values_all_dict.get(cali_dict_str)
                print cali_dict_str
                assert cali_bin_info is not None
                cali_sum = cali_bin_info.get('cali_sum')
                model_sum = cali_bin_info.get('model_sum')
                number = cali_bin_info.get('number')
                number += 1

                eve = events[index]
                teamId = eve['teamId']
                if teamId == home_id:
                    home = 1
                else:
                    home = 0
                event_action = eve['action']
                period = 1 if eve['min'] <= 45 else 2
                context = {'period': period, 'score_difference': eve['scoreDiff'], 'manpower': eve['manPower']}
                home_away_str = 'away' if not home else "home"

                nameInfo = event_action + '-' + home_away_str + '-cluster' + str(
                    cluster_num_list[cluster_counter])  # pass-home-cluster3'
                cluster_counter += 1
                hist = [str(nameInfo)]  # history ignored, so len(hist)=1

                v_home, v_away = find_Qs(hist, self.init_ref_node_tree, context)
                model_value = [v_home, v_away, 0]
                v_game_dict.update({index: {'home': v_home, 'away': v_away, 'end': 0}})

                for i in range(len(self.teams)):  # [home, away,end]
                    cali_sum[i] = cali_sum[i] + calibration_value[i]
                    model_sum[i] = model_sum[i] + model_value[i]

                self.calibration_values_all_dict.update({cali_dict_str: {'cali_sum': cali_sum,
                                                                         'model_sum': model_sum,
                                                                         'number': number}})

                # break

            with open(self.data_store_dir + "/" + json_dir.split('.')[0] + "/" + self.data_name, 'w') as outfile:
                json.dump(v_game_dict, outfile)

    def compute_distance(self):
        cali_dict_strs = self.calibration_values_all_dict.keys()
        for cali_dict_str in cali_dict_strs:
            cali_bin_info = self.calibration_values_all_dict.get(cali_dict_str)
            kld_sum = 0
            mae_sum = 0
            if cali_bin_info['number'] == 0:
                print "number of bin {0} is 0".format(cali_dict_str)
                continue
            cali_record_dict = 'Bin:' + cali_dict_str
            for i in range(len(self.teams)):  # [home, away,end]
                cali_prob = float(cali_bin_info['cali_sum'][i]) / cali_bin_info['number']
                model_prob = float(cali_bin_info['model_sum'][i]) / cali_bin_info['number']
                cali_record_dict += '\t{0}_number'.format(self.teams[i]) + ":" + str(cali_bin_info['number'])
                cali_record_dict += '\t{0}_cali'.format(self.teams[i]) + ":" + str(cali_prob)
                cali_record_dict += '\t{0}_model'.format(self.teams[i]) + ":" + str(model_prob)
                model_prob = model_prob + 1e-10
                cali_prob = cali_prob + 1e-10
                try:
                    kld = cali_prob * math.log(cali_prob / model_prob)
                except:
                    print 'rate is ' + str(cali_prob / model_prob)
                    kld = 0
                kld_sum += kld
                ae = abs(cali_prob - model_prob)
                mae_sum = mae_sum + ae
            cali_record_dict += '\tkld:' + str(kld_sum)
            cali_record_dict += '\tmae:' + str(float(mae_sum) / len(self.teams))
            self.save_calibration_file.write(str(cali_record_dict) + '\n')


def generate_cali_latex_table(result_file_dir):
    calibration_features = ['period', 'score_differential', 'pitch', 'manpower']
    calibration_bins = {'period': {'feature_name': ('sec', 'min'), 'range': (1, 2)},
                        'score_differential': {'feature_name': ('scoreDiff'), 'range': range(-1, 2)},
                        'pitch': {'feature_name': ('x'), 'range': ('left', 'right')},
                        'manpower': {'feature_name': ('manPower'), 'range': range(-1, 2)}
                        }
    with open(result_file_dir) as f:
        data = f.readlines()
    str_all = ''
    ref_dict = {'score_differential': 0, 'manpower': 0, 'period': 0, 'pitch': 0}
    for score_diff in calibration_bins['manpower']['range']:
        ref_dict['manpower'] = score_diff
        for manpower in calibration_bins['score_differential']['range']:
            ref_dict['score_differential'] = manpower
            for period in calibration_bins['period']['range']:
                ref_dict['period'] = period
                for pitch in calibration_bins['pitch']['range']:
                    ref_dict['pitch'] = pitch
                    ref_str = ''
                    for feature in calibration_features:
                        ref_str = ref_str + feature + '_' + str(ref_dict[feature]) + '-'

                    for line in data:
                        eles = line.split('\t')
                        red_str = eles[0].split(':')[1]

                        if ref_str == red_str:
                            number = eles[1].split(':')[1]
                            h_model = round(float(eles[3].split(':')[1]), 4)
                            a_model = round(float(eles[6].split(':')[1]), 4)
                            kld = round(float(eles[10].split(':')[1].replace('\n', '')), 4)
                            mae = round(float(eles[11].split(':')[1].replace('\n', '')), 4)

                            str_all += '{0} & {1} & {2} & {3} & {4} & {5} & {6} & {7} & {8} \\\\ \n'.format(
                                str(score_diff), str(manpower), str(period), str(pitch),
                                str(number), str(h_model), str(a_model), str(kld), str(mae)
                            )

    print str_all + '\hline'
