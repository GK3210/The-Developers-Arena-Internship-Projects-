# Personal Introduction Program

A beginner Python program (Week 1 project) that asks the user a few questions and prints a friendly, personalised welcome message.

## Project Overview
**Goal:** Practice the Python basics - variables, `input()`, `print()`, f-strings, basic math, strings and lists - by building a small interactive program.

**What it does:**
1. Asks for name, age, city, favorite hobby and favorite food (5 questions)
2. Stores the answers in variables (and a list)
3. Calculates approximate birth year and age in 10 years
4. Prints a friendly welcome message

## Setup Instructions
1. Install Python 3.8+ from https://www.python.org/downloads/ (tick **"Add Python to PATH"** on Windows).
2. Check the install: `python --version`
3. Clone this repository:
   ```
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   ```
4. Run the program:
   ```
   python personal_intro.py
   ```
   (Use `python3` on macOS/Linux. No extra libraries needed - `requirements.txt` is empty on purpose.)

*Alternative:* paste the code into [Google Colab](https://colab.research.google.com) and run it in your browser.

## Code Structure
```
.
├── README.md            # Project documentation
├── personal_intro.py    # Main program
├── requirements.txt     # Dependencies (none needed)
└── screenshot.png       # Screenshot of the program running
```
`personal_intro.py` is organised in four commented steps: collect information, do math, use a list, display the message.

## Sample Output
```
What is your name? Alex
How old are you? 21
Which city do you live in? Mumbai
What is your favorite hobby? Coding
What is your favorite food? Pizza

🎉 Welcome Alex! 🎉
You are 21 years old and love Coding.
You live in Mumbai and your favorite food is Pizza.
You were born around 2005, and in 10 years you will be 31.
Keep enjoying Coding, Alex - and happy coding! 🚀
```
![Program screenshot](screenshot.png)

## Technical Details
- **Variables:** `name`, `age`, `city`, `hobby`, `food` store the user's answers.
- **Type conversion:** `input()` returns a string, so `int()` converts age to a number for math.
- **String methods:** `.strip()` removes extra spaces, `.title()` capitalises names.
- **Math:** `birth_year = 2026 - age` and `age + 10`.
- **List:** `facts = [name, age, city, hobby, food]`, with `len(facts)` to count items.
- **f-strings:** `f"Welcome {name}!"` inserts variables into text.

## Testing Evidence
| Test | Input | Expected | Result |
|------|-------|----------|--------|
| Normal input | Alex, 21, mumbai, Coding, Pizza | Welcome message; city shown as "Mumbai" | Pass |
| Extra spaces | "  priya  " as name | Shown as "Priya" | Pass |
| Age math | 21 | Birth year 2005, age in 10 years = 31 | Pass |
| Invalid age | "abc" | Program stops with `ValueError` (known limitation, see below) | Expected |

## What I Learned
- How Python runs code line by line, top to bottom
- Storing data in variables and the difference between text and numbers
- Using `input()` and `print()` for interaction
- Making output readable with f-strings
- Reading error messages (e.g. `ValueError`) and fixing them

## Future Improvements
Add `try/except` so that typing letters for age shows a friendly message instead of an error.
