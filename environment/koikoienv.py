import bisect

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from environment.card_utils import get_card_info, get_month
from environment.card_utils import detect_yaku


class KoiKoiEnv(gym.Env):

    metadata = {"render_modes": ["human"]}

    PHASE_PLAY = 0
    PHASE_DRAW_MATCH = 1
    PHASE_KOIKOI = 2

    # Episode is truncated after this many illegal actions in a row, since an
    # illegal action leaves the state unchanged and a deterministic policy
    # would otherwise repeat it forever.
    MAX_CONSECUTIVE_ILLEGAL = 100

    def __init__(self, opponent_type="random", max_rounds=3):
        super(KoiKoiEnv, self).__init__()
        self.opponent_type = opponent_type

        # -- Action and Observation Setup --
        self.max_hand_size = 8
        self.field_size = 8  # cards dealt to the field
        self.num_cards = 48
        self.max_rounds = max_rounds
        self.current_yakus = {0: set(), 1: set()}

        # A card only stays on the field when no card of its month is there. The deal
        # covers at least 3 months (a month is never dealt 4 times), so the field can
        # grow by at most 9 cards.
        self.max_field_size = self.field_size + 9
        self.NO_MATCH = self.max_field_size

        # Action = play one card + choose match (play hand x * match field y + no match).
        # Hand and field are kept sorted by card id, so slot n is the nth set bit of the
        # matching observation vector.
        self.num_play_actions = self.max_hand_size * (self.max_field_size + 1)
        self.KOIKOI_ACTION = self.num_play_actions
        self.STOP_ACTION = self.num_play_actions + 1
        # When a drawn card matches two field cards: take the lower or higher card id.
        self.DRAW_MATCH_FIRST = self.num_play_actions + 2
        self.DRAW_MATCH_SECOND = self.num_play_actions + 3
        self.total_actions = self.num_play_actions + 4

        self.action_space = spaces.Discrete(self.total_actions)

        # Highest possible yaku value, reached by holding the entire deck.
        max_round_points = detect_yaku(range(self.num_cards))[1]

        # Observation = flattened card representations (hand, field, scores)
        self.observation_space = spaces.Dict({
            "hand": spaces.MultiBinary(self.num_cards),
            "field": spaces.MultiBinary(self.num_cards),
            "cards_left_in_deck": spaces.Discrete(49),
            "last_drawn_card": spaces.MultiBinary(self.num_cards),
            "collected": spaces.MultiBinary(self.num_cards),
            "opponent_collected": spaces.MultiBinary(self.num_cards),
            "opponent_round_score": spaces.Discrete(max_round_points + 1),
            "opponent_score": spaces.Discrete(max_round_points * self.max_rounds + 1),
            "your_round_score": spaces.Discrete(max_round_points + 1),
            "your_score": spaces.Discrete(max_round_points * self.max_rounds + 1),
            "turn": spaces.Discrete(2),
            "round": spaces.Discrete(self.max_rounds),
            "phase": spaces.Discrete(3),
        })

        self.reset()


    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        # Reset multi-round match
        self.round_count = 0
        self.your_score = 0
        self.opponent_score = 0
        self.match_over = False
        self.consecutive_illegal = 0
        self.dealer = int(self.np_random.integers(2))
        opening_info = self._start_new_round()
        info = {"opening_opponent_turn": opening_info} if opening_info is not None else {}
        return self._get_obs(), info

    def _start_new_round(self):
        self._deal()

        # Player hands and collected cards
        self.collected_cards = [[], []]
        self._player_progress = self._yaku_progress(self.collected_cards[0])
        self._opponent_progress = self._yaku_progress(self.collected_cards[1])
        self.current_yakus = {0: set(), 1: set()}
        # Highest yaku value each player has already been offered a decision on.
        self.best_yaku_points = {0: 0, 1: 0}

        self.last_drawn_card = None
        self.pending_draw_card = None

        # Round-specific scores (points are only awarded when a player stops)
        self.your_round_score = 0
        self.opponent_round_score = 0

        # Turn and Koi-Koi state
        self.turn = 0
        self.koikoi_pending = False
        self.pending_yaku = []
        self.pending_player = None
        self.koikoi_declared = [False, False]

        # Round control
        self.round_over = False
        self.winner = None
        self.last_yaku = []

        # The dealer plays first. One opening turn cannot complete a yaku, so it
        # cannot end the round.
        if self.dealer == 1:
            self.turn = 1
            opening_info, _ = self._opponent_turn()
            self.turn = 0
            return opening_info
        return None

    def _deal(self):
        while True:
            self.deck = list(range(self.num_cards))
            self.np_random.shuffle(self.deck)
            self.player_hands = [
                sorted(self.deck.pop(0) for _ in range(self.max_hand_size)),
                sorted(self.deck.pop(0) for _ in range(self.max_hand_size)),
            ]
            self.field = sorted(self.deck.pop(0) for _ in range(self.field_size))

            # Four of a month on the field could never be captured: redeal.
            months = [get_month(c) for c in self.field]
            if max(months.count(m) for m in months) < 4:
                return


    def _get_obs(self):
        return {
            "hand": self._cards_to_binary(self.player_hands[0]),
            "field": self._cards_to_binary(self.field),
            "cards_left_in_deck": len(self.deck),
            "last_drawn_card": self._card_to_binary(self.last_drawn_card),
            "collected": self._cards_to_binary(self.collected_cards[0]),
            "opponent_collected": self._cards_to_binary(self.collected_cards[1]),
            "opponent_round_score": self.opponent_round_score,
            "opponent_score": self.opponent_score,
            "your_round_score": self.your_round_score,
            "your_score": self.your_score,
            "turn": self.turn,
            # round_count reaches max_rounds once the match is over
            "round": min(self.round_count, self.max_rounds - 1),
            "phase": self._phase(),
        }

    def _phase(self):
        if self.koikoi_pending:
            return self.PHASE_KOIKOI
        if self.pending_draw_card is not None:
            return self.PHASE_DRAW_MATCH
        return self.PHASE_PLAY

    def encode_play(self, hand_idx, field_idx):
        """Action for playing a hand slot onto a field slot (or self.NO_MATCH)."""
        return hand_idx * (self.max_field_size + 1) + field_idx

    def action_masks(self):
        """Boolean array of the actions that are currently legal."""
        mask = np.zeros(self.total_actions, dtype=bool)
        if self.match_over:
            return mask
        phase = self._phase()
        if phase == self.PHASE_KOIKOI:
            mask[[self.KOIKOI_ACTION, self.STOP_ACTION]] = True
        elif phase == self.PHASE_DRAW_MATCH:
            mask[[self.DRAW_MATCH_FIRST, self.DRAW_MATCH_SECOND]] = True
        else:
            for hand_idx, card in enumerate(self.player_hands[0]):
                month = get_month(card)
                slots = [i for i, c in enumerate(self.field) if get_month(c) == month]
                # A card that can match must match.
                for slot in slots or [self.NO_MATCH]:
                    mask[self.encode_play(hand_idx, slot)] = True
        return mask

    # List of keys of info to return
    # "player_field_match": the matched field card (or None)
    # "player_field_captured": every field card captured by the played card
    # "player_drawn_card": the drawn card
    # "player_draw_match": matched field card from draw (or None)
    # "player_draw_captured": every field card captured by the drawn card
    # "awaiting_draw_match": True if the drawn card matches two field cards
    # "yaku": list of player yakus (if formed)
    # "awaiting_koikoi": True if awaiting decision
    # "opening_opponent_turn": opponent's first turn of the next round, if it deals
    def step(self, action):
        action = int(action)
        if not 0 <= action < self.total_actions or not self.action_masks()[action]:
            self.consecutive_illegal += 1
            truncated = self.consecutive_illegal >= self.MAX_CONSECUTIVE_ILLEGAL
            return self._get_obs(), -1, False, truncated, {"error": "Illegal action."}
        self.consecutive_illegal = 0

        info = {}
        reward = 0.0

        # Handle Koi-Koi or Stop
        if self.koikoi_pending:
            self.koikoi_pending = False
            if action == self.STOP_ACTION:
                points = sum(y[1] for y in self.pending_yaku)
                self.your_score += points
                self.your_round_score = points
                info.update({
                    "stopped": True,
                    "yaku": self.pending_yaku
                })
                return self._end_round(reward + points, info)
            self.koikoi_declared[0] = True
            info["koikoi"] = True
            return self._finish_player_turn(reward, info)

        # Choose which of two field cards the drawn card captures
        if self.pending_draw_card is not None:
            drawn_card = self.pending_draw_card
            self.pending_draw_card = None
            chosen = self._field_matches(drawn_card)[action - self.DRAW_MATCH_FIRST]
            info["player_draw_captured"] = self._capture(0, drawn_card, chosen)
            info["player_draw_match"] = chosen
            return self._check_player_yaku(reward, info)

        # Decode Action
        hand_idx, field_idx = divmod(action, self.max_field_size + 1)
        played_card = self.player_hands[0].pop(hand_idx)

        # Player Match Phase
        if field_idx == self.NO_MATCH:
            bisect.insort(self.field, played_card)
            info["player_field_match"] = None
            info["player_field_captured"] = []
        else:
            selected_field_card = self.field[field_idx]
            info["player_field_captured"] = self._capture(0, played_card, selected_field_card)
            info["player_field_match"] = selected_field_card
            reward += self._progress_reward()

        # Player Draw Phase
        if self.deck:
            drawn_card = self.deck.pop(0)
            self.last_drawn_card = drawn_card
            info["player_drawn_card"] = drawn_card
            matching_drawn = self._field_matches(drawn_card)

            if len(matching_drawn) == 2:
                self.pending_draw_card = drawn_card
                info["awaiting_draw_match"] = True
                return self._get_obs(), reward, False, False, info

            if matching_drawn:
                info["player_draw_captured"] = self._capture(0, drawn_card, matching_drawn[0])
                info["player_draw_match"] = matching_drawn[0]
            else:
                bisect.insort(self.field, drawn_card)
                info["player_draw_captured"] = []
                info["player_draw_match"] = None

        return self._check_player_yaku(reward, info)

    def _check_player_yaku(self, reward, info):
        reward += self._progress_reward()  # captures from the draw

        # Yaku Check for Player
        yakus, points = detect_yaku(self.collected_cards[0])
        yakus_set = set(y[0] for y in yakus)
        if yakus:
            info["yaku"] = yakus

        # ongoing (small) + formation (big) rewards
        ongoing_reward = sum(self.YAKU_REWARDS.get(y, 0) for y in yakus_set)
        new_yakus = yakus_set - self.current_yakus[0]
        formation_bonus = sum(self.YAKU_FORMATION_BONUS.get(y, 0) for y in new_yakus)

        reward += ongoing_reward + formation_bonus
        self.current_yakus[0] = self.current_yakus[0] | yakus_set  # accumulate

        # Different parameters --
        # progress_delta_reward: small stepwise nudges toward yaku formation.
        # ongoing_reward: holding yakus generates constant positive reinforcement.
        # formation_bonus: one-time bonus when new yaku appears.
        # points: official game score when yakus are scored.

        info["ongoing_yaku_reward"] = ongoing_reward
        info["formation_bonus"] = formation_bonus
        info["new_yakus"] = list(new_yakus)

        # A new or improved yaku offers the choice to stop or continue.
        if points > self.best_yaku_points[0]:
            self.best_yaku_points[0] = points
            self.pending_yaku = yakus
            self.koikoi_pending = True
            self.pending_player = 0
            info["awaiting_koikoi"] = True
            return self._get_obs(), reward, False, False, info

        return self._finish_player_turn(reward, info)

    def _finish_player_turn(self, reward, info):
        # Opponent Turn
        before_prog = self._opponent_progress
        self.turn = 1
        opponent_info, opponent_round_end = self._opponent_turn()
        self.turn = 0  # back to player
        info.update(opponent_info)

        # Blocking Penalty: opponent captured cards from the yaku pools we could still use
        after_prog = self._opponent_progress
        blocking_penalty = 0.0
        for k, penalty in self.YAKU_BLOCKING_PENALTIES.items():
            delta = after_prog[k] - before_prog[k]
            if delta > 0:
                blocking_penalty += penalty * delta

        # cap per step
        blocking_penalty = max(blocking_penalty, self.BLOCKING_PENALTY_CAP)
        reward += blocking_penalty
        info["blocking_penalty"] = blocking_penalty
        # ---

        if opponent_round_end or self._check_round_end():
            return self._end_round(reward, info)

        info["round_over"] = False
        info["match_over"] = False
        return self._get_obs(), reward, False, False, info

    def _end_round(self, reward, info):
        self.round_over = True

        # outcome bonus based on round score differential
        diff = self.your_round_score - self.opponent_round_score
        if diff > 0:
            outcome_bonus = 12  # won the round
            self.dealer = 0
        elif diff < 0:
            outcome_bonus = -8  # lost the round
            self.dealer = 1
        else:
            outcome_bonus = 0   # draw: same dealer again
        reward += outcome_bonus
        info["outcome_bonus"] = outcome_bonus

        self.round_count += 1
        self.match_over = self.round_count >= self.max_rounds
        if not self.match_over:
            opening_info = self._start_new_round()
            if opening_info is not None:
                info["opening_opponent_turn"] = opening_info

        info["round_over"] = True
        info["match_over"] = self.match_over
        return self._get_obs(), reward, self.match_over, False, info

    def _field_matches(self, card):
        month = get_month(card)
        return [c for c in self.field if get_month(c) == month]

    def _capture(self, player, card, field_card):
        """Capture field_card with card; with three of the month on the field, take all
        three. Returns the captured field cards."""
        matches = self._field_matches(card)
        captured = matches if len(matches) == 3 else [field_card]
        for c in captured:
            self.field.remove(c)
        self.collected_cards[player].extend([card, *captured])
        return captured

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
            # Opponent dealt and has played out its hand; the player plays the last card
            return info, done

        # --- Opponent Match Phase ---
        matching_cards = [c for c in hand if self._field_matches(c)]
        card_to_play = int(self.np_random.choice(matching_cards if matching_cards else hand))
        hand.remove(card_to_play)
        info["opponent_played_card"] = card_to_play

        matches = self._field_matches(card_to_play)
        if matches:
            match = int(self.np_random.choice(matches))
            self._capture(1, card_to_play, match)
            info["opponent_play_match"] = match
        else:
            bisect.insort(self.field, card_to_play)
            info["opponent_play_match"] = None

        # --- Opponent Draw Phase ---
        if self.deck:
            drawn_card = self.deck.pop(0)
            info["opponent_drawn_card"] = drawn_card
            matches = self._field_matches(drawn_card)
            if matches:
                match = int(self.np_random.choice(matches))
                self._capture(1, drawn_card, match)
                info["opponent_draw_match"] = match
            else:
                bisect.insort(self.field, drawn_card)
                info["opponent_draw_match"] = None

        self._opponent_progress = self._yaku_progress(collected)

        # --- Yaku Check for Opponent ---
        yakus, points = detect_yaku(collected)
        if yakus:
            info["opponent_yaku"] = yakus
        if points > self.best_yaku_points[1]:
            self.best_yaku_points[1] = points
            # Simple Koi-Koi logic: 30% chance to continue, otherwise stop
            if self.np_random.random() < 0.3:
                self.koikoi_declared[1] = True
                info["opponent_koikoi"] = True
            else:
                info["opponent_koikoi"] = False
                self.opponent_score += points
                self.opponent_round_score = points
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
        print(f"Round: {min(self.round_count + 1, self.max_rounds)}/{self.max_rounds}\n")

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

    def _yaku_progress(self, collected_cards):
        """
        Return a dict of counts useful for Yaku shaping.
        Keys: brights, poetry, blue, ribbon, animal, plain, ino_parts
        """
        prog = {
            "brights": 0,
            "poetry": 0,
            "blue": 0,
            "ribbon": 0,
            "animal": 0,
            "plain": 0,
            "ino_parts": 0,  # boar/deer/butterfly pieces
        }
        have_boar = have_deer = have_butterfly = False

        for cid in collected_cards:
            info = get_card_info(cid)  # {id, month, month_name, type, subtype}
            t = info["type"]
            st = info["subtype"]

            if t == "bright":
                prog["brights"] += 1
            elif t == "ribbon":
                prog["ribbon"] += 1
                if st == "poetry":
                    prog["poetry"] += 1
                if st == "blue":
                    prog["blue"] += 1
            elif t == "animal":
                prog["animal"] += 1
                if st == "boar":
                    have_boar = True
                if st == "deer":
                    have_deer = True
                if st == "butterfly":
                    have_butterfly = True
            elif t == "plain":
                prog["plain"] += 1

        prog["ino_parts"] = int(have_boar) + int(have_deer) + int(have_butterfly)
        return prog

    def _progress_reward(self):
        """Shaping for captures since the last call."""
        new_prog = self._yaku_progress(self.collected_cards[0])
        reward = self._progress_delta_reward(self._player_progress, new_prog)
        self._player_progress = new_prog
        return reward

    def _progress_delta_reward(self, before, after):
        # small, positive-only shaping for progress
        YAKU_SHAPING_WEIGHTS = {
            "brights": 0.8,   # was 0.5
            "poetry":  1.0,   # was 0.7
            "blue":    1.0,   # was 0.7
            "ribbon":  0.3,   # was 0.2
            "animal":  0.35,  # was 0.2
            "plain":   0.12,  # was 0.1
            "ino_parts": 1.1, # was 0.6
        }
        reward = 0.0
        for k, w in YAKU_SHAPING_WEIGHTS.items():
            delta = after[k] - before[k]
            if delta > 0:
                reward += w * delta
        return reward

    # Keys must match the yaku names returned by detect_yaku.
    YAKU_REWARDS = {
        "Kasu": 0.5,
        "Tane": 1.0,
        "Tanzaku":  1.0,
        "Sankou": 1.5,
        "Ame-Shikou": 1.75,
        "Shikou": 2.0,
        "Gokou":  3.0,
        "Inoshikachou": 1.5,
        "Akatan": 1.0,
        "Aotan":  1.0,
    }

    YAKU_FORMATION_BONUS = {
        "Kasu": 4,          # was 2
        "Tane": 8,          # was 5
        "Tanzaku":  8,      # was 5
        "Sankou": 12,       # was 8
        "Ame-Shikou": 15,
        "Shikou": 18,       # was 12
        "Gokou":  30,       # was 20
        "Inoshikachou": 12, # was 8
        "Akatan": 10,       # was 6
        "Aotan":  10,       # was 6
    }

    YAKU_BLOCKING_PENALTIES = {
        "brights":   -0.8,
        "poetry":    -1.0,
        "blue":      -1.0,
        "ribbon":    -0.3,
        "animal":    -0.4,
        "plain":     -0.1,
        "ino_parts": -1.1,
    }
    BLOCKING_PENALTY_CAP = -2.0  # per step floor
