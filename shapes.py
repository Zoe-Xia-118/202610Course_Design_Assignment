# -*- coding: utf-8 -*-
"""
基于坐标的形状设计
====================
以点为基础组建不同形状：Point（点）、Circle（圆）、Triangle（三角形），
并包含合法性检查。进阶部分：等腰/等边/直角三角形判定、椭圆、多边形。

运行：python3 shapes.py
"""
import math
from abc import ABC, abstractmethod

# ============ 基础：点 ============
class Point:
    """平面上的一个点，两个数据成员分别表示横、纵坐标"""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def distance(self, other):
        """返回本点到另一个点的欧氏距离"""
        return math.hypot(self.x - other.x, self.y - other.y)

    def __str__(self):
        return f"({self.x:g}, {self.y:g})"

    def __repr__(self):
        return f"Point({self.x:g}, {self.y:g})"


# ============ 思考题：抽象类设计 ============
class Shape(ABC):
    """抽象基类。

    设计思路：把所有图形“共有”的能力抽出来作为抽象方法
    （周长、面积），让具体图形各自实现。
    好处：调用方只需面向 Shape 编程，无需关心具体类型，
    新图形（五边形、椭圆…）无需改动已有代码即可加入。
    """
    @abstractmethod
    def perimeter(self):
        """返回周长"""

    @abstractmethod
    def area(self):
        """返回面积"""


# ============ 圆 ============
class Circle(Shape):
    """圆：包含一个 Point 圆心 + 半径"""

    def __init__(self, center, radius):
        self.center = center          # Point 类型
        self.radius = float(radius)
        if self.radius < 0:
            raise ValueError("半径不能为负数")

    def relation(self, p):
        """判断给定点 p 是在圆内、圆外还是圆上"""
        d = self.center.distance(p)
        eps = 1e-9                    # 浮点容差，避免“恰好相等”被误判
        if d < self.radius - eps:
            return "圆内"
        if d > self.radius + eps:
            return "圆外"
        return "圆上"

    def perimeter(self):
        return 2 * math.pi * self.radius

    def area(self):
        return math.pi * self.radius ** 2

    def __str__(self):
        return f"圆心{self.center} 半径{self.radius:g}"


# ============ 三角形（含合法性检查） ============
class Triangle(Shape):
    """三角形：三个 Point 成员 + 周长；初始化时校验三点能否构成三角形"""

    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c
        # 三条边长（升序，便于判定特殊三角形）
        self._sides = sorted([a.distance(b), b.distance(c), c.distance(a)])
        if not self._valid():
            raise ValueError(
                f"三点 {a}, {b}, {c} 无法构成三角形：共线或两边之和不大于第三边"
            )

    def _valid(self):
        """合法性检查：面积不为 0（三点不共线）且任意两边之和大于第三边"""
        s1, s2, s3 = self._sides
        eps = 1e-9
        if self.area() < eps:         # 共线三点面积为 0
            return False
        return s1 + s2 > s3 + eps     # 三角形不等式（s3 为最长边）

    def perimeter(self):
        return sum(self._sides)

    def area(self):
        """面积：叉积法（也即鞋带公式的三角形特例）"""
        (x1, y1), (x2, y2), (x3, y3) = (
            (self.a.x, self.a.y), (self.b.x, self.b.y), (self.c.x, self.c.y)
        )
        return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2

    # ---- 进阶：特殊三角形判定 ----
    def is_equilateral(self):
        """等边三角形：三边近似相等"""
        return abs(self._sides[0] - self._sides[2]) < 1e-9

    def is_isosceles(self):
        """等腰三角形：至少两边近似相等"""
        return (abs(self._sides[0] - self._sides[1]) < 1e-9
                or abs(self._sides[1] - self._sides[2]) < 1e-9)

    def is_right(self):
        """直角三角形：最长边平方 ≈ 两短边平方和（勾股定理）"""
        s1, s2, s3 = self._sides
        return abs(s1 * s1 + s2 * s2 - s3 * s3) < 1e-6

    def kinds(self):
        """返回三角形类型描述（进阶）"""
        result = []
        if self.is_equilateral():
            result.append("等边")
        elif self.is_isosceles():
            result.append("等腰")
        if self.is_right():
            result.append("直角")
        return ("、".join(result) + "三角形") if result else "一般三角形"

    def __str__(self):
        return f"三角形 {self.a}-{self.b}-{self.c}"


