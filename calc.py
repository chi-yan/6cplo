import random
from treys import Deck, Evaluator, Card
from itertools import combinations
def validate_hands(hands):
    """
    Validate that there are no duplicate cards across all hands.
    """
    all_known_cards = []
    all_suit_placeholders = {"h": 0, "s": 0, "d": 0, "c": 0}
    
    # First, parse all hands and collect known cards and suit placeholders
    for hand in hands:
        cards = hand.split('.')
        
        # Check if hand has exactly 6 cards
        if len(cards) != 6:
            raise ValueError(f"Hand '{hand}' must contain exactly 6 cards")
            
        for card in cards:
            # Check for valid card format
            if card != "x" and len(card) != 2:
                raise ValueError(f"Invalid card format '{card}' in hand '{hand}'")
                
            if card != "x" and card[0] != "o":
                try:
                    new_card = Card.new(card)
                    if new_card in all_known_cards:
                        raise ValueError(f"Duplicate card '{card}' found in hands")
                    all_known_cards.append(new_card)
                except:
                    raise ValueError(f"Invalid card format '{card}' in hand '{hand}'")
            
            # Track suit placeholders
            if len(card) == 2 and card[0] == "o":
                suit = card[1]
                if suit not in "cdhs":
                    raise ValueError(f"Invalid suit placeholder '{card}' in hand '{hand}'")
                all_suit_placeholders[suit] += 1
                
    # Count how many cards of each suit are known
    used_suits = {"h": 0, "s": 0, "d": 0, "c": 0}
    for card in all_known_cards:
        card_str = Card.int_to_str(card)
        suit = card_str[1].lower()
        used_suits[suit] += 1
    
    # Check if there are enough remaining cards for the placeholders
    for suit in "hdsc":
        available = 13 - used_suits[suit]  # Start with 13 cards per suit, subtract used ones
        needed = all_suit_placeholders[suit]
        if needed > available:
            raise ValueError(f"Not enough remaining cards of suit '{suit}' available. "
                           f"Need {needed} but only {available} remaining")
    
    return True

def parse_hand(hand):
    """
    Parse a dot-separated hand into known cards, suit-specific placeholders, and fully unknown cards.

    Args:
        hand (str): A hand string (e.g., "Ah.Ac.oh.oc.x.x").

    Returns:
        tuple: A list of fully known cards, a dictionary of suit-specific placeholders, and the count of 'x' placeholders.
    """
    known_cards = []
    suit_placeholders = {"h": 0, "s": 0, "d": 0, "c": 0}
    unknown_count = 0

    for card_str in hand.split('.'):
        if card_str == "x":
            unknown_count += 1
        elif len(card_str) == 2:
            if card_str[0] == "o":  # Suit-specific placeholder
                suit = card_str[1]
                if suit in suit_placeholders:
                    suit_placeholders[suit] += 1
            else:  # Regular card
                try:
                    known_cards.append(Card.new(card_str))
                except:
                    print(f"Invalid card format: {card_str}")
                    raise

    return known_cards, suit_placeholders, unknown_count
