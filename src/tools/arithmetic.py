from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtracts two numbers."""
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two numbers."""
    return a * b

@tool
def divide(a: int, b: int) -> int:
    """Divides two numbers."""
    return a / b