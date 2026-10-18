# -*- coding: utf-8 -*-
"""
基于坐标的形状设计
====================
以点为基础组建不同形状：Point（点）、Circle（圆）、Triangle（三角形），
并包含合法性检查。进阶部分：等腰/等边/直角三角形判定、椭圆、多边形。

运行：python3 shapes.py
"""
import json
import math
import sys
from abc import ABC, abstractmethod

# ================================================================
# 公式字典（与 形状设计可视化.html 共享，改一处必须同步改另一处）
# ----------------------------------------------------------------
# 1. 两点距离：sqrt((x1-x2)^2 + (y1-y2)^2)      → Point.distance / JS dist()
# 2. 三角形面积：叉积法 |(x2-x1)(y3-y1)-(x3-x1)(y2-y1)|/2
#                                              → Triangle.area / JS triInfo()
# 3. 三角形合法性：面积 > 1e-9 且最短两边之和 > 最长边 + 1e-9
#                                              → Triangle._valid / JS triInfo()
# 4. 直角三角形判定：c^2 ≈ a^2 + b^2（容差 1e-6）
#                                              → Triangle.is_right / JS triInfo()
# 5. 等腰/等边判定：边长差容差 1e-9            → Triangle.is_* / JS triInfo()
# 6. 圆：周长 2πr，面积 πr^2，点位置判定容差 1e-9
#                                              → Circle / JS generate()
# 7. 椭圆周长：拉马努金公式 h=(rx-ry)^2/(rx+ry)^2
#    P ≈ π(rx+ry)(1 + 3h/(10+sqrt(4-3h)))       → Ellipse.perimeter / JS ellipsePer()
# 8. 多边形面积：鞋带公式 |Σ(xi*yj - xj*yi)|/2  → Polygon.area / JS polyInfo()
# 对拍基准：python3 shapes.py --self-test 输出，与 HTML 内 BASELINE 对照
# ================================================================

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


# ============ 交互式主程序（输入输出版） ============
def read_point(tag):
    """读取一个点：要求输入 'x y'（空格分隔），返回 Point 对象"""
    while True:
        raw = input(f"  请输入{tag}的坐标（x y，空格分隔）：").strip()
        parts = raw.split()
        if len(parts) != 2:
            print("  格式错误：需要两个数字，例如：1 2")
            continue
        try:
            return Point(float(parts[0]), float(parts[1]))
        except ValueError:
            print("  输入不是有效数字，请重新输入")


def read_number(tag):
    """读取一个非负数字（半径、半轴等）"""
    while True:
        try:
            v = float(input(f"  请输入{tag}：").strip())
            if v < 0:
                print("  不能为负数，请重新输入")
                continue
            return v
        except ValueError:
            print("  输入不是有效数字，请重新输入")


def create_point():
    p = read_point("点")
    print(f"  已创建点：{p}")
    print(f"  到原点的距离 = {p.distance(Point(0, 0)):.4f}")


def create_circle():
    center = read_point("圆心")
    r = read_number("半径")
    c = Circle(center, r)
    print(f"  已创建圆：{c}")
    print(f"  周长 = {c.perimeter():.4f}，面积 = {c.area():.4f}")
    if input("  是否再输入一个点，判断它在圆内/上/外？(y/n)：").strip().lower() == "y":
        q = read_point("测试点")
        print(f"  点 {q} 在：{c.relation(q)}")


def create_triangle():
    print("  依次输入三个顶点：")
    a = read_point("顶点A")
    b = read_point("顶点B")
    c = read_point("顶点C")
    try:
        t = Triangle(a, b, c)
    except ValueError as e:
        print(f"  非法三角形被拒绝：{e}")
        return
    print(f"  已创建三角形：{t}")
    print(f"  周长 = {t.perimeter():.4f}，面积 = {t.area():.4f}，类型 = {t.kinds()}")


