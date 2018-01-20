import numpy as np
import os.path
import csv
# import scipy.linalg

# K1ac, K3fdp, L3fdp, K3pep, K2pep, vemax, Kefdp, ne, d, V4max, k1cat, V3max, V2max, ac
def_par_val = np.array([.1, .1, 4e6, .1, .3, 1.1, .45, 2, .25, .2, 1, 1, 1, .1])


def kotte_ck_flux(y, p=def_par_val):
    """calculate flux using convenience kinetics"""

    K1ac, K3fdp, L3fdp, K3pep, K2pep, vemax, Kefdp, ne, d, V4max, k1cat, V3max, V2max, ac = p

    flux_1 = k1cat * y[2] * ac / (ac + K1ac)
    flux_2 = vemax * (1 - 1 / (1 + (Kefdp / y[1]) ** ne))
    # convenience kinetics for flux 3
    fdp_sat = y[1] / K3fdp
    pep_sat = y[0] / K3pep
    nr_3 = V3max*fdp_sat
    dr_3 = 1 + fdp_sat
    regulation_activate = 1/(1 + 1/pep_sat)
    # regulation_inhibition = 1/(1 + pep_sat) # for future reference
    flux_3 = regulation_activate * nr_3/dr_3
    flux_4 = V2max * y[0] / (y[0] + K2pep)
    flux_5 = V4max * y[0]
    flux_6 = d * y[2]
    all_flux = np.hstack((flux_1, flux_2, flux_3, flux_4, flux_5, flux_6))

    return all_flux


def kotte_ck_ode(t, y, par_val):
    """ode calculation using convenience kinetics for flux 3"""

    flux = kotte_ck_flux(y, par_val)
    yd_pep = flux[0] - flux[3] - flux[4]
    yd_fdp = flux[3] - flux[2]
    yd_e = flux[1] - flux[5]

    return np.hstack((yd_pep, yd_fdp, yd_e))


def kotte_flux(y, p=def_par_val):
    """function doc_string"""

    K1ac, K3fdp, L3fdp, K3pep, K2pep, vemax, Kefdp, ne, d, V4max, k1cat, V3max, V2max, ac = p

    flux_1 = k1cat*y[2]*ac/(ac+K1ac)
    flux_2 = vemax*(1-1/(1+(Kefdp/y[1])**ne))
    fdp_sat = 1 + y[1]/K3fdp
    pep_sat = 1 + y[0]/K3pep
    flux_3 = V3max*(fdp_sat-1)*(fdp_sat)**3/(fdp_sat**4+L3fdp*(pep_sat**(-4)))
    flux_4 = V2max*y[0]/(y[0]+K2pep)
    flux_5 = V4max*y[0]
    flux_6 = d*y[2]
    all_flux = np.hstack((flux_1, flux_2, flux_3, flux_4, flux_5, flux_6))

    return all_flux


def kotte_ode(t, y, par_val):

    # K1ac, K3fdp, L3fdp, K3pep, K2pep, vemax, Kefdp, ne, d, V4max, k1cat, V3max, V2max, ac = \
    #     [.1, .1, 4e6, .1, .3, 1.1, .45, 2, .25, .2, 1, 1, 1, .1]
    # par_val = np.vstack((K1ac, K3fdp, L3fdp, K3pep, K2pep, vemax, Kefdp, ne, d, V4max, k1cat, V3max, V2max, ac))

    flux = kotte_flux(y,par_val)
    yd_pep = flux[0] - flux[3] - flux[4]
    yd_fdp = flux[3] - flux[2]
    yd_e = flux[1] - flux[5]

    return np.hstack((yd_pep, yd_fdp, yd_e))


def truncate_values(f, n=3):
    """truncates floats to n specified values after the decimal"""
    if not np.isnan(f):
        s = '{}'.format(f)  # convert float to string
        if 'e' in s or 'E' in s:
            return float('{0:.{1}f}'.format(f, n))
        i, p, d = s.partition('.')
        return float('.'.join([i, (d+'0'*n)[:n]]))
    else:
        return f


