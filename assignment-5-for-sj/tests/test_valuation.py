"""Independent formula and central-difference checks for all five completed tasks."""
import unittest
import numpy as np
import pandas as pd

from fixedincomelib import (
    qfCreateData1D, qfCreateDataCollection, qfCreateBuildMethod,
    qfCreateModelBuildMethodCollection, qfCreateModel,
    qfCreateProductFixedAccruedCashflow, qfCreateValuationParameters,
    qfCreateValuationParametersCollection, qfCreateValueReport,
)
from fixedincomelib.date import Date
from fixedincomelib.market.registries import FundingIdentifier
from fixedincomelib.valuation import ValuationRequest
from fixedincomelib.yield_curve.valuation_engine import ValuationEngineProductFixedAccrued


def build_model():
    base = qfCreateData1D('INSTANTANEOUS FORWARD RATE', 'SOFR-1B-IFR',
        pd.DataFrame({'values': [0.03, 0.04, 0.05]},
            index=['2026-04-02', '2027-01-02', '2028-01-02']))
    funding = qfCreateData1D('INSTANTANEOUS FORWARD RATE', 'SOFR-1B-FUNDING-IFR',
        pd.DataFrame({'values': [0.0, 0.001]},
            index=['2026-07-02', '2027-01-02']))
    methods = qfCreateModelBuildMethodCollection([
        qfCreateBuildMethod('YIELD_CURVE_INDEX', {
            'TARGET': 'SOFR-1B', 'INSTANTANEOUS FORWARD RATE': 'SOFR-1B-IFR'}),
        qfCreateBuildMethod('YIELD_CURVE_FUNDING', {
            'TARGET': 'SOFR-1B-FLAT', 'REFERENCE INDEX': 'SOFR-1B',
            'INSTANTANEOUS FORWARD RATE': 'SOFR-1B-FUNDING-IFR'}),
    ])
    return qfCreateModel('2026-01-02', 'YIELD_CURVE',
        qfCreateDataCollection([base, funding]), methods)


def make_engine(model, date='2026-10-02', notional=1_000_000, currency_map=False):
    product = qfCreateProductFixedAccruedCashflow(
        '2026-04-02', '2026-07-02', 'USD', notional, 'ACT/360',
        payment_date=date, business_day_convention='NONE')
    selection = ({'CURRENCIES': 'USD', 'FUNDING INDICES': 'SOFR-1B-FLAT'}
                 if currency_map else {'FUNDING INDEX': 'SOFR-1B-FLAT'})
    params = qfCreateValuationParametersCollection([
        qfCreateValuationParameters('FUNDING INDEX PARAMETER', selection)])
    return ValuationEngineProductFixedAccrued(model, params, product, ValuationRequest.PV)


