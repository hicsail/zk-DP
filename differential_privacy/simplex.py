import numpy as np


def initialize_tableau(histogram, child_histogram, noisy_child_hist):
    # The objective function coefficients
    obj = -1 * (np.array(child_histogram) - np.array(noisy_child_hist))
    # Add zero coefficients for the slack variable and RHS
    obj = np.concatenate((obj, [0] * 2))  # Add a zero for the slack variable

    # The constraints coefficients
    constraints = np.array([1] * 3 + [0])  # The last 0 is for the slack variable

    # The RHS of the constraints
    b = np.array([1.05 * histogram[0]])

    # Combine the constraints and the objective into the tableau
    tableau = np.vstack([obj, np.concatenate((constraints, b))])

    return tableau


# Perform pivoting (Gauss-Jordan elimination) around the pivot element.
def pivot(tableau, row, col):
    pivot_element = tableau[row, col]
    tableau[row, :] /= pivot_element
    for r in range(tableau.shape[0]):
        if r != row:
            ratio = tableau[r, col]
            tableau[r, :] -= ratio * tableau[row, :]


# Find the pivot row and column using the Bland's rule to avoid cycling.
def find_pivot(tableau):
    # Choose the pivot column
    col = np.argmin(tableau[0, :-1])  # Most negative for maximization

    # Quit if optimal solution found
    if tableau[0, col] >= 0:
        return -1, -1

    # Compute ratio for pivot row selection
    rows = []
    for i in range(1, tableau.shape[0]):
        if tableau[i, col] > 0:
            ratio = tableau[i, -1] / tableau[i, col]
            rows.append((ratio, i))
    if not rows:
        raise ValueError("Problem is unbounded.")

    # Pick the smallest ratio
    row = min(rows)[1]
    return row, col


def simplex_method(_tableau):
    tableau = _tableau.copy()

    while True:
        row, col = find_pivot(tableau)
        if row == -1:
            break
        pivot(tableau, row, col)  # Ensure you have defined or updated the pivot function accordingly

    return tableau


# Example:
histogram = [0.2, 0.3, 0.1, 0.1, 0.3]
noisy_hist = [0, 0, 0, 0, 0]
child_histogram = [0.05, 0.1, 0.15]
noisy_child_hist = [0, 0, 0]

# tableau = initialize_tableau(histogram, child_histogram, noisy_child_hist)

_tableau = np.array(
    [
        [ 1.0,-2.0,-3.0, 0.0, 0.0, 0.0],
        [ 0.0, 1.0, 2.0, 1.0, 0.0,10.0],
        [ 0.0, 2.0, 1.0, 0.0, 1.0, 8.0]
    ]
)
print("\nBefore", _tableau)

tableau = simplex_method(_tableau)

# Display the final tableau
print("\nAfter", tableau)

_transposed = np.array(
    [   
        [ 1.0,-10.0,-8.0, 0.0, 0.0, 0.0],
        [ 0.0, 1.0, 2.0, 1.0, 0.0, 2.0],
        [ 0.0, 2.0, 1.0, 0.0, 1.0, 3.0]
    ]
)

print("\nBefore", _transposed)

transposed = simplex_method(_transposed)

# Display the final tableau
print("\nAfter", transposed)