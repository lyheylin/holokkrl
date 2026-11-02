# Koi-Koi Rules (Project Ruleset v1.1)

**This file is the source of truth for the game rules in this project.** If the code and this file disagree, treat it as a bug and fix the code, or change this file on purpose and record it in the [changelog](#changelog). Don't settle a rules question from memory or another website.

Koi-Koi has no single official rulebook, and sources disagree on many details. This ruleset describes what the engine implements today. It uses a common yaku table with no score multipliers and no instant wins. Section 8 lists every place where other sources differ, so that dropping a rule is a recorded decision. Section 9 lists the rules you can switch with a flag.

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

## Sources

Accessed 2026-11-02. These were read through automated page extraction, so check the original before relying on a fine detail.

- [Koi-Koi, English Wikipedia](https://en.wikipedia.org/wiki/Koi-Koi): yaku table, multipliers and instant wins. The article warns it relies on a single source.
- [こいこい, Japanese Wikipedia](https://ja.wikipedia.org/wiki/こいこい): closest overall match, including optional multipliers and no-score draws.
- [RulesPal Koi-Koi rulebook](https://rulespal.com/koi-koi/rulebook): full turn flow, yaku table and draw rule.
- [Sloperama hanafuda rules](https://sloperama.com/hanafuda/rules.html): turn flow, draws and instant wins. It plays to a 50-point target.
- [Board Game Arena Koi-Koi help](https://en.doc.boardgamearena.com/Gamehelpkoikoi): capture rule, multiplier variants and optional viewing yaku.
- [Nintendo kids' hanafuda page](https://www.nintendo.co.jp/kids/160615/hanafuda02/): seen only as a search result, which gave Gokou 10 and Inoshikachou 5. Nintendo's fuller rules guide could not be retrieved, so it is not used here.

## Changelog

- **v1.1 (2026-11-02):** Added rule flags (section 9) and `must_capture_if_able` for ruling D1. Default gameplay is unchanged.
- **v1 (2026-11-02):** First version, documenting the engine at commit `d054d12`.
