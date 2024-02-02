import math

# https://systems.cs.columbia.edu/private-systems-class/papers/Abowd2019Census.pdf


# L2 Norm
def l2_obj_func(H_list, M_list):
    return sum(math.sqrt(pow((h - m), 2)) for h, m in zip(H_list, M_list))


def l2_gradient(H, M):
    return [-2 * (h - m) for h, m in zip(H, M)]


# fmt: off
# Initialization of variables
n_states = 51  # 51 states
Hist = [4062, 3117, 9821, 15403, 9302, 8981, 13251, 2116, 9647, 2888, 14446, 16138, 15434, 9055, 8586, 1057, 16122, 3315, 262, 15654, 14540, 713, 15048, 10795, 8319, 8294, 7812, 4257, 10490, 6003, 5266, 16331, 4294, 13279, 7531, 14725, 4646, 3736, 11798, 897, 13233, 3536, 10472, 4750, 3798, 15368, 14540, 7053, 12080, 13792, 11412]
noised_H = [4060, 3122, 9823, 15404, 9304, 8984, 13252, 2108, 9651, 2893, 14451, 15143, 15437, 9058, 8581, 959, 16123, 3120, 267, 15655, 14543, 715, 15053, 10800, 8321, 8298, 7815, 4260, 10495, 6008, 5267, 16233, 4299, 13284, 7533, 14627, 4647, 3739, 11803, 886, 13237, 3541, 10433, 4755, 3799, 15301, 14542, 7055, 12093, 13795, 11517]
init_sum = sum(Hist)
init_loss = l2_obj_func(Hist, noised_H)
# fmt: on


# Gradient Descent parameters
l2_rate = 0.001
l2_iter = 1000

for it in range(l2_iter):
    flag = True
    grad_list = l2_gradient(Hist, noised_H)

    _noised_H = noised_H  # Placeholder

    for i, grad in enumerate(grad_list):
        _noised_H[i] = noised_H[i] - l2_rate * grad
        if _noised_H[i] < 0:  # Nonnegativity Check
            flag = False
            break

    # Population Total Constraint (Easing it to 5% allowance in this)
    if init_sum * 1.5 < sum(_noised_H) or init_sum * 0.95 > sum(_noised_H):
        flag = False
        break

    # TODO: Add any other constraints

    if flag == True:
        noised_H = _noised_H

# Results
post_l2_Sum = sum(noised_H)
l2_loss = l2_obj_func(Hist, noised_H)
H_star = noised_H


# L1 Norm


def l1_obj_func(H_hat, H_star):
    return sum(-(h - round(h_s) * (h_s - round(h_s))) for h, h_s in zip(H_hat, H_star))


def subgradient(H_star):
    return [1 if h_s > round(h_s) else -1 if round(h_s) > h_s else 0 for h_s in H_star]


# Gradient Descent parameters
l1_rate = 0.01
l1_iter = 1000000

H_hat = [hs for hs in H_star]
pre_l1_loss = l1_obj_func(H_hat, H_star)


for it in range(l1_iter):
    flag = True
    grad_list = subgradient(H_star)

    _H_hat = H_hat  # Placeholder

    for i, grad in enumerate(grad_list):
        _H_hat[i] = H_hat[i] - l1_rate * grad
        # Nonnegativity and inequality Constraint (Easing it to 5% allowance, Originally == Exact match)
        if _H_hat[i] < 0 or _H_hat[i] > H_star[i] * 1.5 or _H_hat[i] < H_star[i] * 0.95:
            flag = False
            break

    # Population Total Constraint (Easing it to 5% allowance, Originally == Exact match)
    if post_l2_Sum * 1.5 < sum(_H_hat) or post_l2_Sum * 0.95 > sum(_H_hat):
        flag = False
        break

    # TODO: Add any other constraints, including integer-check

    if flag == True:
        H_hat = _H_hat


# Results
post_l1_sum = sum(H_hat)
l1_loss = l1_obj_func(H_hat, H_star)

print("\nInitial / Post-L2 / Pre-L1 / Post-L1")
# print("\n  Hist:", Hist, "/", H_star, "/", H_star, "/", H_hat)
print("\nSum :", init_sum, "/", post_l2_Sum, "/", post_l2_Sum, "/", post_l1_sum)
print("\nLoss:", init_loss, "/", l2_loss, "/", pre_l1_loss, "/", l1_loss)
