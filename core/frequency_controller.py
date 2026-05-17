import time

class FrequencyController:
    def __init__(self):
        self.last_trade_time = {}
        self.mode = "balanced"

        self.mode_settings = {
            "conservative": 900,  # 15 min cooldown
            "balanced": 300,      # 5 min cooldown
            "aggressive": 60      # 1 min cooldown
        }

    def set_mode(self, mode):
        if mode in self.mode_settings:
            self.mode = mode

    def can_trade(self, symbol):
        cooldown = self.mode_settings[self.mode]
        last_time = self.last_trade_time.get(symbol, 0)

        return (time.time() - last_time) > cooldown

    def mark_trade(self, symbol):
        self.last_trade_time[symbol] = time.time()
