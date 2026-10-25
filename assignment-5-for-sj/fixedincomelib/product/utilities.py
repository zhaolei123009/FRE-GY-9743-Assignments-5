"""Long and short product directions."""

from enum import Enum

__all__ = ["LongOrShort"]


class LongOrShort(Enum):
    LONG = "long"
    SHORT = "short"

    @classmethod
    def from_string(cls, value: str) -> "LongOrShort":
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid token: {value}") from None

    def to_string(self) -> str:
        return self.value
