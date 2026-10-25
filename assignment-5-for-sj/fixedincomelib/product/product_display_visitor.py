"""Collect product attributes for display using a visitor."""

from functools import singledispatchmethod

import pandas as pd

from fixedincomelib.product.product_interfaces import Product, ProductVisitor
from fixedincomelib.product.linear_products import (
    ProductFixedAccruedCashflow, ProductOvernightIndexCashflow,
)

__all__ = ["ProductDisplayVisitor"]


class ProductDisplayVisitor(ProductVisitor):
    def __init__(self) -> None:
        self.nvps_ = []

    @singledispatchmethod
    def visit(self, product: Product):
        raise NotImplementedError(f"No display visitor for {product.product_type}")

    def display(self) -> pd.DataFrame:
        return pd.DataFrame(self.nvps_, columns=["Name", "Value"])

    def _common_items(self, product: Product):
        self.nvps_ = [
            ["Product Type", product.product_type],
            ["Notional", product.notional],
            ["Currency", product.currency.value_str],
            ["Long Or Short", product.long_or_short.to_string().upper()],
        ]

    @visit.register
    def _(self, product: ProductFixedAccruedCashflow):
        self._common_items(product)
        self.nvps_.append(["Effective Date", product.effective_date.ISO()])
        self.nvps_.append(["Termination Date", product.termination_date.ISO()])
        self.nvps_.append(["Accrual Basis", product.accrual_basis.value_str])
        self.nvps_.append(["Payment Date", product.payment_date.ISO()])
        self.nvps_.append(["Business Day Convention", product.business_day_convention.value_str])
        self.nvps_.append(["Holiday Convention", product.holiday_convention.value_str])

    @visit.register
    def _(self, product: ProductOvernightIndexCashflow):
        self._common_items(product)
        self.nvps_.append(["Effective Date", product.effective_date.ISO()])
        self.nvps_.append(["Termination Date", product.termination_date.ISO()])
        self.nvps_.append(["ON Index", product.on_index.name()])
        self.nvps_.append(["Compounding Method", product.compounding_method.to_string().upper()])
        self.nvps_.append(["Spread", product.spread])
        self.nvps_.append(["Payment Date", product.payment_date.ISO()])
