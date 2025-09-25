import streamlit as st
import pandas as pd
from utils.calculator import ParlayCalculator
from utils.data_manager import DataManager
from utils.formatters import format_moneyline, format_currency, format_decimal_odds, get_status_emoji
from config import APP_TITLE, WAGER_AMOUNT, NUM_WEEKS, USERS, STATUS_OPTIONS, get_current_nfl_week

def main():
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    initialize_session_state()
    
    st.title("🏈 10-Leg Parlay Dashboard")

    current_week = get_current_nfl_week()

    # Week selection
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.info(f"Current NFL Week: {current_week}")
        st.markdown("Access FanDuel's Odds here: [https://sportsbook.fanduel.com/navigation/nfl](https://sportsbook.fanduel.com/navigation/nfl)")

    with col2:
        selected_week = st.selectbox(
            "Select Week:",
            options=list(range(2, NUM_WEEKS + 1)),
            index=st.session_state.selected_week - 2,  # Convert to 0-based index
            key="week_selector"
        )
        st.session_state.selected_week = selected_week

    with col3:
        if st.button("Go to Current Week", type="primary"):
            st.session_state.selected_week = current_week
            st.rerun()

    # Render the selected week
    render_week_dashboard(st.session_state.selected_week)

def initialize_session_state():
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    if 'calculator' not in st.session_state:
        st.session_state.calculator = ParlayCalculator()
    if 'selected_week' not in st.session_state:
        st.session_state.selected_week = get_current_nfl_week()

def render_week_dashboard(week_num: int):
    wagers = st.session_state.data_manager.load_week_wagers(week_num)
    
    # Create placeholder for parlay summary that will be updated with form values
    parlay_placeholder = st.empty()
    
    st.divider()
    render_wager_grid(week_num, wagers, parlay_placeholder)
    st.divider()
    render_action_buttons(week_num)

def render_parlay_summary(wagers: pd.DataFrame):
    st.subheader("Parlay Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Wager Amount", format_currency(WAGER_AMOUNT))
    
    with col2:
        valid_wagers = []
        for _, row in wagers.iterrows():
            symbol = row['moneyline_symbol']
            value = row['moneyline_value']
            
            # Handle both string and numeric values, and None values
            if (symbol is not None and str(symbol).strip() in ['+', '-'] and 
                value is not None and str(value).strip() != ''):
                try:
                    numeric_value = int(float(str(value)))
                    if numeric_value >= 100:  # Valid odds range
                        valid_wagers.append((str(symbol).strip(), numeric_value))
                except (ValueError, TypeError):
                    continue
        
        if valid_wagers and len(valid_wagers) == 10:
            decimal_odds = st.session_state.calculator.calculate_parlay_odds(valid_wagers)
            payout = st.session_state.calculator.calculate_payout(WAGER_AMOUNT, decimal_odds)
            st.metric("Potential Payout", format_currency(payout))
        else:
            st.metric("Potential Payout", f"$0.00 ({len(valid_wagers)}/10)")
    
    with col3:
        if valid_wagers and len(valid_wagers) == 10:
            st.metric("Parlay Odds", format_decimal_odds(decimal_odds))
        else:
            st.metric("Parlay Odds", "0.00")
    
    with col4:
        completed = len(wagers[(wagers['user'].notna()) & (wagers['user'] != '')])
        st.metric("Wagers Completed", f"{completed}/10")

