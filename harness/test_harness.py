from environment.card_utils import format_card, format_hand
from environment.koikoienv import KoiKoiEnv
from environment.card_data import CARD_DATA


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
    print("\n--- Game State ---")
    print(f"Field:               {format_hand(env.field)}")
    print(f"Your Hand:           {format_hand(env.player_hands[0])}")
    print(f"Your Collected:      {format_hand(env.collected_cards[0])}")
    print(f"Opponent Collected:  {format_hand(env.collected_cards[1])}")
    print(f"Deck: {len(env.deck)} cards remaining")
    print(f"Your Score: {env.your_score} | Opponent Score: {env.opponent_score}")
    print(f"Pending Yaku: {env.pending_yaku if env.koikoi_pending else 'None'}")

def print_turn_info(info):
    print("\n--- Turn Summary ---")

    if "player_drawn_card" in info:
        print(f"You drew: {display_card(info['player_drawn_card'])}")
        if "player_draw_match" in info:
            match = info["player_draw_match"]
            print(f"Matched with: {display_card(match)}" if match is not None else "No match from draw.")

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

    if "opponent_yaku" in info and info["opponent_yaku"]:
        print(f"Opponent formed Yaku: {info['opponent_yaku']}")
        print(f"Opponent chose to: {'Koi-Koi' if info.get('opponent_koikoi') else 'Stop and score'}")
    print("-------------------------------")

def test_game():
    env = KoiKoiEnv()
    obs = env.reset()
    done = False

    print("Welcome to the Koi-Koi test harness!\n")

    while not done:
        print_game_state(env)

        if env.koikoi_pending:
            print("You made Yaku! Choose:")
            print(f"{env.KOIKOI_ACTION}: Koi-Koi")
            print(f"{env.STOP_ACTION}: Stop and score")
            action = int(input("Enter action (Koi-Koi/Stop): "))
        else:
            print("Choose a card to play and field match index:")
            for i, card in enumerate(env.player_hands[0]):
                print(f"{i}: {format_card(card)}")
            hand_idx = int(input("Card index to play: "))
            print("Matching with:")
            for i, card in enumerate(env.field):
                print(f"{i}: {format_card(card)}")
            print(f"{len(env.field)}: No match")
            field_idx = int(input("Field index to match (or No Match): "))
            action = hand_idx * (env.field_size + 1) + field_idx

        obs, reward, done, info = env.step(action)

        print_turn_info(info)

        print(f"\nReward: {reward}")
        print(f"Info: {info}")
        print("-------------------------------")

    print("Game Over!")
    print(f"Final Score: You {env.your_score} | Opponent {env.opponent_score}")

if __name__ == '__main__':
    test_game()
    