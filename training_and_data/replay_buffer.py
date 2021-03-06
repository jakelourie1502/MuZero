import numpy as np
from global_settings import replay_buffer_size, batch_size, device
from global_settings import training_params
import torch
class Replay_Buffer():

    """
    This is a class that can hold the data required for training
    each tuple is :
    obs_t = observed state at that time
    policy_log_t = policy after mcts process
    action_log_t = action chosen, which is a random.choice proprotional to policy.
    reward_log_t+1 = the reward achieved from Ot, At pair.
    done_log_t+1 = whether that Ot, At pair ended the game. note, in our game, reward =1 and done = True happens at the same time.
    fut_val_log_t = 
    """
    def __init__(self):
        self.k = training_params['k']
        self.default_size = batch_size
        self.size = replay_buffer_size
        self.obs = []
        self.action_log = []
        self.reward_logs = []
        self.done_logs = []
        self.fut_val_logs = []
        self.policy_logs = []
        self.search_val_logs = []
    def add_ep_log(self, metrics):
        """Metrics dictionary of the form
        metrics['obs']
        metrics['next_ob']
        metrics['action']
        metrics['reward']
        metrics['done']
        metrics['V']
        """
        self.obs.extend(metrics['obs'])
        self.action_log.extend(metrics['action'])
        self.reward_logs.extend(metrics['reward'])
        self.done_logs.extend(metrics['done'])
        self.fut_val_logs.extend(metrics['V'])
        self.policy_logs.extend(metrics['policy'])
        self.search_val_logs.extend(metrics['search_val_logs'])
    
    def purge(self):
        no_of_examples = len(self.obs)
        if no_of_examples > self.size:
            reduc = no_of_examples - self.size
            self.obs = self.obs[reduc: ]
            self.action_log = self.action_log[reduc: ]
            self.reward_logs = self.reward_logs[reduc: ]
            self.done_logs = self.done_logs[reduc: ]
            self.fut_val_logs = self.fut_val_logs[reduc: ]
            self.policy_logs = self.policy_logs[reduc: ]
            self.search_val_logs = self.search_val_logs[reduc: ]

    def get_sample(self, prioritised_sampling = True, batch_size = batch_size):
        #### Need to add get sample prioritised.
        
        batch_n = batch_size
        if prioritised_sampling:
            
            coefs = torch.abs(torch.tensor(self.search_val_logs)-torch.tensor(self.fut_val_logs))
            coefs = coefs[:-(self.k)]
            coefs = coefs / torch.sum(coefs)
            coefs = np.array(coefs)
            
            weights = (1/(coefs*len(self.search_val_logs)))
            current_length = len(self.obs)-self.k #we don't want one right at the end or it will break.
            indices = np.random.choice(list(range(current_length)),size=batch_n, p=coefs,replace=False)
            weights = [weights[i] for i in indices]
            
        else:
            indices = np.random.randint(low = 0, high = len(self.obs)-self.k, size = batch_n)
            weights = np.ones_like(indices)
        sample_obs = np.array([self.obs[i] for i in indices])
        
        return torch.tensor(sample_obs).to(device), indices, weights
        
