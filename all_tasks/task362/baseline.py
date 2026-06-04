def p(matrix: list[list[int]]) -> list[list[int]]:
    """
    Transforms a matrix by shifting a 'cross' diagonally to the bottom-left.
    The function identifies a cross (a row and column filled with a single
    digit), counts the number of '5's in the rightmost column to determine
    the shift amount, and returns a new matrix with the cross moved.
    Args:
        matrix: A list of lists of integers representing the input matrix.
    Returns:
        A new list of lists of integers with the shifted cross. Non-cross
        elements in the new matrix are 0.
    """
    rows, cols = len(matrix), len(matrix[0])