# ============ 进阶：椭圆 ============
class Ellipse(Shape):
    """椭圆：中心点 + 半长轴 rx + 半短轴 ry"""

    def __init__(self, center, rx, ry):
        self.center = center
        self.rx = float(rx)
        self.ry = float(ry)
        if self.rx < 0 or self.ry < 0:
            raise ValueError("半轴长度不能为负数")
        self.rx, self.ry = max(self.rx, self.ry), min(self.rx, self.ry)

    def perimeter(self):
        """椭圆周长：拉马努金近似公式"""
        h = ((self.rx - self.ry) ** 2) / ((self.rx + self.ry) ** 2)
        return math.pi * (self.rx + self.ry) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))

    def area(self):
        return math.pi * self.rx * self.ry

    def __str__(self):
        return f"椭圆 中心{self.center} 半轴{self.rx:g}×{self.ry:g}"


# ============ 进阶：多边形 ============
class Polygon(Shape):
    """多边形：由若干个 Point 顶点组成（按顺序连接）"""

    def __init__(self, vertices):
        if len(vertices) < 3:
            raise ValueError("至少需要 3 个顶点才能构成多边形")
        self.vertices = list(vertices)

    def perimeter(self):
        total = 0.0
        n = len(self.vertices)
        for i in range(n):
            total += self.vertices[i].distance(self.vertices[(i + 1) % n])
        return total

    def area(self):
        """面积：鞋带公式（Shoelace），顶点按顺序给出"""
        s = 0.0
        n = len(self.vertices)
        for i in range(n):
            p1, p2 = self.vertices[i], self.vertices[(i + 1) % n]
            s += p1.x * p2.y - p2.x * p1.y
        return abs(s) / 2

    def __str__(self):
        return "多边形 " + "-".join(str(p) for p in self.vertices)


# ============ 演示主程序 ============
def demo():
    print("=" * 52)
    print("1. 点（Point）")
    p1, p2 = Point(1, 2), Point(4, 6)
    print(f"  p1={p1}, p2={p2}，两点距离 = {p1.distance(p2):.4f}")

    print("\n2. 圆（Circle）与点在圆内/上/外判定")
    c = Circle(Point(0, 0), 5)
    print(f"  {c}，周长={c.perimeter():.4f}，面积={c.area():.4f}")
    for q in (Point(3, 4), Point(0, 5), Point(6, 0), Point(1, 1)):
        print(f"  点{q} 在：{c.relation(q)}")

    print("\n3. 三角形（Triangle）与合法性检查")
    t1 = Triangle(Point(0, 0), Point(4, 0), Point(0, 3))
    print(f"  {t1}，周长={t1.perimeter():.4f}，面积={t1.area():.4f}，类型：{t1.kinds()}")
    try:
        t2 = Triangle(Point(-2, 1), Point(1, 1), Point(4, 1))   # 三点共线
        print(f"  {t2}")
    except ValueError as e:
        print(f"  非法输入被拒绝：{e}")

    print("\n4. 抽象类设计（思考题）")
    shapes = [Circle(Point(0, 0), 3), Triangle(Point(0, 0), Point(3, 0), Point(0, 4)),
              Ellipse(Point(0, 0), 5, 3), Polygon([Point(0, 0), Point(2, 0),
              Point(3, 2), Point(1, 3), Point(-1, 1)])]
    for s in shapes:
        print(f"  {type(s).__name__:9s}：周长={s.perimeter():8.4f}，面积={s.area():8.4f}")

    print("\n5. 进阶：特殊三角形判定")
    tests = {
        "等腰": [(0, 0), (4, 0), (2, 3)],
        "等边": [(0, 0), (4, 0), (2, math.sqrt(12))],
        "直角": [(0, 0), (3, 0), (0, 4)],
    }
    for name, pts in tests.items():
        tri = Triangle(*(Point(*p) for p in pts))
        print(f"  构造{name}数据 → {tri.kinds()}（周长={tri.perimeter():.4f}）")

    print("\n6. 进阶：椭圆与多边形")
    e = Ellipse(Point(0, 0), 5, 3)
    print(f"  {e}，周长≈{e.perimeter():.4f}，面积={e.area():.4f}")
    poly = Polygon([Point(0, 0), Point(2, 0), Point(3, 2), Point(1, 3), Point(-1, 1)])
    print(f"  {poly}，周长={poly.perimeter():.4f}，面积={poly.area():.4f}")


if __name__ == "__main__":
    demo()
