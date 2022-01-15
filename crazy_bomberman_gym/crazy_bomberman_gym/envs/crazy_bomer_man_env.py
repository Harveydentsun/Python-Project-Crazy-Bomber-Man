import gym
import numpy as np
from gym import spaces

MAX_BOMBERS = 4

class CrazymaaanEnv(gym.Env):

    def __init__(self):

        self.done = False
        self.state = None

    def start(self):
        return True


if __name__ == "__main__":
    history_log = np.load('./log20220106163456.npy', allow_pickle=True)
    history_log
