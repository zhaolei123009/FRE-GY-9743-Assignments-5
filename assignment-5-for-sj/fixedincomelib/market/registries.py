"""Look up indices, funding identifiers and market data conventions."""

from typing import Any, Self, Optional

import pandas as pd
import QuantLib as ql

from fixedincomelib.utilities.utils import Registry
from fixedincomelib.market.basics import Currency

__all__ = [
    "IndexRegistry",
    "DataConventionRegFunction",
    "DataConventionRegistry",
    "DataIdentifierRegistry",
    "FundingIdentifier",
    "FundingIdentifierRegistry",
]


class IndexRegistry:
    _constructors = {
        "SOFR-1B": ql.Sofr,
        "FF-1B": ql.FedFunds,
        "SONIA-1B": ql.Sonia,
    }

    def get(self, key: str) -> ql.OvernightIndex:
        if not isinstance(key, str):
            raise TypeError("Index name must be a string")
        try:
            constructor = self._constructors[key.upper()]
        except KeyError:
            supported = ", ".join(self._constructors)
            raise ValueError(f"Unknown overnight index {key!r}; supported: {supported}") from None
        return constructor()


class DataConventionRegFunction(Registry):

    def __new__(cls) -> Self:
        return super().__new__(cls, "", cls.__name__)

    def register(self, key: Any, value: Any) -> None:
        super().register(key, value)
        self._map[key] = value


class DataConventionRegistry(Registry):

    def __new__(cls) -> Self:
        return super().__new__(cls, "data_conventions", "DataConevention")

    def register(self, key: Any, value: Any) -> None:
        value_ = value.copy()
        super().register(key, value_)
        type = value_["type"]
        value_.pop("type")
        func = DataConventionRegFunction().get(type)
        self._map[key] = func(key, value_)

    def display_all_data_conventions(self) -> pd.DataFrame:
        to_print = []
        for k, v in self._map.items():
            to_print.append([k, v.type()])
        return pd.DataFrame(to_print, columns=["Name", "Type"])


class DataIdentifierRegistry(Registry):

    def __new__(cls) -> Self:
        return super().__new__(cls, "", cls.__name__)

    def register(self, key: Any, value: Any) -> None:
        super().register(key, value)
        self._map[key] = value


class FundingIdentifier(ql.Index):

    def __init__(self, unique_name: str, currency: str, reference_index: Optional[str] = ""):
        self.name_ = unique_name
        self.currency_ = Currency(currency)
        self.reference_index_ = None
        if reference_index != "":
            self.reference_index_ = IndexRegistry().get(reference_index)

    def name(self):
        return self.name_

    def currency(self) -> Currency:
        return self.currency_

    @property
    def reference_index(self) -> ql.Index:
        return self.reference_index_


class FundingIdentifierRegistry(Registry):

    def __new__(cls) -> Self:
        return super().__new__(cls, "fundingidentifiers", "FundingIdentifier")

    def register(self, key: Any, value: Any) -> None:
        super().register(key, value)
        assert "Currency" in value
        reference_index = value.get("Reference Index", "")
        self._map[key.upper()] = FundingIdentifier(key.upper(), value["Currency"], reference_index)

    def get(self, key: Any, **args) -> Any:
        if key.upper() not in self._map:
            raise Exception(f"Cannot find {key} in funding identifier registry.")
        return self._map[key.upper()]

    def display_all_indices(self) -> pd.DataFrame:
        to_print = []
        for k, _ in self._map.items():
            fi: FundingIdentifier = self.get(k)
            to_print.append([k, fi.name()])
        return pd.DataFrame(to_print, columns=["Name", "fundingIdentifier"])
