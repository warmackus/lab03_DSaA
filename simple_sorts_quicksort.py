#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией.

Запуск: python lab03.py --variant N
Выход: self_check, демонстрация стабильности, таблицы бенчмарков,
       графики в каталоге graphs/.
"""
from __future__ import annotations

import argparse
import os
import random
import statistics
import sys
import time
import traceback

import matplotlib

matplotlib.use("Agg")  # без GUI: сохраняем в файлы
import matplotlib.pyplot as plt  # noqa: E402


# ===========================================================================
# 1. Простые сортировки со счётчиками
#    Каждая функция возвращает (список, сравнения, обмены/перемещения)
#    и НЕ меняет вход.
# ===========================================================================


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Пузырёк с досрочным выходом.

    Сложность: лучший O(n) (упорядоченный вход, один проход),
    средний/худший O(n^2). Стабилен.
    """
    arr = list(a)
    n = len(arr)
    comparisons = 0
    swaps = 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return arr, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Вставки со сдвигами.

    Сложность: лучший O(n) (упорядоченный), средний/худший O(n^2).
    Стабилен. Счётчик перемещений — число сдвигов элементов.
    """
    arr = list(a)
    comparisons = 0
    moves = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                moves += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
        if j + 1 != i:
            moves += 1  # постановка key на место
    return arr, comparisons, moves


def selection_sort(a: list) -> tuple[list, int, int]:
    """Выбором. Сложность Θ(n^2) сравнений на ЛЮБОМ входе.

    Обменов не более n-1. Нестабилен.
    """
    arr = list(a)
    n = len(arr)
    comparisons = 0
    swaps = 0
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
    return arr, comparisons, swaps


# ===========================================================================
# 2. QuickSort с рандомизированным опорным элементом
# ===========================================================================


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с рандомизированным pivot (rng.randrange(lo, hi)).

    Среднее O(n log n), худшее O(n^2), но рандомизация делает худший
    случай маловероятным. Возвращает новый список. Нестабилен.
    """
    if rng is None:
        rng = random.Random()
    arr = list(a)
    _qs(arr, 0, len(arr) - 1, rng)
    return arr


def _qs(arr: list, lo: int, hi: int, rng: random.Random) -> None:
    """Итеративный хвостовой рекурсивный QS со схемой Ломуто (пивот в конец)."""
    while lo < hi:
        # Рандомизация: меняем случайный элемент с hi, затем схема Ломуто
        p = rng.randrange(lo, hi + 1)
        arr[p], arr[hi] = arr[hi], arr[p]
        pivot = arr[hi]
        i = lo - 1
        for j in range(lo, hi):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
        mid = i + 1
        # Рекурсия по меньшей части — ограничивает глубину O(log n)
        if mid - lo < hi - mid:
            _qs(arr, lo, mid - 1, rng)
            lo = mid + 1
        else:
            _qs(arr, mid + 1, hi, rng)
            hi = mid - 1


# ===========================================================================
# 3. Демонстрация стабильности
# ===========================================================================


def stability_demo() -> None:
    """Печатает, какие сортировки стабильны на парах (ключ, метка)."""
    base = [(2, "a"), (1, "b"), (2, "c"), (1, "d"), (3, "e"), (2, "f")]

    def as_key_only(fn):
        # Сортируем по ключу p[0]; метка p[1] — только нагрузка
        wrapped = lambda seq: sorted(seq, key=lambda p: p[0])  # noqa: E731
        return None  # заглушка, ниже реальные вызовы

    def run(name: str, sorter) -> list:
        return sorter(list(base))

    # Простые сортировки уже работают со счётчиками — переиспользуем .[0]
    results = {
        "bubble_sort": bubble_sort(base)[0],
        "insertion_sort": insertion_sort(base)[0],
        "selection_sort": selection_sort(base)[0],
        "quick_sort": quick_sort(base, random.Random(0)),
        "sorted()": sorted(base),
    }

    # Для сортировок выше порядок пар определяется сравнением кортежей
    # (ключ, метка). Чтобы показать стабильность по КЛЮЧУ, переопределим
    # сравнение: сортируем только по p[0].
    def by_key_only(sort_fn):
        class K:
            __slots__ = ("p",)

            def __init__(self, p):
                self.p = p

            def __lt__(self, other):  # сравнение только по ключу
                return self.p[0] < other.p[0]

        wrapped = [K(p) for p in base]
        res = sort_fn(wrapped)
        # sort_fn возвращает список K — распакуем обратно в пары
        out = [k.p for k in res]
        return out

    print("\nstability_demo (сравнение только по ключу p[0]):")
    # bubble_sort/insertion_sort/selection_sort работают с list -> обёрнём
    def bubble_keys(a):
        # повторим логику пузырька, но по ключу
        arr = list(a)
        for i in range(len(arr) - 1):
            swapped = False
            for j in range(len(arr) - 1 - i):
                if arr[j].p[0] > arr[j + 1].p[0]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            if not swapped:
                break
        return arr

    def insertion_keys(a):
        arr = list(a)
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j].p[0] > key.p[0]:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr

    def selection_keys(a):
        arr = list(a)
        n = len(arr)
        for i in range(n - 1):
            m = i
            for j in range(i + 1, n):
                if arr[j].p[0] < arr[m].p[0]:
                    m = j
            if m != i:
                arr[i], arr[m] = arr[m], arr[i]
        return arr

    def quick_keys(a):
        arr = list(a)
        rng = random.Random(0)

        def rec(lo, hi):
            while lo < hi:
                p = rng.randrange(lo, hi + 1)
                arr[p], arr[hi] = arr[hi], arr[p]
                pivot = arr[hi].p[0]
                i = lo - 1
                for j in range(lo, hi):
                    if arr[j].p[0] <= pivot:
                        i += 1
                        arr[i], arr[j] = arr[j], arr[i]
                arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
                mid = i + 1
                if mid - lo < hi - mid:
                    rec(lo, mid - 1)
                    lo = mid + 1
                else:
                    rec(mid + 1, hi)
                    hi = mid - 1

        rec(0, len(arr) - 1)
        return arr

    impls = {
        "bubble_sort": bubble_keys,
        "insertion_sort": insertion_keys,
        "selection_sort": selection_keys,
        "quick_sort": quick_keys,
    }

    for name, fn in impls.items():
        # Запускаем сортировку по ключу и печатаем метки
        wrapped = []
        for p in base:
            class K:
                __slots__ = ("p",)

                def __init__(self, p):
                    self.p = p

                def __lt__(self, other):
                    return self.p[0] < other.p[0]

            wrapped.append(K(p))
        # Все реализации выше работают на K-объектах через .p[0]
        class KWithP:
            __slots__ = ("p",)

            def __init__(self, p):
                self.p = p
        # Проще: переделаем base в K-объекты с атрибутом p
        ks = [KWithP(p) for p in base]
        # Наши * _keys функции ожидают объекты с .p[0] — используем их
        res = fn(ks)
        labels = [k.p[1] for k in res]
        keys = [k.p[0] for k in res]
        stable = True
        for key in set(keys):
            order = [lab for k, lab in zip(keys, labels) if k == key]
            if order != sorted(order):
                stable = False
        print(f"  {name:>15}: ключи={keys} метки={labels} -> "
              f"{'стабильна' if stable else 'НЕ стабильна'}")