def render_wager_grid(week_num: int, wagers: pd.DataFrame, parlay_placeholder):
    st.subheader(f"Week {week_num} Wager Selections")
    
    with st.form(f"week_{week_num}_wagers"):
        col1, col2, col3, col4, col5 = st.columns([0.5, 0.8, 1, 3, 1.5])
        col1.write("**#**")
        col2.write("**+/-**")
        col3.write("**Odds**")
        col4.write("**Wager Detail**")
        col5.write("**User**")
        
        wager_inputs = []
        for i in range(1, 11):
            col1, col2, col3, col4, col5 = st.columns([0.5, 0.8, 1, 3, 1.5])
            
            existing_row = wagers[wagers['position'] == i]
            existing = existing_row.iloc[0] if len(existing_row) > 0 else None
            
            with col1:
                st.write(f"{i}")
            
            with col2:
                symbol_idx = 0
                if existing is not None and pd.notna(existing['moneyline_symbol']):
                    if existing['moneyline_symbol'] == '+':
                        symbol_idx = 1
                    elif existing['moneyline_symbol'] == '-':
                        symbol_idx = 2
                
                symbol = st.selectbox(
                    f"Symbol {i}", 
                    options=['', '+', '-'],
                    index=symbol_idx,
                    key=f"symbol_{week_num}_{i}",
                    label_visibility="collapsed"
                )
            
            with col3:
                odds_value = 100
                if existing is not None and pd.notna(existing['moneyline_value']):
                    odds_value = int(existing['moneyline_value'])
                
                odds_value = st.number_input(
                    f"Odds {i}",
                    min_value=100,
                    max_value=9999,
                    value=odds_value,
                    key=f"odds_{week_num}_{i}",
                    label_visibility="collapsed"
                )
            
            with col4:
                detail_value = ""
                if existing is not None and pd.notna(existing['wager_detail']):
                    detail_value = existing['wager_detail']
                
                detail = st.text_input(
                    f"Detail {i}",
                    value=detail_value,
                    key=f"detail_{week_num}_{i}",
                    placeholder="e.g., Chiefs -3.5, Over 47.5",
                    label_visibility="collapsed"
                )
            
            with col5:
                user_idx = 0
                if existing is not None and pd.notna(existing['user']) and existing['user']:
                    try:
                        user_idx = USERS.index(existing['user']) + 1
                    except ValueError:
                        user_idx = 0
                
                user = st.selectbox(
                    f"User {i}",
                    options=[''] + USERS,
                    index=user_idx,
                    key=f"user_{week_num}_{i}",
                    label_visibility="collapsed"
                )
            
            wager_inputs.append({
                'position': i,
                'moneyline_symbol': symbol if symbol else None,
                'moneyline_value': odds_value if symbol else None,
                'wager_detail': detail,
                'user': user if user else None,
                'status': 'pending'
            })
        
        # Calculate parlay odds based on current form values
        current_wagers_df = pd.DataFrame(wager_inputs)
        with parlay_placeholder.container():
            render_parlay_summary(current_wagers_df)
        
        submitted = st.form_submit_button("Save All Wagers", type="primary", use_container_width=True)
        
        if submitted:
            st.session_state.data_manager.save_all_week_wagers(week_num, wager_inputs)
            st.success(f"Week {week_num} wagers saved!")
            st.rerun()

def render_action_buttons(week_num: int):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"Clear Week {week_num}", type="secondary", use_container_width=True, key=f"clear_week_{week_num}"):
            st.session_state.data_manager.clear_week(week_num)
            st.success(f"Week {week_num} cleared!")
            st.rerun()
    
    with col2:
        if st.button(f"Copy from Previous Week", use_container_width=True, key=f"copy_week_{week_num}"):
            if week_num > 1:
                st.session_state.data_manager.copy_week_wagers(week_num - 1, week_num)
                st.success(f"Copied from Week {week_num - 1} to Week {week_num}!")
                st.rerun()
            else:
                st.warning("No previous week to copy from!")
    
    with col3:
        df = st.session_state.data_manager.export_week_data(week_num)
        csv_data = df.to_csv(index=False)
        st.download_button(
            label=f"Export Week {week_num}",
            data=csv_data,
            file_name=f"week_{week_num}_wagers.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"export_week_{week_num}"
        )
    
    with col4:
        if st.button(f"Refresh Data", use_container_width=True, key=f"refresh_week_{week_num}"):
            st.rerun()

if __name__ == "__main__":
    main()