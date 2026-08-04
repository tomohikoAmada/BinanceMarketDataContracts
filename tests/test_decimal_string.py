"""Test DecimalString validation with strict=True Pydantic."""

import json

import pytest
from pydantic import ValidationError

from binance_market_data_contracts.common import (
    ContractModel,
    PositiveQuantityString,
    PriceString,
    QuantityString,
    SignedDecimalString,
)

JSON = "json"


class PriceModel(ContractModel):
    price: PriceString


class QuantityModel(ContractModel):
    quantity: QuantityString


class SignedModel(ContractModel):
    value: SignedDecimalString


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
            "1.2300",  # trailing zeros preserved
        ],
    )
    def test_valid_prices_json(self, valid_price):
        m = PriceModel.model_validate_json(json.dumps({"price": valid_price}))
        assert m.price == valid_price

    @pytest.mark.parametrize(
        "invalid_price",
        [
            "0",
            "-1",
            "1e3",
            "NaN",
            "Infinity",
            "",
            "+1",
            "0001.20",
            ".5",
            "1.",
            " ",
        ],
    )
    def test_invalid_prices_json(self, invalid_price):
        with pytest.raises(ValidationError):
            PriceModel.model_validate_json(json.dumps({"price": invalid_price}))

    def test_integer_passed_as_string_in_strict(self):
        """In strict mode, model_validate with int for str field should fail."""
        with pytest.raises(ValidationError):
            PriceModel.model_validate({"price": 123})

    def test_float_passed_as_string_in_strict(self):
        with pytest.raises(ValidationError):
            PriceModel.model_validate({"price": 123.45})

    def test_trailing_zeros_preserved(self):
        m = PriceModel.model_validate_json(json.dumps({"price": "1.2300"}))
        assert m.price == "1.2300"


class TestQuantityString:
    @pytest.mark.parametrize("valid_qty", ["0", "0.0", "1", "1.5", "0.00000000", "100.50000000"])
    def test_valid_quantities_json(self, valid_qty):
        m = QuantityModel.model_validate_json(json.dumps({"quantity": valid_qty}))
        assert m.quantity == valid_qty

    @pytest.mark.parametrize("invalid_qty", ["-1", "-0.1", "1e3", "-0", "NaN", "+5", "0001", ".5", "5."])
    def test_invalid_quantities_json(self, invalid_qty):
        with pytest.raises(ValidationError):
            QuantityModel.model_validate_json(json.dumps({"quantity": invalid_qty}))

    def test_zero_quantity_valid(self):
        m = QuantityModel.model_validate_json(json.dumps({"quantity": "0"}))
        assert m.quantity == "0"


class TestPositiveQuantityString:
    def test_zero_rejected(self):
        class PosModel(ContractModel):
            qty: PositiveQuantityString

        with pytest.raises(ValidationError):
            PosModel.model_validate_json(json.dumps({"qty": "0"}))

    def test_positive_accepted(self):
        class PosModel(ContractModel):
            qty: PositiveQuantityString

        m = PosModel.model_validate_json(json.dumps({"qty": "1.0"}))
        assert m.qty == "1.0"


class TestSignedDecimalString:
    def test_negative_accepted(self):
        m = SignedModel.model_validate_json(json.dumps({"value": "-0.0001"}))
        assert m.value == "-0.0001"

    def test_positive_accepted(self):
        m = SignedModel.model_validate_json(json.dumps({"value": "0.0001"}))
        assert m.value == "0.0001"

    def test_invalid_format(self):
        with pytest.raises(ValidationError):
            SignedModel.model_validate_json(json.dumps({"value": "1e-3"}))


class TestStrictCoercion:
    """Test that strict=True prevents type coercion."""

    def test_integer_string_not_coerced(self):
        """first_update_id='1' (str for int) must fail."""
        with pytest.raises(ValidationError):
            PriceModel.model_validate_json(json.dumps({"price": 100}))  # int as json number -> fails pattern

    def test_integer_not_coerced_to_bool(self):
        from binance_market_data_contracts.market_events import AggTrade

        with pytest.raises(ValidationError):
            AggTrade.model_validate_json(
                json.dumps(
                    {
                        "metadata": {
                            "venue": "BINANCE",
                            "market": "SPOT",
                            "symbol": "BTCUSDT",
                            "producer": "test",
                            "producer_version": "0.1.0",
                            "connection_id": "c1",
                        },
                        "aggregate_trade_id": 1,
                        "price": "100.0",
                        "quantity": "1.0",
                        "first_trade_id": 1,
                        "last_trade_id": 1,
                        "trade_time_ms": 1000,
                        "buyer_is_maker": 1,
                    }
                )
            )

    def test_float_not_coerced_to_decimal_string(self):
        with pytest.raises(ValidationError):
            PriceModel.model_validate_json(json.dumps({"price": 100.0}))
