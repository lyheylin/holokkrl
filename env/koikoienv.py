import gymnasium as gym
from gymnasium import spaces
import numpy as np
from card_utils import get_month
from card_utils import detect_yaku


class KoiKoiEnv(gym.Env):
    def __init__(self):
        super(KoiKoiEnv, self).__init__()
        
        # -- Action and Observation Setup --
        self.max_hand_size = 8
        self.field_size = 8
        self.deck_size = 48

        # Card IDs from 0 to 47
        self.num_cards = 48

        # Player state flags
        self.koikoi_pending = False
        self.pending_yaku = []
        self.pending_player = None
        self.koikoi_declared = [False, False]  # One for each player

        # Action = play one card + choose match (0 = do nothing / illegal) (play hand x * match field y)
        self.num_play_actions = self.max_hand_size * (self.field_size + 1)  # 8 * 9 = 72 
        self.KOIKOI_ACTION = self.num_play_actions
        self.STOP_ACTION = self.num_play_actions + 1
        self.total_actions = self.num_play_actions + 2

        self.action_space = spaces.Discrete(self.total_actions)

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
        # -- Handle Koi-Koi or Stop Decision --
        if self.koikoi_pending:
            if action == self.KOIKOI_ACTION:
                self.koikoi_declared[self.pending_player] = True
                self.koikoi_pending = False
                return self._get_obs(), 0, False, {"koikoi": True}
            elif action == self.STOP_ACTION:
                reward = sum(y[1] for y in self.pending_yaku)
                self.koikoi_pending = False
                return self._get_obs(), reward, True, {"stopped": True, "yaku": self.pending_yaku}
            else:
                return self._get_obs(), -1, False, {"error": "Invalid action during Koi-Koi decision."}

        try:
                hand_idx = action // (self.field_size + 1)
                field_idx = action % (self.field_size + 1)
        except ValueError:
            return self._get_obs(), -1, True, {"error": "Malformed action."}

        if hand_idx >= len(self.hand):
            return self._get_obs(), -1, True, {"error": "Invalid hand index."}

        played_card = self.hand.pop(hand_idx)
        played_month = get_month(played_card)

        # Build list of matches
        matching_field_cards = [c for c in self.field if get_month(c) == played_month]
        reward = 0

        # Case 1: Match declared
        if field_idx < len(self.field):
            selected_field_card = self.field[field_idx]

            if selected_field_card in matching_field_cards:
                self.field.remove(selected_field_card)
                self.collected.extend([played_card, selected_field_card])
                reward += 1
            else:
            # Invalid match attempt
                return self._get_obs(), -1, True, False, {"error": "Illegal match attempted."} # reward -1, terminated 

        # Case 2: No match or player chooses not to match
        else:
            self.field.append(played_card)

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
            # Optionally: add extra reward here 
        else:
            # No match, place drawn card on field
            self.field.append(drawn_card)

        yakus, round_points = detect_yaku(self.collected)
        if yakus:
            print("Yaku detected:", yakus)
            # For now, just add points and continue
            self.pending_yaku = yakus
            self.your_score += round_points
            reward += round_points  # adjust this to balance early RL

        
        if not self.koikoi_declared[self.turn]:
            self.koikoi_pending = True
            self.pending_player = self.turn
            return self._get_obs(), 0, False, {"yaku": self.pending_yaku, "awaiting_koikoi": True}

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
