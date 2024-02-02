import math

# https://systems.cs.columbia.edu/private-systems-class/papers/Abowd2019Census.pdf


def sum_nested(hist):
    res = 0
    for h in hist:
        res += sum(h)
    return res


# L2 Norm
def l2_obj_func(H_list, M_list):
    return sum(math.sqrt(pow((_h - _m), 2)) for h, m in zip(H_list, M_list) for _h, _m in zip(h, m))


def l2_gradient(H, M):
    return [-2 * (h - m) for h, m in zip(H, M)]


# Initialization of variables
r1 = [4062, 3117, 9821, 15403, 9302]
r2 = [8981, 13251, 2116, 9647, 2888]
r3 = [14446, 16138, 15434, 9055, 8586]
r4 = [1057, 16122, 3315, 262, 15654]
r5 = [14540, 713, 15048, 10795, 8319]
Hist = [r1, r2, r3, r4, r5]

_r1 = [4060, 3122, 9823, 15404, 9304]
_r2 = [8984, 13252, 2108, 9651, 2893]
_r3 = [14451, 15143, 15437, 9058, 8581]
_r4 = [959, 16123, 3120, 267, 15655]
_r5 = [14543, 715, 15053, 10800, 8321]
noised_H = [_r1, _r2, _r3, _r4, _r5]


init_sum = sum_nested(Hist)
init_loss = l2_obj_func(Hist, noised_H)

# Gradient Descent parameters
l2_rate = 0.001
l2_iter = 1000

for it in range(l2_iter):
    flag = True
    grad_list = [l2_gradient(H, M) for H, M in zip(Hist, noised_H)]
     
    _noised_H = noised_H  # Placeholder

    for i, grad in enumerate(grad_list):
        for j, g in enumerate(grad):
            _noised_H[i][j] = noised_H[i][j] - l2_rate * g
            if _noised_H[i][j] < 0:  # Nonnegativity Check
                flag = False
                break

    # Population Total Constraint (Easing it to 5% allowance in this)
    if init_sum * 1.5 < sum_nested(_noised_H) or init_sum * 0.95 > sum_nested(_noised_H):
        flag = False
        break

    # TODO: Add any other constraints

    if flag == True:
        noised_H = _noised_H

# Results
post_l2_Sum = sum_nested(noised_H)
l2_loss = l2_obj_func(Hist, noised_H)
H_star = noised_H


# L1 Norm


def l1_obj_func(H_hat, H_star):
    return sum(-(_h - round(_h_s) * (_h_s - round(_h_s))) for h, h_s in zip(H_hat, H_star) for _h, _h_s in zip(h, h_s))


#TODO: Revisit if H_star as an arg appropriate and if the algo appropriate
def subgradient(H):
    return [1 if h_s > round(h_s) else -1 if round(h_s) > h_s else 0 for h_s in H]


# Gradient Descent parameters
l1_rate = 0.01
l1_iter = 1000000

H_hat = [hs for hs in H_star]
pre_l1_loss = l1_obj_func(H_hat, H_star)


for it in range(l1_iter):
    flag = True
    grad_list = [subgradient(H) for H in H_star]

    _H_hat = H_hat  # Placeholder

    for i, grad in enumerate(grad_list):
        for j, g in enumerate(grad):
            _H_hat[i][j] = H_hat[i][j] - l1_rate * g
            # Nonnegativity and inequality Constraint (Easing it to 5% allowance, Originally == Exact match)
            if _H_hat[i][j] < 0 or _H_hat[i][j] > H_star[i][j] * 1.5 or _H_hat[i][j] < H_star[i][j] * 0.95:
                flag = False
                break

    # Population Total Constraint (Easing it to 5% allowance, Originally == Exact match)
    if post_l2_Sum * 1.5 < sum_nested(_H_hat) or post_l2_Sum * 0.95 > sum_nested(_H_hat):
        flag = False
        break

    # TODO: Add any other constraints, including integer-check

    if flag == True:
        H_hat = _H_hat


# Results
post_l1_sum = sum_nested(H_hat)
l1_loss = l1_obj_func(H_hat, H_star)

print("\nInitial / Post-L2 / Pre-L1 / Post-L1")
# print("\n  Hist:", Hist, "/", H_star, "/", H_star, "/", H_hat)
print("\nSum :", init_sum, "/", post_l2_Sum, "/", post_l2_Sum, "/", post_l1_sum)
print("\nLoss:", init_loss, "/", l2_loss, "/", pre_l1_loss, "/", l1_loss)
