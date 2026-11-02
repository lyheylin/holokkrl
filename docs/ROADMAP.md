# Roadmap

**Goal:** train a model that is proficient at actually winning Koi-Koi games.

"Proficient" is defined in [Phase 6](#phase-6-proficiency-validation) so that the goal can be tested. All numeric targets are provisional, and are expected to be recalibrated when Phase 2 produces real measurements.

## Where the project stands

- **Done:** a rules-tested game engine, a Gymnasium environment and a terminal harness.
- **Not useful yet:** the PPO script. It doesn't use action masking, and its one test run after the engine fixes made illegal moves until the match was cut off. The saved `models/ppo_koikoi.zip` predates those fixes and no longer loads.

### Baselines

Measured on 2026-11-02 at commit `d054d12`, with a one-off script not kept in the repo, over 1,500 12-round matches against the built-in opponent:

| Policy | Match win rate | Round win rate | Points per round (95% CI) | Shaped return per match |
|---|---|---|---|---|
| Random legal moves | 4.3% | 15.0% | -1.58 ± 0.05 | -10.4 |
| Random moves, always stop | 9.5% | 26.2% | -1.21 ± 0.05 | +8.4 |
| Greedy capture, always stop | 71.1% | 54.4% | +0.61 ± 0.05 | +157.3 |

"Points per round" is the score difference (yours minus the opponent's) averaged per round. Greedy plays the capture worth the most by a fixed card ranking.

Two conclusions shape this plan:

1. **Shaped reward is not tracking the game.** Greedy earns +157 shaped reward per match but only about +7 net points, so the agent is mostly being paid for things other than winning. A flat -8 for losing also ignores how many points the opponent scored.
2. **Results are noisy.** A round's score difference has a standard deviation of about 3.5 points, so a ±0.1 points-per-round estimate takes about 4,700 rounds. Small differences between agents can't be judged by a few games.

## Principles

- **Points per round and match win rate are the only measures of skill.** Shaped return is never used to compare agents.
- **Every result comes from the shared evaluation tool**, with confidence intervals, and with both seats played equally when the agent and opponent can swap.
- **Rules questions go to [RULES.md](RULES.md).** A rules change needs an updated ruleset, updated tests and new baselines, and makes earlier models obsolete.
- **Each phase has exit criteria.** If a phase's method doesn't beat what came before it, drop that method and record why.

## Phase 0: Foundations

**Goal:** a clean, documented starting point.

- Merge the documentation and project structure into `master`. The engine fixes are already merged.
- **Decide the target ruleset**, and whether to add the common rules v1 leaves out ([RULES.md section 8](RULES.md#common-rules-this-ruleset-leaves-out)). Multipliers especially change when Koi-Koi is worth declaring, so a model trained without them will misjudge that decision under common rules.
- Resolve ruling D1 (whether you may discard while another hand card can capture).

**Exit:** the documentation and structure are on `master`, and the target ruleset is written in RULES.md and implemented, with tests.

## Phase 1: Two-player engine

**Goal:** let any agent sit in either seat, which self-play and fair evaluation both need.

- Split a pure game core from the Gymnasium wrapper. The core handles rules, state and legal moves, with no rewards or built-in opponent.
- Make the wrapper take any opponent policy.
- Make observations seat-relative and able to include public facts that are missing today: who dealt, whether the opponent has declared Koi-Koi, and the opponent's hand size.
- Consider replacing the 148 slot-based actions with card-based actions, such as "play card 12", so that an action means the same thing in every state.
- Move ruleset options and rewards into configuration.

**Exit:** the existing rules tests pass against the core, seeded games match the current engine for the same choices (apart from any rule changes made on purpose), and a scripted policy can play either seat.

## Phase 2: Evaluation and baseline bots

**Goal:** a trustworthy measure of skill before serious training.

- Build a common agent interface and an arena that plays any two agents in equal seats, using shared seeds where possible.
- Report points per round, round and match win rates and confidence intervals, plus Koi-Koi rate and average points per stop.
- Add scripted benchmark bots:
  - Random.
  - Greedy, from the table above.
  - **Expert**: a hand-written strategy that tracks unseen cards, pursues and blocks yaku, and decides Koi-Koi by risk. It's the main benchmark before self-play.
- Add model and results logging, with the rules version recorded for each run.

**Exit:** the arena reproduces the baselines within their confidence intervals, and Expert beats Greedy with a confidence interval above zero.

## Phase 3: Masked PPO against scripted bots

**Goal:** a first agent that really learns to play.

- Switch to `MaskablePPO` from `sb3-contrib`, which supports `action_masks()`.
- Redesign rewards so that the primary signal is the game result, measured as the round's score difference. Keep only shaping that doesn't change what the best play is (potential-based), then reduce it over training.
- Keep the v1 reward table as a comparison run, to measure what the change gains.
- Add useful features such as the unseen cards and progress towards each yaku.
- Train against a mix of scripted bots, then tune with several seeds.

**Exit** (provisional): over at least 5,000 evaluation rounds, across at least 3 training seeds:
- at least +1.0 points per round against the built-in opponent, with the confidence interval clear of Greedy's;
- a positive score against Greedy with its seat swapped, once Phase 1 allows it; and
- Koi-Koi choices that aren't simply always-stop or always-continue.

## Phase 4: Self-play league

**Goal:** stop the agent from only exploiting fixed bots.

- Train against past versions of itself, kept in a pool alongside the scripted bots.
- Track strength with an Elo-style rating across the pool, and watch for cycles where A beats B, B beats C and C beats A.
- Train a separate "exploiter" against each frozen candidate to measure how much it can be beaten once its style is known. This is the same concern that motivates [NFSP](https://arxiv.org/abs/1603.01121). If simple self-play cycles or stays easy to exploit, NFSP is the next method to try.

**Exit** (provisional): the candidate beats Expert and its own earlier versions with confidence intervals above zero, and a trained exploiter gains less than 0.5 points per round against it.

## Phase 5: Reasoning about hidden cards

**Goal:** add strength from handling hidden information, if it's worth the cost.

Each item is an independent experiment, run in this order and kept only if the arena shows a significant gain:

1. **Oracle guiding:** give training extra access to hidden cards and fade it out, as in [Suphx](https://arxiv.org/abs/2003.13590) for Mahjong.
2. **Search at decision time:** sample plausible hidden cards and evaluate moves by simulation, starting with the Koi-Koi decision, where a mistake costs the most.
3. **Deep Monte-Carlo:** compare it against PPO. [DouZero](https://arxiv.org/abs/2106.06135) used it for a card game with large, changing sets of legal moves.

**Exit:** each experiment has a recorded result, and the best agent is selected for Phase 6.

## Phase 6: Proficiency validation

**Goal:** check the agent against opponents outside its own training.

- Add a way for people to play the trained agent, starting with the terminal harness.
- Run it against experienced human players, and against other Koi-Koi software where practical, under matching rules.
- Review its losses for patterns, and feed any weaknesses back into Phases 3 to 5.

**Definition of proficient** (provisional), under the ruleset chosen in Phase 0:

1. It beats every scripted bot and earlier model, with confidence intervals above zero, over at least 10,000 rounds each.
2. A trained exploiter gains less than 0.5 points per round against it.
3. Against experienced human players, pooled over at least 500 rounds, its points per round has a confidence interval above zero.

The goal is strong, robust play, not provably optimal play. Point 3 is the real test, and also the hardest to arrange: 500 rounds is about 42 full 12-round matches.

## Main risks

| Risk | Mitigation |
|---|---|
| Changing rules after training makes models obsolete | Decide the ruleset in Phase 0 and record the rules version with each model |
| Reward shaping teaches the wrong behaviour | Compare agents only on game results, and reduce shaping over training |
| Overfitting to the built-in opponent | Train against a mix of bots, then a league, and measure with exploiters |
| Comparing agents on too few games | Use the shared arena, with confidence intervals, for every comparison |
| Too few human games for a firm verdict | Pool games across players, and start collecting early in Phase 6 |

## Prior work

The closest Koi-Koi study found is a 2017 Japanese workshop paper, [花札のこいこいにおける方策勾配法とNeural Fitted Q Iteration の適用](https://cir.nii.ac.jp/crid/1050011097178596096). Its search listing reports average scores of -0.3 and 0.5 points against rule-based opponents. The full text couldn't be retrieved, so the setup and scoring aren't confirmed. No Koi-Koi self-play study turned up in this search, so expect to rely on methods from other card games.

Masking is backed by [Huang and Ontañón (2020)](https://arxiv.org/abs/2006.14171), who show that its importance grows as the invalid action space grows.