def flux_1_ident_expression(experimental_data):
    """symbolic and lambdify expression for flux 1 denominator from mathematica"""
    # get variable values (w/o sympy directly from experimental data)
    ac1, x11, x21, x31, v11, v21, v31, v41, \
    ac2, x12, x22, x32, v12, v22, v32, v42 = list(experimental_data)

    # flux numerator and denominator w/o sympy
    # symbolic expression for flux v1 w/o enzyme concentration data
    v1max_no_enzyme_numerator_value = ac1 * v11 * v12 - ac2 * v11 * v12
    v1max_no_enzyme_denominator_value = -(ac2 * v11 - ac1 * v12)
    k1ac_no_enzyme_numerator_value = ac1 * (ac2 * v11 - ac2 * v12)
    k1ac_no_enzyme_denominator_value = -ac2 * v11 + ac1 * v12

    v1max_no_enzyme_value = v1max_no_enzyme_numerator_value/v1max_no_enzyme_denominator_value
    k1ac_no_enzyme_value = k1ac_no_enzyme_numerator_value/k1ac_no_enzyme_denominator_value

    # symbolic expression for flux v1 w/ enzyme concentration data
    k1cat_enzyme_numerator_value = - ac1 * v11 * v12 + ac2 * v11 * v12
    k1cat_enzyme_denominator_value = -(ac1 * v12 * x31 - ac2 * v11 * x32)
    k1cat_enzyme_value = k1cat_enzyme_numerator_value/k1cat_enzyme_denominator_value
    k1ac_enzyme_numerator_value = ac1 * (-ac2 * v12 * x31 + ac2 * v11 * x32)
    k1ac_enzyme_denominator_value = ac1 * v12 * x31 - ac2 * v11 * x32
    k1ac_enzyme_value = k1ac_enzyme_numerator_value/k1ac_enzyme_denominator_value

    return [v1max_no_enzyme_numerator_value, v1max_no_enzyme_denominator_value, v1max_no_enzyme_value], \
           [k1ac_no_enzyme_numerator_value, k1ac_no_enzyme_denominator_value, k1ac_no_enzyme_value], \
           [k1cat_enzyme_numerator_value, k1cat_enzyme_denominator_value, k1cat_enzyme_value], \
           [k1ac_enzyme_numerator_value, k1ac_enzyme_denominator_value, k1ac_enzyme_value]


def flux_2_ident_expression(experimental_data):
    """symbolic and lambdify expression for flux 2 denominator from mathematica"""
    # get variable values (w/o sympy directly from experimental data)
    _, x21, _, x31, v11, v21, v31, v41, \
    _, x22, _, x32, v12, v22, v32, v42 = list(experimental_data)

    # symbolic expression for v2
    # V2max
    v2max_numerator_value = -v21 * v22 * x21 + v21 * v22 * x22
    v2max_denominator_value = -(v22 * x21 - v21 * x22)
    # K2pep
    k2pep_numerator_value = x21 * (v21 * x22 - v22 * x22)
    k2pep_denominator_value = v22 * x21 - v21 * x22
    v2max_value = v2max_numerator_value/v2max_denominator_value
    k2pep_value = k2pep_numerator_value/k2pep_denominator_value

    return [v2max_numerator_value, v2max_denominator_value, v2max_value], \
           [k2pep_numerator_value, k2pep_denominator_value, k2pep_value]


