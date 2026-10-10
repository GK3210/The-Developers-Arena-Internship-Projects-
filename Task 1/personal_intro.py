"""
Personal Introduction Program
-----------------------------
Week 1 Project - Python Basics

Asks the user a few questions and prints a friendly welcome message.
Concepts used: variables, input(), print(), f-strings, type conversion,
basic math, strings, and lists.
"""

# ---------- Step 1: Greet and collect information ----------
print("=" * 40)
print("   Personal Introduction Program")
print("=" * 40)

# input() always returns text (a string), so we store each answer in a variable
name = input("What is your name? ").strip().title()
age = int(input("How old are you? "))          # convert text to a whole number
city = input("Which city do you live in? ").strip().title()
hobby = input("What is your favorite hobby? ").strip()
food = input("What is your favorite food? ").strip()

# ---------- Step 2: Small calculations (basic math) ----------
birth_year = 2026 - age                        # approximate birth year
age_in_ten_years = age + 10

# ---------- Step 3: Use a list ----------
facts = [name, age, city, hobby, food]         # a list holds many items
print()
print(f"(Your answers were saved in a list with {len(facts)} items.)")

# ---------- Step 4: Display a friendly welcome message ----------
print()
print(f"🎉 Welcome {name}! 🎉")
print(f"You are {age} years old and love {hobby}.")
print(f"You live in {city} and your favorite food is {food}.")
print(f"You were born around {birth_year}, and in 10 years you will be {age_in_ten_years}.")
print(f"Keep enjoying {hobby}, {name} - and happy coding! 🚀")