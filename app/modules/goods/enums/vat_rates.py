from enum import Enum


class VATRate(Enum):
    NONE = 0
    VAT_0 = 1
    VAT_10 = 2
    VAT_20 = 3

    def get_rate(self) -> int:
        """
        Returns the VAT rate
        """
        return {
            VATRate.NONE: 0,
            VATRate.VAT_0: 0,
            VATRate.VAT_10: 10,
            VATRate.VAT_20: 20
        }[self]
