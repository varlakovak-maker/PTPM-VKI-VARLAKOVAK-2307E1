import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from delivery_service import calculate_delivery_cost

INVALID = (-1, "0000-00-00")
SEND_DATE = "2026-09-03"  # фиксированная дата отправки в модуле


class TestInputValidation(unittest.TestCase):
    def test_weight_below_minimum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(0.09, 100, "обычный"), INVALID)

    def test_zero_weight_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(0, 100, "обычный"), INVALID)

    def test_negative_weight_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(-5, 100, "обычный"), INVALID)

    def test_weight_above_maximum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(50.01, 100, "обычный"), INVALID)

    def test_distance_below_minimum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1, 0, "обычный"), INVALID)

    def test_distance_above_maximum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1, 5001, "обычный"), INVALID)

    def test_unknown_package_type_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "срочный"), INVALID)

    def test_empty_package_type_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1, 100, ""), INVALID)

    def test_minimum_weight_and_distance_are_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(0.1, 1, "обычный"), INVALID)

    def test_maximum_weight_and_distance_are_accepted(self):
        self.assertNotEqual(calculate_delivery_cost(50.0, 5000, "обычный"), INVALID)


class TestCostCalculation(unittest.TestCase):
    def test_base_cost_for_light_regular_parcel(self):
        # 200 + 100 * 5 = 700
        self.assertEqual(calculate_delivery_cost(1, 100, "обычный")[0], 700)

    def test_cost_for_minimal_distance(self):
        # 200 + 1 * 5 = 205
        self.assertEqual(calculate_delivery_cost(1, 1, "обычный")[0], 205)

    def test_weight_just_below_5kg_has_no_coefficient(self):
        self.assertEqual(calculate_delivery_cost(4.99, 100, "обычный")[0], 700)

    def test_weight_exactly_5kg_gets_medium_coefficient(self):
        # граница диапазона 5..20 кг: 700 * 1.2 = 840
        self.assertEqual(calculate_delivery_cost(5.0, 100, "обычный")[0], 840)

    def test_weight_just_above_5kg_gets_medium_coefficient(self):
        self.assertEqual(calculate_delivery_cost(5.01, 100, "обычный")[0], 840)

    def test_weight_just_below_20kg_keeps_medium_coefficient(self):
        self.assertEqual(calculate_delivery_cost(19.99, 100, "обычный")[0], 840)

    def test_weight_exactly_20kg_gets_heavy_coefficient(self):
        # 700 * 1.5 = 1050
        self.assertEqual(calculate_delivery_cost(20.0, 100, "обычный")[0], 1050)

    def test_maximum_weight_gets_heavy_coefficient(self):
        self.assertEqual(calculate_delivery_cost(50.0, 100, "обычный")[0], 1050)

    def test_fragile_parcel_adds_300(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "хрупкий")[0], 1000)

    def test_dangerous_parcel_adds_1000(self):
        self.assertEqual(calculate_delivery_cost(1, 100, "опасный")[0], 1700)

    def test_fragile_surcharge_is_added_after_weight_coefficient(self):
        # 700 * 1.2 + 300 = 1140
        self.assertEqual(calculate_delivery_cost(10, 100, "хрупкий")[0], 1140)


class TestExpressDelivery(unittest.TestCase):
    def test_express_regular_parcel_costs_more_than_standard(self):
        standard = calculate_delivery_cost(1, 1000, "обычный", False)[0]
        express = calculate_delivery_cost(1, 1000, "обычный", True)[0]
        self.assertGreater(express, standard)

    def test_express_dangerous_parcel_costs_more_than_standard(self):
        standard = calculate_delivery_cost(1, 1000, "опасный", False)[0]
        express = calculate_delivery_cost(1, 1000, "опасный", True)[0]
        self.assertGreater(express, standard)

    def test_express_is_not_slower_than_standard(self):
        standard = calculate_delivery_cost(1, 3000, "обычный", False)[1]
        express = calculate_delivery_cost(1, 3000, "обычный", True)[1]
        self.assertLessEqual(express, standard)

    def test_express_long_distance_is_twice_as_fast(self):
        # 5000 км: стандарт 10 дней, экспресс 5 дней
        self.assertEqual(calculate_delivery_cost(1, 5000, "обычный", True)[1], "2026-09-08")

    def test_express_delivery_takes_at_least_one_day_on_medium_distance(self):
        self.assertGreater(calculate_delivery_cost(1, 500, "обычный", True)[1], SEND_DATE)

    def test_express_delivery_takes_at_least_one_day_on_short_distance(self):
        self.assertGreater(calculate_delivery_cost(1, 1, "обычный", True)[1], SEND_DATE)


class TestDeliveryDate(unittest.TestCase):
    def test_short_distance_takes_one_day(self):
        self.assertEqual(calculate_delivery_cost(1, 1, "обычный")[1], "2026-09-04")

    def test_distance_499_km_takes_one_day(self):
        self.assertEqual(calculate_delivery_cost(1, 499, "обычный")[1], "2026-09-04")

    def test_distance_500_km_takes_one_day(self):
        self.assertEqual(calculate_delivery_cost(1, 500, "обычный")[1], "2026-09-04")

    def test_distance_1000_km_takes_two_days(self):
        self.assertEqual(calculate_delivery_cost(1, 1000, "обычный")[1], "2026-09-05")

    def test_maximum_distance_takes_ten_days(self):
        self.assertEqual(calculate_delivery_cost(1, 5000, "обычный")[1], "2026-09-13")

    def test_result_has_expected_types_and_date_format(self):
        result = calculate_delivery_cost(1, 100, "обычный")
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], int)
        self.assertRegex(result[1], r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
