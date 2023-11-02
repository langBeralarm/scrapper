def custom_add(x: int, y: int) -> int:
    """
    Adds two ints and returns the sum.
    """
    return x + y


if __name__ == "__main__":
    res: int = custom_add(4, 5)  # pragma: no cover
