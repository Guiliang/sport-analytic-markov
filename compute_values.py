import os
import pickle

if __name__ == "__main__":
    soccer_data_dir = '/cs/oschulte/soccer-data/sequences_append_goal/'

    dir_all = os.listdir(soccer_data_dir)
    save_model_dir = ''
    markov_model = pickle.load(open(save_model_dir, 'r'))

    markov_model.obj.occ = len(dir_all)
    # execfile('hockey001.py')

    print 'computing Q-values for home team ...'
    m = 1
    markov_model.value_iteration(5, 0.00001, m, 0)

    markov_model.visit2()  # set all the vis to 1
    print 'computing Q-values for away team ...'
    markov_model.value_iteration(5, 0.00001, m, 1)

    markov_model.visit2()
    print 'computing impacts for home team ...'
    markov_model.visit(m, 0)

    markov_model.visit2()
    print 'computing impacts for away team ...'
    markov_model.visit(m, 1)
    #

    RefNode.allEvents = allEvents
    RefNode.allHome = allHome
    RefNode.cluster = cluster
    sys.stdout = open('./modelOutput/statesinfoTest.txt', 'w')
    markov_model.visit2()
    m = 1
    markov_model.visit6()
    sys.stdout = sys.__stdout__
    print '************************************************************'

    sys.stdout = open('./modelOutput/transitioninfoTest.txt', 'w')
    markov_model.visit2()
    m = 1
    markov_model.visit7()
    sys.stdout = sys.__stdout__
    print '************************************************************'
