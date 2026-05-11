#!/usr/bin/env python3
"""Log an espresso shot. Run right after pulling."""

from db import get_conn

def get_float(label, lo=None, hi=None):
    while True:
        try:
            val = float(input(f"{label}: ").strip())
            if (lo is None or val >= lo) and (hi is None or val <= hi):
                return val
            print(f"  Enter a value between {lo} and {hi}.")
        except ValueError:
            print("  Enter a number.")

def get_int(label, lo=None, hi=None):
    while True:
        try:
            val = int(input(f"{label}: ").strip())
            if (lo is None or val >= lo) and (hi is None or val <= hi):
                return val
            print(f"  Enter a value between {lo} and {hi}.")
        except ValueError:
            print("  Enter a whole number.")

def pick_bean(cur):
    cur.execute("SELECT id, name, roaster FROM beans ORDER BY created_at DESC")
    beans = cur.fetchall()
    if not beans:
        print("No beans registered. Run add_bean.py first.")
        raise SystemExit(1)
    print("\nBeans:")
    for i, (bid, name, roaster) in enumerate(beans, 1):
        tag = f" ({roaster})" if roaster else ""
        print(f"  {i}. {name}{tag}")
    while True:
        choice = input("Select bean (number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(beans):
            return beans[int(choice) - 1][0]
        print(f"  Enter a number 1–{len(beans)}.")

def main():
    print("\n--- Log Espresso Shot ---")
    with get_conn() as conn, conn.cursor() as cur:
        bean_id = pick_bean(cur)

        dose  = get_float("Dose (g in)", lo=5, hi=30)
        yield_ = get_float("Yield (g out)", lo=5, hi=120)
        ratio = yield_ / dose
        time_ = get_int("Shot time (seconds)", lo=5, hi=120)

        grind = input("Grind setting (e.g. '12', '3.5'): ").strip() or None
        rating = get_int("Taste rating (1–5)", lo=1, hi=5)
        notes  = input("Notes (optional): ").strip() or None

        cur.execute(
            """
            INSERT INTO shots (bean_id, dose_g, yield_g, time_sec, grind_setting, taste_rating, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, shot_at
            """,
            (bean_id, dose, yield_, time_, grind, rating, notes),
        )
        shot_id, shot_at = cur.fetchone()

    print(f"\nShot #{shot_id} saved at {shot_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Ratio: 1:{ratio:.2f}  |  {dose}g → {yield_}g in {time_}s  |  Rating: {rating}/5\n")

if __name__ == "__main__":
    main()
