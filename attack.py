from sage.all import *
from clt import CLT
from util import *
import argparse

def orthogonal_lattice(omega, x0):
    l = len(omega)

    M = block_matrix([[identity_matrix(l), omega.column()],[zero_matrix(ZZ, 1, l), x0]])
    while True:
        last_col = M.column(l)
        nonzero = [(i,x) for i,x in enumerate(last_col) if x]
        (index, minimum) = min(nonzero, key = lambda x: x[1])

        # if number of nonzero entries in the last column is 1, we're done
        if len(nonzero) == 1:
            break

        # subtract x//minimum from each row (except the row with the min entry) 
        for i,x in enumerate(last_col):
            if i != index:
                M.add_multiple_of_row(i, index, -(x//minimum))

    M = M.delete_rows([index, l]).delete_columns([l])

    return M

@profile(LOG, "Attack time")
def attack(mmap, l):
    omega = vector(ZZ, [mmap.run(mmap.k, True) * mmap.p_zt for i in range(l)])
    #print omega    
    u = orthogonal_lattice(omega, mmap.x0)
    u = u.LLL()

    # find all vectors u small enough in this lattice
    u_max = 2**(mmap.eta-1) // Integer(mmap.n * (2**(2*mmap.rho_f))).isqrt()
    us = matrix([row for row in u.rows() if row.norm() < u_max])
    #print "u:", u.nrows()
    #print "us:", us.nrows()

    rk = us.right_kernel()
    rs = matrix(ZZ, rk.matrix()).LLL()

    #print "rs:", rs.nrows()
    factors = set()

    for r in rs:
        s = rk.random_element()

        sw = s * omega
        if Zmod(mmap.x0)(sw) == 0:
            continue
        else:
            factors.add(gcd(sw, mmap.x0))

    success = False;
    for x in factors:
        if x > 1:
            success = True
    
    return factors, success


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

    lam = 5
    k = 5
    l = 80

    parser = argparse.ArgumentParser(description='''CLT attack''');

    parser.add_argument('-lam', dest='lam', default=lam, type=int, 
        help='Security parameter, default is ' + str(lam))
    parser.add_argument('-k', dest='k', default=k, type=int, 
        help='Multilinearity parameter, default is ' + str(k))
    parser.add_argument('-l', dest='l', default=l, type=int, 
        help='Number of encodings, default is ' + str(l))

    params = parser.parse_args()

    lam = params.lam
    k = params.k
    l = params.l


    maxTries = 3
    success = False
    attempt = 1
    while (not success):
        params = CLT.set_params(lam, k)
        mmap = CLT(params)
        f,success = attack(mmap, l)
        attempt = attempt + 1
        if attempt > maxTries and not success:
            l = l + 10
            attempt = 1

    # see if we actually have any factors of x

    print ""
    print "lambda:", lam
    print "level(k):", k
    print "num_encodings:", l
    
    if success == True:
        print "Attack succeeded"
    else: print "Attack failed"


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
