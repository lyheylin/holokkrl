# Environment Reference

This page describes `KoiKoiEnv` in `environment/koikoienv.py`, a [Gymnasium](https://gymnasium.farama.org/) environment. The game rules are in [RULES.md](RULES.md). Everything here is the interface and training setup, and can change without changing the game.

## Overview

- The agent is always player 0. The opponent is built into the environment and plays inside `step()`.
- One episode is one match of `max_rounds` rounds.
- Each `step()` handles one agent decision, so a turn can take up to three steps: play, draw choice and Koi-Koi decision.

## Actions

`Discrete(148)`. Check `env.action_masks()` for the actions that are legal right now.

| Actions | Meaning | Legal when |
|---|---|---|
| 0–143 | Play a hand slot onto a field slot: `env.encode_play(hand_idx, field_idx)`, which equals `hand_idx * 18 + field_idx` | Playing, and the card and slot satisfy R4.3 |
| Field slot 17 (`env.NO_MATCH`) | Play the card with no capture | The card has no match on the field |
| 144 (`KOIKOI_ACTION`) | Declare Koi-Koi | At a Koi-Koi decision |
| 145 (`STOP_ACTION`) | Stop and score | At a Koi-Koi decision |
| 146 (`DRAW_MATCH_FIRST`) | Capture the lower card ID of the two matches | At a draw choice |
| 147 (`DRAW_MATCH_SECOND`) | Capture the higher card ID of the two matches | At a draw choice |

- **Slots:** hand and field are sorted by card ID, so slot *n* is the *n*th set bit of the `hand` or `field` observation.
- **Field size:** the field holds at most 17 cards. The deal covers at least 3 months, and only a card with no month on the field can stay there.
- **Three matches:** any of the three field slots is legal, and all give the same result.

## Observations

`Dict` space:

| Key | Space | Meaning |
|---|---|---|
| `hand`, `field` | `MultiBinary(48)` | Cards in your hand and on the field |
| `collected`, `opponent_collected` | `MultiBinary(48)` | Each player's collected pile |
| `last_drawn_card` | `MultiBinary(48)` | Your most recent draw this round |
| `cards_left_in_deck` | `Discrete(49)` | Draw pile size |
| `your_round_score`, `opponent_round_score` | `Discrete(52)` | Points awarded this round, which stay 0 until someone stops |
| `your_score`, `opponent_score` | `Discrete(51 * max_rounds + 1)` | Match totals |
| `round` | `Discrete(max_rounds)` | Current round, starting at 0 |
| `phase` | `Discrete(3)` | 0 play, 1 draw choice, 2 Koi-Koi decision |
| `turn` | `Discrete(2)` | Always 0 when returned, so it carries no information |

The opponent's hand and the deck order are hidden. The observation doesn't say who dealt or whether the opponent declared Koi-Koi.

## Opponent

Despite the `opponent_type="random"` argument, which is ignored, the built-in opponent is one fixed policy:

- It plays a random card that can capture, or any random card if none can.
- It picks randomly between two matches.
- At each decision it declares Koi-Koi with probability 0.3 and otherwise stops.

## Rewards

Rewards are training signals and not part of the rules. They are summed per step:

| Component | Value | When |
|---|---|---|
| Illegal action | -1 | The state doesn't change |
| Progress shaping | See weights below, per card count gained | You capture cards, on a play or a draw |
| Ongoing yaku | Per yaku held: Kasu 0.5; Tane, Tanzaku, Akatan and Aotan 1.0; Sankou and Inoshikachou 1.5; Ame-Shikou 1.75; Shikou 2.0; Gokou 3.0 | End of each of your turns |
| Formation bonus | First time per round: Kasu 4; Tane and Tanzaku 8; Akatan and Aotan 10; Sankou and Inoshikachou 12; Ame-Shikou 15; Shikou 18; Gokou 30 | Yaku completed |
| Game points | Your yaku total | You stop |
| Blocking penalty | See weights below, floored at -2.0 per opponent turn | Opponent captures cards, except on its opening turn of a round |
| Round outcome | +12 win, -8 loss, 0 draw | Round ends |

| Category | Brights | Poetry | Blue | Ribbon | Animal | Plain | Boar/deer/butterfly |
|---|---|---|---|---|---|---|---|
| Shaping weight | 0.8 | 1.0 | 1.0 | 0.3 | 0.35 | 0.12 | 1.1 |
| Blocking weight | -0.8 | -1.0 | -1.0 | -0.3 | -0.4 | -0.1 | -1.1 |

A card can count in more than one category. For example, a poetry ribbon counts as both Poetry and Ribbon.

**Shaped reward is not a measure of skill.** It doesn't track game points, so report points per round and win rate. See [ROADMAP.md](ROADMAP.md).

## Episode behaviour

- **Termination:** `terminated` is true after the last round.
- **Truncation:** `truncated` is true after 100 illegal actions in a row, which stops a deterministic policy from repeating one forever.
- **New rounds:** a step that ends a round returns the first observation of the next round. If the opponent deals, it has already taken its opening turn, reported in `info["opening_opponent_turn"]`. `reset()` reports it the same way.
- **Seeding:** `reset(seed=n)` reproduces the whole match, given the same actions.

## Useful `info` keys

| Key | Meaning |
|---|---|
| `error` | The action was illegal |
| `awaiting_koikoi`, `awaiting_draw_match` | A decision is needed next |
| `yaku` | Yaku you currently hold, as `(name, points)` pairs |
| `stopped`, `koikoi` | Your decision this step |
| `player_field_match`, `player_field_captured` | Chosen field card and all cards captured by your play |
| `player_drawn_card`, `player_draw_match`, `player_draw_captured` | Your draw and what it captured |
| `opponent_played_card`, `opponent_play_match`, `opponent_drawn_card`, `opponent_draw_match` | The opponent's turn |
| `opponent_yaku`, `opponent_koikoi` | Opponent's yaku, and its decision if it made one this turn |
| `ongoing_yaku_reward`, `formation_bonus`, `new_yakus`, `blocking_penalty`, `outcome_bonus` | Reward components |
| `round_over`, `match_over` | Round and match status |
