import gymnasium as gym
from gymnasium import spaces
import numpy as np
from environment.card_utils import get_month
from environment.card_utils import detect_yaku


class KoiKoiEnv(gym.Env):

    metadata = {"render_modes": ["human"]}

    def __init__(self, opponent_type="random", max_rounds=3):
        super(KoiKoiEnv, self).__init__()
        self.opponent_type = opponent_type
        
        # -- Action and Observation Setup --
        self.max_hand_size = 8
        self.field_size = 8
        self.num_cards = 48
        self.rng = np.random.default_rng()
        self.max_rounds = max_rounds
        
        # Action = play one card + choose match (0 = do nothing / illegal) (play hand x * match field y + no match)
        self.num_play_actions = self.max_hand_size * (self.field_size + 1)  # 8 * 9 = 72 
        self.KOIKOI_ACTION = self.num_play_actions
        self.STOP_ACTION = self.num_play_actions + 1
        self.total_actions = self.num_play_actions + 2

        self.action_space = spaces.Discrete(self.total_actions)

        # Observation = flattened card representations (hand, field, scores)
        self.observation_space = spaces.Dict({
            "hand": spaces.MultiBinary(self.num_cards),
            "field": spaces.MultiBinary(self.num_cards),
            "cards_left_in_deck": spaces.Discrete(49),
            "last_drawn_card": spaces.MultiBinary(self.num_cards),
            "collected": spaces.MultiBinary(self.num_cards),
            "opponent_collected": spaces.MultiBinary(self.num_cards),
            "opponent_round_score": spaces.Discrete(20),
            "opponent_score": spaces.Discrete(100),
            "your_round_score": spaces.Discrete(20),
            "your_score": spaces.Discrete(100),
            "turn": spaces.Discrete(2),
            "round": spaces.Discrete(self.max_rounds),
        })

        self.reset()

    
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        # Reset multi-round match
        self.round_count = 0
        self.your_score = 0
        self.opponent_score = 0
        self.match_over = False
        self._start_new_round()
        return self._get_obs(), {}
        
    def _start_new_round(self):
        self.deck = list(range(self.num_cards))
        self.rng.shuffle(self.deck)

        # Player hands and collected cards
        self.player_hands = [[], []]
        self.collected_cards = [[], []]
        self.player_hands[0] = [self.deck.pop(0) for _ in range(self.max_hand_size)]
        self.player_hands[1] = [self.deck.pop(0) for _ in range(self.max_hand_size)]

        # Field and last drawn
        self.field = [self.deck.pop(0) for _ in range(self.field_size)]
        self.last_drawn_card = None

        # Round-specific scores
        self.your_round_score = 0
        self.opponent_round_score = 0

        # Turn and Koi-Koi state
        self.turn = 0
        self.koikoi_pending = False
        self.pending_yaku = []
        self.pending_player = None
        self.koikoi_declared = [False, False]
        self.opponent_koikoi = False
        self.player_koikoi = False

        # Round control
        self.round_over = False
        self.winner = None
        self.last_yaku = []


    def _get_obs(self):
        return {
            "hand": self._cards_to_binary(self.player_hands[0]),
            "field": self._cards_to_binary(self.field),
            "cards_left_in_deck": len(self.deck),
            "last_drawn_card": self._card_to_binary(self.last_drawn_card) if self.last_drawn_card else np.zeros(self.num_cards, dtype=np.int8),
            "collected": self._cards_to_binary(self.collected_cards[0]),
            "opponent_collected": self._cards_to_binary(self.collected_cards[1]),
            "opponent_round_score": self.opponent_round_score,
            "opponent_score": self.opponent_score,
            "your_round_score": self.your_round_score,
            "your_score": self.your_score,
            "turn": self.turn,
            "round": self.round_count,
        }

    # List of keys of info to return
    # "played_card": the card the player played
    # "player_field_match": the matched field card (or None)
    # "player_drawn_card": the drawn card
    # "player_draw_match": matched field card from draw (or None)
    # "yaku": list of player yakus (if formed)
    # "awaiting_koikoi": True if awaiting decision
    def step(self, action):
        hand = self.player_hands[0]
        collected = self.collected_cards[0]
        terminated = False
        truncated = False
        info = {}
        reward = 0

        # Handle Koi-Koi or Stop
        if self.koikoi_pending:
            if action == self.KOIKOI_ACTION:
                self.koikoi_declared[self.pending_player] = True
                self.koikoi_pending = False
                return self._get_obs(), 0, False, False, {"koikoi": True}
            elif action == self.STOP_ACTION:
                reward = sum(y[1] for y in self.pending_yaku)
                self.koikoi_pending = False
                self.your_score += reward
                self.your_round_score = reward
                self.round_over = True
                info.update({
                    "stopped": True,
                    "yaku": self.pending_yaku
                })
            else:
                return self._get_obs(), -1, False, False, {"error": "Invalid action during Koi-Koi decision."}

        # Check if hand is empty before playing
        if not hand:
            self.round_over = True

        if self.round_over:
            self.round_count += 1
            if self.round_count >= self.max_rounds:
                terminated = True
            else:
                self._start_new_round()
            info["round_over"] = True
            info["match_over"] = self.round_count >= self.max_rounds
            return self._get_obs(), reward, terminated, truncated, info

        # Decode Action
        try:
            hand_idx = action // (self.field_size + 1)
            field_idx = action % (self.field_size + 1)
        except Exception:
            return self._get_obs(), -1, False, False, {"error": "Malformed action."}

        if hand_idx >= len(hand):
            return self._get_obs(), -1, False, False, {"error": "Invalid hand index."}

        played_card = hand.pop(hand_idx)
        played_month = get_month(played_card)
        matching_field_cards = [c for c in self.field if get_month(c) == played_month]

        # Player Match Phase
        if field_idx < len(self.field):
            selected_field_card = self.field[field_idx]
            if selected_field_card in matching_field_cards:
                self.field.remove(selected_field_card)
                collected.extend([played_card, selected_field_card])
                info["player_field_match"] = selected_field_card
                reward += 1 # Basic reward implementation //need update
            else:
                # hand.insert(hand_idx, played_card) 
                return self._get_obs(), -1, False, False, {"error": "Illegal match attempted."}
        else:
            self.field.append(played_card)
            info["player_field_match"] = None

        # Player Draw Phase
        if self.deck:
            drawn_card = self.deck.pop(0)
            self.last_drawn_card = drawn_card
            info["player_drawn_card"] = drawn_card
            drawn_month = get_month(drawn_card)
            matching_drawn = [c for c in self.field if get_month(c) == drawn_month]

            if matching_drawn:
                matched_card = matching_drawn[0]
                self.field.remove(matched_card)
                collected.extend([drawn_card, matched_card])
                info["player_draw_match"] = matched_card
            else:
                self.field.append(drawn_card)
                info["player_draw_match"] = None

        # Yaku Check for Player
        yakus, points = detect_yaku(collected)
        if yakus:
            self.pending_yaku = yakus
            self.your_score += points
            self.your_round_score += points
            reward += points
            info["yaku"] = yakus
            if not self.koikoi_declared[self.turn]:
                self.koikoi_pending = True
                self.pending_player = self.turn
                info["awaiting_koikoi"] = True
                return self._get_obs(), 0, False, False, info

        # Opponent Turn
        self.turn = 1
        opponent_info, opponent_round_end = self._opponent_turn()
        info.update(opponent_info)

        self.round_over = self._check_round_end() or self.round_over or opponent_round_end
        if self.round_over:
            self.round_count += 1
            if self.round_count >= self.max_rounds:
                terminated = True  # Gym expects episode over
            else:
                # Automatically start new round
                self._start_new_round()

        self.turn = 0  # back to player
        info["round_over"] = self.round_over
        info["match_over"] = self.round_count >= self.max_rounds

        return self._get_obs(), reward, terminated, truncated, info

    # List of keys of info to return:
    # "opponent_played_card"
    # "opponent_play_match"
    # "opponent_drawn_card"
    # "opponent_draw_match"
    # "opponent_yaku": opponent yaku list (if any)
    # "opponent_koikoi": True if they chose koi-koi, False if they stopped
    def _opponent_turn(self):
        hand = self.player_hands[1]
        collected = self.collected_cards[1]
        done = False
        info = {}

        if not hand:
            # Opponent has no cards left, round ends
            done = True
            return info, done

        # --- Opponent Match Phase ---
        matching_cards = [c for c in hand if any(get_month(c) == get_month(f) for f in self.field)]
        card_to_play = self.rng.choice(matching_cards if matching_cards else hand)
        hand.remove(card_to_play)
        info["opponent_played_card"] = card_to_play

        matches = [c for c in self.field if get_month(c) == get_month(card_to_play)]
        if matches:
            match = self.rng.choice(matches)
            self.field.remove(match)
            collected.extend([card_to_play, match])
            info["opponent_play_match"] = match
        else:
            self.field.append(card_to_play)
            info["opponent_play_match"] = None

        # --- Opponent Draw Phase ---
        if self.deck:
            drawn_card = self.deck.pop(0)
            info["opponent_drawn_card"] = drawn_card
            matches = [c for c in self.field if get_month(c) == get_month(drawn_card)]
            if matches:
                match = self.rng.choice(matches)
                self.field.remove(match)
                collected.extend([drawn_card, match])
                info["opponent_draw_match"] = match
            else:
                self.field.append(drawn_card)
                info["opponent_draw_match"] = None

        # --- Yaku Check for Opponent ---
        yakus, points = detect_yaku(collected)
        if yakus:
            info["opponent_yaku"] = yakus
            self.opponent_score += points
            self.opponent_round_score += points
            # Simple Koi-Koi logic: 30% chance to continue, otherwise stop
            if not self.opponent_koikoi:
                if self.rng.random() < 0.3:
                    self.opponent_koikoi = True
                    info["opponent_koikoi"] = True
                else:
                    info["opponent_koikoi"] = False
                    done = True
            else:
                # Already in Koi-Koi, continue
                info["opponent_koikoi"] = True

        # --- Round End if Hand Empty ---
        if not hand:
            done = True

        return info, done


    def _check_round_end(self):
        hands_empty = all(len(h) == 0 for h in self.player_hands)
        deck_empty = len(self.deck) == 0
        return hands_empty or deck_empty

    def render(self, mode="human"):
        print(f"Hand: {self.player_hands[0]}")
        print(f"Field: {self.field}")
        print(f"Collected: {self.collected_cards[0]}")
        print(f"Opponent Collected: {self.collected_cards[1]}")
        print(f"Score: You {self.your_score} - Opponent {self.opponent_score}")
        print(f"Round: {self.round_count + 1}/{self.max_rounds}\n")

    def _cards_to_binary(self, cards):
        binary = np.zeros(self.num_cards, dtype=np.int8)
        for card in cards:
            binary[card] = 1
        return binary

    def _card_to_binary(self, card):
        binary = np.zeros(self.num_cards, dtype=np.int8)
        if card is not None:
            binary[card] = 1
        return binary