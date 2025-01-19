import streamlit as st
from calc import validate_hands, simulate_omaha

def main():
    st.title("6c-plo Simulator")
    st.write("""
    Enter hands in the format: "Ah.Ac.oh.oc.x.x" where:
    - Regular cards: Ah, Kd, 2c, etc.
    - Suit placeholders: oh (any heart), od (any diamond), etc.
    - Unknown cards: x
    """)

    # Sidebar controls
    st.sidebar.header("Simulation Settings")
    num_players = st.sidebar.selectbox(
        "Number of Players",
        options=list(range(2, 11)),
        index=1
    )
    
    num_simulations = st.sidebar.number_input(
        "Number of Simulations",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=1000
    )

    # Create input fields for each player's hand
    hands = []
    for i in range(num_players):
        hand = st.text_input(
            f"Player {i+1}'s hand",
            value="x.x.x.x.x.x" if i > 0 else "Ah.Ac.oh.oc.x.x",
            key=f"player_{i}"
        )
        hands.append(hand)

    # Add a run button
    if st.button("Run Simulation"):
        try:
            # Validate hands
            with st.spinner("Validating hands..."):
                validate_hands(hands)
            
            # Run simulation
            with st.spinner(f"Running {num_simulations} simulations..."):
                results = simulate_omaha(hands, num_simulations=num_simulations)
            
            # Display results
            st.header("Results")
            
            # Display results for each player
            for i, hand in enumerate(hands):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"Player {i+1}: {hand}")
                with col2:
                    win_percentage = results[hand]
                    st.write(f"{win_percentage:.2f}%")
                
                # Add a progress bar for visual representation
                st.progress(win_percentage / 100)

            # Display total (should be close to 100%)
            # st.write(f"Total: {sum(results.values()):.2f}%")

        except ValueError as e:
            st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

    # Add help section
    with st.expander("Help & Examples"):
        st.markdown("""
        ### Card Format:
        - Regular cards: Ah (Ace of hearts), Kd (King of diamonds), 2c (2 of clubs), etc.
        - Suit placeholders: oh (any heart), od (any diamond), os (any spade), oc (any club)
        - Unknown cards: x (any card)
        
        ### Example Hands:
        1. `Ah.Ac.oh.oc.x.x` - Ace of hearts, Ace of clubs, any heart, any club, and two random cards
        2. `x.x.x.x.x.x` - Completely random hand
        3. `Kh.Kd.oh.od.x.x` - King of hearts, King of diamonds, any heart, any diamond, and two random cards
        
        ### Notes:
        - Each hand must contain exactly 6 cards
        - Cards must be separated by dots (.)
        - No duplicate cards are allowed across all hands
                    
        ### Disclaimer:
        This simulator is designed for educational purposes only. It does not guarantee any specific results in real-life games or tournaments.
  
        """)

if __name__ == "__main__":
    main()
