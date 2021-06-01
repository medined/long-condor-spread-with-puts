
class RejectTracker:
    def __init__(self):
        self.reasons = {}

    def __add_reason(self, reason):
        if reason not in self.reasons:
            self.reasons[reason] = 0
        self.reasons[reason] = self.reasons[reason] + 1

    def not_four_puts(self):
        self.__add_reason('not_four_puts')

    def not_min_three_otm_puts(self):
        self.__add_reason('not_min_three_otm_puts')

    def no_p4_puts(self):
        self.__add_reason('no_p4_puts')

    def not_four_lcs(self):
        self.__add_reason('not_four_lcs')

    def below_min_p1_mark(self):
        self.__add_reason('below_min_p1_mark')

    def zero_bid_size(self):
        self.__add_reason('zero_bid_size')
