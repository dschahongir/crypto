class SignalState:
    def __init__(self):
        self.touched_lower = False
        self.confirmed = False
        self.touch_price = None
        self.touch_time = None