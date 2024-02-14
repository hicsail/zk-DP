import numpy as np


def init_prime_tableau(coeffs, constraints):
    coeffs = np.array(coeffs)
    constraints = np.array(constraints)
    coeffs *= -1

    # Add zero coefficients for the slack variable and RHS
    obj = np.concatenate((coeffs, [0] * (len(constraints) + 1)))

    # The constraints coefficients
    eyes = np.eye(len(constraints))
    last_col = constraints[:, -1].reshape(-1, 1)
    constraints_ = constraints[:, :-1]
    concatenated = np.hstack((constraints_, eyes))
    constraints = np.hstack((concatenated, last_col))

    # Combine the constraints and the objective into the tableau
    tableau = np.vstack([obj, constraints])
    lmc = np.array([1] + [0] * (len(tableau) - 1))
    lmc = lmc.reshape(-1, 1)
    tableau = np.hstack((lmc, tableau))

    return tableau


def init_dual_tableau(coeffs, constraints):
    coeffs = np.array(coeffs)
    constraints = np.array(constraints)
    constraints[:,-1] = -constraints[:,-1]
    
    # Add zero coefficients for the slack variable and RHS
    obj = np.concatenate((constraints[:,-1], [0] * (len(coeffs) + 1)))

    # The constraints coefficients
    eyes = np.eye(len(coeffs))
    last_col = coeffs.reshape(-1, 1)
    constraints_ = constraints[:, :-1].T
    concatenated = np.hstack((constraints_, eyes))
    constraints = np.hstack((concatenated, last_col))

    # Combine the constraints and the objective into the tableau
    tableau = np.vstack([obj, constraints])
    lmc = np.array([1] + [0] * (len(tableau) - 1))
    lmc = lmc.reshape(-1, 1)
    tableau = np.hstack((lmc, tableau))

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
coeffs = [2.0, 3.0]
constraints = [[1.0, 2.0, 10], [2.0, 1.0, 8]]
_p_tableau = init_prime_tableau(coeffs, constraints)

assert np.array_equal(_p_tableau, np.array([[1.0, -2.0, -3.0, 0.0, 0.0, 0.0], [0.0, 1.0, 2.0, 1.0, 0.0, 10.0], [0.0, 2.0, 1.0, 0.0, 1.0, 8.0]]))
print("\nBefore", _p_tableau)

p_tableau = simplex_method(_p_tableau)

# Display the final tableau
print("\nAfter", p_tableau)

_d_tableau = init_dual_tableau(coeffs, constraints)

print("\nBefore", _d_tableau)
assert np.array_equal(_d_tableau, np.array([[1.0, -10.0, -8.0, 0.0, 0.0, 0.0], [0.0, 1.0, 2.0, 1.0, 0.0, 2.0], [0.0, 2.0, 1.0, 0.0, 1.0, 3.0]]))
d_tableau = simplex_method(_d_tableau)

# Display the final tableau
print("\nAfter", d_tableau)
assert d_tableau[0, -1] == p_tableau[0, -1]

# _tableau = np.array(
#     [
#         [ 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0],
#         [ 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 2254000.0*1.05],
#         [ 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 2254000.0*0.95],
#     ]
# )
# print("\nBefore", _tableau)

# tableau = simplex_method(_tableau)

# # Display the final tableau
# print("\nAfter", tableau)

# _transposed = np.array(
#     [
#         [ 1.0,-2254000.0*1.05,-2254000.0*0.95, 0.0, 0.0, 0.0],
#         [ 0.0, 1.0, 1.0, 1.0, 0.0, -1.0],
#         [ 0.0, 1.0, 1.0, 0.0, 1.0, -1.0],
#     ]
# )
