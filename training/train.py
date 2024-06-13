import gym
import numpy as np
import tensorflow as tf
from tensorflow.keras import models, layers, optimizers
from replay_buffer import ReplayBuffer
from environments.pacman_env import PacmanEnv

def build_q_network(input_shape, num_actions):
    model = models.Sequential()
    model.add(layers.Conv2D(32, (8, 8), strides=4, activation='relu', input_shape=input_shape))
    model.add(layers.Conv2D(64, (4, 4), strides=2, activation='relu'))
    model.add(layers.Conv2D(64, (3, 3), strides=1, activation='relu'))
    model.add(layers.Flatten())
    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dense(num_actions, activation='linear'))
    model.compile(optimizer=optimizers.Adam(learning_rate=0.0001), loss='mse')
    return model

def train_agent(env, num_episodes=1000, batch_size=32, gamma=0.99, epsilon_start=1.0, epsilon_end=0.1, epsilon_decay=0.995, buffer_size=50000, min_replay_size=1000):
    replay_buffer = ReplayBuffer(buffer_size)
    q_network = build_q_network(env.observation_space.shape, env.action_space.n)
    target_network = build_q_network(env.observation_space.shape, env.action_space.n)
    target_network.set_weights(q_network.get_weights())

    epsilon = epsilon_start
    for episode in range(num_episodes):
        state = env.reset()
        state = np.expand_dims(state, axis=0)
        total_reward = 0
        done = False

        while not done:
            if np.random.rand() < epsilon:
                action = env.action_space.sample()
            else:
                q_values = q_network.predict(state)
                action = np.argmax(q_values[0])

            next_state, reward, done, _ = env.step(action)
            next_state = np.expand_dims(next_state, axis=0)
            replay_buffer.add((state, action, reward, next_state, done))
            state = next_state
            total_reward += reward

            if len(replay_buffer) >= min_replay_size:
                batch = replay_buffer.sample(batch_size)
                states, actions, rewards, next_states, dones = zip(*batch)
                states = np.concatenate(states)
                next_states = np.concatenate(next_states)
                targets = rewards + gamma * np.amax(target_network.predict(next_states), axis=1) * (1 - np.array(dones))
                targets_full = q_network.predict(states)
                indices = np.arange(batch_size)
                targets_full[indices, actions] = targets
                q_network.fit(states, targets_full, epochs=1, verbose=0)

            if done:
                print(f"Episode {episode + 1}/{num_episodes}, Total Reward: {total_reward}")
                if episode % 10 == 0:
                    target_network.set_weights(q_network.get_weights())
                if episode % 50 == 0:
                    q_network.save(f"pacman_model_{episode + 1}.h5")

        epsilon = max(epsilon_end, epsilon * epsilon_decay)

if __name__ == "__main__":
    env = PacmanEnv()
    train_agent(env)
