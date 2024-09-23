class KrakenOrder():
    def __init__(self, ordertype, type, pair, userref=None, volume=None, price=None, price2=None, trigger=None, leverage=None,
            oflags=None, timeinforce=None, starttm=0, expiretm=0, close_ordertype=None, close_price=None, close_price2=None,
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
        self.close_ordertype = close_ordertype
        self.close_price = close_price
        self.close_price2 = close_price2
        self.deadline = deadline
        self.validate = validate
        self.otp = otp

    def __str__(self):
        return str({
            'ordertype': self.ordertype,
            'type': self.type,
            'pair': self.pair,
            'userref': self.userref,
            'volume': self.volume,
            'price': self.price,
            'price2': self.price2,
            'trigger': self.trigger,
            'leverage': self.leverage,
            'oflags': self.oflags,
            'timeinforce': self.timeinforce,
            'starttm': self.starttm,
            'expiretm': self.expiretm,
            'close_ordertype': self.close_ordertype,
            'close_price': self.close_price,
            'close_price2': self.close_price2,
            'deadline': self.deadline,
            'validate': self.validate,
            'otp': self.otp
            })

