class KrakenOrder():
    def __init__(self, ordertype, type, pair, userref=None, volume=None, price=None, price2=None, trigger=None, leverage=None,
            oflags=None, timeinforce=None, starttm=0, expiretm=0, closeordertype=None, close_price=None, close_price2=None,
            deadline=None, validate=True, otp=None):
        self.ordertype = ordertype
        self.type = type
        self.pair = pair
        self.userref = userref
        self.volume = volume
        self.price = price
        self.price2 = price2
        self.trigger = trigger
        self.leverage = leverage
        self.oflags = oflags
        self.timeinforce = timeinforce
        self.starttm = starttm
        self.expiretm = expiretm
        self.closeordertype = closeordertype
        self.close_price = close_price
        self.close_price2 = clowe_price2
        self.deadline = deadline
        self.validate = validate
        self.otp = otp

    def __str__(self):
        return str({
            'ordertype': self.ordertype
            'type': self.type
            'pair': self.pair
            'userref': self.userref
            'volume': self.volume
            'price': self.price
            'price2': self.price2
            'trigger': self.trigger
            'leverage': self.leverage
            'oflags': self.oflags
            'timeinforce': self.timeinforce
            'starttm': self.starttm
            'expiretm': self.expiretm
            'closeordertype': self.closeordertype
            'close_price': self.close_price
            'close_price2': self.clowe_price2
            'deadline': self.deadline
            'validate': self.validate
            'otp': self.otp
            })
