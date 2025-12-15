"""
tests_main.py — точка входа для автотестов (без GUI).

Собирается отдельным PyInstaller-EXE: tests.exe.

Проблема Windows: при двойном клике консольное приложение может мгновенно закрыться,
и пользователь "не видит" что произошло. Поэтому:
- пишем лог рядом с tests.exe
- по умолчанию (в frozen/EXE) ждём Enter в конце, если запуск без аргументов
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback


def _ensure_imports() -> None:
    """
    Когда запускаем из исходников из папки tests/, нужно уметь импортировать
    `models.py` и другие модули из родительской папки IDEF0_editor/.
    """
    here = os.path.dirname(__file__)
    base = os.path.abspath(os.path.join(here, ".."))
    if base not in sys.path:
        sys.path.insert(0, base)


def _fail(msg: str) -> None:
    raise AssertionError(msg)


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        _fail(msg)


def test_arrow_endpoints_and_clearance() -> None:
    """
    Проверяем ключевую геометрию:
    - конец/начало на границе блока
    - маршрут использует "подлёт" снаружи (endpoint_clearance) и возвращается к границе
    """
    _ensure_imports()
    from models import Block, Arrow

    b1 = Block(block_id="block_1", x=100, y=100, width=100, height=60)
    b2 = Block(block_id="block_2", x=300, y=100, width=100, height=60)

    a = Arrow(
        arrow_id="arrow_1",
        from_block_id=b1.id,
        to_block_id=b2.id,
        from_side="right",
        to_side="left",
    )
    a.endpoint_clearance = 12.0

    # Точки соединения на границе
    x1, y1 = a._get_side_point(b1, "right")
    x2, y2 = a._get_side_point(b2, "left")
    _assert(x1 == b1.x + b1.width / 2 and y1 == b1.y, "Start point должен быть на границе блока (right)")
    _assert(x2 == b2.x - b2.width / 2 and y2 == b2.y, "End point должен быть на границе блока (left)")

    path = a.calculate_routing_path(b1, b2, [b1, b2])
    _assert(len(path) >= 2, "Маршрут должен содержать минимум 2 точки")
    _assert(path[0] == (x1, y1), "Первая точка маршрута должна быть на границе start-блока")
    _assert(path[-1] == (x2, y2), "Последняя точка маршрута должна быть на границе end-блока")

    # Должна быть как минимум одна точка "снаружи" (подлёт) возле start/end
    _assert(
        any(abs(p[0] - (x1 + a.endpoint_clearance)) < 1e-6 and abs(p[1] - y1) < 1e-6 for p in path),
        "В маршруте должен присутствовать подлёт от start (x1 + clearance, y1)",
    )
    _assert(
        any(abs(p[0] - (x2 - a.endpoint_clearance)) < 1e-6 and abs(p[1] - y2) < 1e-6 for p in path),
        "В маршруте должен присутствовать подлёт к end (x2 - clearance, y2)",
    )


def test_routing_avoids_obstacle_block() -> None:
    """
    Базовая проверка обхода препятствия:
    между двумя блоками ставим третий блок и ожидаем, что маршрут не пройдет через него.
    """
    _ensure_imports()
    from models import Block, Arrow

    b1 = Block(block_id="block_1", x=100, y=100, width=120, height=70)
    b2 = Block(block_id="block_2", x=520, y=100, width=120, height=70)
    obstacle = Block(block_id="block_obs", x=310, y=100, width=220, height=140)

    a = Arrow(
        arrow_id="arrow_1",
        from_block_id=b1.id,
        to_block_id=b2.id,
        from_side="right",
        to_side="left",
    )
    a.endpoint_clearance = 12.0

    path = a.calculate_routing_path(b1, b2, [b1, b2, obstacle])
    _assert(len(path) >= 2, "Маршрут должен содержать минимум 2 точки")

    hits = []
    for i in range(len(path) - 1):
        p1 = path[i]
        p2 = path[i + 1]
        if a._line_intersects_block(p1[0], p1[1], p2[0], p2[1], obstacle):
            hits.append((i, p1, p2))
    _assert(not hits, f"Маршрут пересекает obstacle: {hits}")


def test_arrow_serialization_roundtrip() -> None:
    """Проверяем, что важные поля стрелки сериализуются и читаются обратно без падений."""
    _ensure_imports()
    from models import Arrow

    a = Arrow(
        arrow_id="arrow_1",
        from_block_id="block_1",
        to_block_id="block_2",
        from_side="right",
        to_side="left",
        color="#000000",
        width=3,
        style="dashed",
        text="t",
        route_locked=True,
        locked_path=[[1, 2], [3, 4]],
    )
    a.from_attachment_point = 2
    a.to_attachment_point = 0
    a.bend_x = 111
    a.bend_y = 222

    d = a.to_dict()
    b = Arrow()
    b.update_from_dict(d)

    _assert(b.id == a.id, "id должен сохраняться")
    _assert(b.route_locked == a.route_locked, "route_locked должен сохраняться")
    _assert(b.locked_path == a.locked_path, "locked_path должен сохраняться")
    _assert(b.bend_x == a.bend_x and b.bend_y == a.bend_y, "bend должен сохраняться")


TESTS = [
    test_arrow_endpoints_and_clearance,
    test_routing_avoids_obstacle_block,
    test_arrow_serialization_roundtrip,
]


def _default_log_path() -> str:
    base_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "tests_last_run.log")


def run_tests() -> int:
    print("IDEF0 Editor — автотесты (smoke/regression)")
    print("=" * 60)
    passed = 0
    failed = 0

    for t in TESTS:
        name = t.__name__
        try:
            t()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            traceback.print_exc()
            failed += 1

    print("-" * 60)
    print(f"ИТОГО: PASS={passed}, FAIL={failed}")
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--no-pause", action="store_true", help="Не ждать Enter в конце (удобно для CI/терминала).")
    p.add_argument("--pause", action="store_true", help="Всегда ждать Enter в конце.")
    p.add_argument("--log", default=_default_log_path(), help="Путь к лог-файлу.")
    args = p.parse_args(argv)

    exit_code = 1
    log_path = args.log
    try:
        exit_code = run_tests()
        return exit_code
    except Exception:
        print("[FATAL] Непойманная ошибка раннера. См. лог.")
        traceback.print_exc()
        exit_code = 1
        return exit_code
    finally:
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("IDEF0 Editor — tests.exe log\n")
                f.write(f"exit_code={exit_code}\n")
        except Exception:
            pass

        should_pause = False
        if args.pause:
            should_pause = True
        else:
            if getattr(sys, "frozen", False) and not args.no_pause and (argv is None or len(argv) == 0):
                should_pause = True

        if should_pause:
            try:
                print(f"\nЛог: {log_path}")
                input("Нажмите Enter чтобы закрыть окно...")
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())


