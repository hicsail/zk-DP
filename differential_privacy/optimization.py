from picozk import *

# https://systems.cs.columbia.edu/private-systems-class/papers/Abowd2019Census.pdf


def l2_gradient(parent_val, child_hist):
    return -2 * (parent_val - sum(child_hist))


def calc_l2_gnorm(parent_val, child_hist):
    grad = l2_gradient(parent_val, child_hist)
    return grad**2


def L2_optimization(parent_hist, child_hist, l2_rate, l2_iter):
    for _ in range(l2_iter):
        grad = l2_gradient(parent_hist, child_hist)
        for i in range(len(child_hist)):
            child_hist[i] = child_hist[i] - l2_rate * grad
    return child_hist
