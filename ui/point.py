from typing import Any, Generator
from numpy import linspace
from json import dump, load

uuid_count = 0

def uuid() -> int:
    global uuid_count
    uuid_count += 1
    return uuid_count


class Point:
    def __init__(self, ab: tuple[float, float]) -> None:
        self.origin = ab
        self.a, self.b = ab
        self.uuid = uuid()

    def __repr__(self) -> str:
        return f"{self.origin}"

    def __str__(self) -> str:
        return f"a={self.a} b={self.b}"

    def to_json_item(self) -> dict:
        return {
            "type" : "Point",
            "origin": list(self.origin)
        }

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Point):
            return self.a == value.a and self.b == value.b
        return False


class Animation:
    def __init__(self, origin: Point, end: Point) -> None:
        self.origin = origin
        self.end = end
        self.uuid = uuid()

    def as_tuple(self) -> tuple[Point, Point]:
        return (self.origin, self.end)

    def get_iter(self, n: int):
        As = linspace(self.origin.b, self.end.b, n)
        Bs = linspace(self.origin.a, self.end.a, n)
        for (a, b) in zip(As, Bs):
            yield (a, b)

    def to_json_item(self) -> dict:
        start = self.origin.origin
        end = self.end.origin
        return {
            "type": "Animation",
            "origin" : list(start),
            "end" : list(end),
        }

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Animation):
            return self.origin == value.origin and self.end == value.end
        return False

    def __str__(self) -> str:
        return f"a = ({self.origin.a} -> {self.end.a}) b = ({self.origin.b} -> {self.end.b})"

    def __repr__(self) -> str:
        return f"Animation[({self.origin.a} -> {self.end.a})({self.origin.b} -> {self.end.b})]"


class Libary:
    def __init__(self) -> None:
        self.animations: list[Animation] = []
        self.points: list[Point] = []
        self.loaded_path = None

    def load_file(self, fpath: str):
        self.loaded_path = fpath
        with open(fpath, "r") as f:
            content: list = load(f)

        item: dict
        for item in content:
            if item["type"] == "Point":
                point = Point(item["origin"])
                self.points.append(point)

            if item["type"] == "Animation":
                animation = Animation(Point(item["origin"]), Point(item["end"]))
                self.animations.append(animation)

    def get(self, uuid: int) -> Point | Animation:
        for p in self.points:
            if p.uuid == uuid:
                return p

        for animation in self.animations:
            if animation.uuid == uuid:
                return animation
        raise ValueError

    def add_to_lib(self, new: Point | Animation):
        if isinstance(new, Point):
            if new in self.points:
                return
            self.points.append(new)

        if isinstance(new, Animation):
            print(new, self.animations, self.animations[0] == new)
            if new in self.animations:
                return
            self.animations.append(new)


        if self.loaded_path is None:
            return

        file_content: list[Point | Animation] = []
        file_content.extend(self.points)
        file_content.extend(self.animations)
        content = [p.to_json_item() for p in file_content]
        with open(self.loaded_path, "w") as f:
            dump(content, f, indent=4)

    def uuid_item_pairs(self) -> Generator[tuple[int, Animation] | tuple[int, Point], Any, None]:
        for p in self.points:
            yield (p.uuid, p)

        for ani in self.animations:
            yield (ani.uuid, ani)

    def uuids(self) -> list[int]:
        uuids = []
        for p in self.points:
            uuids.append(p.uuid)
        for ani in self.animations:
            uuids.append(ani.uuid)
        return uuids

    def data_points(self) -> list[Point | Animation]:
        data = []
        for p in self.points:
            data.append(p)
        for ani in self.animations:
            data.append(ani)
        return data
