import gym
import numpy as np
from gym import spaces

class KoiKoiEnv(gym.Env):
    def __init__(self):
        super(KoiKoiEnv, self).__init__()
        
        # -- Example Action and Observation Setup --
        self.max_hand_size = 8
        self.field_size = 8
        self.deck_size = 48

        # Card IDs from 0 to 47
        self.num_cards = 48

        # Action = play one card + choose match (0 = do nothing / illegal)
        self.action_space = spaces.Discrete(self.max_hand_size)

        # Observation = flattened card representations (hand, field, scores)
        self.observation_space = spaces.Dict({
            "hand": spaces.MultiBinary(self.num_cards),
            "field": spaces.MultiBinary(self.num_cards),
            "collected": spaces.MultiBinary(self.num_cards),
            "opponent_score": spaces.Discrete(100),
            "your_score": spaces.Discrete(100),
            "turn": spaces.Discrete(2),
        })

        self.reset()

    def reset(self):
        # Initialize game state
        self.deck = list(range(self.num_cards))
        np.random.shuffle(self.deck)

        self.hand = self.deck[:self.max_hand_size]
        self.field = self.deck[self.max_hand_size:self.max_hand_size + self.field_size]
        self.collected = []
        self.opponent_score = 0
        self.your_score = 0
        self.turn = 0

        # Remove dealt cards from deck
        self.deck = self.deck[self.max_hand_size + self.field_size:]

        return self._get_obs()

    def _get_obs(self):
        obs = {
            "hand": self._cards_to_binary(self.hand),
            "field": self._cards_to_binary(self.field),
            "collected": self._cards_to_binary(self.collected),
            "opponent_score": self.opponent_score,
            "your_score": self.your_score,
            "turn": self.turn
        }
        return obs

    def step(self, action):
        # Validate action
        if action < 0 or action >= len(self.hand):
            return self._get_obs(), -1, True, {}

        # Simulate card play and matching logic (placeholder)
        played_card = self.hand.pop(action)
        match_found = played_card in self.field  # simplistic match rule

        if match_found:
            self.field.remove(played_card)
            self.collected.append(played_card)
            reward = 1  # placeholder
        else:
            self.field.append(played_card)
            reward = 0

        # Draw a card from the deck
        if self.deck:
            drawn = self.deck.pop(0)
            if drawn in self.field:
                self.field.remove(drawn)
                self.collected.append(drawn)
            else:
                self.field.append(drawn)

        done = len(self.hand) == 0 or len(self.deck) == 0
        info = {}

        return self._get_obs(), reward, done, info

    def render(self, mode='human'):
        print(f"Hand: {self.hand}")
        print(f"Field: {self.field}")
        print(f"Collected: {self.collected}")
        print(f"Score: You {self.your_score} - Opponent {self.opponent_score}")

    def _cards_to_binary(self, cards):
        bin_vec = np.zeros(self.num_cards, dtype=int)
        for c in cards:
            bin_vec[c] = 1
        return bin_vec
