"""Test DecimalString validation."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from binance_market_data_contracts.common import (
    ContractModel,
    NonNegativeDecimalString,
    PositiveDecimalString,
    PriceString,
    QuantityString,
)


class PriceModel(ContractModel):
    price: PriceString


class QuantityModel(ContractModel):
    quantity: QuantityString


class PositiveModel(ContractModel):
    value: PositiveDecimalString


class NonNegativeModel(ContractModel):
    value: NonNegativeDecimalString


class TestPriceString:
    @pytest.mark.parametrize(
        "valid_price",
        [
            "1",
            "1.0",
            "0.1",
            "29500.50",
            "0.00000001",
            "100000.12345678",
        ],
    )
    def test_valid_prices(self, valid_price):
        m = PriceModel(price=valid_price)
        assert m.price == valid_price

    @pytest.mark.parametrize(
        "invalid_price,reason",
        [
            ("0", "zero price not allowed"),
            ("-1", "negative"),
            ("-0.1", "negative"),
            (1.0, "float not string"),
            (0, "int not string"),
            ("1e3", "scientific notation"),
            ("NaN", "NaN"),
            ("Infinity", "Infinity"),
            ("-Infinity", "-Infinity"),
            ("", "empty string"),
            (" ", "whitespace"),
            ("+1", "leading plus"),
            ("0001.20", "leading zeros"),
            (".5", "leading dot"),
            ("1.", "trailing dot"),
        ],
    )
    def test_invalid_prices(self, invalid_price, reason):
        with pytest.raises((PydanticValidationError, ValueError)):
            PriceModel(price=invalid_price)

    def test_trailing_zeros_preserved(self):
        m = PriceModel(price="1.2300")
        assert m.price == "1.2300"


class TestQuantityString:
    @pytest.mark.parametrize(
        "valid_qty",
        [
            "0",
            "0.0",
            "1",
            "1.5",
            "0.00000000",
            "100.50000000",
        ],
    )
    def test_valid_quantities(self, valid_qty):
        m = QuantityModel(quantity=valid_qty)
        assert m.quantity == valid_qty

    @pytest.mark.parametrize(
        "invalid_qty",
        [
            "-1",
            "-0.1",
            (1.0),
            ("1e3"),
            ("-0"),
            ("NaN"),
            ("+5"),
            ("0001"),
            (".5"),
            ("5."),
        ],
    )
    def test_invalid_quantities(self, invalid_qty):
        with pytest.raises((PydanticValidationError, ValueError)):
            QuantityModel(quantity=invalid_qty)

    def test_zero_quantity_valid(self):
        m = QuantityModel(quantity="0")
        assert m.quantity == "0"

    def test_trailing_zeros_preserved(self):
        m = QuantityModel(quantity="0.12340000")
        assert m.quantity == "0.12340000"


class TestPositiveDecimalString:
    def test_zero_rejected(self):
        with pytest.raises((PydanticValidationError, ValueError)):
            PositiveModel(value="0")


class TestNonNegativeDecimalString:
    def test_zero_accepted(self):
        m = NonNegativeModel(value="0")
        assert m.value == "0"

    def test_negative_rejected(self):
        with pytest.raises((PydanticValidationError, ValueError)):
            NonNegativeModel(value="-1")
