class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = int(price)

    def info(self):
        return f"{self.name}: ¥{self.price}"

    def to_dict(self):
        return {"name": self.name, "price": self.price}

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["name"], d["price"])


class Food(MenuItem):
    def __init__(self, name, price, calorie):
        super().__init__(name, price)
        self.calorie = int(calorie)

    def info(self):
        return f"{self.name}: ¥{self.price}（{self.calorie}kcal）"

    def to_dict(self):
        base = super().to_dict()
        base["calorie"] = self.calorie
        return base

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["price"], d.get("calorie", 0))


class Drink(MenuItem):
    def __init__(self, name, price, volume_ml):
        super().__init__(name, price)
        self.volume_ml = int(volume_ml)

    def info(self):
        return f"{self.name}: ¥{self.price}（{self.volume_ml}ml）"

    def to_dict(self):
        base = super().to_dict()
        base["volume_ml"] = self.volume_ml
        return base

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["price"], d.get("volume_ml", 0))


class Dessert(MenuItem):
    def __init__(self, name, price, sugar_g):
        super().__init__(name, price)
        self.sugar_g = int(sugar_g)

    def info(self):
        return f"{self.name}: ¥{self.price}（糖質 {self.sugar_g}g）"

    def to_dict(self):
        base = super().to_dict()
        base["sugar_g"] = self.sugar_g
        return base

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["price"], d.get("sugar_g", 0))