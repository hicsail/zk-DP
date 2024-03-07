import picozk as pzk

# https://systems.cs.columbia.edu/private-systems-class/papers/Abowd2019Census.pdf


def bit_decompose(x, num_bits):
    bits = pzk.util.encode_int(x.val, x.field)[-num_bits:]
    sbits = [pzk.SecretInt(b) for b in bits]

    new_x = 0
    for i, sb in enumerate(reversed(sbits)):
        pzk.assert0((sb - 1) * sb) # asserting that it's a bit val (0 or 1)
        new_x += 2**i * sb
    pzk.assert0(new_x - x) # validating that the decomposition was properly performed

    return sbits


def div_trunc(x):
    xv = pzk.val_of(x)
    txv = xv // 1000  # quotient
    tx = pzk.SecretInt(txv)
    rv = xv - (txv * 1000)  # remainder
    r = pzk.SecretInt(rv)
    rb = bit_decompose(r, 10)
    # print("trunc", xv, txv, rv)
    pzk.assert0(x - (tx * 1000 + r))
    return tx


def l2_gradient(parent_val, child_hist):
    return -2 * (parent_val - sum(child_hist))


def calc_l2_gnorm(parent_val, child_hist):
    grad = l2_gradient(parent_val, child_hist)
    return grad**2


def L2_optimization(parent_val, child_hist, l2_iter):
    # Optimization
    for _ in range(l2_iter):
        grad = l2_gradient(parent_val, child_hist)
        # print("grad:", pzk.val_of(grad))
        for i in range(len(child_hist)):
            child_hist[i] = child_hist[i] - div_trunc(grad)
    return child_hist