def flux_3_ident_expression(experimental_data):
    """symbolic and lambdify expression for flux 3 denominator from mathematica"""

    # truncate experiment values
    experimental_data = map(truncate_values, list(experimental_data))

    # get variable values (w/o sympy directly from experimental data)
    ac1, x11, x21, x31, v11, v21, v31, v41, \
    ac2, x12, x22, x32, v12, v22, v32, v42, \
    ac3, x13, x23, x33, v13, v23, v33, v43 = list(experimental_data)
    # ac = experimental_data[range(0, 24, 8)]
    # x_ranges = [range(i, 24, 8) for i in range(1, 4)]
    # all_x_ranges = [list(np.array(x_ranges)[:, i]) for i in range(0, 3)]
    # x = [experimental_data[all_x_ranges[i]] for i in range(0, 3)]
    # v_ranges = [range(i, 24, 8) for i in range(4, 8)]
    # all_v_ranges = [list(np.array(v_ranges)[:, j]) for j in range(0, 3)]
    # v = [experimental_data[all_v_ranges[j]] for j in range(0, 3)]

    # symbolic expression for v3
    # V3max
    sqrt_v3max_nr_1 = ((v31*v33*x11*x12*x21*x22 - v32*v33*x11*x12*x21*x22 - v32*v33*x11*x13*x21*x22 +
                        v31*v33*x12*x13*x21*x22 + v32*v33*x11*x12*x21*x23 - v31*v32*x11*x13*x21*x23 +
                        v32*v33*x11*x13*x21*x23 - v31*v32*x12*x13*x21*x23 - v31*v33*x11*x12*x22*x23 +
                        v31*v32*x11*x13*x22*x23 + v31*v32*x12*x13*x22*x23 - v31*v33*x12*x13*x22*x23)**2 -
                       4*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                           v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)*
                       (v31*v33*x11*x12*x13*x21*x22 - v32*v33*x11*x12*x13*x21*x22 - v31*v32*x11*x12*x13*x21*x23 +
                        v32*v33*x11*x12*x13*x21*x23 + v31*v32*x11*x12*x13*x22*x23 - v31*v33*x11*x12*x13*x22*x23))
    sqrt_v3max_nr_1 = truncate_values(sqrt_v3max_nr_1, 10)
    v3max_nr_1_value = -v31*v32*v33*x11*x12*x21 + v31*v32*v33*x11*x13*x21 + v31*v32*v33*x11*x12*x22 - \
                       v31*v32*v33*x12*x13*x22 - v31*v32*v33*x11*x13*x23 + v31*v32*v33*x12*x13*x23 - \
                      (v31*v32*v33*x12*x21*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                            v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                            v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                            v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                            v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                            v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                            np.sqrt(sqrt_v3max_nr_1)))/\
                      (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                          v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                      (v31*v32*v33*x13*x21*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                            v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                            v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                            v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                            v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                            v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                            np.sqrt(sqrt_v3max_nr_1)))/\
                      (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                          v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                      (v31*v32*v33*x11*x22*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                            v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                            v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                            v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                            v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                            v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                            np.sqrt(sqrt_v3max_nr_1)))/\
                      (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                          v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                      (v31*v32*v33*x13*x22*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                            v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                            v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                            v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                            v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                            v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                            np.sqrt(sqrt_v3max_nr_1)))/\
                      (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                          v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                      (v31*v32*v33*x11*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                            v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                            v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                            v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                            v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                            v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                            np.sqrt(sqrt_v3max_nr_1)))/\
                      (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                          v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                      (v31*v32*v33*x12*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                            v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                            v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                            v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                            v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                            v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                            np.sqrt(sqrt_v3max_nr_1)))/\
                      (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                          v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23))
    v3max_dr_1_value = -v32*v33*x11*x12*x21 + v32*v33*x11*x13*x21 + v31*v33*x11*x12*x22 -  \
                        v31*v33*x12*x13*x22 - v31*v32*x11*x13*x23 + v31*v32*x12*x13*x23
    v3max_1_value = v3max_nr_1_value/v3max_dr_1_value

    # v3max = second solution
    sqrt_v3max_nr_2 = ((v31*v33*x11*x12*x21*x22 - v32*v33*x11*x12*x21*x22 - v32*v33*x11*x13*x21*x22 +
                        v31*v33*x12*x13*x21*x22 + v32*v33*x11*x12*x21*x23 - v31*v32*x11*x13*x21*x23 +
                        v32*v33*x11*x13*x21*x23 - v31*v32*x12*x13*x21*x23 - v31*v33*x11*x12*x22*x23 +
                        v31*v32*x11*x13*x22*x23 + v31*v32*x12*x13*x22*x23 - v31*v33*x12*x13*x22*x23)**2 -
                       4*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                          v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)*
                       (v31*v33*x11*x12*x13*x21*x22 - v32*v33*x11*x12*x13*x21*x22 - v31*v32*x11*x12*x13*x21*x23 +
                        v32*v33*x11*x12*x13*x21*x23 + v31*v32*x11*x12*x13*x22*x23 - v31*v33*x11*x12*x13*x22*x23))
    sqrt_v3max_nr_2 = truncate_values(sqrt_v3max_nr_2, 10)
    v3max_nr_2_value = -v31*v32*v33*x11*x12*x21 + v31*v32*v33*x11*x13*x21 + v31*v32*v33*x11*x12*x22 - \
                        v31*v32*v33*x12*x13*x22 - v31*v32*v33*x11*x13*x23 + v31*v32*v33*x12*x13*x23 - \
                        (v31*v32*v33*x12*x21*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sqrt_v3max_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                        (v31*v32*v33*x13*x21*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sqrt_v3max_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                        (v31*v32*v33*x11*x22*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sqrt_v3max_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                        (v31*v32*v33*x13*x22*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sqrt_v3max_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                        (v31*v32*v33*x11*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sqrt_v3max_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                        (v31*v32*v33*x12*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sqrt_v3max_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23))
    v3max_dr_2_value = -v32*v33*x11*x12*x21 + v32*v33*x11*x13*x21 + v31*v33*x11*x12*x22 - \
                       v31*v33*x12*x13*x22 - v31*v32*x11*x13*x23 + v31*v32*x12*x13*x23
    v3max_2_value = v3max_nr_2_value/v3max_dr_2_value

    # K3fdp
    sq_nr_1_k3fdp = ((v31*v33*x11*x12*x21*x22 - v32*v33*x11*x12*x21*x22 - v32*v33*x11*x13*x21*x22 +
                        v31*v33*x12*x13*x21*x22 + v32*v33*x11*x12*x21*x23 - v31*v32*x11*x13*x21*x23 +
                        v32*v33*x11*x13*x21*x23 - v31*v32*x12*x13*x21*x23 - v31*v33*x11*x12*x22*x23 +
                        v31*v32*x11*x13*x22*x23 + v31*v32*x12*x13*x22*x23 - v31*v33*x12*x13*x22*x23)**2 -
                       4*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                          v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)*
                       (v31*v33*x11*x12*x13*x21*x22 - v32*v33*x11*x12*x13*x21*x22 - v31*v32*x11*x12*x13*x21*x23 +
                        v32*v33*x11*x12*x13*x21*x23 + v31*v32*x11*x12*x13*x22*x23 - v31*v33*x11*x12*x13*x22*x23))
    sq_nr_1_k3fdp = truncate_values(sq_nr_1_k3fdp, 10)
    k3fdp_nr_1_value = -v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 + v31*v32*x11*x13*x21*x23 - \
                       v32*v33*x11*x13*x21*x23 - v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 + \
                       (v32*v33*x11*x21*x22*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                              np.sqrt(sq_nr_1_k3fdp)))/\
                       (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                       (v31*v33*x12*x21*x22*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                              np.sqrt(sq_nr_1_k3fdp)))/\
                       (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                       (v32*v33*x11*x21*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                              np.sqrt(sq_nr_1_k3fdp)))/\
                       (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                           v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                       (v31*v32*x13*x21*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                              np.sqrt(sq_nr_1_k3fdp)))/\
                       (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                           v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                       (v31*v33*x12*x22*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                              np.sqrt(sq_nr_1_k3fdp)))/\
                       (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                           v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                       (v31*v32*x13*x22*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 -
                                              np.sqrt(sq_nr_1_k3fdp)))/ \
                       (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                           v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23))
    k3fdp_dr_1_value = -v32*v33*x11*x12*x21 + v32*v33*x11*x13*x21 + v31*v33*x11*x12*x22 -  \
                        v31*v33*x12*x13*x22 - v31*v32*x11*x13*x23 + v31*v32*x12*x13*x23
    k3fdp_1_value = k3fdp_nr_1_value/k3fdp_dr_1_value

    # K3fdp 2
    sq_k3fdp_nr_2 = ((v31*v33*x11*x12*x21*x22 - v32*v33*x11*x12*x21*x22 - v32*v33*x11*x13*x21*x22 +
                        v31*v33*x12*x13*x21*x22 + v32*v33*x11*x12*x21*x23 - v31*v32*x11*x13*x21*x23 +
                        v32*v33*x11*x13*x21*x23 - v31*v32*x12*x13*x21*x23 - v31*v33*x11*x12*x22*x23 +
                        v31*v32*x11*x13*x22*x23 + v31*v32*x12*x13*x22*x23 - v31*v33*x12*x13*x22*x23)**2 -
                       4*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                          v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)*
                       (v31*v33*x11*x12*x13*x21*x22 - v32*v33*x11*x12*x13*x21*x22 - v31*v32*x11*x12*x13*x21*x23 +
                        v32*v33*x11*x12*x13*x21*x23 + v31*v32*x11*x12*x13*x22*x23 - v31*v33*x11*x12*x13*x22*x23))
    sq_k3fdp_nr_2 = truncate_values(sq_k3fdp_nr_2, 10)
    k3fdp_nr_2_value = -v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 + v31*v32*x11*x13*x21*x23 - \
                        v32*v33*x11*x13*x21*x23 - v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 + \
                        (v32*v33*x11*x21*x22*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sq_k3fdp_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                        (v31*v33*x12*x21*x22*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sq_k3fdp_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                        (v32*v33*x11*x21*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sq_k3fdp_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                        (v31*v32*x13*x21*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sq_k3fdp_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) + \
                        (v31*v33*x12*x22*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sq_k3fdp_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)) - \
                        (v31*v32*x13*x22*x23*(-v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 +
                                              v32*v33*x11*x13*x21*x22 - v31*v33*x12*x13*x21*x22 -
                                              v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 -
                                              v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 +
                                              v31*v33*x11*x12*x22*x23 - v31*v32*x11*x13*x22*x23 -
                                              v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 +
                                              np.sqrt(sq_k3fdp_nr_2)))/\
                        (2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 - v31*v32*x13*x21*x23 -
                            v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23))
    k3fdp_dr_2_value = -v32*v33*x11*x12*x21 + v32*v33*x11*x13*x21 + v31*v33*x11*x12*x22 -  \
                          v31*v33*x12*x13*x22 - v31*v32*x11*x13*x23 + v31*v32*x12*x13*x23
    k3fdp_2_value = k3fdp_nr_2_value/k3fdp_dr_2_value

    # K3pep
    sq_k3pep_nr_1 = ((v31*v33*x11*x12*x21*x22 - v32*v33*x11*x12*x21*x22 - v32*v33*x11*x13*x21*x22 +
                      v31*v33*x12*x13*x21*x22 + v32*v33*x11*x12*x21*x23 - v31*v32*x11*x13*x21*x23 +
                      v32*v33*x11*x13*x21*x23 - v31*v32*x12*x13*x21*x23 - v31*v33*x11*x12*x22*x23 +
                      v31*v32*x11*x13*x22*x23 + v31*v32*x12*x13*x22*x23 - v31*v33*x12*x13*x22*x23)**2 -
                     4*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                        v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)*
                     (v31*v33*x11*x12*x13*x21*x22 - v32*v33*x11*x12*x13*x21*x22 - v31*v32*x11*x12*x13*x21*x23 +
                      v32*v33*x11*x12*x13*x21*x23 + v31*v32*x11*x12*x13*x22*x23 - v31*v33*x11*x12*x13*x22*x23))
    sq_k3pep_nr_1 = truncate_values(sq_k3pep_nr_1, 10)
    k3pep_nr_1_value = -v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 + v32*v33*x11*x13*x21*x22 - \
                        v31*v33*x12*x13*x21*x22 - v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 - \
                        v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 + v31*v33*x11*x12*x22*x23 - \
                        v31*v32*x11*x13*x22*x23 - v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 - \
                        np.sqrt(sq_k3pep_nr_1)
    k3pep_dr_1_value = 2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                             v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)
    k3pep_1_value = k3pep_nr_1_value/k3pep_dr_1_value

    sq_k3pep_nr_2 = ((v31*v33*x11*x12*x21*x22 - v32*v33*x11*x12*x21*x22 - v32*v33*x11*x13*x21*x22 +
                      v31*v33*x12*x13*x21*x22 + v32*v33*x11*x12*x21*x23 - v31*v32*x11*x13*x21*x23 +
                      v32*v33*x11*x13*x21*x23 - v31*v32*x12*x13*x21*x23 - v31*v33*x11*x12*x22*x23 +
                      v31*v32*x11*x13*x22*x23 + v31*v32*x12*x13*x22*x23 - v31*v33*x12*x13*x22*x23)**2 -
                     4*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                        v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)*
                     (v31*v33*x11*x12*x13*x21*x22 - v32*v33*x11*x12*x13*x21*x22 - v31*v32*x11*x12*x13*x21*x23 +
                      v32*v33*x11*x12*x13*x21*x23 + v31*v32*x11*x12*x13*x22*x23 - v31*v33*x11*x12*x13*x22*x23))
    sq_k3pep_nr_2 = truncate_values(sq_k3pep_nr_2, 10)
    k3pep_nr_2_value = -v31*v33*x11*x12*x21*x22 + v32*v33*x11*x12*x21*x22 + v32*v33*x11*x13*x21*x22 - \
                        v31*v33*x12*x13*x21*x22 - v32*v33*x11*x12*x21*x23 + v31*v32*x11*x13*x21*x23 - \
                        v32*v33*x11*x13*x21*x23 + v31*v32*x12*x13*x21*x23 + v31*v33*x11*x12*x22*x23 - \
                        v31*v32*x11*x13*x22*x23 - v31*v32*x12*x13*x22*x23 + v31*v33*x12*x13*x22*x23 + \
                        np.sqrt(sq_k3pep_nr_2)
    k3pep_dr_2_value = 2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                             v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)
    k3pep_2_value = k3pep_nr_2_value/k3pep_dr_2_value

    return [v3max_nr_1_value, v3max_dr_1_value, v3max_1_value], \
           [k3fdp_nr_1_value, k3fdp_dr_1_value, k3fdp_1_value], \
           [k3pep_nr_1_value, k3pep_dr_1_value, k3pep_1_value], \
           [v3max_nr_2_value, v3max_dr_2_value, v3max_2_value], \
           [k3fdp_nr_2_value, k3fdp_dr_2_value, k3fdp_2_value], \
           [k3pep_nr_2_value, k3pep_dr_2_value, k3pep_2_value]


