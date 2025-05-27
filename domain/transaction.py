class Transaction:
    def __init__(self, date: str, amount: str, note: str):
        self.date = date
        self.amount = amount
        self.note = note

    def to_row(self) -> list[str]:
        return [self.date, self.amount, self.note]
