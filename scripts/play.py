"""Play Koi-Koi in the terminal against the built-in opponent."""

import argparse
from datetime import datetime
import logging

from holokkrl.envs.koikoi_env import KoiKoiEnv
from holokkrl.game.cards import format_card, format_hand


def configure_logging(enable_logging):
    if enable_logging:
        logging.basicConfig(
            filename=f"koikoi_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
    else:
        logging.basicConfig(level=logging.CRITICAL)  # Suppress logging output


def print_game_state(env):
    state_str = (
        f"Field:               {format_hand(env.field)}\n"
        f"Your Hand:           {format_hand(env.player_hands[0])}\n"
        f"Your Collected:      {format_hand(env.collected_cards[0])}\n"
        f"Opponent Collected:  {format_hand(env.collected_cards[1])}\n"
        f"Deck: {len(env.deck)} cards remaining\n"
        f"Your Score: {env.your_score} | Opponent Score: {env.opponent_score}\n"
        f"Pending Yaku: {env.pending_yaku if env.koikoi_pending else 'None'}"
    )
    print("\n--- Game State ---")
    print(state_str)
    logging.info("GAME STATE:\n%s", state_str)


def print_match(match, no_match_text):
    print(f"Matched with: {format_card(match)}" if match is not None else no_match_text)


def print_opponent_turn(info):
    if "opponent_played_card" in info:
        print(f"Opponent played: {format_card(info['opponent_played_card'])}")
    if "opponent_play_match" in info:
        print_match(info["opponent_play_match"], "No match for played card.")

    if "opponent_drawn_card" in info:
        print(f"Opponent drew: {format_card(info['opponent_drawn_card'])}")
    if "opponent_draw_match" in info:
        print_match(info["opponent_draw_match"], "No match from draw.")

    if "opponent_koikoi" in info:
        print(f"Opponent formed Yaku: {info['opponent_yaku']}")
        print(f"Opponent chose to: {'Koi-Koi' if info['opponent_koikoi'] else 'Stop and score'}")


def print_turn_info(info):
    logging.info("TURN INFO: %s", info)
    print("\n--- Turn Summary ---")

    if "player_drawn_card" in info:
        print(f"You drew: {format_card(info['player_drawn_card'])}")
    if "player_draw_match" in info:
        print_match(info["player_draw_match"], "No match from draw.")

    print_opponent_turn(info)

    if "opening_opponent_turn" in info:
        print("New round: the opponent deals and plays first.")
        print_opponent_turn(info["opening_opponent_turn"])
    print("-------------------------------")


def read_action(env):
    if env.koikoi_pending:
        print("You made Yaku! Choose:")
        print(f"{env.KOIKOI_ACTION}: Koi-Koi")
        print(f"{env.STOP_ACTION}: Stop and score")
        return int(input("Enter action (Koi-Koi/Stop): "))

    if env.pending_draw_card is not None:
        first, second = env._field_matches(env.pending_draw_card)
        print(f"You drew {format_card(env.pending_draw_card)}, which matches two field cards. Choose:")
        print(f"{env.DRAW_MATCH_FIRST}: {format_card(first)}")
        print(f"{env.DRAW_MATCH_SECOND}: {format_card(second)}")
        return int(input("Enter action (capture): "))

    print("Choose a card to play and field match index:")
    for i, card in enumerate(env.player_hands[0]):
        print(f"{i}: {format_card(card)}")
    hand_idx = int(input("Card index to play: "))
    print("Matching with:")
    for i, card in enumerate(env.field):
        print(f"{i}: {format_card(card)}")
    print(f"{env.NO_MATCH}: No match")
    field_idx = int(input("Field index to match (or No Match): "))
    return env.encode_play(hand_idx, field_idx)


def play_game(enable_logging):
    configure_logging(enable_logging)
    env = KoiKoiEnv()
    obs, info = env.reset()
    terminated = False
    truncated = False

    logging.info("GAME START")
    print("Welcome to Koi-Koi!\n")
    if "opening_opponent_turn" in info:
        print_turn_info(info)

    while not (terminated or truncated):
        print_game_state(env)
        action = read_action(env)
        obs, reward, terminated, truncated, info = env.step(action)

        logging.info("STEP: action=%s, reward=%s, terminated=%s, truncated=%s, obs=%s, info=%s",
                     action, reward, terminated, truncated, obs, info)

        print_turn_info(info)

        print(f"\nReward: {reward}")
        print(f"Info: {info}")
        print("-------------------------------")

    logging.info("GAME OVER: Final Score: You %s | Opponent %s", env.your_score, env.opponent_score)
    print("Game Over!")
    print(f"Final Score: You {env.your_score} | Opponent {env.opponent_score}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Play Koi-Koi in the terminal")
    parser.add_argument("--log", action="store_true", help="Enable logging to file")
    args = parser.parse_args()
    play_game(enable_logging=args.log)
