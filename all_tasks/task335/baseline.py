def p(matrix: list[list[int]]):
    """
    Draws an L-shaped line of 4s from a 2 to an 8 in a 2D matrix.
    The function finds the unique 2 and 8, then draws a line by first moving
    horizontally from the 2's row to the 8's column, and then vertically to
    the 8's row. The line is made of 4s and does not overwrite the 2 and 8.
    Args:
        matrix: A list of lists of integers (0, 2, 8). It is modified in-place.
    """
