import tqdm
import numpy
import matplotlib.pyplot as plt

from config import Config
from environment import BitStringEnvironment
from policy import Policy, EGreedyPolicy, StrictlyGreedyPolicy
from dqn import DQN
from replay import Replay, CircularBuffer
from utils import moving_average


def train(dqn: DQN, policy: Policy, config: Config):
    replay_buffer = CircularBuffer(config.REPLAY_BUFFER_SIZE)
    cumulative_loss = 0.0
    batch_counter = 0
    losses = []
    num_steps_needed = []

    for _ in tqdm.tqdm(range(config.NUM_EPISODES)):
        environment = BitStringEnvironment(config.STRING_LENGTH, config.DEVICE)

        num_environment_steps = 0
        while True:
            # check for end of episode
            if environment.is_finished() or num_environment_steps >= config.MAX_EPISODE_STEPS:
                num_steps_needed.append(num_environment_steps)
                break

            # do action in environment
            state, goal = environment.get_state_and_goal()
            action = policy.get_action(dqn, state, goal)
            next_state, reward = environment.perform_action(action)

            # save replay of action
            replay = Replay(
                state=state,
                goal=goal,
                action=action,
                reward=reward,
                next_state=next_state,
                is_finished=environment.is_finished()
            )
            replay_buffer.enqueue(replay)

            # optimize dqn and policy
            batch = numpy.random.choice(replay_buffer.to_list(), config.BATCH_SIZE, replace=True)
            loss_value = dqn.step_batch(batch)
            cumulative_loss += loss_value

            batch_counter += 1
            if batch_counter >= config.LOGGING_RATE:
                losses.append(cumulative_loss)
                cumulative_loss = 0.0
                batch_counter = 0

            policy.step()

            # increment
            num_environment_steps += 1

    metrics = {
        "loss": losses,
        "num_steps": num_steps_needed,
    }

    return dqn, policy, metrics


def evaluate(dqn: DQN, policy: Policy, num_episodes: int):
    num_steps_needed = []

    for _ in tqdm.tqdm(range(num_episodes)):
        environment = BitStringEnvironment(config.STRING_LENGTH, config.DEVICE)

        num_environment_steps = 0
        while True:
            # check for end of episode
            if environment.is_finished() or num_environment_steps >= config.MAX_EPISODE_STEPS:
                num_steps_needed.append(num_environment_steps)
                break

            # do action in environment
            state, goal = environment.get_state_and_goal()
            action = policy.get_action(dqn, state, goal)
            _, _ = environment.perform_action(action)

            # increment
            num_environment_steps += 1

    metrics = {
        "num_steps": num_steps_needed,
    }

    return metrics


if __name__ == "__main__":
    config = Config(device="cpu")

    dqn = DQN(
        config.STRING_LENGTH,
        config.DISCOUNT,
        config.DQN_MOMENTUM,
        config.LEARNING_RATE,
        config.DEVICE,
    )
    policy = EGreedyPolicy(config.POLICY_EPSILON)

    # train
    dqn, policy, train_metrics = train(dqn, policy, config)

    plt.plot(train_metrics["loss"], label="loss")
    plt.legend()
    plt.show()

    # evaluate
    eval_metrics = evaluate(dqn, StrictlyGreedyPolicy(), num_episodes=config.NUM_EVAL_EPISODES)

    print(eval_metrics)
    plt.hist(eval_metrics["num_steps"])
    plt.show()
