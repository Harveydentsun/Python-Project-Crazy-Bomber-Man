import os

import crazy_bomberman_gym

import gym
import numpy as np
from pathlib import Path
import pickle
from DQAgent import DQAgent
import cfg
import random
import pygame
from connector import main_train


def bomberman_train(log_path):

    n=6
    IMG_SIZE = (11, 13) #
    learning_rate = 0.00025
    dropout = 0
    replay_memory_size = 2e4
    replay_start_size = 1e4
    minibatch_size = 32
    discount_factor = 0.99
    epsilon = 1
    epsilon_decrease_rate = 9e-6
    min_epsilon = 0.1
    experiences = []
    training_count = 0
    episode = 0
    frame_counter = 0
    load=None
    max_episodes = 10000000

    state_file = Path('data/bombermaaan.pickle')
    if state_file.exists():
        pickle_in = open(state_file, 'rb')
        learning_rate = pickle.load(pickle_in)
        dropout = pickle.load(pickle_in)
        replay_memory_size = pickle.load(pickle_in)
        minibatch_size = pickle.load(pickle_in)
        discount_factor = pickle.load(pickle_in)
        epsilon = pickle.load(pickle_in)
        epsilon_decrease_rate = pickle.load(pickle_in)
        min_epsilon = pickle.load(pickle_in)
        experiences = pickle.load(pickle_in)
        training_count = pickle.load(pickle_in)
        episode = pickle.load(pickle_in)
        frame_counter = pickle.load(pickle_in)
        pickle_in.close()

    # Setup
    environment = 'bombermaaan-v0'
    env = gym.make(environment)
    env.start() #

    network_input_shape = (11, IMG_SIZE[1], IMG_SIZE[0])
    DQA = DQAgent(n, network_input_shape, replay_memory_size=replay_memory_size, minibatch_size=minibatch_size,
                  learning_rate=learning_rate, discount_factor=discount_factor, dropout_prob=dropout, epsilon=epsilon,
                  epsilon_decrease_rate=epsilon_decrease_rate, min_epsilon=min_epsilon, load_path=load)
    # Restore state
    model_file = Path('crazy_bomberman_gym/data/bombermaaan.h5')
    if model_file.exists():
        DQA.DQN.model.load_weights(model_file)

    model_file = Path('crazy_bomberman_gym/data/bombermaaan_target.h5')
    if model_file.exists():
        DQA.DQN_target.model.load_weights(model_file)

    DQA.experiences = experiences
    DQA.training_count = training_count

    episode = 0
    gameid = 0

    while episode < max_episodes:

        main_train(cfg, DQA, gameid)
        print("complete game:", gameid)

        try:
            experiences_log = np.load(log_path+"\\log%s.npy" % gameid, allow_pickle=True)
        except:
            continue

        actions_list = ["up", "down", "right", "left", "bomb", None]

        for i in range(len(experiences_log) - 1):
            experiences_log[i]["dest"] = experiences_log[i + 1]["state"]
            experiences_log[i]["dest"] = experiences_log[i]["dest"].reshape((1, 11, 13, 11))
            experiences_log[i]["state"] = experiences_log[i]["state"].reshape((1, 11, 13, 11))
            if "Enemy1" not in experiences_log[i + 1]:
                experiences_log[i + 1]["Enemy1"] = 0
            if "Enemy0" not in experiences_log[i + 1]:
                experiences_log[i + 1]["Enemy0"] = 0
            HP0 = experiences_log[i]["Hero"]
            HP1 = experiences_log[i]["Enemy0"] + experiences_log[i]["Enemy1"]
            detaHP0 = experiences_log[i + 1]["Hero"] - HP0
            detaHP1 = experiences_log[i + 1]["Enemy0"] + experiences_log[i + 1]["Enemy1"] - HP1
            temp_reward = (detaHP0 * 2.0 / max(HP0, 1)) - (detaHP1 * 1.0 / max(HP1, 1))
            experiences_log[i]["reward"] = temp_reward * 100
            experiences_log[i]["final"] = False
            experiences_log[i]["action_index"] = actions_list.index(experiences_log[i]["action"])
        experiences_log[len(experiences_log) - 2]["final"] = True
        experiences_log = experiences_log.tolist()
        del experiences_log[-1]
        experiences_log = np.asarray(experiences_log)

        for i in range(len(experiences_log)):

            DQA.add_experience(experiences_log[i])

            # Train the agent
            if len(DQA.experiences) >= replay_start_size:
                if episode % 8 == 0:
                    DQA.train()

                if DQA.training_count % 500 == 0:
                    DQA.reset_target_network()

                DQA.update_epsilon()

            episode += 1

            if episode % 100 == 0:
                data_dir = Path('data')
                if not os.path.exists('data'):
                    os.mkdir(data_dir)

                DQA.DQN.model.save_weights('data/bombermaaan.h5')
                DQA.DQN_target.model.save_weights('data/bombermaaan_target.h5')


                pickle_out = open('data/bombermaaan.pickle', 'wb')
                pickle.dump(DQA.learning_rate, pickle_out)
                pickle.dump(DQA.dropout_prob, pickle_out)
                pickle.dump(DQA.replay_memory_size, pickle_out)
                pickle.dump(DQA.minibatch_size, pickle_out)
                pickle.dump(DQA.discount_factor, pickle_out)
                pickle.dump(DQA.epsilon, pickle_out)
                pickle.dump(DQA.epsilon_decrease_rate, pickle_out)
                pickle.dump(DQA.min_epsilon, pickle_out)
                pickle.dump(DQA.experiences, pickle_out)
                pickle.dump(DQA.training_count, pickle_out)
                pickle.dump(episode, pickle_out)
                pickle.dump(frame_counter, pickle_out)
                pickle_out.close()
        print("load game:", gameid, "experiences size:", len(DQA.experiences))
        gameid += 1

if __name__ == "__main__":
    bomberman_train("D:\\Crazy_Bomber_Man\\crazy_bomberman_gym\\log")