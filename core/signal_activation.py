class SignalActivationLayer:
    def __init__(self):
        self.miss_count = {}

    def should_force_activation(self, symbol):
        return self.miss_count.get(symbol, 0) > 20

    def register_miss(self, symbol):
        self.miss_count[symbol] = self.miss_count.get(symbol, 0) + 1

    def register_signal(self, symbol):
        self.miss_count[symbol] = 0