def call_truncate_method(ident_value_list, parameter_count, expression_count=3):
    flux_ident_value = np.zeros((parameter_count, expression_count))
    for i, j in enumerate(ident_value_list):
        trunc_value = map(truncate_values, j)
        # trunc_value = map(float, trunc_value)
        flux_ident_value[i, :] = np.array(trunc_value)
    return flux_ident_value


def run_flux_ident(ident_function_list, data, flux_id=()):
    number_of_parameters = 0
    try:
        number_of_parameters_per_flux = [None] * len(ident_function_list)
    except TypeError:
        number_of_parameters_per_flux = [None]
    ident_value_list = []
    flux_id_list = []
    iterator = 0
    if not flux_id:
        flux_id = range(1, len(ident_function_list)+1)
    try:
        for func, i_d in zip(ident_function_list, flux_id):
            ident_value = func(data)
            ident_value_list.append(ident_value)
            flux_id_list.append(i_d)
            number_of_expressions = len(ident_value[0])
            number_of_parameters_per_flux[iterator] = len(ident_value)
            iterator += 1
            number_of_parameters += len(ident_value)
    except TypeError:
        ident_value = ident_function_list(data)
        ident_value_list.append(ident_value)
        flux_id_list.append(flux_id)
        number_of_expressions = len(ident_value[0])
        number_of_parameters_per_flux[iterator] = len(ident_value)
        number_of_parameters += len(ident_value)

    ident_value_array = np.zeros((number_of_parameters, number_of_expressions))
    irow = 0
    all_flux_ident = []
    for iflux in ident_value_list:
        truncated_ident_value = call_truncate_method(iflux, len(iflux))
        all_flux_ident.append(truncated_ident_value)
        nrows, ncolumns = np.shape(truncated_ident_value)
        ident_value_array[irow:(irow + nrows), :] = truncated_ident_value
        irow += nrows
    return ident_value_array, number_of_parameters_per_flux, ncolumns, all_flux_ident, flux_id_list