# ===========================================================================
# 4. Классы входов (детерминированно по seed)
# ===========================================================================


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    rng = random.Random(seed + n)
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "ordered": sorted(data),
        "random": data,
        "reversed": sorted(data, reverse=True),
    }


# ===========================================================================
# 5. Верификация
# ===========================================================================

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


class SelfCheckError(Exception):
    pass


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise SelfCheckError(msg)


def check_algorithm(fn) -> None:
    boundary = [[], [7], [5, 5, 5, 5], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} не список: {type(res).__name__}")
        expect(is_sorted(res), f"порядок нарушен на {a}: {res}")
        expect(sorted(res) == sorted(a), f"не перестановка {a}: {res}")
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        res = fn(list(a))
        expect(res == sorted(a), f"расходится с sorted() на {a}: {res}")


def check_counters() -> None:
    # selection: ровно n(n-1)/2 сравнений
    _, cmp_sel, _ = selection_sort([3, 1, 2, 5, 4])
    expect(cmp_sel == 10, f"selection comparisons={cmp_sel}, ожидалось 10")
    # bubble на упорядоченном: n-1 сравнений (один проход, без обменов)
    _, cmp_b, swp_b = bubble_sort([1, 2, 3, 4, 5])
    expect(cmp_b == 4, f"bubble ordered comparisons={cmp_b}, ожидалось 4")
    expect(swp_b == 0, f"bubble ordered swaps={swp_b}, ожидалось 0")
    # insertion на упорядоченном: n-1 сравнений, 0 сдвигов
    _, cmp_i, mv_i = insertion_sort([1, 2, 3, 4, 5])
    expect(cmp_i == 4, f"insertion ordered comparisons={cmp_i}, ожидалось 4")
    expect(mv_i == 0, f"insertion ordered moves={mv_i}, ожидалось 0")


def self_check() -> None:
    checks = [(name, lambda fn=fn: check_algorithm(fn))
              for name, fn in ALGORITHMS.items()]
    checks.append(("счётчики", check_counters))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            print(f"  {name}: не реализовано — {err}")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: провалено {failed}; замеры отменены.")
    print("self_check: OK")


# ===========================================================================
# 6. Бенчмарк
# ===========================================================================

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5


def bench(fn, data: list) -> float:
    fn(list(data))  # прогрев
    times = []
    for _ in range(REPEATS):
        arg = list(data)
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int, out_dir: str = "graphs") -> None:
    os.makedirs(out_dir, exist_ok=True)
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    # Собираем данные для графиков
    results = {}
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        results[name] = {}
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                results[name].setdefault(cls, []).append((n, t))
                print(f"  n={n:>7}  вход={cls:<10} t={t:.6f} c")

    # Графики log-log
    for name, cls_data in results.items():
        plt.figure(figsize=(7, 5))
        for cls, pts in cls_data.items():
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            plt.loglog(xs, ys, marker="o", label=cls)
        plt.title(f"{name}: время от n (log-log)")
        plt.xlabel("n")
        plt.ylabel("t, с")
        plt.grid(True, which="both", alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"{name}.png"), dpi=130)
        plt.close()
    print(f"\nГрафики сохранены в {out_dir}/")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True)
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()