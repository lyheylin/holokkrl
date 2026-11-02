# Holo's Hanafuda Rules Checklist

This records how the traditional Koi-Koi mode in **hololive Holo's Hanafuda** works, as checked in the game. Holo Awase, the power-up variant, is out of scope. No public source has the full rules. [RULES.md section 10](RULES.md#10-target-game-holos-hanafuda) turns these results into rules, so look rules up there. [Open items](#open-items) lists what's still open, and the [evidence log](#evidence-log) lists the screenshots saved so far. [HOLOS_HANAFUDA_CARDS.md](HOLOS_HANAFUDA_CARDS.md) maps the game's cards to the engine's.

The [free Steam demo](https://store.steampowered.com/app/3758120/hololive_Holos_Hanafuda_Demo/) includes Koi-Koi, offline, on Windows.

## Open items

This is the list to work through. Close an item by recording what settled it and removing its row.

### Blocks building a rule

| Item | What's needed | Evidence that would settle it |
|---|---|---|
| G2 | How the R10.2 ribbon bonus works when ribbons overlap with Tanzaku or with the other ribbon yaku | A score screen with Akatan or Aotan plus extra ribbons, ideally also one with all 6 |

### Not seen in the game

The rule shown is assumed until it's seen.

| Item | Question | Assumed rule | Evidence that would settle it |
|---|---|---|---|
| B4 | Does four of a month on the field void the deal? | Yes | Seeing it happen, or a help page |
| B5 | Do four pairs on the field void the deal? | Yes (R10.9) | Seeing it happen, or a help page |
| D5 | Can both players declare Koi-Koi in a round? | No, because D4 ends the round first | A round where it happens would disprove this |
| F2 | Hands run out after a Koi-Koi with no new yaku | 0 for both | The score screen from such a round |
| F3 | Hands run out with a yaku never stopped on | 0 for both | The score screen from such a round |
| F4 | Can the match length be changed? | 3 rounds | The mode's setup screen |
| F5 | What decides a tied match? | A draw | The result screen from a tied match |

### Recorded, but not yet matched to a screenshot

Your recorded results are the only evidence for these so far.

| Rule | Checklist | Screenshot to look for |
|---|---|---|
| R10.1: viewing yaku | A6 to A10 | Hanami, Tsukimi or both, ideally with a bright yaku |
| R10.3: sake cup counts toward Kasu | A20 | A Kasu group that includes card 32 |
| R10.4: Teshi and Kuttsuki | A22, B6 to B8 | Either result, or a help page |
| R10.5: dealer switches after a drawn round | B3 | A drawn round, then the next round's first player |
| R10.6: yaku after the opponent's Koi-Koi ends the round | D4 | That round's score screen |
| R10.7: 7 or more doubles | E1 | A score of 7 or more |
| R10.8: doubling after the opponent's Koi-Koi, and ×4 | E2, E3 | A score after the opponent's Koi-Koi, one of them with a total of 7 or more |
| Bright yaku and Inoshikachou points | A1 to A5, A11 | Their score screens |

### Cards not yet seen in a type's group

Their types come from their position in the card list. Any score or collected screen that shows them confirms them: 0, 1, 2, 3, 15, 16, 19, 24, 26, 28, 30, 31, 32, 37, 38, 39, 40, 44.

### Building the rules

None of the rules in RULES.md section 10 is in the engine yet. That work is tracked in [Phase 0 of the roadmap](ROADMAP.md#phase-0-foundations).

## Evidence log

Images are in the local [`screenshots/`](../screenshots/README.md) folder.

| File | Shows | Settles | Test |
|---|---|---|---|
| `card_list.png` | All 48 cards, by month | The card mapping in [HOLOS_HANAFUDA_CARDS.md](HOLOS_HANAFUDA_CARDS.md) | |
| `round1_result.png` | Round 1 score: Tane 1, total 1 | Part of A18 | `tests/test_score_screens.py` |
| `round2_result.png` | Round 2 score: Tan 1, Kasu 1, total 2 | Part of A17, A19 and A21 | `tests/test_score_screens.py` |
| `round3_collected.png` | Everything collected in round 3 | Card types of the 20 cards | `tests/test_score_screens.py` |
| `round3_result.png` | Round 3 score: Tan 1, Kasu 1, total 2 | Part of A17, A19 and A21 | `tests/test_score_screens.py` |

## How to record results

1. Capture these screens first, since they may settle most of the list at once:
   - **S1:** the in-game yaku list.
   - **S2:** any tutorial or help page on Koi-Koi rules.
   - **S3:** the mode's setup screen, and any rule options on it.
2. Save score screens with the collected cards visible in [`screenshots/`](../screenshots/README.md). These become test cases.
3. Fill in the **Result** column as you go. Write "not seen" for anything that didn't come up.

Rare cases may not come up in a short session, especially B4 to B8 and A1. Anything not seen stays marked unverified in RULES.md, with the most common rule assumed, until it's observed.

## A. Yaku and points

Mostly from S1.

| #   | Unknown                                                                               | Engine assumes             | Result                                                                                            |
| --- | ------------------------------------------------------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------- |
| A1  | Gokou (5 brights) points                                                              | 10                         | 10                                                                                                |
| A2  | Shikou (4 brights, no rain man) points                                                | 8                          | 8                                                                                                 |
| A3  | Ame-Shikou (4 brights with rain man) points                                           | 7                          | 7                                                                                                 |
| A4  | Sankou (3 brights) points                                                             | 5                          | 5                                                                                                 |
| A5  | Do 3 brights including the rain man score?                                            | No                         | No                                                                                                |
| A6  | Hanami (curtain + sake cup) points                                                    | Not implemented            | 5                                                                                                 |
| A7  | Tsukimi (moon + sake cup) points                                                      | Not implemented            | 5                                                                                                 |
| A8  | Holding both viewing yaku: is it the sum, or a separate yaku?                         | Not implemented            | 10                                                                                                |
| A9  | Do the viewing yaku stack with bright yaku?                                           | Not implemented            | yes                                                                                               |
| A10 | Does capturing a November card or the rain man cancel the viewing yaku?               | Not implemented            | no                                                                                                |
| A11 | Inoshikachou points                                                                   | 5                          | 5                                                                                                 |
| A12 | Does Inoshikachou gain points for extra animals?                                      | No                         | no                                                                                                |
| A13 | Akatan points                                                                         | 5                          | 5                                                                                                 |
| A14 | Aotan points                                                                          | 5                          | 5                                                                                                 |
| A15 | Do Akatan and Aotan gain points for extra ribbons?                                    | No                         | 1 per                                                                                             |
| A16 | Holding Akatan and Aotan: is it the sum, or a separate yaku? Does Tanzaku also score? | Sum, and Tanzaku scores    | yes                                                                                               |
| A17 | Tanzaku: cards needed, points, bonus per extra                                        | 5 cards, 1, +1             | 5, 1, 1                                                                                           |
| A18 | Tane: cards needed, points, bonus per extra                                           | 5 cards, 1, +1             | 5, 1, 1                                                                                           |
| A19 | Kasu: cards needed, points, bonus per extra                                           | 10 cards, 1, +1            | 10, 1, 1                                                                                          |
| A20 | Does the sake cup also count toward Kasu?                                             | No                         | Yes                                                                                               |
| A21 | Do other yaku stack with each other, or does only the highest score?                  | All stack, one bright yaku | all stack, one bright                                                                             |
| A22 | Any yaku not listed above, including game-specific ones?                              | None                       | Yes, Teshi: four same month cards in opening hand, Kuttsuki: 4 paired month cards in opening hand |

## B. Deal and first player

From S2, or seen in play.

| #   | Unknown                                                                         | Engine assumes  | Result        |
| --- | ------------------------------------------------------------------------------- | --------------- | ------------- |
| B1  | Who deals the first round, and how is it chosen?                                | Random          | Random        |
| B2  | Who plays first after a win? After a loss?                                      | Round winner    | Winner        |
| B3  | Who plays first after a drawn round?                                            | Same dealer     | Switch dealer |
| B4  | Does four of a month on the field void the deal?                                | Yes             | Not seen      |
| B5  | Do four pairs on the field void the deal?                                       | No              | Not seen      |
| B6  | Does an opening hand with four of a month win at once (Teshi)? How many points? | No              | yes, 6        |
| B7  | Does an opening hand with four pairs win at once (Kuttsuki)? How many points?   | No              | yes, 6        |
| B8  | What happens if both players are dealt an instant-win hand?                     | Not implemented | Restart round |

## C. Playing cards

Try these in play.

| #   | Unknown                                                                                                                  | Engine assumes | Result |
| --- | ------------------------------------------------------------------------------------------------------------------------ | -------------- | ------ |
| C1  | With one card that can capture and one that can't, is the non-capturing card playable? This sets `must_capture_if_able`. | Yes            | Yes    |
| C2  | Can a card that has a match be played without capturing?                                                                 | No             | No     |
| C3  | Two matches for a played card: do you choose?                                                                            | Yes            | Yes    |
| C4  | Two matches for a drawn card: do you choose?                                                                             | Yes            | Yes    |
| C5  | Is any card wild, such as the November lightning card?                                                                   | No             | No     |

## D. Koi-Koi decisions

Try these in play.

| #   | Unknown                                                                                                           | Engine assumes  | Result   |
| --- | ----------------------------------------------------------------------------------------------------------------- | --------------- | -------- |
| D1  | After declaring, are you offered a new decision on a later new yaku?                                              | Yes, repeatedly | Yes      |
| D2  | Is the decision also offered when an extra card only raises Tanzaku, Tane or Kasu?                                | Yes             | Yes      |
| D3  | Is the decision offered on your final turn, or does the round end automatically?                                  | Offered         | Offered  |
| D4  | If your opponent declared and you then complete a yaku, does the round end automatically, or do you still choose? | You choose      | Ends     |
| D5  | Can both players have declared Koi-Koi in the same round?                                                         | Yes             | Not seen |
| D6  | If you declared and your opponent stops, do you score 0?                                                          | Yes             | Yes      |

## E. Scoring

Try these in play, and read them from score screens.

| #   | Unknown                                                                              | Engine assumes | Result      |
| --- | ------------------------------------------------------------------------------------ | -------------- | ----------- |
| E1  | Does a total of 7 or more double?                                                    | No             | Yes         |
| E2  | Scoring after the opponent declared: is it doubled? A guide says yes, so confirm it. | No             | Yes         |
| E3  | Do both doublings combine to ×4?                                                     | No             | Yes         |
| E4  | Does your own Koi-Koi raise your score, per declaration? By how much?                | No             | No          |
| E5  | Do brights face up at the deal multiply the score?                                   | No             | No          |
| E6  | Is a round's score capped?                                                           | No             | No          |
| E7  | Does the loser lose points, or does only the winner gain?                            | Winner only    | Winner only |

## F. End of round and match

Try these in play, or read them from S3.

| #   | Unknown                                                                          | Engine assumes       | Result     |
| --- | -------------------------------------------------------------------------------- | -------------------- | ---------- |
| F1  | Hands run out and nobody holds a yaku: what is scored, and who?                  | 0 for both           | 0 for both |
| F2  | Hands run out after a Koi-Koi with no new yaku: what is scored?                  | 0 for both           | Not seen   |
| F3  | Hands run out while a player holds a yaku they never stopped on: what is scored? | 0 for both           | Not seen   |
| F4  | Is an offline match always 3 rounds, or can the length be changed?               | 3 by default         | Not seen   |
| F5  | What decides a tied match: a draw, an extra round, or the dealer?                | Draw                 | Not seen   |
| F6  | Do players start from a set score? Can a match end early, such as at 0 points?   | From 0, no early end | From 0, no |

## G. Questions raised by the results

These came up while turning the results into rules. Until they're answered, RULES.md section 10 uses the reading shown, or marks the rule as open.

| #   | Unknown                                                                                                                         | Reading used for now                                                               | Result          |
| --- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------- |
| G1  | A16 was answered "yes" to an either-or question. Do Akatan and Aotan add together, and does Tanzaku also score?                 | Both yes, as the engine does                                                       | Both yes        |
| G2  | For the A15 bonus, what do these score before any doubling? (a) Akatan plus 2 other ribbons. (b) All 6 poetry and blue ribbons. | Open: a literal reading gives (a) 7 + Tanzaku 1 = 8 and (b) 8 + 8 + Tanzaku 2 = 18 | Not sure        |
| G3  | If the played card completes a yaku, does the decision or automatic end come before the draw?                                   | After the draw, as in R5.1                                                         | After the draw. |
| G4  | Who deals after a round restarted under B8?                                                                                     | Same dealer                                                                        | Same dealer     |
| G5  | Score screens that show a rule from RULES.md section 10: doubling, a Koi-Koi, a viewing yaku, the sake cup in Kasu, or a ribbon bonus. A ribbon bonus screen would also settle G2. | The three saved rounds show none of these | |