def get_ident_value(ident_function_list, experimental_data_list, original_data_set_id, flux_ids):
    all_data_ident_lists = []
    all_data_all_fun_ident_value = []
    try:
        number_of_parameters_per_flux = [0]*len(ident_function_list)
    except TypeError:
        number_of_parameters_per_flux = [0]
    number_of_expressions_per_parameter = 0
    for index, data_set in enumerate(experimental_data_list):
        print('Identifiability for Dataset {} of {}: Original ID: {}\n'.format(index + 1,
                                                                               len(experimental_data_list),
                                                                               original_data_set_id[index]))
        identifiability_values, number_of_parameters_per_flux, \
        number_of_expressions_per_parameter, all_fun_ident_values, flux_id_list = run_flux_ident(ident_function_list,
                                                                                                 data_set, flux_ids)
        all_data_ident_lists.append(identifiability_values)
        all_data_all_fun_ident_value.append(all_fun_ident_values)

    # classify ident data based on number of ident functions instead of by data sets
    # convert to multi dimensional list = data set size x number of parameters per flux x number of fluxes/functions
    number_of_data_sets = len(experimental_data_list)
    # all_fun_ident_list = []
    all_fun_array_list = []
    try:
        for ifun in range(0, len(ident_function_list)):
            all_ident_data_in_fun = []
            for idata in all_data_all_fun_ident_value:
                all_ident_data_in_fun.append(idata[ifun])
            # all_fun_ident_list.append(all_ident_data_in_fun)
            # array - number of data sets x number of parameters per identifiability function/flux
            ident_fun_array = np.zeros((number_of_data_sets, number_of_parameters_per_flux[ifun], 3))
            for idata_id, idata_set_value in enumerate(all_ident_data_in_fun):
                ident_fun_array[idata_id, :, 0] = idata_set_value[:, 0]
                ident_fun_array[idata_id, :, 1] = idata_set_value[:, 1]
                ident_fun_array[idata_id, :, 2] = idata_set_value[:, 2]
            all_fun_array_list.append(ident_fun_array)
    except TypeError:
        ifun = 0
        all_ident_data_in_fun = []
        for idata in all_data_all_fun_ident_value:
            all_ident_data_in_fun.append(idata[ifun])
        # all_fun_ident_list.append(all_ident_data_in_fun)
        # array - number of data sets x number of parameters per identifiability function/flux
        ident_fun_array = np.zeros((number_of_data_sets, number_of_parameters_per_flux[ifun], 3))
        for idata_id, idata_set_value in enumerate(all_ident_data_in_fun):
            ident_fun_array[idata_id, :, 0] = idata_set_value[:, 0]
            ident_fun_array[idata_id, :, 1] = idata_set_value[:, 1]
            ident_fun_array[idata_id, :, 2] = idata_set_value[:, 2]
        all_fun_array_list.append(ident_fun_array)


    total_parameters_identified = sum(number_of_parameters_per_flux)
    all_identifiability_values = \
        np.zeros((number_of_data_sets * total_parameters_identified, number_of_expressions_per_parameter))
    array_index = 0
    for idata in all_data_ident_lists:
        all_identifiability_values[array_index:(array_index + total_parameters_identified), :] = idata
        array_index += total_parameters_identified
    return all_identifiability_values, number_of_parameters_per_flux, all_fun_array_list


