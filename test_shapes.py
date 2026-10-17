# -*- coding: utf-8 -*-
"""shapes.py 的单元测试：验证点、圆、三角形、椭圆、多边形的核心行为。"""
import math
import unittest

from shapes import Point, Circle, Triangle, Ellipse, Polygon


class TestPoint(unittest.TestCase):
    def test_distance(self):
        p1, p2 = Point(1, 2), Point(4, 6)
        self.assertAlmostEqual(p1.distance(p2), 5.0)


class TestCircle(unittest.TestCase):
    def setUp(self):
        self.c = Circle(Point(0, 0), 5)

    def test_relation(self):
        self.assertEqual(self.c.relation(Point(3, 4)), "圆上")
        self.assertEqual(self.c.relation(Point(0, 5)), "圆上")
        self.assertEqual(self.c.relation(Point(1, 1)), "圆内")
        self.assertEqual(self.c.relation(Point(6, 0)), "圆外")

    def test_area_perimeter(self):
        self.assertAlmostEqual(self.c.area(), math.pi * 25)
        self.assertAlmostEqual(self.c.perimeter(), 2 * math.pi * 5)


class TestTriangle(unittest.TestCase):
    def test_valid(self):
        t = Triangle(Point(0, 0), Point(4, 0), Point(0, 3))
        self.assertAlmostEqual(t.perimeter(), 12.0)
        self.assertAlmostEqual(t.area(), 6.0)

    def test_collinear_rejected(self):
        with self.assertRaises(ValueError):
            Triangle(Point(-2, 1), Point(1, 1), Point(4, 1))

    def test_too_flat_rejected(self):
        with self.assertRaises(ValueError):
            Triangle(Point(0, 0), Point(1, 0), Point(2, 0))

    def test_kinds(self):
        self.assertEqual(Triangle(Point(0, 0), Point(3, 0), Point(0, 4)).kinds(), "直角三角形")
        self.assertEqual(Triangle(Point(0, 0), Point(4, 0), Point(2, 3)).kinds(), "等腰三角形")
        self.assertEqual(
            Triangle(Point(0, 0), Point(4, 0), Point(2, math.sqrt(12))).kinds(),
            "等边三角形",
        )


class TestEllipse(unittest.TestCase):
    def test_area(self):
        e = Ellipse(Point(0, 0), 5, 3)
        self.assertAlmostEqual(e.area(), math.pi * 15)


class TestPolygon(unittest.TestCase):
    def test_area_perimeter(self):
        poly = Polygon([Point(0, 0), Point(2, 0), Point(3, 2), Point(1, 3), Point(-1, 1)])
        self.assertAlmostEqual(poly.area(), 7.5)

    def test_too_few_vertices(self):
        with self.assertRaises(ValueError):
            Polygon([Point(0, 0), Point(1, 1)])


if __name__ == "__main__":
    unittest.main()
