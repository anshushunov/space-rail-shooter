import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from check_models import LIMITS, evaluate  # noqa: E402

LIM = LIMITS["ship"]
OK_DIMS = (3.4, 4.3, 1.9)
OK_TRIS = 2400


class EvaluateTests(unittest.TestCase):
    def test_valid_model_has_no_problems(self):
        self.assertEqual(evaluate("ship", OK_TRIS, OK_DIMS, LIM), [])

    def test_tris_bounds_are_inclusive(self):
        self.assertEqual(evaluate("ship", 1500, OK_DIMS, LIM), [])
        self.assertEqual(evaluate("ship", 3000, OK_DIMS, LIM), [])

    def test_tris_just_outside_bounds_fail(self):
        for tris in (1499, 3001):
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
        self.assertEqual(len(evaluate("ship", 9000, (0.0, 0.0, 0.0), LIM)), 4)


if __name__ == "__main__":
    unittest.main()