def ident_parameter_name(parameter_id, flux_name=()):
    parameter_list = ['V1max', 'K1ac (no enz)', 'k1cat', 'K1ac (enz)',
                      'V2max', 'K2pep',
                      'V3max (1)', 'K3fdp (1)', 'K3pep (1)',
                      'V3max (2)', 'K3fdp (2)', 'K3pep (2)']
    flux_parameter_list = {"flux1":['V1max', 'K1ac (no enz)', 'k1cat', 'K1ac (enz)'],
                           "flux2":['V2max', 'K2pep'],
                           "flux3":['V3max (1)', 'K3fdp (1)', 'K3pep (1)',
                                    'V3max (2)', 'K3fdp (2)', 'K3pep (2)']}
    if flux_name:
        try:
            parameter_name = [flux_parameter_list[name][id] for name, id in zip(flux_name, parameter_id)]
        except TypeError:
            parameter_name = flux_parameter_list[flux_name][parameter_id]
    else:
        try:
            parameter_name = [parameter_list[id] for id in parameter_id]
        except TypeError:
            parameter_name = parameter_list[parameter_id]
    return parameter_name


def flux_based_id(parameter_id):
    parameter_list = ['V1max', 'K1ac (no enz)', 'k1cat', 'K1ac (enz)',
                      'V2max', 'K2pep',
                      'V3max (1)', 'K3fdp (1)', 'K3pep (1)',
                      'V3max (2)', 'K3fdp (2)', 'K3pep (2)']
    flux_parameter_list = {"flux1": ['V1max', 'K1ac (no enz)', 'k1cat', 'K1ac (enz)'],
                           "flux2": ['V2max', 'K2pep'],
                           "flux3": ['V3max (1)', 'K3fdp (1)', 'K3pep (1)',
                                     'V3max (2)', 'K3fdp (2)', 'K3pep (2)']}
    try:
        parameter_name = [(id, parameter_list[id]) for id in parameter_id]
    except TypeError:
        parameter_name = (parameter_id, parameter_list[parameter_id])
    chosen_flux_name = []
    chosen_flux_parameter_id = []
    chosen_flux_orig_id = []
    if isinstance(parameter_name, list):
        for orig_id, j_parameter in parameter_name:
            p_boolean = []
            for flux_name in flux_parameter_list:
                boolean_existence = [True if j_parameter==parameter_k_flux else False
                                     for parameter_k_flux in flux_parameter_list[flux_name]]
                p_boolean.append(boolean_existence)
                if any(boolean_existence):
                    chosen_flux_name.append(flux_name)
                    chosen_flux_parameter_id.append([i for i, val in enumerate(boolean_existence) if val][0])
                    chosen_flux_orig_id.append(orig_id)
    else:
        for flux_name in flux_parameter_list:
            boolean_existence = [True if parameter_name[1] == parameter_k_flux else False
                                 for parameter_k_flux in flux_parameter_list[flux_name]]
            if any(boolean_existence):
                chosen_flux_name.append(flux_name)
                chosen_flux_parameter_id.append([i for i, val in enumerate(boolean_existence) if val])
                chosen_flux_orig_id.append(parameter_name[0])
    return chosen_flux_name, chosen_flux_parameter_id, chosen_flux_orig_id


