"""Compounding labels and IFR data conventions from the course template."""

from abc import ABC
from enum import Enum

import pandas as pd
import QuantLib as ql

from fixedincomelib.market.basics import BusinessDayConvention, HolidayConvention
from fixedincomelib.market.registries import DataConventionRegFunction, IndexRegistry

__all__ = ["CompoundingMethod", "DataConvention", "DataConventionIFR"]


class CompoundingMethod(Enum):
    SIMPLE = "simple"
    ARITHMETIC = "arithmetic"
    COMPOUND = "compound"

    @classmethod
    def from_string(cls, value: str) -> "CompoundingMethod":
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid token: {value}") from None

    def to_string(self) -> str:
        return self.value


class DataConvention(ABC):

    _type = ""

    def __init__(self, unique_name: str, type: str, content: dict):
        super().__init__()
        self.conv_name = unique_name.upper()
        self.conv_type = type.upper()
        self.content = content
        assert len(self.content) != 0

    @property
    def name(self):
        return self.conv_name

    @classmethod
    def type(cls):
        return cls._type

    def display(self):
        to_print = []
        for k, v in self.content.items():
            k_ = k
            if k_.endswith("_"):
                k_ = k[:-1]
            to_print.append([k_.upper(), v])
        return pd.DataFrame(to_print, columns=["Name", "Value"])


class DataConventionIFR(DataConvention):

    _type = "INSTANTANEOUS FORWARD RATE"

    def __init__(self, unique_name, content):

        if len(content) != 3:
            raise ValueError(f"{unique_name}: content should have 3 fields, got {len(content)}")

        self.index_ = None

        upper_content = {k.upper(): v for k, v in content.items()}
        for k, v in upper_content.items():
            if k.upper() == "INDEX":
                self.index_ = v
            elif k == "BUSINESS_DAY_CONVENTION":
                self.business_day_convention_ = v
            elif k == "HOLIDAY_CONVENTION":
                self.holiday_convention_ = v

        super().__init__(unique_name, DataConventionIFR._type, self.__dict__.copy())

    @property
    def index(self) -> ql.Index:
        return IndexRegistry().get(self.index_)

    @property
    def business_day_convention(self) -> BusinessDayConvention:
        return BusinessDayConvention(self.business_day_convention_)

    @property
    def holiday_convention(self) -> HolidayConvention:
        return HolidayConvention(self.holiday_convention_)


DataConventionRegFunction().register(DataConventionIFR._type, DataConventionIFR)
