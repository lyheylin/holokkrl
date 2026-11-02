from environment.card_utils import format_card, format_hand
from environment.koikoienv import KoiKoiEnv
from environment.card_data import CARD_DATA
import logging
import argparse
from datetime import datetime

def configure_logging(enable_logging):
    if enable_logging:
        logging.basicConfig(
            filename=f"koikoi_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
    else:
        logging.basicConfig(level=logging.CRITICAL)  # Suppress logging output

def display_card(card):
    if card is None:
        return "None"
    if card < 0 or card >= len(CARD_DATA):
        return f"{card} (Invalid)"
    card_info = CARD_DATA[card]
    month = card_info[1] + 1
    ctype = card_info[2]
    subtype = card_info[3]
    if subtype:
        return f"{card} (Month {month}, {ctype}, {subtype})"
    return f"{card} (Month {month}, {ctype})"

def display_cards(cards):
    return [display_card(card) for card in cards]

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

def print_opponent_turn(info):
    if "opponent_played_card" in info:
        print(f"Opponent played: {display_card(info['opponent_played_card'])}")
    if "opponent_play_match" in info:
        match = info["opponent_play_match"]
        print(f"Matched with: {display_card(match)}" if match is not None else "No match for played card.")

    if "opponent_drawn_card" in info:
        print(f"Opponent drew: {display_card(info['opponent_drawn_card'])}")
    if "opponent_draw_match" in info:
        match = info["opponent_draw_match"]
        print(f"Matched with: {display_card(match)}" if match is not None else "No match from draw.")

    if "opponent_koikoi" in info:
        print(f"Opponent formed Yaku: {info['opponent_yaku']}")
        print(f"Opponent chose to: {'Koi-Koi' if info['opponent_koikoi'] else 'Stop and score'}")

def print_turn_info(info):
    logging.info("TURN INFO: %s", info)
    print("\n--- Turn Summary ---")

    if "player_drawn_card" in info:
        print(f"You drew: {display_card(info['player_drawn_card'])}")
    if "player_draw_match" in info:
        match = info["player_draw_match"]
        print(f"Matched with: {display_card(match)}" if match is not None else "No match from draw.")

    print_opponent_turn(info)

    if "opening_opponent_turn" in info:
        print("New round: the opponent deals and plays first.")
        print_opponent_turn(info["opening_opponent_turn"])
    print("-------------------------------")

def test_game(enable_logging):
    configure_logging(enable_logging)
    env = KoiKoiEnv()
    obs, info = env.reset()
    terminated = False
    truncated = False

    logging.info("GAME START")
    print("Welcome to the Koi-Koi test harness!\n")
    if "opening_opponent_turn" in info:
        print_turn_info(info)

    while not (terminated or truncated):
        print_game_state(env)

        if env.koikoi_pending:
            print("You made Yaku! Choose:")
            print(f"{env.KOIKOI_ACTION}: Koi-Koi")
            print(f"{env.STOP_ACTION}: Stop and score")
            action = int(input("Enter action (Koi-Koi/Stop): "))
        elif env.pending_draw_card is not None:
            first, second = env._field_matches(env.pending_draw_card)
            print(f"You drew {format_card(env.pending_draw_card)}, which matches two field cards. Choose:")
            print(f"{env.DRAW_MATCH_FIRST}: {format_card(first)}")
            print(f"{env.DRAW_MATCH_SECOND}: {format_card(second)}")
            action = int(input("Enter action (capture): "))
        else:
            print("Choose a card to play and field match index:")
            for i, card in enumerate(env.player_hands[0]):
                print(f"{i}: {format_card(card)}")
            hand_idx = int(input("Card index to play: "))
            print("Matching with:")
            for i, card in enumerate(env.field):
                print(f"{i}: {format_card(card)}")
            print(f"{env.NO_MATCH}: No match")
            field_idx = int(input("Field index to match (or No Match): "))
            action = env.encode_play(hand_idx, field_idx)

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
    parser = argparse.ArgumentParser(description="Koi-Koi Test Harness")
    parser.add_argument("--log", action="store_true", help="Enable logging to file")
    args = parser.parse_args()
    test_game(enable_logging=args.log)
