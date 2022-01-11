# User files
import conf as conf
from cdPendulum import CDPendulum
from Network import Network, ReplayMemory
# pytorch
import torch
# numpy
import numpy as np
from numpy.random import randint, uniform

# Initialize environment
model      = CDPendulum()
# Initilalize replay memory D to capacity N
rb         = ReplayMemory(conf.REPLAY_MEMORY_SIZE) 
# Initialize action-value function Q with random weights \theta
Q_function = Network(model.nx + model.nu, model.nu)
# Initialize target action-value function \hat{Q} 
Q_target   = Network(model.nx + model.nu, model.nu)
#                                                 with weights \theta^- = \theta
Q_target.copy(Q_function)
#exploration_prob = conf.INITIAL_EXPLORATION
'''TODO:  change this variable back when finished debugging'''
exploration_prob = 0.
counter = 0
# for episode 1, M do
for episode in np.arange(0, conf.N_EPISODES):
    # Initialize sequence s_1 = \{x_1\} ...
    s = model.pendulum.reset()
    # for t = 1, T do 
    for t in np.arange(0, conf.MAX_EPISODE_LENGTH):
        counter += 1
    # With probability \epsilon select a random action a_t
        if uniform(0,1) < exploration_prob:
            a = randint(model.nu)
    # otherwise select a_t = \argmax_a Q(s_t, a; \theta)
        else:
            input = np.concatenate((s,model.actions)).T
            a = int(torch.argmin(Q_function(torch.Tensor(input)[0])))
        # Execute action a_t in the emulator and observe reward r_t and image x_{t+1}
        s_next, r = model.step(a)
        done = 0 if (episode == conf.N_EPISODES - 1) else 1 # mask to check if the next state is the one that terminates the episode
        # Set s_{t+1} = s_t , a_t, x_{t+1}
        # Store experience (s_t, a_t, r_t, s_{t+1}) in D
        rb.push(s, a, r, s_next, done)
        s = s_next
        # Sample random minibatch of experiences (s_j, a_j, r_j, s_{j+1}) from D
        try:
            minibatch = rb.sample(conf.MINIBATCH_SIZE)
        except ValueError:
            # print is here just for debugging
            print("Sample larger than population or is negative")
            continue
        # Set y_i = r_j if episode terminates at step j+1
        # Set y_i = r_j + \gamma \max_{a'} \hat{Q}(s_{j+1}, a'; \theta^-) otherwise
        y = 0
        for sample in minibatch:
            input = np.concatenate((sample.next_state,model.actions)).T
            y += sample.reward + sample.done*conf.GAMMA*float(torch.max(Q_target(torch.Tensor(input)[0]))) # with done we are sure that this will be equal to sample.reward 
        

        # Perform a gradient descent step on (y_i - Q(s_j, a_j; \theta))^2 with respect to the weights \theta
        '''TODO: i don't get this: do we have to implement Stocastic gradient descent but im not sure how for now'''

        # Every C steps reset \hat{Q} = Q
        if (counter == conf.NETWORK_RESET):
            counter = 0                         # by resetting to 0 the next iteration will change it back to 1 and correctly count to 4
            Q_target.copy(Q_function)
# end for
# end for