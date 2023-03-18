class Config:
    # environment
    STRING_LENGTH: int = 2

    # policy
    POLICY_EPSILON: float = 0.8

    # simulation
    NUM_EPISODES: int = 5000
    MAX_EPISODE_STEPS: int = 10
    REPLAY_BUFFER_SIZE: int = 50

    # optimization
    LEARNING_RATE: float = 0.005
    BATCH_SIZE: int = 20
    DISCOUNT: float = 0.3  # lower means more discount
    DQN_MOMENTUM: float = 0.75

    # logging
    LOGGING_RATE: int = 10
