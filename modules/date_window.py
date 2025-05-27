import json
import os
from datetime import datetime, timedelta

STATE_FILE = 'state/state.json'
DATE_FORMAT = '%Y-%m-%d'

def load_state():
    if not os.path.exists(STATE_FILE):
        raise FileNotFoundError("Missing state file. Please initialize 'state.json'.")
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_next_week_window():
    state = load_state()
    last_end_str = state['last_run_end']
    last_end = datetime.strptime(last_end_str, DATE_FORMAT)

    # Define next window
    start = last_end + timedelta(days=1)
    end = start + timedelta(days=6)

    return start.date(), end.date()

def update_state_with_end_date(end_date):
    state = {'last_run_end': end_date.strftime(DATE_FORMAT)}
    save_state(state)
