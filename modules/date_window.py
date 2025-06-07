import json
import os
from datetime import datetime, timedelta

STATE_FILE = 'state/state.json'
MONTH_FORMAT = '%Y-%m'

def load_state():
    if not os.path.exists(STATE_FILE):
        raise FileNotFoundError("Missing state file. Please initialize 'state.json'.")
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_window_from_month():
    state = load_state()

    if 'month_to_run' not in state:
        raise KeyError("Missing 'month_to_run' in state.json. Expected format: 'YYYY-MM'.")

    month_str = state['month_to_run']
    try:
        start = datetime.strptime(month_str, MONTH_FORMAT)
    except ValueError:
        raise ValueError("Invalid 'month_to_run' format. Expected 'YYYY-MM'.")

    end = start + timedelta(days=10)

    return start.date(), end.date()

def update_state_with_next_month(start_date):
    # Compute the first day of the next month
    if start_date.month == 12:
        next_month = datetime(start_date.year + 1, 1, 1)
    else:
        next_month = datetime(start_date.year, start_date.month + 1, 1)

    state = load_state()
    state['month_to_run'] = next_month.strftime(MONTH_FORMAT)
    save_state(state)
