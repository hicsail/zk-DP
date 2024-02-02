import math

# https://systems.cs.columbia.edu/private-systems-class/papers/Abowd2019Census.pdf


# L2 Norm
def l2_obj_func(H_list, M_list):
    return sum(math.sqrt(pow((h - m), 2)) for h, m in zip(H_list, M_list))


def l2_gradient(H, M):
    return [-2 * (h - m) for h, m in zip(H, M)]


def L2_optimization(Hist, noised_H, l2_rate, l2_iter, init_sum):

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
    
    return noised_H


def l1_obj_func(H_hat, H_star):
    return sum(-(h - round(h_s) * (h_s - round(h_s))) for h, h_s in zip(H_hat, H_star))


def subgradient(H_star):
    #TODO: Revisit if H_star as an arg appropriate and if the algo appropriate
    return [1 if h_s > round(h_s) else -1 if round(h_s) > h_s else 0 for h_s in H_star]


def L1_optimization(H_hat, H_star, l1_rate, l1_iter, post_l2_Sum):
    
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
            continue

        # TODO: Add any other constraints, including integer-check

        if flag == True:
            H_hat = _H_hat

    return H_hat


# Initialization of variables
     #  r0,   r1,   r2,   r3,   r4
MA = [4062, 3117, 9821, 15403, 9302]
NY = [8981, 13251, 2116, 9647, 2888]
CA = [14446, 16138, 15434, 9055, 8586]
IL = [1057, 16122, 3315, 262, 15654]
AK = [14540, 713, 15048, 10795, 8319]


Hist = [MA[i] + NY[i] + CA[i] + IL[i] + AK[i] for i in range(len(MA))]

_MA = [4060, 3122, 9823, 15404, 9304]
_NY = [8984, 13252, 2108, 9651, 2893]
_CA = [14451, 15143, 15437, 9058, 8581]
_IL = [959, 16123, 3120, 267, 15655]
_AK = [14543, 715, 15053, 10800, 8321]
noised_H = [_MA[i] + _NY[i] + _CA[i] + _IL[i] + _AK[i] for i in range(len(_MA))]

init_sum = sum(Hist)
init_loss = l2_obj_func(Hist, noised_H)


# L2
l2_rate = 0.001
l2_iter = 1000

# Results
H_star = L2_optimization(Hist, noised_H, l2_rate, l2_iter, init_sum)
post_l2_Sum = sum(H_star)
l2_loss = l2_obj_func(Hist, H_star)


# L1
l1_rate = 0.01
l1_iter = 1000

H_hat = [hs for hs in H_star]
pre_l1_loss = l1_obj_func(H_hat, H_star)

# Results
H_hat = L1_optimization(H_hat, H_star, l1_rate, l1_iter, post_l2_Sum)
post_l1_sum = sum(H_hat)
l1_loss = l1_obj_func(H_hat, H_star)

print("\nInitial / Post-L2 / Pre-L1 / Post-L1")
# print("\n  Hist:", Hist, "/", H_star, "/", H_star, "/", H_hat)
print("\nSum :", init_sum, "/", post_l2_Sum, "/", post_l2_Sum, "/", post_l1_sum)
print("\nLoss:", init_loss, "/", l2_loss, "/", pre_l1_loss, "/", l1_loss)