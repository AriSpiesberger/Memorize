"""One randomly initialised transformer, 100 math tasks, pure RL, a free-length workspace.

In what order do they saturate?

Tasks run in ten tiers, from one-digit arithmetic up to eigenvalues and eigenvectors
(see TASKS, or run --list). One model learns all of them at once; a task token tells
it which one it is looking at. Problems are written as plain text ("12+34", "2 1;1 2").

Sequence:   [task] input [sep]  workspace ... [end-think]  answer ... [eos]

The workspace is free text from the same characters as the problems. The model chooses
how long to think by emitting [end-think] (capped at --max-think). Nothing checks the
workspace; only the answer is rewarded. It starts out thinking ~4 characters and can
learn to think longer.

Reward: 1 for an exact answer, else --partial x (fraction of characters right).
Update: REINFORCE with a group baseline (G samples per problem), entropy bonus on the
answer that decays over training (it stops the policy collapsing to a constant answer
before it has looked at the input, see parity).
Eval:   greedy exact accuracy on held-out problems never trained on, per task. A task is
"saturated" the first time it reaches --saturate accuracy; the order of saturation is the result.

  python addition/math100.py --list                          # every task, with an example
  python addition/math100.py --out addition/results/math100  # train (resumes if the dir has a checkpoint)
  python addition/math100.py --report addition/results/math100
"""
import argparse, json, math, os, random, time
from fractions import Fraction
from math import comb, gcd, isqrt, perm, factorial
import torch, torch.nn as nn, torch.nn.functional as F

# ---------------------------------------------------------------- tasks
TASKS = []                                    # (tier, name, generator(rng) -> (input, answer))
def task(tier):
    def reg(fn): TASKS.append((tier, fn.__name__, fn)); return fn
    return reg

vec = lambda v: " ".join(map(str, v))
mat = lambda M: ";".join(vec(r) for r in M)
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def mv(A, v): return [sum(a * b for a, b in zip(r, v)) for r in A]
def det(M):
    M = [[Fraction(x) for x in r] for r in M]; n, d = len(M), Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None: return 0
        if p != c: M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return int(d)
