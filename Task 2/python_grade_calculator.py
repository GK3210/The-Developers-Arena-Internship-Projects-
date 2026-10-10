"""
Student Grade Calculator
The Developers Arena - Data Science Internship, Task 2 (Week 2)

Takes a student's name and marks (0-100), validates the input with a
while loop, and returns a grade (A-F) with an encouraging message.

Grading logic:
    A: 90-100 | B: 80-89 | C: 70-79 | D: 60-69 | F: 0-59
"""


def get_grade(marks):
    """Return (grade, message) for the given marks using if-elif-else."""
    if marks >= 90:
        return "A", "Outstanding! Excellent work! \U0001F31F"
    elif marks >= 80:
        return "B", "Very Good! Keep it up! \U0001F44D"
    elif marks >= 70:
        return "C", "Good job! A little more effort and you'll reach the top! \U0001F4AA"
    elif marks >= 60:
        return "D", "You passed! Keep practicing, you can do better! \U0001F4DA"
    else:
        return "F", "Don't give up! Review the topics and try again, you've got this! \U0001F680"


def get_student_name():
    """Ask for the student's name; keep asking until it is not empty."""
    while True:
        name = input("Enter student name: ").strip()
        if name:
            return name
        print("Name cannot be empty. Please try again.")


def get_valid_marks():
    """Ask for marks; keep asking (while loop) until a number 0-100 is entered."""
    while True:
        raw = input("Enter marks (0-100): ").strip()
        try:
            marks = float(raw)
        except ValueError:
            print("Invalid input! Please enter a number (e.g. 85).")
            continue
        if marks < 0 or marks > 100:
            print("Invalid marks! Marks must be between 0 and 100.")
            continue
        return int(marks) if marks.is_integer() else marks


def show_result(name, marks):
    """Print the formatted result for a student."""
    grade, message = get_grade(marks)
    print(f"\n\U0001F4CA RESULT FOR {name.upper()}:")
    print(f"Marks: {marks}/100")
    print(f"Grade: {grade}")
    print(f"Message: {message}")


def main():
    print("=== Student Grade Calculator ===")
    while True:
        name = get_student_name()
        marks = get_valid_marks()
        show_result(name, marks)
        again = input("\nCalculate another student? (yes/no): ").strip().lower()
        if again not in ("yes", "y"):
            print("Thank you for using the Student Grade Calculator. Goodbye!")
            break
        print()


if __name__ == "__main__":
    main()
