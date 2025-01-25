class BacktestConfig:
    def __init__(self, 
                 initial_capital=100000, 
                 trade_percentage=0.1,
                 commission_per_share=0.005,
                 variable_fee=0.00018,
                 bid_ask_spread=0.0002,
                 price_impact_coef=0.002):
        self.initial_capital = initial_capital
        self.trade_percentage = trade_percentage
        self.commission_per_share = commission_per_share
        self.variable_fee = variable_fee
        self.bid_ask_spread = bid_ask_spread
        self.price_impact_coef = price_impact_coef