def inv(M):
    n = len(M); A = [[Fraction(x) for x in r] + [Fraction(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0); A[c], A[p] = A[p], A[c]
        A[c] = [x / A[c][c] for x in A[c]]
        for r in range(n):
            if r != c: f = A[r][c]; A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [[int(x) for x in r[n:]] for r in A]
def rank(M):
    M = [[Fraction(x) for x in r] for r in M]; rk, rows, cols = 0, len(M), len(M[0])
    for c in range(cols):
        p = next((r for r in range(rk, rows) if M[r][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for r in range(rows):
            if r != rk and M[r][c] != 0: f = M[r][c] / M[rk][c]; M[r] = [a - f * b for a, b in zip(M[r], M[rk])]
        rk += 1
    return rk
def unimodular(r, n, ops):                    # integer matrix with integer inverse
    P = [[int(i == j) for j in range(n)] for i in range(n)]
    for _ in range(ops):
        i, j = r.sample(range(n), 2); c = r.choice([-1, 1]); P[i] = [a + c * b for a, b in zip(P[i], P[j])]
    return P
def primitive(v):
    g = 0
    for x in v: g = gcd(g, abs(x))
    v = [x // g for x in v]
    return [-x for x in v] if next(x for x in v if x) < 0 else v
def similar(r, n, ops, D):                    # M = P diag(D) P^-1: integer, eigenvalues D, eigenvectors = columns of P
    P = unimodular(r, n, ops); Dm = [[D[i] if i == j else 0 for j in range(n)] for i in range(n)]
    return mm(mm(P, Dm), inv(P)), P
def frac(f): return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"
def cmp(a, b): return "<" if a < b else ">" if a > b else "="
PRIMES = [p for p in range(2, 1000) if all(p % q for q in range(2, isqrt(p) + 1))]
def rnd_nz(r, lo, hi):
    while True:
        x = r.randint(lo, hi)
        if x: return x

# tier 1: one step on small numbers
@task(1)
def succ(r): n = r.randrange(1000); return f"{n}", f"{n + 1}"
@task(1)
def pred(r): n = r.randrange(1, 1000); return f"{n}", f"{n - 1}"
@task(1)
def add1(r): a, b = r.randrange(10), r.randrange(10); return f"{a}+{b}", f"{a + b}"
@task(1)
def sub1(r): a, b = r.randrange(10), r.randrange(10); return f"{a}-{b}", f"{a - b}"
@task(1)
def max2(r): a, b = r.randrange(100), r.randrange(100); return f"{a} {b}", f"{max(a, b)}"
@task(1)
def min2(r): a, b = r.randrange(100), r.randrange(100); return f"{a} {b}", f"{min(a, b)}"
@task(1)
def compare(r):
    a = r.randrange(100); b = a if r.random() < 0.2 else r.randrange(100); return f"{a} {b}", cmp(a, b)
@task(1)
def even(r): n = r.randrange(1000); return f"{n}", f"{n % 2}"
@task(1)
def double(r): n = r.randrange(500); return f"{n}", f"{2 * n}"
@task(1)
def half(r): n = r.randrange(1000); return f"{n}", f"{n // 2}"

# tier 2: two-digit arithmetic
@task(2)
def add2(r): a, b = r.randrange(100), r.randrange(100); return f"{a}+{b}", f"{a + b}"
@task(2)
def sub2(r): a, b = r.randrange(100), r.randrange(100); return f"{a}-{b}", f"{a - b}"
@task(2)
def mul1(r): a, b = r.randrange(10), r.randrange(10); return f"{a}*{b}", f"{a * b}"
@task(2)
def mul21(r): a, b = r.randrange(10, 100), r.randrange(10); return f"{a}*{b}", f"{a * b}"
@task(2)
def intdiv(r): a, b = r.randrange(100), r.randrange(1, 10); return f"{a}/{b}", f"{a // b}"
@task(2)
def mod(r): a, b = r.randrange(100), r.randrange(2, 10); return f"{a}%{b}", f"{a % b}"
@task(2)
def modadd7(r): a, b = r.randrange(7), r.randrange(7); return f"{a}+{b}", f"{(a + b) % 7}"
@task(2)
def modadd97(r): a, b = r.randrange(97), r.randrange(97); return f"{a}+{b}", f"{(a + b) % 97}"
@task(2)
def absdiff(r): a, b = r.randrange(100), r.randrange(100); return f"{a} {b}", f"{abs(a - b)}"
@task(2)
def add3terms(r): a, b, c = (r.randrange(10) for _ in range(3)); return f"{a}+{b}+{c}", f"{a + b + c}"

# tier 3: multi-digit arithmetic, powers, digits
@task(3)
def add3(r): a, b = r.randrange(1000), r.randrange(1000); return f"{a}+{b}", f"{a + b}"
@task(3)
def sub3(r): a, b = r.randrange(1000), r.randrange(1000); return f"{a}-{b}", f"{a - b}"
@task(3)
def mul22(r): a, b = r.randrange(10, 100), r.randrange(10, 100); return f"{a}*{b}", f"{a * b}"
@task(3)
def add4(r): a, b = r.randrange(10000), r.randrange(10000); return f"{a}+{b}", f"{a + b}"
@task(3)
def square(r): n = r.randrange(100); return f"{n}", f"{n * n}"
@task(3)
def cube(r): n = r.randrange(22); return f"{n}", f"{n ** 3}"
@task(3)
def pow2(r): n = r.randrange(20); return f"{n}", f"{2 ** n}"
@task(3)
def digitsum(r): n = r.randrange(10 ** 6); return f"{n}", f"{sum(map(int, str(n)))}"
@task(3)
def digitroot(r): n = r.randrange(1, 10 ** 6); return f"{n}", f"{1 + (n - 1) % 9}"
@task(3)
def reversenum(r): n = r.randrange(10 ** 6); return f"{n}", str(int(str(n)[::-1]))

# tier 4: number theory
@task(4)
def gcd2(r): a, b = r.randrange(1, 100), r.randrange(1, 100); return f"{a} {b}", f"{gcd(a, b)}"
@task(4)
def lcm2(r): a, b = r.randrange(1, 31), r.randrange(1, 31); return f"{a} {b}", f"{a * b // gcd(a, b)}"
@task(4)
def isprime(r):
    if r.random() < 0.5: n = r.choice(PRIMES)
    else:
        n = r.randrange(4, 1000)
        while n in PRIMES: n = r.randrange(4, 1000)
    return f"{n}", f"{int(n in PRIMES)}"
@task(4)
def smallestfactor(r): n = r.randrange(2, 1000); return f"{n}", f"{next(p for p in PRIMES + [n] if n % p == 0)}"
@task(4)
def numdivisors(r): n = r.randrange(1, 200); return f"{n}", f"{sum(n % d == 0 for d in range(1, n + 1))}"
@task(4)
def sumdivisors(r): n = r.randrange(1, 100); return f"{n}", f"{sum(d for d in range(1, n + 1) if n % d == 0)}"
@task(4)
def modinv97(r): a = r.randrange(1, 97); return f"{a}", f"{pow(a, -1, 97)}"
@task(4)
def modpow13(r): a, b = r.randrange(13), r.randrange(21); return f"{a}^{b}", f"{pow(a, b, 13)}"
@task(4)
def modmul97(r): a, b = r.randrange(97), r.randrange(97); return f"{a}*{b}", f"{a * b % 97}"
@task(4)
def isqrt_(r): n = r.randrange(10000); return f"{n}", f"{isqrt(n)}"

# tier 5: lists and sequences
def digits_list(r, n, hi=10): return [r.randrange(hi) for _ in range(n)]
@task(5)
def listsum(r): l = digits_list(r, 5); return vec(l), f"{sum(l)}"
@task(5)
def listmax(r): l = digits_list(r, 5, 100); return vec(l), f"{max(l)}"
@task(5)
def sort5(r): l = digits_list(r, 5); return vec(l), vec(sorted(l))
@task(5)
def median5(r): l = digits_list(r, 5, 100); return vec(l), f"{sorted(l)[2]}"
@task(5)
def mean4(r): l = digits_list(r, 4, 100); return vec(l), f"{sum(l) // 4}"
@task(5)
def counteven(r): l = digits_list(r, 6); return vec(l), f"{sum(x % 2 == 0 for x in l)}"
@task(5)
def fib(r):
    n = r.randrange(25); a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return f"{n}", f"{a}"
@task(5)
def triangular(r): n = r.randrange(100); return f"{n}", f"{n * (n + 1) // 2}"
@task(5)
def arithnext(r): a, d = r.randint(-20, 20), r.randint(-9, 9); return vec([a, a + d, a + 2 * d]), f"{a + 3 * d}"
@task(5)
def geomnext(r): a, q = r.randint(1, 9), r.randint(2, 4); return vec([a, a * q, a * q * q]), f"{a * q ** 3}"

# tier 6: combinatorics and bases
@task(6)
def factorial_(r): n = r.randrange(10); return f"{n}", f"{factorial(n)}"
@task(6)
def choose(r): n = r.randrange(16); k = r.randrange(n + 1); return f"{n} {k}", f"{comb(n, k)}"
@task(6)
def permute(r): n = r.randrange(10); k = r.randrange(n + 1); return f"{n} {k}", f"{perm(n, k)}"
@task(6)
def tobinary(r): n = r.randrange(256); return f"{n}", f"{n:b}"
@task(6)
def frombinary(r): n = r.randrange(256); return f"{n:b}", f"{n}"
@task(6)
def tobase3(r):
    n = r.randrange(243); s, m = "", n
    while True:
        s = str(m % 3) + s; m //= 3
        if not m: break
    return f"{n}", s
@task(6)
def tohex(r): n = r.randrange(4096); return f"{n}", f"{n:x}"
@task(6)
def popcount(r): n = r.randrange(1024); return f"{n}", f"{bin(n).count('1')}"
@task(6)
def collatz(r):
    n = r.randint(1, 60); m, s = n, 0
    while m != 1: m = m // 2 if m % 2 == 0 else 3 * m + 1; s += 1
    return f"{n}", f"{s}"
@task(6)
def catalan(r): n = r.randrange(12); return f"{n}", f"{comb(2 * n, n) // (n + 1)}"

# tier 7: algebra and fractions
@task(7)
def linear(r):
    a, x, b = rnd_nz(r, -9, 9), r.randint(-9, 9), r.randint(-20, 20); return f"{a}x{b:+d}={a * x + b}", f"{x}"
@task(7)
def polyeval(r):
    a, b, c, x = (r.randint(-5, 5) for _ in range(4)); return f"{a} {b} {c}:{x}", f"{a * x * x + b * x + c}"
@task(7)
def quadroots(r):
    p, q = sorted((r.randint(-9, 9), r.randint(-9, 9))); return f"{-(p + q)} {p * q}", vec([p, q])
@task(7)
def system2(r):
    while True:
        A = [[r.randint(-5, 5) for _ in range(2)] for _ in range(2)]
        if det(A): break
    x = [r.randint(-9, 9) for _ in range(2)]; b = mv(A, x)
    return mat([A[0] + [b[0]], A[1] + [b[1]]]), vec(x)
@task(7)
def derivative(r): c = [r.randint(-9, 9) for _ in range(4)]; return vec(c), vec([3 * c[0], 2 * c[1], c[2]])
@task(7)
def polymul11(r):
    a, b, c, d = (r.randint(-9, 9) for _ in range(4)); return f"{a} {b}*{c} {d}", vec([a * c, a * d + b * c, b * d])
@task(7)
def arithsum(r):
    a, d, n = r.randint(-9, 9), r.randint(-9, 9), r.randint(1, 20); return f"{a} {d} {n}", f"{n * a + d * n * (n - 1) // 2}"
@task(7)
def fracadd(r):
    a, b, c, d = r.randint(1, 9), r.randint(1, 9), r.randint(1, 9), r.randint(1, 9)
    return f"{a}/{b}+{c}/{d}", frac(Fraction(a, b) + Fraction(c, d))
@task(7)
def fracsimplify(r): p, q = r.randint(1, 99), r.randint(1, 99); return f"{p}/{q}", frac(Fraction(p, q))
@task(7)
def fraccompare(r):
    a, b = r.randint(1, 9), r.randint(1, 9)
    if r.random() < 0.2: k = r.randint(2, 5); c, d = a * k, b * k
    else: c, d = r.randint(1, 9), r.randint(1, 9)
    return f"{a}/{b} {c}/{d}", cmp(Fraction(a, b), Fraction(c, d))

# tier 8: vectors and 2x2 matrices
def rmat(r, n, lo, hi): return [[r.randint(lo, hi) for _ in range(n)] for _ in range(n)]
def rvec(r, n, lo, hi): return [r.randint(lo, hi) for _ in range(n)]
@task(8)
def dot3(r): u, v = rvec(r, 3, -9, 9), rvec(r, 3, -9, 9); return mat([u, v]), f"{sum(a * b for a, b in zip(u, v))}"
@task(8)
def vecadd3(r): u, v = rvec(r, 3, -9, 9), rvec(r, 3, -9, 9); return mat([u, v]), vec([a + b for a, b in zip(u, v)])
@task(8)
def cross3(r):
    u, v = rvec(r, 3, -5, 5), rvec(r, 3, -5, 5)
    return mat([u, v]), vec([u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]])
@task(8)
def det2(r): M = rmat(r, 2, -9, 9); return mat(M), f"{det(M)}"
@task(8)
def trace2(r): M = rmat(r, 2, -9, 9); return mat(M), f"{M[0][0] + M[1][1]}"
@task(8)
def transpose2(r): M = rmat(r, 2, -9, 9); return mat(M), mat([list(c) for c in zip(*M)])
@task(8)
def matvec2(r): M, v = rmat(r, 2, -5, 5), rvec(r, 2, -5, 5); return f"{mat(M)}:{vec(v)}", vec(mv(M, v))
@task(8)
def matmul2(r): A, B = rmat(r, 2, -5, 5), rmat(r, 2, -5, 5); return f"{mat(A)}*{mat(B)}", mat(mm(A, B))
@task(8)
def det3(r): M = rmat(r, 3, -3, 3); return mat(M), f"{det(M)}"
@task(8)
def inverse2(r): P = unimodular(r, 2, r.randint(1, 4)); return mat(P), mat(inv(P))

# tier 9: more linear algebra
@task(9)
def matpow2(r):
    M, k = rmat(r, 2, -2, 2), r.randint(2, 4); P = M
    for _ in range(k - 1): P = mm(P, M)
    return f"{mat(M)}^{k}", mat(P)
@task(9)
def rank3(r):
    k = r.randint(0, 3); M = [[0] * 3 for _ in range(3)]
    for _ in range(k):
        u, v = rvec(r, 3, -2, 2), rvec(r, 3, -2, 2); M = [[M[i][j] + u[i] * v[j] for j in range(3)] for i in range(3)]
    return mat(M), f"{rank(M)}"
@task(9)
def system3(r):
    while True:
        A = rmat(r, 3, -3, 3)
        if det(A): break
    x = rvec(r, 3, -5, 5); b = mv(A, x)
    return mat([row + [bi] for row, bi in zip(A, b)]), vec(x)
@task(9)
def eigvals2(r):
    D = sorted(r.sample(range(-5, 6), 2)); M, _ = similar(r, 2, r.randint(1, 3), D); return mat(M), vec(D)
@task(9)
def charpoly2(r):
    M = rmat(r, 2, -9, 9); return mat(M), vec([-(M[0][0] + M[1][1]), det(M)])
@task(9)
def trace3(r): M = rmat(r, 3, -9, 9); return mat(M), f"{sum(M[i][i] for i in range(3))}"
@task(9)
def matvec3(r): M, v = rmat(r, 3, -3, 3), rvec(r, 3, -3, 3); return f"{mat(M)}:{vec(v)}", vec(mv(M, v))
@task(9)
def normsq3(r): v = rvec(r, 3, -9, 9); return vec(v), f"{sum(x * x for x in v)}"
@task(9)
def orthogonal(r):
    u = rvec(r, 3, -4, 4)
    if r.random() < 0.5:
        w = rvec(r, 3, -2, 2); v = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]
    else: v = rvec(r, 3, -4, 4)
    return mat([u, v]), f"{int(sum(a * b for a, b in zip(u, v)) == 0)}"
@task(9)
def adjugate2(r): (a, b), (c, d) = rmat(r, 2, -9, 9); return mat([[a, b], [c, d]]), mat([[d, -b], [-c, a]])

# tier 10: eigenvectors and harder matrix work
@task(10)
def eigvec2max(r):
    D = r.sample(range(-5, 6), 2); M, P = similar(r, 2, r.randint(1, 3), D)
    i = D.index(max(D)); return mat(M), vec(primitive([P[0][i], P[1][i]]))
@task(10)
def eigvec2min(r):
    D = r.sample(range(-5, 6), 2); M, P = similar(r, 2, r.randint(1, 3), D)
    i = D.index(min(D)); return mat(M), vec(primitive([P[0][i], P[1][i]]))
@task(10)
def eigvals3(r):
    D = [r.randint(-3, 3) for _ in range(3)]; M, _ = similar(r, 3, r.randint(1, 3), D); return mat(M), vec(sorted(D))
@task(10)
def eigvec3max(r):
    D = r.sample(range(-3, 4), 3); M, P = similar(r, 3, r.randint(1, 3), D)
    i = D.index(max(D)); return mat(M), vec(primitive([P[k][i] for k in range(3)]))
@task(10)
def det4(r): M = rmat(r, 4, 0, 1); return mat(M), f"{det(M)}"
@task(10)
def matsquare3(r): M = rmat(r, 3, -2, 2); return mat(M), mat(mm(M, M))
@task(10)
def inverse3(r): P = unimodular(r, 3, r.randint(2, 4)); return mat(P), mat(inv(P))
@task(10)
def nullspace23(r):
    while True:
        u, v = rvec(r, 3, -4, 4), rvec(r, 3, -4, 4)
        c = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        if any(c): return mat([u, v]), vec(primitive(c))
@task(10)
def polymul22(r):
    a, b = rvec(r, 3, -4, 4), rvec(r, 3, -4, 4)
    return f"{vec(a)}*{vec(b)}", vec([sum(a[i] * b[k - i] for i in range(3) if 0 <= k - i < 3) for k in range(5)])
@task(10)
def cubicroots(r):
    x = sorted(r.randint(-4, 4) for _ in range(3))
    return vec([-sum(x), x[0] * x[1] + x[0] * x[2] + x[1] * x[2], -x[0] * x[1] * x[2]]), vec(x)

assert len(TASKS) == 100, len(TASKS)

# ---------------------------------------------------------------- vocabulary
CHARS = "0123456789+-*/%^:;=<> abcdefghijklmnopqrstuvwxyz"
C = len(CHARS); CI = {c: i for i, c in enumerate(CHARS)}
PAD, SEP, END, EOS, TASK0 = C, C + 1, C + 2, C + 3, C + 4
V = TASK0 + len(TASKS)
def encode(s): return [CI[c] for c in s]
def decode(t): return "".join(CHARS[i] for i in t if i < C)
THINK_OK = torch.full((V,), float("-inf")); THINK_OK[:C] = 0; THINK_OK[END] = 0     # workspace: any character, or stop
ANS_OK = torch.full((V,), float("-inf")); ANS_OK[:C] = 0; ANS_OK[EOS] = 0            # answer: any character, or stop
THINK_MUST = THINK_OK.clone(); THINK_MUST[END] = float("-inf")                          # workspace below --min-think: no stop

# ---------------------------------------------------------------- model (small GPT with a KV cache)
class Block(nn.Module):
    def __init__(s, d, h):
        super().__init__(); s.h = h
        s.ln1, s.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        s.qkv, s.o = nn.Linear(d, 3 * d), nn.Linear(d, d)
        s.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
    def forward(s, x, mask, cache=None, t=0):
        """cache: preallocated (k, v) buffers (B, heads, Tmax, dh). This call's keys/values are written at
        positions t..t+T-1 in place, and attention reads positions 0..t+T-1."""
        B, T, D = x.shape
        q, k, v = s.qkv(s.ln1(x)).view(B, T, 3, s.h, D // s.h).permute(2, 0, 3, 1, 4)
        if cache is not None:
            cache[0][:, :, t : t + T] = k; cache[1][:, :, t : t + T] = v
            k, v = cache[0][:, :, : t + T], cache[1][:, :, : t + T]
        a = (F.scaled_dot_product_attention(q, k, v, is_causal=True) if mask is None    # packed rows: causal is exact
             else F.scaled_dot_product_attention(q, k, v, attn_mask=mask))
        x = x + s.o(a.transpose(1, 2).reshape(B, T, D))
        return x + s.mlp(s.ln2(x))

class GPT(nn.Module):
    def __init__(s, maxlen, d, layers, heads):
        super().__init__(); s.heads = heads
        s.tok, s.pos = nn.Embedding(V, d), nn.Embedding(maxlen, d)
        s.blocks = nn.ModuleList(Block(d, heads) for _ in range(layers))
        s.ln, s.head = nn.LayerNorm(d), nn.Linear(d, V)
    def new_cache(s, B, Tmax):
        w = s.head.weight; d = w.shape[1]
        return [tuple(torch.empty(B, s.heads, Tmax, d // s.heads, device=w.device, dtype=w.dtype) for _ in range(2))
                for _ in s.blocks]
    def forward(s, tok, pos, mask, cache=None, t=0):
        x = s.tok(tok) + s.pos(pos)
        for i, b in enumerate(s.blocks): x = b(x, mask, None if cache is None else cache[i], t)
        return s.head(s.ln(x))

def full_mask(valid):                         # causal, ignore padding, every position sees itself
    T = valid.shape[1]; causal = torch.tril(torch.ones(T, T, dtype=torch.bool, device=valid.device))
    m = causal[None] & valid[:, None, :]
    return (m | torch.eye(T, dtype=torch.bool, device=valid.device)[None])[:, None]

def pad_prompts(prompts, dev):
    L = max(map(len, prompts)); tok = torch.full((len(prompts), L), PAD, dtype=torch.long)
    for i, p in enumerate(prompts): tok[i, L - len(p):] = torch.tensor(p)
    return tok.to(dev)

@torch.no_grad()
def generate(model, prompts, greedy, max_think, max_ans, min_think=0):
    """Think until [end-think], answer until [eos]. Returns prompt tokens, generated tokens, phase per generated
    token (0 think, 1 answer, -1 padding) and a 'sampled' mask (False for padding and for tokens forced by the caps).

    KV cache: buffers are allocated once at full length and written in place. Finished sequences are dropped
    from the batch as they finish (compacted when a quarter of the batch is done), so one long thinker does
    not keep the whole batch running."""
    dev = next(model.parameters()).device; B = len(prompts)
    tok = pad_prompts(prompts, dev); Lp = tok.shape[1]; G = max_think + max_ans + 2
    out = torch.full((B, G), PAD, dtype=torch.long, device=dev)
    phases = torch.full((B, G), -1, dtype=torch.long, device=dev); sampled = torch.zeros(B, G, dtype=torch.bool, device=dev)
    keys = torch.zeros(B, Lp + G, dtype=torch.bool, device=dev); keys[:, :Lp] = tok != PAD
    cur = (keys[:, :Lp].cumsum(1) - 1).clamp(min=0)
    cache = model.new_cache(B, Lp + G)
    last = model(tok, cur, full_mask(keys[:, :Lp]), cache, 0)[:, -1]; cur = cur[:, -1]
    think_ok, ans_ok, think_must = THINK_OK.to(dev), ANS_OK.to(dev), THINK_MUST.to(dev)
    END_t, EOS_t, PAD_t, M1, ONE = (torch.tensor(v, device=dev) for v in (END, EOS, PAD, -1, 1))   # no host->GPU copy per step
    rows = torch.arange(B, device=dev)                       # original index of each active row
    phase = torch.zeros(B, dtype=torch.long, device=dev); n_think = torch.zeros_like(phase); n_ans = torch.zeros_like(phase)
    done = torch.zeros(B, dtype=torch.bool, device=dev); used = 0
    for j in range(G):
        allowed = think_must if j < min_think else think_ok    # think token j is the j-th workspace character
        lg = last.float() + torch.where((phase == 0)[:, None], allowed, ans_ok)
        a = lg.argmax(-1) if greedy else torch.distributions.Categorical(logits=lg).sample()
        force_end = (phase == 0) & (n_think >= max_think); force_eos = (phase == 1) & (n_ans >= max_ans)
        a = torch.where(force_end, END_t, a); a = torch.where(force_eos, EOS_t, a); a = torch.where(done, PAD_t, a)
        out[rows, j] = a; phases[rows, j] = torch.where(done, M1, phase); sampled[rows, j] = ~done & ~force_end & ~force_eos
        used = j + 1
        n_think += (phase == 0) & ~done; n_ans += (phase == 1) & ~done
        finished = done | ((phase == 1) & (a == EOS))
        phase = torch.where((phase == 0) & (a == END) & ~done, ONE, phase); done = finished
        n_live = len(rows) - int(done.sum())
        if n_live == 0: break
        size = -(-n_live // 64) * 64                         # drop finished rows, but only to multiples of 64:
        if size * 4 <= len(rows) * 3:                        # every new batch shape costs an MPS kernel compile
            keep = torch.cat([(~done).nonzero().squeeze(1), done.nonzero().squeeze(1)])[:size]
            rows, a, cur, phase, n_think, n_ans, done, keys = (x[keep] for x in (rows, a, cur, phase, n_think, n_ans, done, keys))
            cache = [(k[keep], v[keep]) for k, v in cache]
        t = Lp + j; keys[:, t] = a != PAD; cur = cur + 1
        m = keys[:, : t + 1].clone(); m[:, t] = True
        last = model(a[:, None], cur[:, None], m[:, None, None, :], cache, t)[:, -1]
    return tok, out[:, :used], phases[:, :used], sampled[:, :used]

def packed_batches(tok, gen, budget):
    """Training forward without padding masks: each row becomes prompt + generated tokens with no left padding,
    so plain causal attention is exact (pads only trail). Rows are sorted by length and cut into micro-batches of
    about `budget` tokens, each trimmed to its own longest row. Yields (row indices, packed tokens, prompt lengths)."""
    P, Gt = tok.tolist(), gen.tolist()
    rows = []
    for i, (p, g) in enumerate(zip(P, Gt)):
        p = [t for t in p if t != PAD]
        n = len(g)
        while n and g[n - 1] == PAD: n -= 1
        rows.append((len(p) + n, i, p + g[:n], len(p)))
    rows.sort()
    while rows:
        k = 1
        while k < len(rows) and (k + 1) * rows[k][0] <= budget: k += 1
        chunk, rows = rows[:k], rows[k:]
        T = chunk[-1][0]
        packed = torch.full((len(chunk), T), PAD, dtype=torch.long)
        for j, (_, _, seq, _) in enumerate(chunk): packed[j, : len(seq)] = torch.tensor(seq)
        yield [c[1] for c in chunk], packed, [c[3] for c in chunk]

def policy_terms(model, packed, plen, gen, ph, min_think=0):
    """Log-prob of each generated token and the character entropy at that position, aligned with gen (B, G)."""
    dev = gen.device; B, T = packed.shape; Gn = gen.shape[1]
    pos = torch.arange(T, device=dev).expand(B, T)
    logits = model(packed, pos, None)                                   # (B, T, V)
    idx = (torch.tensor(plen, device=dev)[:, None] - 1 + torch.arange(Gn, device=dev)[None]).clamp(max=T - 1)
    logits = logits.gather(1, idx[..., None].expand(B, Gn, logits.shape[-1])).float()
    early = (torch.arange(Gn, device=dev) < min_think)[None, :, None]          # same masks the sampler used
    think_mask = torch.where(early, THINK_MUST.to(dev), THINK_OK.to(dev))
    logits = logits + torch.where((ph == 0)[..., None], think_mask, ANS_OK.to(dev))
    lp = logits.log_softmax(-1).gather(-1, gen[..., None]).squeeze(-1)
    # entropy of WHICH character, not of whether to stop: a bonus on the stop tokens would
    # flatten them and make the model think and answer longer for no reason
    lpc = logits[..., :C].log_softmax(-1); ent = -(lpc.exp() * lpc).sum(-1)
    # while thinking: entropy of the yes/no decision "stop now?", which keeps short thinking explored
    # (pulls p(stop) toward 1/2, not toward 1/50 like a bonus over the whole distribution would)
    pe = logits.log_softmax(-1)[..., END].exp().clamp(1e-6, 1 - 1e-6)
    ent_stop = -(pe * pe.log() + (1 - pe) * (1 - pe).log()) * ~early[..., 0]
    return lp, ent, ent_stop

def split(gen, ph):
    """Per row: (workspace text, answer text, workspace length)."""
    res = []
    for g, p in zip(gen.tolist(), ph.tolist()):
        think = [t for t, q in zip(g, p) if q == 0 and t != END]; ans = [t for t, q in zip(g, p) if q == 1 and t != EOS]
        res.append((decode(think), decode(ans), len(think)))
    return res

def score(a, t, partial):
    if a == t: return 1.0
    return partial * sum(x == y for x, y in zip(a, t)) / max(len(a), len(t), 1)

# ---------------------------------------------------------------- data
def build_heldout(n_held, seed):
    """Per task: a held-out set never trained on. Small problem spaces hold out 20%."""
    held = {}
    for ti, (_, name, fn) in enumerate(TASKS):
        r = random.Random(seed * 7919 + ti); seen = {}
        for _ in range(3000):
            x, y = fn(r); seen.setdefault(x, y)
        items = sorted(seen.items()); r.shuffle(items)
        k = min(n_held, len(items) // 5) if len(items) < 1000 else n_held
        held[name] = items[:k]
    return held

def sample_train(r, ti, held_inputs):
    fn = TASKS[ti][2]
    for _ in range(100):
        x, y = fn(r)
        if x not in held_inputs: return x, y
    return x, y

def prompt(ti, x): return [TASK0 + ti] + encode(x) + [SEP]

# ---------------------------------------------------------------- report
def report(d, thresholds=(0.1, 0.5, 0.9)):        # ranked by first step at >= 0.9 (saturation)
    rows = [json.loads(l) for l in open(os.path.join(d, "log.jsonl")) if '"eval"' in l]
    if not rows: print("no evals logged yet"); return
    first = {}
    for row in rows:
        for name, m in row["eval"].items():
            for th in thresholds:
                if m["acc"] >= th and (name, th) not in first: first[name, th] = row["step"]
    last = rows[-1]["eval"]; tier = {n: t for t, n, _ in TASKS}
    order = sorted(last, key=lambda n: (first.get((n, 0.9), 1e12), first.get((n, 0.5), 1e12), first.get((n, 0.1), 1e12), -last[n]["acc"]))
    print(f"after step {rows[-1]['step']}: {sum(m['acc'] >= 0.9 for m in last.values())}/100 tasks at >= 90% held-out (saturated)")
    print(f"{'task':16s} tier  " + "  ".join(f"first>={th:<4}" for th in thresholds) + "   now  think")
    for n in order:
        f = "  ".join(f"{first.get((n, th), '-')!s:>10s}" for th in thresholds)
        print(f"{n:16s} {tier[n]:4d}  {f}   {last[n]['acc']:.2f}  {last[n]['think']:5.1f}")

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="addition/results/math100", help="run directory (log, samples, checkpoint)")
    ap.add_argument("--list", action="store_true", help="print every task with an example and exit")
    ap.add_argument("--report", default=None, help="print the saturation order of a run directory and exit")
    ap.add_argument("--steps", type=int, default=200000)
    ap.add_argument("--batch", type=int, default=32, help="problems per step (tasks drawn uniformly)")
    ap.add_argument("--group", type=int, default=8, help="samples per problem")
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--d", type=int, default=256)
    ap.add_argument("--layers", type=int, default=4)
    ap.add_argument("--heads", type=int, default=8)
    ap.add_argument("--max-think", type=int, default=64, help="workspace cap (characters)")
    ap.add_argument("--min-think", type=int, default=16, help="workspace floor: [end-think] is blocked before this many characters")
    ap.add_argument("--think-bias", type=float, default=3.0, help="initial logit of [end-think]: 3 means ~4 characters at the start")
    ap.add_argument("--eos-bias", type=float, default=3.0, help="initial logit of [eos]")
    ap.add_argument("--think-cost", type=float, default=0.0, help="reward penalty per workspace character")
    ap.add_argument("--partial", type=float, default=0.5, help="credit for a wrong answer = this x fraction of characters right")
    ap.add_argument("--ent-answer", type=float, default=0.3, help="entropy bonus on answer tokens at the start")
    ap.add_argument("--ent-answer-final", type=float, default=0.03)
    ap.add_argument("--ent-decay", type=int, default=50000, help="steps over which the answer entropy bonus decays linearly")
    ap.add_argument("--ent-think", type=float, default=0.01, help="entropy bonus on workspace tokens")
    ap.add_argument("--ent-stop", type=float, default=0.05, help="entropy bonus on the stop-thinking decision (keeps the workspace explored)")
    ap.add_argument("--adv-norm", type=int, default=1, help="1: divide advantages by the group's reward std (+0.1)")
    ap.add_argument("--held", type=int, default=200, help="held-out problems per task")
    ap.add_argument("--eval-every", type=int, default=2000)
    ap.add_argument("--eval-n", type=int, default=64, help="held-out problems per task per eval")
    ap.add_argument("--saturate", type=float, default=0.9, help="held-out accuracy that counts as saturated")
    ap.add_argument("--log-every", type=int, default=100)
    ap.add_argument("--save-every", type=int, default=2000)
    ap.add_argument("--mb-tokens", type=int, default=32768, help="tokens per training micro-batch (rows x longest row)")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.report: report(args.report); return
    if args.list:
        r = random.Random(0)
        for t, n, fn in TASKS:
            x, y = fn(r); print(f"tier {t:2d}  {n:16s} {x:28s} -> {y}")
        return

    torch.set_num_threads(args.threads)
    dev = ("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device
    active = list(range(len(TASKS)))                 # every task, every run
    held = build_heldout(args.held, args.seed); held_in = {n: {x for x, _ in held[n]} for n in held}
    max_in = max(len(x) for v in held.values() for x, _ in v) + 4
    max_ans = max(len(y) for v in held.values() for _, y in v) + 4
    maxlen = 2 + max_in + args.max_think + 1 + max_ans + 2

    os.makedirs(args.out, exist_ok=True)
    ck = os.path.join(args.out, "ckpt.pt")
    model = GPT(maxlen, args.d, args.layers, args.heads)
    with torch.no_grad(): model.head.bias[END] = args.think_bias; model.head.bias[EOS] = args.eos_bias
    model.to(dev); opt = torch.optim.Adam(model.parameters(), lr=args.lr); start, saturated = 0, {}
    if os.path.exists(ck):
        s = torch.load(ck, map_location=dev); model.load_state_dict(s["model"]); opt.load_state_dict(s["opt"])
        start, saturated = s["step"] + 1, s["saturated"]
        print(f"resumed from step {s['step']} ({len(saturated)} tasks saturated so far)")
    else:
        json.dump(vars(args), open(os.path.join(args.out, "args.json"), "w"), indent=1)
    print(f"{len(active)} tasks, {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params, device {dev}, "
          f"max input {max_in}, max answer {max_ans}, workspace cap {args.max_think}", flush=True)
    log_f = open(os.path.join(args.out, "log.jsonl"), "a"); samp_f = open(os.path.join(args.out, "samples.jsonl"), "a")

    def evaluate(step):
        model.eval(); res, samples = {}, {}
        items = [(ti, x, y) for ti in active for x, y in held[TASKS[ti][1]][: args.eval_n]]
        for i in range(0, len(items), 1024):
            chunk = items[i : i + 1024]
            _, gen, ph, _ = generate(model, [prompt(ti, x) for ti, x, _ in chunk], True, args.max_think, max_ans, args.min_think)
            for (ti, x, y), (think, ans, n) in zip(chunk, split(gen.cpu(), ph.cpu())):
                m = res.setdefault(TASKS[ti][1], dict(acc=0.0, partial=0.0, think=0.0, n=0))
                m["acc"] += ans == y; m["partial"] += score(ans, y, 1.0); m["think"] += n; m["n"] += 1
                if len(samples.setdefault(TASKS[ti][1], [])) < 3: samples[TASKS[ti][1]].append(dict(input=x, think=think, answer=ans, target=y))
        for m in res.values():
            n = m.pop("n"); m["acc"] /= n; m["partial"] /= n; m["think"] /= n
        model.train(); return res, samples

    sync = torch.mps.synchronize if dev == "mps" else torch.cuda.synchronize if dev == "cuda" else (lambda: None)
    t0, acc_r, acc_think, acc_ent = time.time(), [], [], []
    tm = dict(data=0.0, gen=0.0, reward=0.0, update=0.0)          # seconds per phase since the last log line
    for step in range(start, args.steps + 1):
        if step % args.eval_every == 0:
            res, samples = evaluate(step)
            new = [n for n, m in res.items() if m["acc"] >= args.saturate and n not in saturated]
            for n in new: saturated[n] = step
            log_f.write(json.dumps(dict(step=step, eval=res)) + "\n"); log_f.flush()
            samp_f.write(json.dumps(dict(step=step, samples=samples)) + "\n"); samp_f.flush()
            solved = sum(m["acc"] >= args.saturate for m in res.values())
            print(f"== eval step {step}: {solved}/{len(res)} tasks saturated (>= {args.saturate:.0%} held-out), "
                  f"mean acc {sum(m['acc'] for m in res.values()) / len(res):.3f}, "
                  f"mean workspace {sum(m['think'] for m in res.values()) / len(res):.1f} chars", flush=True)
            if new:
                tier = {n: t for t, n, _ in TASKS}
                print("   SATURATED: " + ", ".join(f"{n} (tier {tier[n]}, ws '{samples[n][0]['think']}')" for n in sorted(new, key=tier.get)), flush=True)
        if step % args.save_every == 0 and step > start:
            torch.save(dict(model=model.state_dict(), opt=opt.state_dict(), step=step, saturated=saturated), ck)
        if step == args.steps: break

        ta = time.time()
        r = random.Random(args.seed * 1_000_003 + step)
        probs = []
        for _ in range(args.batch):
            ti = r.choice(active); x, y = sample_train(r, ti, held_in[TASKS[ti][1]]); probs.append((ti, x, y))
        prompts = [prompt(ti, x) for ti, x, _ in probs for _ in range(args.group)]
        tb = time.time()
        tok, gen, ph, sampled = generate(model, prompts, False, args.max_think, max_ans, args.min_think)
        sync(); tc = time.time()
        parts = split(gen.cpu(), ph.cpu())
        rew = torch.tensor([score(ans, probs[i // args.group][2], args.partial) - args.think_cost * n
                            for i, (_, ans, n) in enumerate(parts)], device=dev)
        rg = rew.view(-1, args.group); adv = rg - rg.mean(1, keepdim=True)
        if args.adv_norm: adv = adv / (rg.std(1, keepdim=True) + 0.1)   # signal on a fixed scale, even when rewards are tiny
        adv = adv.view(-1)

        sync(); td = time.time()
        c_ans = args.ent_answer_final + (args.ent_answer - args.ent_answer_final) * max(0.0, 1 - step / args.ent_decay)
        opt.zero_grad(); ent_sum, ans_n, nrows = 0.0, 0.0, gen.shape[0]
        for idx, packed, plen in packed_batches(tok, gen, args.mb_tokens):
            i = torch.tensor(idx, device=dev); Gn = min(gen.shape[1], packed.shape[1] - min(plen) + 1)
            g, p, sm = gen[i, :Gn], ph[i, :Gn], sampled[i, :Gn].float()
            lp, ent, ent_stop = policy_terms(model, packed.to(dev), plen, g, p, args.min_think)
            think_m, ans_m = sm * (p == 0), sm * (p == 1)
            loss = (-(adv[i, None] * lp * sm).sum(1) - c_ans * (ent * ans_m).sum(1) - args.ent_think * (ent * think_m).sum(1)
                    - args.ent_stop * (ent_stop * think_m).sum(1)).sum() / nrows
            loss.backward()
            ent_sum += (ent.detach() * ans_m).sum(); ans_n += ans_m.sum()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        sync(); te = time.time()
        tm["data"] += tb - ta; tm["gen"] += tc - tb; tm["reward"] += td - tc; tm["update"] += te - td

        acc_r.append(rew.mean().item()); acc_think.append(sum(p[2] for p in parts) / len(parts))
        acc_ent.append((ent_sum / max(float(ans_n), 1.0)).item() if torch.is_tensor(ent_sum) else 0.0)
        if step % args.log_every == 0:
            row = dict(step=step, reward=sum(acc_r) / len(acc_r), think=sum(acc_think) / len(acc_think),
                       ans_entropy=sum(acc_ent) / len(acc_ent), ent_coef=c_ans, sec=time.time() - t0,
                       ms_per_step={k: round(1000 * v / len(acc_r)) for k, v in tm.items()})
            log_f.write(json.dumps(row) + "\n"); log_f.flush()
            print(f"step {step:6d} {row['sec']:6.0f}s  reward {row['reward']:.3f}  workspace {row['think']:5.1f}  "
                  f"answer entropy {row['ans_entropy']:.2f} (bonus {c_ans:.3f})  "
                  f"ms/step " + " ".join(f"{k} {v}" for k, v in row["ms_per_step"].items()), flush=True)
            acc_r, acc_think, acc_ent = [], [], []; tm = dict.fromkeys(tm, 0.0)
    torch.save(dict(model=model.state_dict(), opt=opt.state_dict(), step=args.steps, saturated=saturated), ck)

if __name__ == "__main__":
    main()
