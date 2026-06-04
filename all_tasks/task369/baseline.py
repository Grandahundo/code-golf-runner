def p(matrix):
    """
    Finds regions of 0s in a matrix and fills each region with its size.
    The algorithm iterates through each cell of the matrix. If a cell contains a 0,
    it means we've found a new, uncounted region. A Breadth-First Search (BFS)
    is then started from that cell to find all connected 0s. The coordinates of
    these 0s are stored. Once the entire region is found, we calculate its size
    and fill all the stored coordinates in the matrix with that size.
    Args:
        matrix (list[list[int]]): A 2D list of 5s and 0s.
    Returns:
        list[list[int]]: The modified matrix with 0-regions filled by their size.
    """
    rows, cols = len(matrix), len(matrix[0])
