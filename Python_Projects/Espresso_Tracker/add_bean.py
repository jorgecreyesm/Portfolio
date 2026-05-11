#!/usr/bin/env python3
"""Register a new bag of coffee beans."""

from db import get_conn

ROAST_LEVELS = ["light", "medium-light", "medium", "medium-dark", "dark"]

def prompt(label, required=True):
    while True:
        val = input(f"{label}: ").strip()
        if val or not required:
            return val or None
        print("  Required — please enter a value.")

def pick_roast():
    for i, level in enumerate(ROAST_LEVELS, 1):
        print(f"  {i}. {level}")
    while True:
        choice = input("Roast level (1-5): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= 5:
            return ROAST_LEVELS[int(choice) - 1]
        print("  Enter a number 1–5.")

def main():
    print("\n--- Add New Bean ---")
    name    = prompt("Bean name (e.g. 'Ethiopia Yirgacheffe')")
    roaster = prompt("Roaster", required=False)
    print("Roast level:")
    roast   = pick_roast()
    origin  = prompt("Origin / region", required=False)

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO beans (name, roaster, roast_level, origin) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, roaster, roast, origin),
        )
        bean_id = cur.fetchone()[0]

    print(f"\nSaved '{name}' as bean ID {bean_id}.\n")

if __name__ == "__main__":
    main()
