from langchain_core.tools import tool

@tool
def calculate(a: float | int  , b: float | int, operation: str):
    """
    Perform a mathematical operation on two numbers.
    Use this for addition, subtraction, multiplication, or division.
    'operation' must be one of: 'add', 'subtract', 'multiply', 'divide', 'power`.
    """

    if operation == 'add':
        return add(a, b)
    elif operation == 'subtract':
        return substract()
    elif operation == 'multiply':
        return multiply(a, b)
    elif operation == 'divide':
        return divide(a, b)
    else:
        return f"This operation {operation} is not defined."

def add(a, b):
    """
    Add two numbers.
    """
    return a+b

def substract(a, b):
    """
    Subtract two numbers.
    """
    return a-b

def multiply(a, b):
    """
    Multiply two numbers.
    """
    return a * b


def divide(a, b):
    """
    Divide two numbers.
    """
    if b==0:
        return 0
    return a / b

def power(a, b):
    """
    Raise a number to the power of b.
    """
    return a ** b
