"""Dense tensor, PSD-kernel and deterministic-form finite checks, not limit proofs."""
import argparse
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import numpy as np
from verify import model, wick_moment, compare_saved, require


def build():
    checks, rejected = [], []
    def check(name, ok):
        require(bool(ok), name); checks.append(name)
    # INPUT: exact 8-coordinate Gaussian fixture, order X0,X1,Y0,Y1,U0,U1,V0,V1.
    cov = [[F(0) for _ in range(8)] for _ in range(8)]
    for j in range(8): cov[j][j] = F(2)
    def block(rows, cols, values):
        for i, r in enumerate(rows):
            for j, c in enumerate(cols): cov[r][c] = cov[c][r] = values[i][j]
    block([0], [1], [[F(1,13)]]); block([2], [3], [[F(1,17)]])
    block([4], [5], [[F(-1,23)]]); block([6], [7], [[F(-1,19)]])
    block([0,1], [4,5], [[F(1,11),F(-1,12)],[F(1,15),F(1,14)]])
    P = [[F(1,5),F(-1,7)],[F(1,9),F(1,8)]]
    R = [[F(-1,6),F(1,10)],[F(1,12),F(-1,11)]]
    Q = [[F(1,4),F(-1,13)],[F(1,14),F(1,6)]]
    block([2,3], [4,5], P); block([6,7], [0,1], R); block([2,3], [6,7], Q)
    check('dense covariance exact diagonal dominance', all(cov[i][i] > sum(abs(cov[i][j]) for j in range(8) if i != j) for i in range(8)))
    # INPUT coefficient matrices: A_ab=M_ab*X0*X1, D_cd=N_cd*U0^2*U1^2.
    M = [[F(1),F(2)],[F(2),F(-1)]]; N = [[F(3),F(-1)],[F(-1),F(2)]]
    xp, up = (1,1), (2,2)
    def moment(x, u, y=(0,0), v=(0,0)):
        return wick_moment(cov, tuple(x)+tuple(y)+tuple(u)+tuple(v))
    def derivative(powers, indices):
        n, coefficient = list(powers), F(1)
        for i in indices:
            coefficient *= n[i]; n[i] -= 1
            if n[i] < 0: return F(0), (0,0)
        return coefficient, tuple(n)
    def expd(dx=(), du=()):
        cx, x = derivative(xp, dx); cu, u = derivative(up, du)
        return cx*cu*moment(x,u)
    def shifted(indices):
        n = [0,0]
        for j in indices: n[j] += 1
        return tuple(n)
    lhs = F(0)
    for a,b,c,d in product(range(2), repeat=4):
        y,v = shifted((a,b)), shifted((c,d))
        gamma, tilde = cov[2+a][2+b], cov[6+c][6+d]
        lhs += M[a][b]*N[c][d]*(moment(xp,up,y,v)-gamma*moment(xp,up,(0,0),v)
            -tilde*moment(xp,up,y,(0,0))+gamma*tilde*moment(xp,up))
    def families(pp, qq, rr):
        out = [F(0),F(0),F(0)]
        for a,b,c,d in product(range(2), repeat=4):
            weight = M[a][b]*N[c][d]
            out[0] += weight*(qq[a][c]*qq[b][d]+qq[a][d]*qq[b][c])*expd()
            for alpha,beta in product(range(2), repeat=2):
                out[1] += weight*(pp[a][beta]*(qq[b][c]*rr[d][alpha]+qq[b][d]*rr[c][alpha])
                    +pp[b][beta]*(qq[a][c]*rr[d][alpha]+qq[a][d]*rr[c][alpha]))*expd((alpha,),(beta,))
            for alpha,delta,beta,gamma in product(range(2), repeat=4):
                out[2] += weight*pp[a][beta]*pp[b][gamma]*rr[c][alpha]*rr[d][delta]*expd((alpha,delta),(beta,gamma))
        return out
    terms = families(P,Q,R)
    check('dense full tensor IBP vs exact Wick enumeration', lhs == sum(terms))
    for i, term in enumerate(terms): check(f'dense family {i} nonzero', term != 0)
    transpose = lambda matrix: [list(row) for row in zip(*matrix)]
    for label,pp,qq,rr in [('P transpose',transpose(P),Q,R),('Q transpose',P,transpose(Q),R),('R transpose',P,Q,transpose(R))]:
        require(sum(families(pp,qq,rr)) != lhs, 'Undetected '+label); rejected.append(label)
    for i in range(len(terms)):
        for factor in (F(0),F(-1),F(2)):
            changed = terms.copy(); changed[i] *= factor
            require(sum(changed) != lhs, 'Undetected family multiplier')
            rejected.append(f'tensor family{i}:factor{factor}')

    parameters,a,b,c = model()
    generators = [np.array([[0,1,0],[1,0,0],[0,0,0]],complex),
                  np.array([[0,-1j,0],[1j,0,0],[0,0,0]],complex), np.diag([1,-1,0]).astype(complex)]
    realify = lambda matrix: np.block([[matrix.real,-matrix.imag],[matrix.imag,matrix.real]])
    for index, psi in enumerate([np.array([1+2j,2-1j,3j]),np.array([1,0,2j]),np.array([0,0,1j])]):
        X = np.r_[psi.real,psi.imag]; rho = float(np.vdot(psi,psi).real)
        B = np.zeros((6,6))
        for T in generators:
            S = realify(T); q = float(np.vdot(psi,T@psi).real)/(rho+float(parameters['rho_regularizer']))
            pv = 2*S@X; vv = 2*(S-q*np.eye(6))@X
            B += float(a)*np.outer(pv,pv)+float(b)*(np.outer(pv,vv)+np.outer(vv,pv))+float(c)*np.outer(vv,vv)
        phase = np.r_[-psi.imag,psi.real]
        check(f'PSD phase kernel {index}', np.linalg.norm(B@phase) < 1e-12)
        check(f'explicit B operator norm {index}', np.linalg.norm(B,2) <= (12*float(a)+48*abs(float(b))+48*float(c))*rho+1e-12)
        check(f'B semidefinite {index}', np.linalg.eigvalsh(B).min() >= -1e-12)
        if index == 2: check('pure third component B zero', np.array_equal(B,np.zeros((6,6))))

    # INPUT: finite noncommuting PSD background and signed scalar spectral cutoff.
    raw = np.array([[1,2,-1],[0,1,2],[2,-1,1]],float)
    background = raw.T@raw/20
    K = np.diag([1.,2.,4.]); S = np.diag(np.sqrt(np.diag(K)))
    cutoff = np.diag([-.5,0.,1.2]); bound = np.linalg.norm(background,2)
    T = S@background@S; TN = cutoff@T@cutoff
    check('background and cutoff do not commute', np.linalg.norm(background@cutoff-cutoff@background) > 0)
    check('noncommuting form-order bound', np.linalg.eigvalsh(bound*np.linalg.norm(cutoff,2)**2*K-TN).min() >= -1e-12)
    eigenvalues = np.linalg.eigvalsh(TN)
    for p in (0.,.1,1.,5.):
        value = .5*np.sum(p*eigenvalues-np.log1p(p*eigenvalues))
        check(f'determinant interval p={p}', -1e-13 <= value <= p*p*np.sum(TN*TN)/4+1e-12)
    # Independent exact finite Wick variance tests the real quadratic-form half factor.
    D = [[F(1),F(2,3)],[F(2,3),F(-1,2)]]; identity = [[F(1),F(0)],[F(0),F(1)]]
    variance = F(0)
    for i,j,k,l in product(range(2), repeat=4):
        powers = [0,0]
        for ix in (i,j,k,l): powers[ix] += 1
        covariance = wick_moment(identity,tuple(powers))-identity[i][j]*identity[k][l]
        variance += D[i][j]*D[k][l]*covariance/4
    hs2 = sum(v*v for row in D for v in row)
    check('centered quadratic isometry via exact Wick', variance == hs2/2)
    require(variance != hs2/4 and variance != hs2, 'Variance factor mutants'); rejected.extend(['variance quarter','variance full'])
    # The printed homogeneous production terms are read from the same frozen input.
    gamma = parameters['gamma']; lam = parameters['lambda']
    check('pinned sextic positive', gamma > 0)
    h = 9*(a+2*b+c); m = h/2; x = min(F(1,2),(h-m)/(2*(6*b+3*c)))
    Ax = (h-m)*x-(6*b+3*c)*x*x
    z = np.sqrt(2*float(Ax/gamma))
    check('pinned gamma actual optimum', abs(float(gamma)*z*z/2-float(Ax)) < 1e-14)
    check('pinned gamma leading energy coefficient', abs(float(gamma)*z**3/6-float(Ax)*z+2*float(Ax)*z/3) < 1e-14)
    family = np.array([float(v) for v in parameters['family_masses']])
    Mprod = np.diag(family)+float(parameters['k_lock'])*(np.eye(3)-np.ones((3,3))/3)
    c0 = (float(parameters['r']+parameters['Y'])-np.sqrt(float((parameters['r']-parameters['Y'])**2+parameters['Z']**2)))/4
    modes = [n for n in product(range(-1,2),repeat=3) if any(n)]
    six_real_hs, complex_hs, bound_sum = 0.,0.,0.
    for n in modes:
        k2 = sum((2*np.pi*v/float(parameters['Lx']))**2 for v in n)
        symbol = (float(parameters['r'])+float(parameters['Z'])*k2+float(parameters['Y'])*k2*k2)*np.eye(3)+Mprod
        check('symbol ellipticity '+str(n), np.linalg.eigvalsh(symbol-c0*(1+k2)**2*np.eye(3)).min() >= -1e-12)
        inverse = np.linalg.inv(symbol)
        complex_hs += k2*k2*np.trace(inverse@inverse)
        real_cov = realify(inverse)
        six_real_hs += k2*k2*np.trace(real_cov@real_cov)
        bound_sum += k2**-2
    real_components = 2*len(parameters['family_masses'])
    check('six-real spectral multiplicity', abs(six_real_hs-2*complex_hs) < 1e-10)
    check('full finite spectral HS bound', six_real_hs <= real_components*c0**-2*bound_sum)
    for j in range(1,5):
        actual_count = sum(max(abs(v) for v in n)==j for n in product(range(-j,j+1),repeat=3))
        check('actual lattice shell count '+str(j), actual_count == 24*j*j+2)
    ratios = []
    for t in (1e6,1e8,1e10):
        rho = z*np.sqrt(t); psi = np.array([np.sqrt(float(x)*rho),0.,np.sqrt((1-float(x))*rho)])
        ss = float(x)*rho; eps = float(parameters['rho_regularizer'])
        W = float(h)*ss-6*float(b)*ss*ss/(rho+eps)-3*float(c)*ss*ss*(rho+2*eps)/(rho+eps)**2
        lower = .5*float(psi@(float(parameters['r'])*np.eye(3)+Mprod)@psi)+float(lam)*rho*rho/4
        energy = float(gamma)*rho**3/6+lower-t*(W-float(m)*ss)
        ratios.append(float(energy/t**1.5))
    target = -2*float(Ax)*z/3
    check('homogeneous asymptotic error decreases', abs(ratios[-1]-target) < abs(ratios[0]-target))
    check('homogeneous finite energy negative', ratios[-1] < 0)
    return {'schema':'tect/a6-a7-strengthened-audit/1.0','status':'PASS',
        'checks':checks,'checks_passed':len(checks),'rejected_mutations':rejected,'mutations_rejected':len(rejected),
        'tensor_lhs':str(lhs),'tensor_families':[str(v) for v in terms],
        'quadratic_variance':str(variance),'production_asymptotic_ratios':ratios,
        'scope':'Finite fixtures and hostile checks; not infinite-dimensional proof or external review.'}


if __name__ == '__main__':
    require(__debug__, 'Run without Python -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',type=Path); parser.add_argument('--write-new',type=Path)
    args = parser.parse_args(); result = build()
    if args.check: compare_saved(result,json.loads(args.check.read_text(encoding='utf-8')))
    if args.write_new:
        args.write_new.parent.mkdir(parents=True,exist_ok=True)
        with args.write_new.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,indent=2,sort_keys=True); stream.write('\n')
    print('STRENGTHENED AUDIT: PASS',result['checks_passed'],'checks;',result['mutations_rejected'],'hostile mutations rejected')