def simulate_omaha(hands, num_simulations=10000):
    """
    Simulate 6-card Omaha poker hands with suit-specific placeholders and unknown cards.
    """
    evaluator = Evaluator()
    results = {hand: 0 for hand in hands}
    
    # Parse hands into known cards, suit-specific placeholders, and unknowns
    parsed_hands = [parse_hand(hand) for hand in hands]

    for _ in range(num_simulations):
        deck = Deck()
        for known_cards, _, _ in parsed_hands:
            for card in known_cards:
                if card in deck.cards:
                    deck.cards.remove(card)

        # Simulate hands
        simulated_hands = []
        for known_cards, suit_placeholders, unknown_count in parsed_hands:
            current_hand = known_cards.copy()
            
            # Handle suit-specific placeholders
            for suit, count in suit_placeholders.items():
                suit_int = "cdhs".index(suit)
                possible_cards = [
                    card for card in deck.cards 
                    if Card.get_suit_int(card) == suit_int
                ]
                
                for _ in range(count):
                    if possible_cards:
                        chosen_card = random.choice(possible_cards)
                        current_hand.append(chosen_card)
                        deck.cards.remove(chosen_card)
                        possible_cards.remove(chosen_card)

            # Handle unknown cards
            for _ in range(unknown_count):
                if deck.cards:
                    card = random.choice(deck.cards)
                    current_hand.append(card)
                    deck.cards.remove(card)

            simulated_hands.append(current_hand)

        # Deal board
        board = deck.draw(5)

        # Evaluate hands
        scores = []
        for hand in simulated_hands:
            best_score = float('inf')
            for hole_combo in combinations(hand, 2):
                for board_combo in combinations(board, 3):
                    score = evaluator.evaluate(list(board_combo), list(hole_combo))
                    best_score = min(best_score, score)
            scores.append(best_score)

        # Determine winners
        min_score = min(scores)
        winning_indices = [i for i, score in enumerate(scores) if score == min_score]
        win_share = 1.0 / len(winning_indices)  # Split pot equally among all winners
        
        # Add win share to each winning hand
        for idx in winning_indices:
            results[hands[idx]] += win_share

    # Convert to percentages
    total_simulations = num_simulations
    
    # For identical hands, combine their results
    final_results = {}
    for hand in hands:
        if hand not in final_results:
            # Count how many times this hand appears
            identical_hands = hands.count(hand)
            if identical_hands > 1:
                # Split the total result among identical hands
                final_results[hand] = (results[hand] / total_simulations * 100) / identical_hands
            else:
                final_results[hand] = (results[hand] / total_simulations * 100)

    return final_results

if __name__ == "__main__":
    # Test Case 1: Valid hands with identical hands
    try:
        print("Test Case 1: Valid hands")
        hands = ["Ah.Ac.oh.oc.x.x", "x.x.x.x.x.x", "x.x.x.x.x.x"]
        validate_hands(hands)
        print("Validation passed!")
        results = simulate_omaha(hands, num_simulations=10000)
        print(f"Number of players: {len(hands)}")
        # Since results is a dictionary, we need to iterate through it properly
        for i, hand in enumerate(hands):
            print(f"Player {i+1} ({hand}): {results[hand]:.2f}%")
    except ValueError as e:
        print(f"Error: {e}")

    print("\n" + "="*50 + "\n")  # Separator

    # Test Case 2: Invalid hands with duplicate cards
    try:
        print("Test Case 2: Invalid hands with duplicate 5h")
        invalid_hands = ["5h.Ac.oh.oc.x.x", "5h.2c.x.x.x.x", "x.x.x.x.x.x"]
        validate_hands(invalid_hands)
        results = simulate_omaha(invalid_hands, num_simulations=10000)
        for hand, win_percentage in results.items():
            print(f"{hand}: {win_percentage:.2f}%")
    except ValueError as e:
        print(f"Error: {e}")

    # Test Case 3: Invalid number of cards
    try:
        print("\nTest Case 3: Invalid number of cards")
        invalid_hands = ["Ah.Ac.oh.oc.x", "7d.2c.x.x.x.x"]  # First hand has only 5 cards
        validate_hands(invalid_hands)
    except ValueError as e:
        print(f"Error: {e}")

    # Test Case 4: Too many suit placeholders
    try:
        print("\nTest Case 4: Too heart placeholders")
        invalid_hands = ["Ah.oh.oh.oh.oh.oh", "7d.2c.oh.oh.oh.x", "oh.oh.oh.oh.oh.oh"]  # Too many heart placeholders
        validate_hands(invalid_hands)
    except ValueError as e:
        print(f"Error: {e}")

    # Test Case 5: Invalid card format
    try:
        print("\nTest Case 5: Invalid card format")
        invalid_hands = ["1h.Ac.oh.oc.x.x", "7d.2c.x.x.x.x"]  # 1h is not a valid card format
        validate_hands(invalid_hands)
    except ValueError as e:
        print(f"Error: {e}")
