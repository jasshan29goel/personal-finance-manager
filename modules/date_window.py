import json
import os
from datetime import datetime, timedelta, date
from constants import STATE_FILE, MONTH_FORMAT, MONTH_TO_RUN_FIELD


def load_state():
    if not os.path.exists(STATE_FILE):
        raise FileNotFoundError(f"Missing state file. Please initialize {STATE_FILE}.")
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_window_from_month() -> tuple[date, date]:
    state = load_state()

    if MONTH_TO_RUN_FIELD not in state:
        raise KeyError(f"Missing {MONTH_TO_RUN_FIELD} in {STATE_FILE}. Expected format: {MONTH_FORMAT}.")

    month_str = state[MONTH_TO_RUN_FIELD]
    try:
        start = datetime.strptime(month_str, MONTH_FORMAT)
    except ValueError:
        raise ValueError(f"Invalid {MONTH_TO_RUN_FIELD} format. Expected {MONTH_FORMAT}.")

    end = start + timedelta(days=10)

    return start.date(), end.date()

def update_state_with_next_month(start_date):
    # Compute the first day of the next month
    if start_date.month == 12:
        next_month = datetime(start_date.year + 1, 1, 1)
    else:
        next_month = datetime(start_date.year, start_date.month + 1, 1)

    state = load_state()
    state[MONTH_TO_RUN_FIELD] = next_month.strftime(MONTH_FORMAT)
    save_state(state)
