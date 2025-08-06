from environment.card_utils import format_card, format_hand
from environment.koikoienv import KoiKoiEnv

def display_cards(cards):
    return [f"{card} (Month {card // 4 + 1})" for card in cards]

def print_game_state(env):
    print("\n--- Game State ---")
    print(f"Field:               {format_hand(env.field)}")
    print(f"Your Hand:           {format_hand(env.player_hands[0])}")
    print(f"Your Collected:      {format_hand(env.collected_cards[0])}")
    print(f"Opponent Collected:  {format_hand(env.collected_cards[1])}")
    print(f"Deck: {len(env.deck)} cards remaining")
    print(f"Your Score: {env.your_score} | Opponent Score: {env.opponent_score}")
    print(f"Pending Yaku: {env.pending_yaku if env.koikoi_pending else 'None'}")



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

        print(f"\nReward: {reward}")
        print(f"Info: {info}")
        print("-------------------------------")

    print("Game Over!")
    print(f"Final Score: You {env.your_score} | Opponent {env.opponent_score}")

if __name__ == '__main__':
    test_game()
