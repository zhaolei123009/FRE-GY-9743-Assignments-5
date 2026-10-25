"""Create and display cashflow products."""

from typing import Optional

import pandas as pd

from fixedincomelib.date.basics import Date, TermOrDate
from fixedincomelib.market.basics import (
    AccrualBasis, BusinessDayConvention, Currency, HolidayConvention,
)
from fixedincomelib.market.data_conventions import CompoundingMethod
from fixedincomelib.product import (
    Product, ProductDisplayVisitor,
    ProductFixedAccruedCashflow, ProductOvernightIndexCashflow,
)

__all__ = [
    "qfCreateProductFixedAccruedCashflow",
    "qfCreateProductOvernightIndexCashflow",
    "qfDisplayProduct",
]


def qfCreateProductFixedAccruedCashflow(
    effective_date: str,
    termination_date: str,
    currency: str,
    notional: float,
    accrual_basis: str,
    payment_date: Optional[str] = "",
    business_day_convention: str = "F",
    holiday_convention: str = "USGS",
) -> ProductFixedAccruedCashflow:
    """Create a fixed-accrual cashflow; omitted payment defaults to termination."""
    return ProductFixedAccruedCashflow(
        Date(effective_date), Date(termination_date), Currency(currency), notional,
        AccrualBasis(accrual_basis),
        None if payment_date is None or payment_date == "" else Date(payment_date),
        BusinessDayConvention(business_day_convention or "F"),
        HolidayConvention(holiday_convention or "USGS"),
    )


def qfCreateProductOvernightIndexCashflow(
    effective_date: str,
    term_or_termination_date: str,
    overnight_index: str,
    notional: float,
    compounding_method: str = "compound",
    spread: float = 0.0,
    payment_date: Optional[str] = "",
) -> ProductOvernightIndexCashflow:
    """Create an overnight cashflow from a date or tenor such as '3M'."""
    if not isinstance(term_or_termination_date, str) or not term_or_termination_date:
        raise ValueError("term_or_termination_date must be a nonempty date or tenor string")
    return ProductOvernightIndexCashflow(
        Date(effective_date), TermOrDate(term_or_termination_date), overnight_index,
        CompoundingMethod.from_string(compounding_method), spread, notional,
        None if payment_date is None or payment_date == "" else Date(payment_date),
    )


def qfDisplayProduct(product: Product) -> pd.DataFrame:
    """Collect a product's features through its visitor and return Name/Value."""
    if not isinstance(product, Product):
        raise TypeError("product must be a Product")
    visitor = ProductDisplayVisitor()
    product.accept(visitor)
    return visitor.display()
