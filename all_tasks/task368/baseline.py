def p(matrix: list[list[int]]) -> list[list[int]]:
    """
    Colors rectangles made of 5s with the pattern of a non-5 rectangle.
    Args:
        matrix: A 10x10 list of lists containing 0s (background), one
                rectangle of various digits, and other rectangles of 5s.
                All rectangles have the same area.
    Returns:
        A new 10x10 matrix with the 5-rectangles colored in.
    """
