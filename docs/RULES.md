# Koi-Koi Rules (Project Ruleset v1.1)

**This file is the source of truth for the game rules in this project.** If the code and this file disagree, treat it as a bug and fix the code, or change this file on purpose and record it in the [changelog](#changelog). Don't settle a rules question from memory or another website.

Koi-Koi has no single official rulebook, and sources disagree on many details. This ruleset describes what the engine implements today. It uses a common yaku table with no score multipliers and no instant wins. Section 8 lists every place where other sources differ, so that dropping a rule is a recorded decision. Section 9 lists the rules you can switch with a flag, section 10 gives the rules of the game the first model is being trained for, and section 11 explains where rules are set and how to change them.

Rule IDs such as `R4.2` are stable. Use them in code comments, tests and discussion.

## 1. Equipment

**R1.1** Two players use a 48-card hanafuda deck with 12 months and 4 cards per month. The deck has 5 brights, 9 animals, 10 ribbons and 24 plains.

**R1.2** Each card has exactly one type. The sake cup (card 32) is only an animal and doesn't also count as a plain.

| Month | Plant | Card IDs and types |
|---|---|---|
| Jan | Pine | 0 bright (crane), 1 poetry ribbon, 2 plain, 3 plain |
| Feb | Plum | 4 animal (warbler), 5 poetry ribbon, 6 plain, 7 plain |
| Mar | Cherry | 8 bright (curtain), 9 poetry ribbon, 10 plain, 11 plain |
| Apr | Wisteria | 12 animal (cuckoo), 13 ribbon, 14 plain, 15 plain |
| May | Iris | 16 animal (bridge), 17 ribbon, 18 plain, 19 plain |
| Jun | Peony | 20 animal (butterflies), 21 blue ribbon, 22 plain, 23 plain |
| Jul | Bush clover | 24 animal (boar), 25 ribbon, 26 plain, 27 plain |
| Aug | Susuki | 28 bright (moon), 29 animal (geese), 30 plain, 31 plain |
| Sep | Chrysanthemum | 32 animal (sake cup), 33 blue ribbon, 34 plain, 35 plain |
| Oct | Maple | 36 animal (deer), 37 blue ribbon, 38 plain, 39 plain |
| Nov | Willow | 40 bright (rain man), 41 animal (swallow), 42 ribbon, 43 plain (lightning) |
| Dec | Paulownia | 44 bright (phoenix), 45 plain, 46 plain, 47 plain |

## 2. Match structure

**R2.1** A match is a fixed number of rounds. The engine default is 3, and `max_rounds` changes it. Traditional play uses 12 rounds, and 6 is also common.

**R2.2** The player with the higher total score after the last round wins. Equal totals are a drawn match.

**R2.3** The dealer of the first round is chosen at random.

**R2.4** The winner of a round deals the next round. After a drawn round, the same dealer deals again.

## 3. The deal

**R3.1** Each player receives 8 cards, hidden from the other player. 8 cards go face up on the field, and the remaining 24 form the face-down draw pile.

**R3.2** If all four cards of a month land on the field, the deal is void and is redone.

## 4. Turns

**R4.1** The dealer plays first, then players alternate. Each player takes 8 turns in a round.

**R4.2** A turn has two steps, in this order:

1. **Play:** play any one card from your hand and resolve it under R4.3. Flag R9.1 can restrict which cards you may play.
2. **Draw:** turn over the top card of the draw pile and resolve it under R4.3.

**R4.3** A played or drawn card resolves by how many field cards share its month:

| Same-month cards on the field | Result |
|---|---|
| 0 | The card stays on the field. |
| 1 | You must capture that card. Both go to your collected pile. |
| 2 | You must capture one of them, and you choose which. Both the played and the drawn card follow this rule. |
| 3 | You capture all three. All four cards go to your collected pile. |

**R4.4** Collected cards are visible to both players and stay collected for the rest of the round.

## 5. Yaku

**R5.1** Yaku are checked on your collected pile after your draw step. Only the cards you collected count.

**R5.2** At most one bright yaku applies, the highest you qualify for. All other yaku stack with each other and with a bright yaku.

| Yaku | Requirement | Points |
|---|---|---|
| Gokou | All 5 brights | 10 |
| Shikou | 4 brights, not including the rain man | 8 |
| Ame-Shikou | 4 brights, including the rain man | 7 |
| Sankou | 3 brights, not including the rain man | 5 |
| Inoshikachou | Boar, deer and butterflies (24, 36, 20) | 5 |
| Akatan | All 3 poetry ribbons (1, 5, 9) | 5 |
| Aotan | All 3 blue ribbons (21, 33, 37) | 5 |
| Tanzaku | 5 or more ribbons of any kind | 1, +1 per ribbon past 5 |
| Tane | 5 or more animals | 1, +1 per animal past 5 |
| Kasu | 10 or more plains | 1, +1 per plain past 10 |

**R5.3** Two brights plus the rain man is not a yaku.

**R5.4** Your *yaku total* is the sum of all yaku you currently hold. For example, holding all six poetry and blue ribbons gives Akatan 5 + Aotan 5 + Tanzaku 2 = 12.

## 6. Koi-Koi and scoring

**R6.1** You get a decision at the end of your turn only if your yaku total is higher than it has been at any earlier point in the round. A new yaku always raises it, and so does an extra card in Tanzaku, Tane or Kasu.

**R6.2** You must choose one of:

- **Stop:** you score your current yaku total, your opponent scores 0 even if they hold yaku, and the round ends.
- **Koi-Koi:** nobody scores, and play continues with your opponent's turn.

**R6.3** Points are only awarded by stopping. A yaku you hold is not banked if you continue.

**R6.4** You may declare Koi-Koi any number of times in a round. After declaring it, you can stop only at your next R6.1 decision.

**R6.5** If your opponent stops after you declared Koi-Koi, you score 0 for the round.

**R6.6** The score is not multiplied. There is no doubling at 7 or more points, for Koi-Koi, or for face-up brights.

**R6.7** The decision is also offered on your final turn, even though choosing Koi-Koi there means scoring nothing.

## 7. End of a round

**R7.1** A round ends when a player stops, or when both hands are empty.

**R7.2** If both hands empty with no stop, the round is a draw. Both players score 0, including any player who holds yaku or declared Koi-Koi. The dealer stays the same.

## 8. Rulings and differences from other sources

### Rulings where sources disagree

| ID | Project ruling | What the sources say |
|---|---|---|
| D1 | By default, a card you play can be any card in your hand, even if a different card could capture (R4.2). The other reading is available as flag R9.1. | Japanese Wikipedia doesn't address it. English Wikipedia and Board Game Arena can be read as requiring a capture whenever any hand card can make one. Set the flag to match the game you're playing on. |
| D2 | Sankou excludes the rain man (R5.2). | English and Japanese Wikipedia exclude it. RulesPal's table lists it among the eligible cards. |
| D3 | Akatan, Aotan and Inoshikachou have no +1 for extra cards (R5.2). | Wikipedia lists no bonus. RulesPal adds +1 per extra card. |
| D4 | Koi-Koi can be declared repeatedly (R6.4). | Wikipedia notes both one call per hand and one per yaku-forming turn. |
| D5 | A higher Tanzaku, Tane or Kasu count re-offers the decision (R6.1). | Sources commonly refer to forming a yaku and rarely address upgrades directly. This is the project's reading. |
| D6 | A drawn round scores 0 for both players (R7.2). | Sloperama, RulesPal and Japanese Wikipedia agree. English Wikipedia gives the dealer 1 point, and Board Game Arena's default gives the start player 6. |
| D7 | The match length defaults to 3 rounds (R2.1). | 12 is traditional, and 6 is also used. The default of 3 is a project convenience. |

### Common rules this ruleset leaves out

Most sources treat the first three rows as standard, so **they matter if the goal is to beat opponents playing common rules.** None are implemented.

| Rule | What it does | Sources |
|---|---|---|
| Score multipliers | Double a total of 7 or more. Also double when the opponent had declared Koi-Koi. Together they make ×4. | Wikipedia (English and Japanese) and RulesPal. Japanese Wikipedia says some rulesets don't use them. Board Game Arena and Sloperama use other multiplier systems. |
| Viewing yaku | Tsukimi-zake (moon + sake cup) and Hanami-zake (curtain + sake cup), 5 points each. | Wikipedia and RulesPal list them. Wikipedia and Board Game Arena note they may be turned off. |
| Teshi and Kuttsuki | An opening hand of four of a month, or four pairs, wins 6 points at once. | Wikipedia, RulesPal, Sloperama and Board Game Arena. |
| Four pairs on the field | Voids the deal, like R3.2. | Wikipedia, RulesPal, Sloperama and Board Game Arena. |
| Sake cup as a plain | It also counts toward Kasu. | Wikipedia notes this as a rule-dependent option. |
| Point value tables | Higher values such as Gokou 15. | Japanese Wikipedia lists these as alternatives. |
| Dealer's privilege | The dealer scores on a drawn round. | See D6. |

## 9. Rule flags

Flags switch between versions of a rule, because the games a model plays on may differ. Each flag has a default, and with every flag at its default the game follows the rules above.

| ID | Flag | Default | When on |
|---|---|---|---|
| R9.1 | `must_capture_if_able` | Off | If any card in your hand can capture, you must play one of those cards. You may discard only when none of them can. |

**R9.2** A model may only run on an engine with exactly the same flags and ruleset version it was trained under. Loading it under anything else is refused. A model with no recorded rules is also refused.

**R9.3** A flag applies to both players for a whole match and can't change during it. Changing a flag or the ruleset version means training a new model.

**R9.4** The ruleset version in this file's title must match `RULESET_VERSION` in `holokkrl/game/rules.py`. Raise it whenever gameplay changes. Changes that only reword this file don't need a new version.

## 10. Target game: Holo's Hanafuda

The first model is being trained for the traditional Koi-Koi mode of **hololive Holo's Hanafuda**. Holo Awase, its power-up variant, is out of scope.

**This section is that game's ruleset, but the engine doesn't run it yet.** The engine follows sections 1 to 7 until the settings below are built. To look up a Holo's Hanafuda rule, check here first. If a rule isn't listed as different, sections 1 to 7 apply.

The checklist IDs below refer to [the checklist](HOLOS_HANAFUDA_CHECKLIST.md), which holds the recorded answers. Its `D` items are separate from the rulings `D1` to `D7` in section 8.

Each rule has one of these statuses:

- **Game:** checked in the game and recorded in the checklist.
- **Guide:** a published guide says so, but it wasn't seen in the game.
- **Assumed:** not seen, so the most common rule is assumed.

### Rules that differ from sections 1 to 7

Setting names are proposals until they're built. Each setting's default keeps the behaviour of sections 1 to 7, and the last value shown is the one this game uses.

| ID | Holo's Hanafuda rule | Replaces | Planned setting | Checklist | Status |
|---|---|---|---|---|---|
| R10.1 | Hanami (curtain + sake cup, cards 8 and 32) and Tsukimi (moon + sake cup, cards 28 and 32) score 5 each, or 10 together. They stack with bright yaku. Capturing a November card or the rain man doesn't cancel them. | R5.2 | `viewing_yaku`: off → on | A6 to A10 | Game |
| R10.2 | Akatan and Aotan gain 1 point per extra ribbon. Inoshikachou has no such bonus. | R5.2, ruling D3 | `ribbon_set_extra_points`: 0 → 1 | A12, A15 | Game, but see open item G2 |
| R10.3 | The sake cup also counts as a plain for Kasu, and it's still an animal. | R1.2, R5.2 | `sake_cup_counts_as_plain`: off → on | A20 | Game |
| R10.4 | An opening hand with four of a month (Teshi) or four pairs (Kuttsuki) wins 6 points at once. If both players are dealt one, the round restarts with the same dealer. | R3.1 | `opening_hand_win_points`: 0 → 6 | A22, B6 to B8, G4 | Game |
| R10.5 | The dealer switches after a drawn round. | R2.4, R7.2 | `draw_switches_dealer`: off → on | B3 | Game |
| R10.6 | If your opponent declared Koi-Koi and you complete a yaku, the round ends at once and you score it, with no decision. So only one player can declare Koi-Koi in a round. | R6.2 | `koikoi_ends_on_opponent_yaku`: off → on | D4, D5 | Game. The one-declarer part follows from it, and wasn't seen. |
| R10.7 | A yaku total of 7 or more is doubled. | R6.6 | `double_at_seven`: off → on | E1 | Game |
| R10.8 | A score is doubled if the opponent had declared Koi-Koi. With R10.7 this makes ×4. | R6.6 | `double_against_koikoi`: off → on | E2, E3 | Game |
| R10.9 | Four pairs on the field void the deal. | R3.2 | `field_four_pairs_void_deal`: off → on | B5 | Assumed |

R10.7 and R10.8 are applied to the yaku total. A total of 5 scored after the opponent declared is worth 10. A total of 7 is worth 14, or 28 after the opponent declared.

### Rules that match sections 1 to 7

These need no new setting. If one turns out to be wrong, it moves to the table above.

| Rule | Same as | Checklist | Status |
|---|---|---|---|
| Deck, 8 cards each and 8 on the field, dealer plays first | R1.1, R3.1, R4.1 | | Guide |
| Bright yaku points, and 3 brights with the rain man don't score | R5.2, R5.3 | A1 to A5 | Game |
| Inoshikachou, Akatan and Aotan are worth 5 each before any R10.2 bonus | R5.2 | A11, A13, A14 | Game |
| Akatan and Aotan add together, and Tanzaku also scores | R5.4 | A16, G1 | Game |
| Tanzaku 5 cards, Tane 5 cards, Kasu 10 cards, each worth 1 and +1 per extra | R5.2 | A17 to A19 | Game |
| All yaku stack, with one bright yaku at most | R5.2 | A21 | Game |
| First dealer is random, and the round winner deals next | R2.3, R2.4 | B1, B2 | Game |
| Four of a month on the field voids the deal | R3.2 | B4 | Assumed |
| A non-capturing card is playable while another card could capture, so `must_capture_if_able` stays off | R4.2, R9.1 | C1 | Game |
| A card with a match must capture, you choose between two matches, and no card is wild | R4.3 | C2 to C5 | Game |
| Koi-Koi can be repeated, a higher Tanzaku, Tane or Kasu re-offers it, and it's offered on the final turn | R6.1, R6.4, R6.7 | D1 to D3 | Game |
| If you declared and your opponent scores, you score 0 | R6.5 | D6 | Game |
| Yaku are checked after the draw, including when the played card completes one | R5.1 | G3 | Game |
| Your own Koi-Koi and face-up brights don't multiply, there's no score cap, and only the winner gains points | R6.6 | E4 to E7 | Game |
| Hands run out and nobody holds a yaku: 0 for both | R7.2 | F1 | Game |
| Hands run out with a yaku held or after a Koi-Koi: 0 for both | R7.2 | F2, F3 | Assumed |
| Match length is 3 rounds | R2.1 | F4 | Guide. Whether it can be changed wasn't seen. |
| Equal totals are a drawn match | R2.2 | F5 | Assumed |
| Players start from 0, and a match has no early end | R2.2 | F6 | Game |

### Still open

The checklist's [open items](HOLOS_HANAFUDA_CHECKLIST.md#open-items) track everything unsettled. R10.2 can't be built exactly until item G2 is answered, because it isn't known how the bonus works when ribbons overlap. Three rounds of score screens are saved and match the engine (`tests/test_score_screens.py`), but they only show Tane, Tanzaku and Kasu at low scores. None of the rules R10.1 to R10.9 has been tested against a score screen yet.

The game redraws the deck. [HOLOS_HANAFUDA_CARDS.md](HOLOS_HANAFUDA_CARDS.md) maps its cards to the card IDs in section 1. Each month's order matches, and the art can be misleading, so go by position.

Sources for this section, accessed 2026-11-02:

- [4Gamer rule guide](https://www.4gamer.net/games/873/G087373/20250715033/): deal, turns, cards, 3 rounds and doubling. Its yaku table is an image, so point values could not be read.
- [Famitsu review](https://www.famitsu.com/article/202507/47715): the stop or Koi-Koi decision, and that yaku lists can be viewed in the game.
- [Steam demo page](https://store.steampowered.com/app/3758120/hololive_Holos_Hanafuda_Demo/): the demo includes Koi-Koi.
- [Official site](https://holo-no-hanafuda.com/): checked, and no rules page was found.

## 11. How rules are set and changed

### Where each rule is set

Only `must_capture_if_able` and the match length can be set today. Everything else is written into the code, and the last column is what would need to change to make it configurable. The file names are short for `holokkrl/game/` (`rules.py`, `cards.py`, `yaku.py`) and `holokkrl/envs/` (`koikoi_env.py`, `rewards.py`).

| Rule | Set in | Today | Affected by |
|---|---|---|---|
| Rule flags and ruleset version | `RuleConfig`, `RULESET_VERSION` in `rules.py` | Configurable | |
| R1: deck, months and card types | `CARD_DATA` in `cards.py` | Fixed | |
| R2.1: match length | `max_rounds` argument of `KoiKoiEnv` | Configurable, but not part of a model's recorded rules | |
| R2.3: first dealer | `KoiKoiEnv.reset` | Fixed | |
| R2.4: next dealer | `KoiKoiEnv._end_round` | Fixed | R10.5 |
| R3.1: deal sizes | `max_hand_size`, `field_size` in `KoiKoiEnv.__init__` | Fixed | |
| R3.2: void deals | `KoiKoiEnv._deal` | Fixed | R10.9 |
| Instant wins at the deal | Not implemented. They'd go in `KoiKoiEnv._start_new_round`. | Absent | R10.4 |
| R4.2, R9.1: legal plays | `KoiKoiEnv.action_masks` | Flag | |
| R4.3: captures | `KoiKoiEnv._capture`, `_field_matches` | Fixed | |
| R5: yaku, requirements and points | `detect_yaku` in `yaku.py` | Fixed | R10.1, R10.2, R10.3 |
| R6.1, R6.2: decision and stop score, for you | `KoiKoiEnv._check_player_yaku`, `_step_koikoi_decision` | Fixed | R10.6, R10.7, R10.8 |
| R6.1, R6.2: decision and stop score, for the opponent | `KoiKoiEnv._opponent_turn` | Fixed | R10.6, R10.7, R10.8 |
| R7: end of a round | `KoiKoiEnv._check_round_end`, `_end_round` | Fixed | |

Some things that aren't rules still depend on them:

- **Both players:** the player and the built-in opponent have separate code for decisions and scoring. A rule change there has to be made in both.
- **Score limits:** `max_round_points` in `KoiKoiEnv.__init__` sets the observation's score ranges from `detect_yaku`. A multiplier has to raise it, or scores will fall outside the observation space.
- **Rewards:** `ONGOING_YAKU_REWARDS` and `FORMATION_BONUSES` in `rewards.py` are keyed by yaku name. A new yaku earns no shaped reward until it's added there. `yaku_progress` also counts cards by a single type.
- **Instant wins:** a round can end before anyone acts, including inside `reset`, which nothing handles yet.

### How to change a rule

1. **Record it.** Update sections 1 to 7 or 10 here. Holo's Hanafuda results also go in the checklist. Add a changelog entry.
2. **Add a setting if the rule varies between games.** Add a field to `RuleConfig` with a default that keeps the current behaviour, list it in section 9, and read it through `self.rules`.
3. **Change the code** in the places listed above, and add any script option needed.
4. **Raise the version** if gameplay changed (R9.4). Saved models are then refused, and so are models saved before a new setting was added, because the recorded rules no longer match (R9.2).
5. **Test it** with the setting on and off, and confirm that the default behaviour is unchanged.
6. **Re-measure the baselines** in [ROADMAP.md](ROADMAP.md) if the target rules changed.

If the game turns out to work differently and the setting already exists, only the preset value, its test and the tables here need changing.

### Making more rules configurable

- `RuleConfig` is the one place a game's rules are chosen. Anything else, such as a preset or a config file, should only build a `RuleConfig`, so that models keep recording and matching their rules.
- `signature()` records every `RuleConfig` field, so a new setting is automatically tied to saved models.
- Use a number for any setting with a value that might vary, such as `opening_hand_win_points`, and an on or off flag otherwise.
- A planned `RuleConfig.holos_hanafuda()` preset will turn on the values in section 10, with a `--holos-hanafuda` script option.
- To make a fixed rule configurable, such as the yaku points in `detect_yaku`, move its value into `RuleConfig` with the current value as the default.

## Sources

Accessed 2026-11-02. These were read through automated page extraction, so check the original before relying on a fine detail.

- [Koi-Koi, English Wikipedia](https://en.wikipedia.org/wiki/Koi-Koi): yaku table, multipliers and instant wins. The article warns it relies on a single source.
- [こいこい, Japanese Wikipedia](https://ja.wikipedia.org/wiki/こいこい): closest overall match, including optional multipliers and no-score draws.
- [RulesPal Koi-Koi rulebook](https://rulespal.com/koi-koi/rulebook): full turn flow, yaku table and draw rule.
- [Sloperama hanafuda rules](https://sloperama.com/hanafuda/rules.html): turn flow, draws and instant wins. It plays to a 50-point target.
- [Board Game Arena Koi-Koi help](https://en.doc.boardgamearena.com/Gamehelpkoikoi): capture rule, multiplier variants and optional viewing yaku.
- [Nintendo kids' hanafuda page](https://www.nintendo.co.jp/kids/160615/hanafuda02/): seen only as a search result, which gave Gokou 10 and Inoshikachou 5. Nintendo's fuller rules guide could not be retrieved, so it is not used here.

## Changelog

- **v1.1, update (2026-11-03):** Recorded the Holo's Hanafuda results and card mapping in section 10, and added section 11 on how rules are set and changed. Gameplay is unchanged.
- **v1.1, update (2026-11-02):** Added section 10 on the target game. Gameplay is unchanged.
- **v1.1 (2026-11-02):** Added rule flags (section 9) and `must_capture_if_able` for ruling D1. Default gameplay is unchanged.
- **v1 (2026-11-02):** First version, documenting the engine at commit `d054d12`.
