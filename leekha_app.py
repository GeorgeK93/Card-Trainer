import streamlit as st
import random
from collections import Counter

# ---------- Setup ----------
suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
deck = [f"{rank}{suit}" for suit in suits for rank in ranks]

suit_order = {"♠": 0, "♥": 1, "♣": 2, "♦": 3}
rank_order = {
    "A": 0, "K": 1, "Q": 2, "J": 3, "10": 4,
    "9": 5, "8": 6, "7": 7, "6": 8, "5": 9,
    "4": 10, "3": 11, "2": 12
}

def sort_key(card):
    if card.startswith("10"):
        rank = "10"
        suit = card[2]
    else:
        rank = card[0]
        suit = card[1]
    return (suit_order[suit], rank_order[rank])

def format_card_html(card):
    if card.startswith("10"):
        rank = "10"
        suit = card[2]
    else:
        rank = card[0]
        suit = card[1]

    color_map = {"♠": "black", "♥": "red", "♣": "green", "♦": "blue"}
    color = color_map.get(suit, "black")

    return f"""
    <div style='text-align:center; padding:4px; border:1px solid #ccc; border-radius:6px; width:50px; height:60px; display:inline-block; margin:2px;'>
        <div style='font-size:18px; font-weight:bold;'>{rank}</div>
        <div style='color:{color}; font-size:20px;'>{suit}</div>
    </div>
    """

# ---------- New Game Reset ----------
def reset_game():
    random.shuffle(deck)
    hands = [deck[i*13:(i+1)*13] for i in range(4)]
    st.session_state.your_hand = sorted(hands[0], key=sort_key)
    st.session_state.other_hands = [hands[1], hands[2], hands[3]]
    st.session_state.round = 1
    st.session_state.played_suits = []
    st.session_state.history = []
    st.session_state.quizzes = [4, 7, 10]
    st.session_state.quiz_pending = False
    st.session_state.quiz_inputs = {}
    st.session_state.quiz_result = None

if "your_hand" not in st.session_state:
    reset_game()

# ---------- UI ----------
st.title("🃏 Leekha Card Tracker")

if st.button("🔄 New Game"):
    reset_game()
    st.rerun()

if st.session_state.round <= 13:
    st.subheader(f"Round {st.session_state.round}")

    # ---------- Quiz Block ----------
    if st.session_state.quiz_pending:
        st.markdown(f"## 🔎 Suit Quiz - Before Round {st.session_state.round}")
        guesses = {}
        guesses["♠"] = st.number_input("How many ♠ (Spades) are left?", min_value=0, max_value=13, key="guess_spades")
        guesses["♥"] = st.number_input("How many ♥ (Hearts) are left?", min_value=0, max_value=13, key="guess_hearts")
        guesses["♣"] = st.number_input("How many ♣ (Clubs) are left?", min_value=0, max_value=13, key="guess_clubs")
        guesses["♦"] = st.number_input("How many ♦ (Diamonds) are left?", min_value=0, max_value=13, key="guess_diamonds")

        if st.button("Submit Guess"):
            suit_counts = Counter(st.session_state.played_suits)
            score = 0
            result_lines = []
            for suit in ["♠", "♥", "♣", "♦"]:
                played = suit_counts.get(suit, 0)
                remaining = 13 - played
                user_guess = guesses[suit]
                correct = user_guess == remaining
                if correct:
                    score += 1
                result = "✅ Correct" if correct else f"❌ Wrong (Actual: {remaining})"
                result_lines.append(f"**{suit}** — You guessed {user_guess} → {result}")

            st.session_state.quiz_result = (score, result_lines)
            st.session_state.quiz_pending = False
            st.rerun()

    elif st.session_state.quiz_result:
        score, result_lines = st.session_state.quiz_result
        st.markdown("## Quiz Results")
        for line in result_lines:
            st.markdown(line)
        st.success(f"You got {score}/4 correct!")
        if st.button("Continue to next round"):
            st.session_state.quiz_result = None
            st.rerun()

    else:
        st.markdown("### Your Hand:")
        hand_len = max(1, len(st.session_state.your_hand))
        cols = st.columns(hand_len)
        for i, card in enumerate(st.session_state.your_hand):
            with cols[i]:
                if st.button(" ", key=f"card_{i}", help=f"Play {card}", use_container_width=True):
                    st.session_state.selected_card = card
                st.markdown(format_card_html(card), unsafe_allow_html=True)

# ---------- Play Round ----------
if "selected_card" in st.session_state and st.session_state.round <= 13:
    your_card = st.session_state.selected_card
    st.session_state.your_hand.remove(your_card)

    p2 = st.session_state.other_hands[0].pop(0)
    p3 = st.session_state.other_hands[1].pop(0)
    p4 = st.session_state.other_hands[2].pop(0)

    round_result = f"You - {your_card} | P2 - {p2} | P3 - {p3} | P4 - {p4}"
    st.session_state.history.append(round_result)

    for card in [your_card, p2, p3, p4]:
        st.session_state.played_suits.append(card[-1])

    st.session_state.round += 1
    del st.session_state.selected_card

    # Flag if a quiz is needed
    if st.session_state.round in st.session_state.quizzes:
        st.session_state.quiz_pending = True

    st.rerun()

# ---------- Show Last Played Round ----------
if st.session_state.round <= 13 and st.session_state.history:
    st.markdown("### Last Played Round:")
    last = st.session_state.history[-1]
    parts = last.split(" | ")
    styled_parts = []
    for part in parts:
        label, card = part.split(" - ")
        card_html = format_card_html(card)
        styled_parts.append(f"<b>{label}</b>: {card_html}")
    st.markdown("<div style='margin-bottom:8px;'>" + " ".join(styled_parts) + "</div>", unsafe_allow_html=True)

# ---------- Game Complete ----------
if st.session_state.round > 13:
    st.header("🏆 Game Complete")
    st.markdown("### All Rounds:")
    for line in st.session_state.history:
        parts = line.split(" | ")
        styled_parts = []
        for part in parts:
            label, card = part.split(" - ")
            card_html = format_card_html(card)
            styled_parts.append(f"<b>{label}</b>: {card_html}")
        st.markdown("<div style='margin-bottom:8px;'>" + " ".join(styled_parts) + "</div>", unsafe_allow_html=True)

