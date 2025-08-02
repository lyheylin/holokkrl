import gymnasium as gym
from gymnasium import spaces
import numpy as np
from card_utils import get_month
from card_utils import detect_yaku


class KoiKoiEnv(gym.Env):
    def __init__(self):
        super(KoiKoiEnv, self).__init__()
        
        # -- Example Action and Observation Setup --
        self.max_hand_size = 8
        self.field_size = 8
        self.deck_size = 48

        # Card IDs from 0 to 47
        self.num_cards = 48

        # Action = play one card + choose match (0 = do nothing / illegal) E.g. (2,4) = play hand[2], match with field[4].
        self.action_space = spaces.Tuple((
            spaces.Discrete(self.max_hand_size),       # play from hand
            spaces.Discrete(self.field_size + 1)       # match with field (or "no match" = field_size)
        ))

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
        hand_idx, field_idx = action

        if hand_idx >= len(self.hand):
            return self._get_obs(), -1, True, False, {}

        played_card = self.hand.pop(hand_idx)
        played_month = get_month(played_card)

        # Build list of matches
        matching_field_cards = [c for c in self.field if get_month(c) == played_month]

        # Case 1: Match declared
        if field_idx < len(self.field):
            selected_field_card = self.field[field_idx]

            if selected_field_card in matching_field_cards:
                self.field.remove(selected_field_card)
                self.collected.extend([played_card, selected_field_card])
                reward = 1
            else:
            # Invalid match attempt
                reward = -1
                terminated = True
                return self._get_obs(), reward, terminated, False, {}

        # Case 2: No match or player chooses not to match
        else:
            self.field.append(played_card)
            reward = 0

        # Draw a card from the deck
        if self.deck:
            drawn_card = self.deck.pop(0)
            drawn_month = get_month(drawn_card)

            matching_field_cards = [c for c in self.field if get_month(c) == drawn_month]

        if matching_field_cards:
            # For now, auto-pick the first match
            matched_card = matching_field_cards[0]
            self.field.remove(matched_card)
            self.collected.extend([drawn_card, matched_card])
            # Optionally add extra reward here if you want
        else:
            # No match, place drawn card on field
            self.field.append(drawn_card)

        yakus, round_points = detect_yaku(self.collected)
        if yakus:
            print("🎉 Yaku detected:", yakus)
            # For now, just add points and continue
            self.your_score += round_points
            reward += round_points  # adjust this to balance early RL

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