def create_ellipse():
    center = read_point("中心")
    rx = read_number("半长轴 rx")
    ry = read_number("半短轴 ry")
    e = Ellipse(center, rx, ry)
    print(f"  已创建椭圆：{e}")
    print(f"  周长 ≈ {e.perimeter():.4f}，面积 = {e.area():.4f}")


def create_polygon():
    while True:
        try:
            n = int(input("  请输入顶点个数（>=3）：").strip())
            if n >= 3:
                break
            print("  至少需要 3 个顶点")
        except ValueError:
            print("  请输入整数")
    verts = [read_point(f"顶点{i + 1}") for i in range(n)]
    poly = Polygon(verts)
    print(f"  已创建多边形：{poly}")
    print(f"  周长 = {poly.perimeter():.4f}，面积 = {poly.area():.4f}")


MENU = """
==============================
 基于坐标的形状设计（交互版）
==============================
 1. 创建点（Point）
 2. 创建圆（Circle）+ 点在圆内/上/外判定
 3. 创建三角形（Triangle）含合法性检查
 4. 创建椭圆（Ellipse）
 5. 创建多边形（Polygon）
 0. 退出
------------------------------
 请输入功能编号："""


def self_test():
    """生成对拍基准：固定用例的标准结果，供 HTML 端自检比对。

    运行：python3 shapes.py --self-test
    """
    cases = []

    c = Circle(Point(0, 0), 5)
    cases.append({
        "id": "circle_r5",
        "desc": "圆 圆心(0,0) 半径5",
        "expected": {
            "perimeter": c.perimeter(),
            "area": c.area(),
            "point_on": c.relation(Point(3, 4)),
            "point_inside": c.relation(Point(1, 1)),
            "point_outside": c.relation(Point(6, 0)),
        },
    })

    t1 = Triangle(Point(0, 0), Point(4, 0), Point(0, 3))
    cases.append({
        "id": "triangle_345",
        "desc": "三角形 (0,0)(4,0)(0,3) 直角三角形",
        "expected": {"perimeter": t1.perimeter(), "area": t1.area(), "kind": t1.kinds()},
    })

    t2 = Triangle(Point(0, 0), Point(4, 0), Point(2, 3))
    cases.append({
        "id": "triangle_isosceles",
        "desc": "三角形 (0,0)(4,0)(2,3) 等腰三角形",
        "expected": {"perimeter": t2.perimeter(), "area": t2.area(), "kind": t2.kinds()},
    })

    t3 = Triangle(Point(0, 0), Point(4, 0), Point(2, math.sqrt(12)))
    cases.append({
        "id": "triangle_equilateral",
        "desc": "三角形 (0,0)(4,0)(2,√12) 等边三角形",
        "expected": {"perimeter": t3.perimeter(), "area": t3.area(), "kind": t3.kinds()},
    })

    e = Ellipse(Point(0, 0), 5, 3)
    cases.append({
        "id": "ellipse_5x3",
        "desc": "椭圆 中心(0,0) 半轴5×3",
        "expected": {"perimeter": e.perimeter(), "area": e.area()},
    })

    poly = Polygon([Point(0, 0), Point(2, 0), Point(3, 2), Point(1, 3), Point(-1, 1)])
    cases.append({
        "id": "polygon_5",
        "desc": "多边形 (0,0)(2,0)(3,2)(1,3)(-1,1)",
        "expected": {"perimeter": poly.perimeter(), "area": poly.area()},
    })

    return {"version": 1, "cases": cases}


def main():
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), ensure_ascii=False, indent=2))
        return
    handlers = {"1": create_point, "2": create_circle, "3": create_triangle,
                "4": create_ellipse, "5": create_polygon}
    while True:
        choice = input(MENU).strip()
        if choice == "0":
            print("已退出，再见！")
            break
        handler = handlers.get(choice)
        if handler is None:
            print("  无效编号，请输入 0~5")
            continue
        print()
        try:
            handler()
        except ValueError as e:
            print(f"  输入不合法：{e}")
        print()


if __name__ == "__main__":
    main()
