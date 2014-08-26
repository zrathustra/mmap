from sage.all import *
from clt import CLT
from util import *

@profile(LOG, "orthogonal lattice")
def orthogonal_lattice(omega, x0):

    l = len(omega)

    mat = block_matrix([[identity_matrix(l), omega.column()],[zero_matrix(ZZ, 1, l), x0]])
    while True:
        last_col = mat.column(l)
        nonzero = [(i,x) for i,x in enumerate(last_col) if x]
        (index, minimum) = min(nonzero, key = lambda x: x[1])

        # if number of nonzero entries in the last column is 1, we're done
        if len(nonzero) == 1:
            break

        # subtract x//minimum from each row (except the row with the min entry) 
        for i,x in enumerate(last_col):
            if i != index:
                mat.add_multiple_of_row(i, index, -(x//minimum))

    mat = mat.delete_rows([index, l]).delete_columns([l])

    return mat

def attack(mmap, l):
    omega = vector(ZZ, [mmap.run(mmap.k, True) * mmap.p_zt for i in range(l)])

    u = orthogonal_lattice(omega, mmap.x0)

def test(mmap, l):
    ''' test the orthogonal_lattice method '''
    omega = vector(ZZ, [mmap.run(mmap.k, True) * mmap.p_zt for i in range(l)])

    u = orthogonal_lattice(omega, mmap.x0)
    u = block_matrix([[u], [zero_matrix(ZZ, 1, l)]])
    passes = 0
    for i in range(500):
        v = random_vector(ZZ, l) * u
        if Zmod(mmap.x0)(v * omega) == 0:
            passes += 1

    return passes

if __name__=="__main__":
    lam = 10
    k = 5
    l = 1000

    params = CLT.set_params(lam, k)
    mmap = CLT(params)

    attack(mmap, l)

# attack psuedocode

# generate a bunch of level-k encodings of 0 c_i
# multiply all c_i by p_zt yielding w_i for each c_i
# compute lattice L orthogonal to w = (w_1, ..., w_l)
    # run LLL/BKZ on basis B of L
# get all vectors {u} in B that are short enough
# compute lattice L_r orthogonal to L with basis B_r
    # run LLL/BKZ on basis B_r

# for r in reduced_B_r
    # compute s such that <s, r> = 0 (mod x_0)
    # if <s, w> = 0 (mod x_0)
        # continue to next loop iteration
    # compute p = gcd(<s, w>, x_0)
    # p should be a factor of x_0

# repeat algorithm until x_0 is fully factored