def kotte_parameter_name(parameter_id):
    parameter_list = ['K1ac', 'K3fdp', 'L3fdp', 'K3pep',
                      'K2pep', 'vemax', 'Kefdp', 'ne', 'd',
                      'V4max', 'k1cat', 'V3max', 'V2max', 'ac']
    try:
        return [parameter_list[id] for id in parameter_id]
    except TypeError:
        return parameter_list[parameter_id]


def kotte_experiment_type_name(experiment_id):
    experiment_type_name_list = ['wildtype acetate', 'acetate perturbation', 'k1cat perturbation',
                                 'V3max perturbation', 'V2max perturbation']
    try:
        return [experiment_type_name_list[index] for index in experiment_id]
    except TypeError:
        return experiment_type_name_list[experiment_id]


def experiment_name(experiment_id, experiment_details):
    try:
        parameter_changed = kotte_parameter_name([int(experiment_details["indices"][i, 0]) for i in experiment_id])
        parameter_value = [experiment_details["indices"][i, 1] for i in experiment_id]
    except TypeError:
        parameter_changed = kotte_parameter_name(int(experiment_details["indices"][experiment_id, 0]))
        parameter_value = experiment_details["indices"][experiment_id, 1]
    experiment_name_list = ['{} changes {}'.format(j_p_change, j_p_value)
                            for j_p_change, j_p_value in zip(parameter_changed, parameter_value)]
    return experiment_name_list


def process_ident_data(ident_values, number_data):
    # create signed boolean array for identifiability
    signed_ident_values = np.sign(ident_values)
    ident_fun_val = []
    for id in range(0, number_data):
        ident_fun_val.append(signed_ident_values[id * 12:(id + 1) * 12, -1])
    p_list = [[p_id for p_id, val in enumerate(data_set) if val > 0] for data_set in ident_fun_val]
    p_list_boolean = [[True if parameter_id in list_1 else False for parameter_id in range(0, 12)] for list_1 in p_list]
    return p_list, np.array(p_list_boolean)


def boolean_ident_info(ident_values, number_of_parameters):
    signed_ident_values = np.sign(ident_values)
    p_list = [[p_id for p_id, val in enumerate(data_set) if val > 0] for data_set in signed_ident_values]
    p_list_boolean = [[True if parameter_id in list_1 else False for parameter_id in range(0, number_of_parameters)]
                      for list_1 in p_list]
    return p_list, np.array(p_list_boolean)


def create_data_for_file(ident_details, number_fluxes, fp_list, data_list):
    """create data for write/append all data to file"""
    number_data, p = ident_details["boolean"].shape
    write_2_file_data = []
    write_2_file_data.append(['Identifiable Perturbations'])
    flux_id, parameter_id, i = 1, 1, 0
    # perturbation_keys = parameter_list.keys()
    while i < p:
        write_2_file_data.append(['Flux {}, Parameter {}'.format(flux_id, parameter_id)])
        key_id = 'flux{}p{}'.format(flux_id, parameter_id)
        write_2_file_data.append(fp_list[key_id])
        if parameter_id < ident_details["parameters"][flux_id - 1]:
            parameter_id += 1
        else:
            if flux_id < number_fluxes:
                flux_id += 1
            else:
                flux_id = 1
            parameter_id = 1
        i += 1
    for j in range(0, number_data):
        write_2_file_data.append(['Parameters Identified by Data set {}'.format(j + 1)])
        key_id = 'dataset{}'.format(j + 1)
        write_2_file_data.append(data_list[key_id])
        # write_2_file_data.append(['Parameter Perturbations in Data Set {}'.format(j+1)])
        # write_2_file_data.append(perturbation_list[key_id])
    return write_2_file_data


