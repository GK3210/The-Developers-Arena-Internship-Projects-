# Student Grade Calculator

**The Developers Arena - Data Science Internship | Task 2 (Week 2): Making Decisions & Repeating Tasks in Python**

## 1. Project Overview
A Python command-line program that takes a student's name and marks (0-100) and returns a grade (A, B, C, D or F) along with an encouraging message.

**Goals**
- Practise `if-elif-else` statements and comparison operators
- Use a `while` loop to handle invalid inputs
- Write reusable functions
- Add basic error handling (`try-except`)

## 2. Setup Instructions
1. Install Python 3.8 or newer from https://www.python.org/downloads/
2. Clone the repository:
   ```
   git clone https://github.com/GK3210/<your-repo-name>.git
   cd <your-repo-name>
   ```
3. Run the program:
   ```
   python grade_calculator.py
   ```
No external libraries are needed.

## 3. Code Structure
```
.
├── README.md             # Project documentation
├── grade_calculator.py   # Main program
├── test_cases.txt        # Test cases and results
└── screenshots/          # Screenshots of the program running
```

## 4. Technical Details

### Grading Logic
| Marks  | Grade | Message                                  |
|--------|-------|------------------------------------------|
| 90-100 | A     | Outstanding! Excellent work!             |
| 80-89  | B     | Very Good! Keep it up!                   |
| 70-79  | C     | Good job! A little more effort...        |
| 60-69  | D     | You passed! Keep practicing...           |
| 0-59   | F     | Don't give up! Review and try again...   |

### Functions Used
- `get_grade(marks)` - uses `if-elif-else` to return the grade and message.
- `get_student_name()` - `while` loop that re-asks until a non-empty name is entered.
- `get_valid_marks()` - `while` loop with `try-except`; rejects text and values outside 0-100.
- `show_result(name, marks)` - prints the formatted result.
- `main()` - runs the program and allows multiple students.

### Algorithm
1. Ask for the student's name.
2. Ask for marks; repeat until a number between 0 and 100 is entered.
3. Compare marks against the grade boundaries from highest to lowest.
4. Print marks, grade and message.
5. Ask whether to evaluate another student.

## 5. Sample Output
```
Enter student name: Priya
Enter marks (0-100): 85

RESULT FOR PRIYA:
Marks: 85/100
Grade: B
Message: Very Good! Keep it up!
```

## 6. Visual Documentation
Screenshots are in the `screenshots/` folder (valid input, all grades, invalid input handling).

## 7. Testing Evidence
See `test_cases.txt` - 15 boundary-value tests and 5 invalid-input tests, all passing.

## Author
Gautam Kurpatwar - https://github.com/GK3210
