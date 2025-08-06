import gymnasium as gym
from gymnasium import spaces
import numpy as np
from env.card_utils import get_month
from env.card_utils import detect_yaku


class KoiKoiEnv(gym.Env):
    def __init__(self):
        super(KoiKoiEnv, self).__init__()
        
        # -- Action and Observation Setup --
        self.max_hand_size = 8
        self.field_size = 8
        self.deck_size = 48
        self.rng = np.random.default_rng()

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
        self.rng.shuffle(self.deck)

        self.player_hands = [[], []]
        self.collected_cards = [[], []]

        self.player_hands[0] = [self.deck.pop(0) for _ in range(self.max_hand_size)]  # Player
        self.player_hands[1] = [self.deck.pop(0) for _ in range(self.max_hand_size)]  # Opponent

        self.field = [self.deck.pop(0) for _ in range(self.field_size)]
        self.opponent_score = 0
        self.your_score = 0
        self.turn = 0
        self.opponent_koikoi = False
        self.player_koikoi = False

        self.round_over = False
        self.winner = None
        self.last_yaku = []

        # Remove dealt cards from deck
        # self.deck = self.deck[self.max_hand_size + self.field_size:]

        return self._get_obs()

    def _get_obs(self):
        obs = {
            "hand": self._cards_to_binary(self.player_hands[self.turn]),
            "field": self._cards_to_binary(self.field),
            "collected": self._cards_to_binary(self.collected_cards[self.turn]),
            "opponent_score": self.opponent_score,
            "your_score": self.your_score,
            "turn": self.turn
        }
        return obs

    def step(self, action):
        hand = self.player_hands[0]
        collected = self.collected_cards[0]
        done = False
        info = {}
        reward = 0

        # Handle Koi-Koi or Stop
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

        # Decode Action
        try:
            hand_idx = action // (self.field_size + 1)
            field_idx = action % (self.field_size + 1)
        except Exception:
            return self._get_obs(), -1, True, {"error": "Malformed action."}

        if hand_idx >= len(hand):
            return self._get_obs(), -1, True, {"error": "Invalid hand index."}

        played_card = hand.pop(hand_idx)
        played_month = get_month(played_card)
        matching_field_cards = [c for c in self.field if get_month(c) == played_month]

        # Player Match Phase
        if field_idx < len(self.field):
            selected_field_card = self.field[field_idx]
            if selected_field_card in matching_field_cards:
                self.field.remove(selected_field_card)
                collected.extend([played_card, selected_field_card])
                reward += 1  # Basic reward for a successful match
            else:
                return self._get_obs(), -1, True, {"error": "Illegal match attempted."}
        else:
            self.field.append(played_card)

        # Player Draw Phase
        if self.deck:
            drawn_card = self.deck.pop(0)
            drawn_month = get_month(drawn_card)
            matching_drawn = [c for c in self.field if get_month(c) == drawn_month]

            if matching_drawn:
                matched_card = matching_drawn[0]
                self.field.remove(matched_card)
                collected.extend([drawn_card, matched_card])
            else:
                self.field.append(drawn_card)

        # Yaku Check for Player
        yakus, points = detect_yaku(collected)
        if yakus:
            self.pending_yaku = yakus
            self.your_score += points
            reward += points
            if not self.koikoi_declared[self.turn]:
                self.koikoi_pending = True
                self.pending_player = self.turn
                return self._get_obs(), 0, False, {"yaku": yakus, "awaiting_koikoi": True}

        # Game End Check
        if self._check_game_end():
            return self._get_obs(), reward, True, {"game_end": True}

        # Opponent Turn
        self.turn = 1  # Switch to opponent
        opponent_done = self._opponent_turn()

        # Final Check After Opponent Turn
        done = opponent_done or self._check_game_end()
        self.turn = 0  # Back to player's turn

        return self._get_obs(), reward, done, info


    def _opponent_turn(self):
        hand = self.player_hands[1]
        collected = self.collected_cards[1]
        reward = 0
        done = False

        # Opponent Match Phase
        if hand:
            matching_cards = [
                card for card in hand
                if any(get_month(c) == get_month(card) for c in self.field)
            ]
            card_to_play = self.rng.choice(matching_cards if matching_cards else hand)
            hand.remove(card_to_play)

            matches = [c for c in self.field if get_month(c) == get_month(card_to_play)]
            if matches:
                match = self.rng.choice(matches)
                self.field.remove(match)
                collected.extend([card_to_play, match])
            else:
                self.field.append(card_to_play)

        # Opponent Draw Phase
        if self.deck:
            drawn_card = self.deck.pop(0)
            matches = [c for c in self.field if get_month(c) == get_month(drawn_card)]
            if matches:
                match = self.rng.choice(matches)
                self.field.remove(match)
                collected.extend([drawn_card, match])
            else:
                self.field.append(drawn_card)

        # Yaku Check for Opponent
        yakus, points = detect_yaku(collected)
        if yakus:
            self.opponent_score += points
            if self.opponent_koikoi:
                # Continue playing, already declared
                return False
            elif self.rng.random() < 0.3:  # Random Koi-Koi
                self.opponent_koikoi = True
                return False
            else:
                # Opponent stops the round
                return True

        return False


    def render(self, mode='human'):
        print(f"Hand: {self.player_hands[0]}")
        print(f"Field: {self.field}")
        print(f"Self Collected: {self.collected_cards[0]}")
        print(f"Opponent Collected: {self.collected_cards[1]}")
        print(f"Score: You {self.your_score} - Opponent {self.opponent_score}")

    def _cards_to_binary(self, cards):
        bin_vec = np.zeros(self.num_cards, dtype=int)
        for c in cards:
            bin_vec[c] = 1
        return bin_vec
    
    def _check_game_end(self):
        both_hands_empty = all(len(h) == 0 for h in self.player_hands)
        deck_empty = len(self.deck) == 0
        return both_hands_empty or deck_empty