def write_results_2_file(ident_details, number_fluxes, fp_list, data_list):
    write_2_file_data = create_data_for_file(ident_details, number_fluxes, fp_list, data_list)
    # write results to file
    path = "~" + "shyam" + r"\Documents\Courses\CHE1125Project\Results\ident\python2\kotte_ident_results.txt"
    fullpath = os.path.expanduser(path)
    with open(fullpath, 'a') as fh:
       writer = csv.writer(fh, delimiter="\t")
       [writer.writerow(r) for r in write_2_file_data]
       fh.close()
    return None


    # dataset dependent classification of parameters
    # data_list = data_based_processing(ident_details)

    # most useful dataset - based on number of parameter identified
    # max_data = get_most_useful_dataset(ident_details["boolean"])


    # choose additional data sets and consequently, experiments (if possible) to identify other parameters not
    # identified by chosen data set(s)
    # new_combos = calculate_experiment_combos(ident_details, experiment_details, perturbation_details, data_list)


def one_sample_ident_fun(ident_fun_list, sample_data, choose, flux_ids):
    if choose:
        try:
            chosen_values = list(sample_data["values"][:choose, :])
        except TypeError:
            iter_chosen_value = []
            for indexes in range(0, len(choose)):
                iter_chosen_value.append(list(sample_data["values"][indexes, :]))
            chosen_values = iter_chosen_value[:]
    else:
        chosen_values = list(sample_data["values"][:, :])
    # run identification function through every chosen data combination supplied as input
    _, parameters_per_flux, all_fun_array_list = get_ident_value(ident_fun_list, chosen_values, choose, flux_ids)
    return parameters_per_flux, all_fun_array_list


def multi_sample_ident_fun(ident_fun_list, all_data, choose, flux_ids):
    all_sample_ident_details = []
    for i_sample, sample_data in enumerate(all_data):
        parameters_per_flux, one_sample_all_fun_array_list = one_sample_ident_fun(ident_fun_list, sample_data,
                                                                                  choose, flux_ids)
        # process info from each sample (number of samples > 1 when noisy data is used) of experimental data sets
        all_fun_ident_details = []
        for ifun, ifun_data in enumerate(one_sample_all_fun_array_list):
            number_of_data_sets, number_of_parameters, _ = ifun_data.shape
            # process denominator info only
            _, plist_boolean = boolean_ident_info(ifun_data[:, :, -1], number_of_parameters)
            ident_details = {"boolean": plist_boolean,
                             "values": ifun_data,
                             "parameters": number_of_parameters,
                             "flux id": flux_ids[ifun]}
            all_fun_ident_details.append(ident_details)
        all_sample_ident_details.append(all_fun_ident_details)
    return all_sample_ident_details


def flux_ident_2_data_combination(all_data, flux_ids, choose=()):
    """perform identifiability separately for each set of functions and generate separate identifiability info"""
    # 2 data combination ident list
    ident_fun_2_data = (flux_1_ident_expression, flux_2_ident_expression)
    all_sample_all_fun_ident_info = multi_sample_ident_fun(ident_fun_2_data, all_data, choose, flux_ids)
    return all_sample_all_fun_ident_info


def flux_ident_3_data_combination(all_data, flux_ids, choose=()):
    """perform identifiability separately for each set of functions and generate separate identifiability info"""
    # 3 data combination ident list
    ident_fun_3_data = (flux_3_ident_expression)
    all_sample_all_fun_ident_info = multi_sample_ident_fun(ident_fun_3_data, all_data, choose, flux_ids)
    return all_sample_all_fun_ident_info


def establish_kotte_flux_identifiability(all_data, choose=()):
    """call all identifiability evaluation funcs above and print numerical results"""
    # identifiability function list
    ident_fun_list = (flux_1_ident_expression, flux_2_ident_expression, flux_3_ident_expression)

    all_sample_ident_details = []
    for i_sample, sample_data in enumerate(all_data):
        if choose:
            try:
                chosen_values = list(sample_data["values"][:choose, :])
            except TypeError:
                iter_chosen_value = []
                for indexes in range(0, len(choose)):
                    iter_chosen_value.append(list(sample_data["values"][indexes, :]))
                chosen_values = iter_chosen_value[:]
        else:
            chosen_values = list(sample_data["values"][:, :])
        # chosen_details = all_data["details"][0:choose, :]

        # number_fluxes = len(ident_fun_list)
        number_data = len(chosen_values)
        ident_values, parameters_per_flux, all_fun_array_list = get_ident_value(ident_fun_list, chosen_values, choose)

        # process identifiability data
        _, plist_boolean = process_ident_data(ident_values, number_data)
        ident_details = {"boolean": plist_boolean, "values": ident_values, "parameters": parameters_per_flux}

        # flux_name, parameter_id = return_flux_based_id([5])
        # parameter_name = ident_parameter_name(parameter_id, flux_name)
        all_sample_ident_details.append(ident_details)

    return all_sample_ident_details


def select_experiment_for_dataset(experiment_id):
    return None

def loop_through_experiments(experiments_per_dataset, total_experiments):
    chosen_ids = [0]
    for experiment in experiments_per_dataset:

        pass
    experimental_data = []
    return experimental_data
