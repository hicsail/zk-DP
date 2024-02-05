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
        if init_sum * 1.05 < sum(_noised_H) or init_sum * 0.95 > sum(_noised_H):
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
            if _H_hat[i] < 0 or _H_hat[i] > H_star[i] * 1.05 or _H_hat[i] < H_star[i] * 0.95:
                flag = False
                break

        # Population Total Constraint (Easing it to 5% allowance, Originally == Exact match)
        if post_l2_Sum * 1.05 < sum(_H_hat) or post_l2_Sum * 0.95 > sum(_H_hat):
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



parent_node = [MA, NY, CA, IL, AK]
US_Hist = [sum(values) for values in zip(*parent_node)]

noised_H = [42997, 48355, 45541, 45180, 44754] # TODO: Un-hard-code

init_sum = sum(US_Hist)
init_loss = l2_obj_func(US_Hist, noised_H)

l2_rate = 0.001
l2_iter = 1000
l1_rate = 0.01
l1_iter = 1000

# L2

# Results
H_star = L2_optimization(US_Hist, noised_H, l2_rate, l2_iter, init_sum)
post_l2_Sum = sum(H_star)
l2_loss = l2_obj_func(US_Hist, H_star)


# L1
H_hat = [hs for hs in H_star]
pre_l1_loss = l1_obj_func(H_hat, H_star)
H_hat = L1_optimization(H_hat, H_star, l1_rate, l1_iter, post_l2_Sum)
post_l1_sum = sum(H_hat)
l1_loss = l1_obj_func(H_hat, H_star)


def generate_child(parent_node, parent_sum, l1_rate, l1_iter, l2_rate, l2_iter, parent_iter):
    # TODO: Un-hard-code
    _MA = [4058, 3022, 7823, 15400, 9314]
    _NY = [8981, 13230, 2111, 9650, 2883]
    _CA = [14351, 15444, 15537, 9018, 8681]
    _IL = [951, 16233, 3320, 267, 15555]
    _AK = [14535, 700, 15053, 10801, 8323]
    noised_children = [_MA, _NY, _CA, _IL, _AK]
    
    _parent_sum = 0
    l2_loss_ttl = 0
    l1_loss_ttl = 0
    
    for _ in range(parent_iter):
        
        parent_node_hat = parent_node # Placeholder
        temp_l2_loss = 0
        temp_l1_loss = 0

        for idx, obj_hist in enumerate(parent_node_hat):

            init_sum = sum(obj_hist)

            # L2
            H_star = L2_optimization(obj_hist, noised_children[idx], l2_rate, l2_iter, init_sum)
            post_l2_Sum = sum(H_star)
            temp_l2_loss += l2_obj_func(obj_hist, H_star)

            # L1
            H_hat = [hs for hs in H_star]
            H_hat = L1_optimization(H_hat, H_star, l1_rate, l1_iter, post_l2_Sum)
            post_l1_sum = sum(H_hat)
            temp_l1_loss += l1_obj_func(H_hat, H_star)

            _parent_sum += post_l1_sum
            parent_node_hat[idx] = H_hat

        #TODO: compliance check
        if _parent_sum < 1.05 * parent_sum and _parent_sum > 0.95 * parent_sum:
            parent_node = parent_node_hat
            l2_loss_ttl = temp_l2_loss
            l1_loss_ttl = temp_l1_loss

        #TODO: Reconstruct Parent hist
            

    return parent_node, l2_loss_ttl, l1_loss_ttl

parent_iter = 100
parent_node, l2_loss_ttl, l1_loss_ttl = generate_child(parent_node, post_l1_sum, l1_rate, l1_iter, l2_rate, l2_iter, parent_iter)
post_child_gen_sum = sum(k for s in parent_node for k in s)

US_Hist_hat = [sum(values) for values in zip(*parent_node)]

print("\nInitial / Post-L2 / Pre-L1 / Post-L1 / Post Child")
print("\nSum :", init_sum, "/", post_l2_Sum, "/", post_l2_Sum, "/", post_l1_sum, "/", post_child_gen_sum)
print("\nLoss:", init_loss, "/", l2_loss, "/", pre_l1_loss, "/", l1_loss, "/", l2_loss_ttl, "&", l1_loss_ttl)

print("\nInit US Hist:", US_Hist)
print("\nResulting US Hist:", US_Hist_hat)
assert US_Hist_hat == [43060.33774073523, 49268.885995691875, 45477.37740735129, 45137.13767719148, 44745.89351598362]