class ValuationTests(unittest.TestCase):
    def setUp(self):
        self.model = build_model()
        self.date = Date('2026-10-02')

    def assert_blocks_close(self, actual, expected, **kwargs):
        self.assertEqual(len(actual), len(expected))
        for a, e in zip(actual, expected):
            np.testing.assert_allclose(a, e, **kwargs)

    def central_difference(self, value):
        result = []
        for name, count in zip(self.model.component_indices, self.model.num_sub_components):
            block = np.zeros(count)
            component = self.model.retrieve_model_component(name)
            for i in range(count):
                original = float(component.state_data[1, i])
                try:
                    component.perturb_model_parameter(i, original + 1e-6, True)
                    up = value()
                    component.perturb_model_parameter(i, original - 1e-6, True)
                    down = value()
                    block[i] = (up - down) / 2e-6
                finally:
                    component.perturb_model_parameter(i, original, True)
            result.append(block)
        return result

    def test_independent_cashflow_formula(self):
        # ACT/ACT ISDA model clock, ACT/360 cash accrual. No holiday rolls here.
        t1, t, ts = 90 / 365, 273 / 365, 181 / 365
        cash = 1_000_000 * 91 / 360
        df = np.exp(-0.03*t1 - 0.04*(t-t1) - 0.001*(t-ts))
        engine = make_engine(self.model)
        engine.calculate_value()
        self.assertAlmostEqual(engine.value, cash*df, places=8)
        self.assertEqual(engine.cash, 0.0)
        g = []
        engine.calculate_risk(g)
        self.assert_blocks_close(g, [
            -cash*df*np.array([t1, t-t1, 0.0]),
            -cash*df*np.array([ts, t-ts])], atol=1e-8)

    def test_local_gradient_dates_and_extrapolation(self):
        component = self.model.retrieve_model_component('SOFR-1B')
        for date in ['2026-01-02', '2026-04-02', '2026-10-02', '2029-01-02']:
            d = Date(date)
            g = np.full(3, 9.0)
            self.assertIsNone(component.discount_factor_gradient_wrt_state(d, g))
            numeric = self.central_difference(lambda: component.discount_factor(d))[0]
            np.testing.assert_allclose(g, numeric, rtol=1e-8, atol=1e-9)
            component.discount_factor_gradient_wrt_state(d, g, scaler=-2, accumulate=True)
            np.testing.assert_allclose(g, -numeric, rtol=1e-8, atol=1e-9)

    def test_model_gradient_against_finite_differences(self):
        for target in ['SOFR-1B', 'SOFR-1B-FLAT']:
            g = []
            self.assertIsNone(self.model.discount_factor_gradient_wrt_state(target, self.date, g))
            numerical = self.central_difference(lambda: self.model.discount_factor(target, self.date))
            self.assert_blocks_close(g, numerical, rtol=1e-8, atol=1e-9)
            self.model.discount_factor_gradient_wrt_state(target, self.date, g, scaler=2, accumulate=True)
            self.assert_blocks_close(g, [3*x for x in numerical], rtol=1e-8, atol=1e-9)
            self.model.discount_factor_gradient_wrt_state(target, self.date, g, scaler=-1)
            self.assert_blocks_close(g, [-x for x in numerical], rtol=1e-8, atol=1e-9)

    def test_engine_risk_against_finite_differences(self):
        for notional in [1_000_000, -1_000_000, 0]:
            engine = make_engine(self.model, notional=notional)
            def pv():
                engine.calculate_value()
                return engine.value
            g = []
            engine.calculate_risk(g)
            numerical = self.central_difference(pv)
            self.assert_blocks_close(g, numerical, rtol=1e-8, atol=2e-5)
            engine.calculate_risk(g, scaler=-2, accumulate=True)
            self.assert_blocks_close(g, [-x for x in numerical], rtol=1e-8, atol=2e-5)

    def test_past_today_and_accumulation(self):
        for date in ['2026-01-01', '2026-01-02']:
            engine = make_engine(self.model, date=date)
            engine.calculate_value()
            expected = 1_000_000*91/360 if date == '2026-01-02' else 0
            self.assertAlmostEqual(engine.value, expected)
            self.assertAlmostEqual(engine.cash, expected)
            g = [np.ones(3), np.ones(2)]
            engine.calculate_risk(g, accumulate=True)
            self.assert_blocks_close(g, [np.ones(3), np.ones(2)])
            engine.calculate_risk(g)
            self.assert_blocks_close(g, [np.zeros(3), np.zeros(2)])
            empty = []
            engine.calculate_risk(empty, accumulate=True)
            self.assert_blocks_close(empty, [np.zeros(3), np.zeros(2)])

    def test_reference_chain_three_levels_and_cycle(self):
        # Construct a third level from an existing component via a fresh identifier.
        from fixedincomelib.yield_curve import YieldCurveModelComponent
        source = self.model.retrieve_model_component('SOFR-1B-FLAT')
        identifier = FundingIdentifier('TEST-THIRD', 'USD')
        identifier.reference_index_ = source.component_identifier
        third = YieldCurveModelComponent(self.model.value_date, identifier,
            source.state_data.copy(), source.build_method)
        self.model.set_model_component(identifier.name(), third)
        g = []
        self.model.discount_factor_gradient_wrt_state('TEST-THIRD', self.date, g)
        numeric = self.central_difference(lambda: self.model.discount_factor('TEST-THIRD', self.date))
        self.assert_blocks_close(g, numeric, rtol=1e-8, atol=1e-9)
        identifier.reference_index_ = identifier
        with self.assertRaisesRegex(ValueError, 'Circular'):
            self.model.discount_factor_gradient_wrt_state('TEST-THIRD', self.date, [])

    def test_currency_map_and_public_report(self):
        engine = make_engine(self.model, currency_map=True)
        engine.calculate_value()
        pv = qfCreateValueReport(self.model, engine.product_, engine.valuation_parameters_collection_, 'PV')
        self.assertTrue(np.isclose(pv[0][1], engine.value))
        report = qfCreateValueReport(self.model, engine.product_, engine.valuation_parameters_collection_, 'FirstOrderRisk')
        raw = []
        engine.calculate_risk(raw)
        self.assert_blocks_close(report.state_gradient, raw)
        np.testing.assert_allclose(report.display()['VALUES'], np.concatenate(raw)*1e-4)

    def test_invalid_local_inputs(self):
        c = self.model.retrieve_model_component('SOFR-1B')
        with self.assertRaises(ValueError):
            c.discount_factor_gradient_wrt_state(Date('2025-12-31'), np.zeros(3))
        with self.assertRaises(ValueError):
            c.discount_factor_gradient_wrt_state(self.date, np.zeros(2))
        with self.assertRaises(TypeError):
            c.discount_factor_gradient_wrt_state(self.date, np.zeros(3, dtype=int))


if __name__ == '__main__':
    unittest.main()
