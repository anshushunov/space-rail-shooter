import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from check_models import LIMITS, evaluate  # noqa: E402

LIM = LIMITS["ship"]
TRIS_LO, TRIS_HI = LIM["tris"]
OK_TRIS = (TRIS_LO + TRIS_HI) // 2
OK_DIMS = tuple((LIM[a][0] + LIM[a][1]) / 2 for a in "xyz")


class EvaluateTests(unittest.TestCase):
    def test_valid_model_has_no_problems(self):
        self.assertEqual(evaluate("ship", OK_TRIS, OK_DIMS, LIM), [])

    def test_tris_bounds_are_inclusive(self):
        self.assertEqual(evaluate("ship", TRIS_LO, OK_DIMS, LIM), [])
        self.assertEqual(evaluate("ship", TRIS_HI, OK_DIMS, LIM), [])

    def test_tris_just_outside_bounds_fail(self):
        for tris in (TRIS_LO - 1, TRIS_HI + 1):
            with self.subTest(tris=tris):
                problems = evaluate("ship", tris, OK_DIMS, LIM)
                self.assertEqual(len(problems), 1)
                self.assertIn("треугольников", problems[0])

    def test_each_axis_just_outside_range_fails(self):
        eps = 0.01
        for i, axis in enumerate("xyz"):
            lo, hi = LIM[axis]
            for bad in (lo - eps, hi + eps):
                with self.subTest(axis=axis, value=bad):
                    dims = list(OK_DIMS)
                    dims[i] = bad
                    problems = evaluate("ship", OK_TRIS, tuple(dims), LIM)
                    self.assertEqual(len(problems), 1)
                    self.assertIn(f"размер {axis}=", problems[0])

    def test_axis_bounds_are_inclusive(self):
        for i, axis in enumerate("xyz"):
            for bound in LIM[axis]:
                with self.subTest(axis=axis, value=bound):
                    dims = list(OK_DIMS)
                    dims[i] = bound
                    self.assertEqual(evaluate("ship", OK_TRIS, tuple(dims), LIM), [])

    def test_problems_accumulate(self):
        self.assertEqual(len(evaluate("ship", TRIS_HI * 10, (0.0, 0.0, 0.0), LIM)), 4)


class LimitsTableTests(unittest.TestCase):
    def test_every_entry_has_ordered_ranges(self):
        for name, lim in LIMITS.items():
            with self.subTest(model=name):
                self.assertEqual(set(lim), {"tris", "x", "y", "z"})
                for key, (lo, hi) in lim.items():
                    self.assertLess(lo, hi, f"{name}.{key}")
                    self.assertGreater(lo, 0, f"{name}.{key}")

    def test_expected_models_present(self):
        self.assertIn("ship", LIMITS)


if __name__ == "__main__":
    unittest.main()
