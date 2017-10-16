import numpy as np
from sympy import *
from generate_noisy_data import generate_noisy_data

# generate noisy experimental data for testing identifiability
y0 = np.array([5, 1, 1])
all_options_exp_1 = []
all_options_exp_2 = []
all_options_exp_3 = []
cvode_options = ['Newton', 'Adams', 1e-6, 1e-6, 100]

# experiment 1
ode_par_val_experiment_1 = np.array([.1, .1, 4e6, .1, .3, 1.1, .45, 2, .25, .2, 1, 1, 1, .1])
all_options_exp_1.append(cvode_options)
all_options_exp_1.append(ode_par_val_experiment_1)
# generate data using MWC Kinetics
_, y_nss_exp1, flux_nss_exp1, _, _, _, _, _, _ = generate_noisy_data(y0, all_options_exp_1, 1)

# experiment 2
ode_par_val_experiment_2 = np.array([.1, .1, 4e6, .1, .3, 1.1, .45, 2, .25, .2, 1, 1, 1, .5])
all_options_exp_2.append(cvode_options)
all_options_exp_2.append(ode_par_val_experiment_2)
# generate data using MWC Kinetics
_, y_nss_exp2, flux_nss_exp2, _, _, _, _, _, _ = generate_noisy_data(y0, all_options_exp_2, 1)

# experiment 3
ode_par_val_experiment_3 = np.array([.1, .1, 4e6, .1, .3, 1.1, .45, 2, .25, .2, 1, 1, 1, 1])
all_options_exp_3.append(cvode_options)
all_options_exp_3.append(ode_par_val_experiment_3)
# generate data using MWC Kinetics
_, y_nss_exp3, flux_nss_exp3, _, _, _, _, _, _ = generate_noisy_data(y0, all_options_exp_3, 1)

# experimental data based on order of inputs for lambdify expressions
exp_flux_index = np.array([0, 3, 2, 4])
experimental_data = np.hstack((ode_par_val_experiment_1[-1], y_nss_exp1, flux_nss_exp1[exp_flux_index],
                               ode_par_val_experiment_2[-1], y_nss_exp2, flux_nss_exp2[exp_flux_index],
                               ode_par_val_experiment_3[-1], y_nss_exp3, flux_nss_exp3[exp_flux_index]))

# symbolic expression for flux 3
ac1, ac2, ac3, x11, x12, x13, x21, x22, x23, x31, x32, x33, \
v31, v32, v33, v11, v12, v13, v21, v22, v23, v41, v42, v43 = \
    symbols('ac1, ac2, ac3, x11, x12, x13, x21, x22, x23, x31, x32, x33,'
            ' v31, v32, v33, v11, v12, v13, v21, v22, v23, v41, v42, v43', positive=True)
variables = [ac1, x11, x21, x31, v11, v21, v31, v41,
             ac2, x12, x22, x32, v12, v22, v32, v42,
             ac3, x13, x23, x33, v13, v23, v33, v43]

# use denominator generated from mathematica to test identifiability for all fluxes
# V3max
V3max_sol_1 = -v32*v33*x11*x12*x21 + v32*v33*x11*x13*x21 + v31*v33*x11*x12*x22 - \
              v31*v33*x12*x13*x22 - v31*v32*x11*x13*x23 + v31*v32*x12*x13*x23
v3max_fun_expression = lambdify([variables], V3max_sol_1, "numpy")
print("V3max Denominator:", v3max_fun_expression(experimental_data))

# K3fdp
K3fdp_sol_1 = -v32*v33*x11*x12*x21 + v32*v33*x11*x13*x21 + v31*v33*x11*x12*x22 - \
              v31*v33*x12*x13*x22 - v31*v32*x11*x13*x23 + v31*v32*x12*x13*x23
k3fdp_fun_expression = lambdify([variables], K3fdp_sol_1, "numpy")
print("K3fdp Denominator:", k3fdp_fun_expression(experimental_data))

# K3pep
K3pep_sol_1 = 2*(-v32*v33*x11*x21*x22 + v31*v33*x12*x21*x22 + v32*v33*x11*x21*x23 -
                 v31*v32*x13*x21*x23 - v31*v33*x12*x22*x23 + v31*v32*x13*x22*x23)
k3pep_fun_expression = lambdify([variables], K3pep_sol_1, "numpy")
print("K3pep Denominator:", k3pep_fun_expression(experimental_data))

# K3fdp_sol_2
# K3pep_sol_2
# V3max_sol_2 = -v32*v33*x11*x12*x21 + v32*v33*x11*x13*x21 + v31*v33*x11*x12*x22 - \
#               v31*v33*x12*x13*x22 - v31*v32*x11*x13*x23 + v31*v32*x12*x13*x23

# symbolic expression for flux v1 w/o enzyme concentration data
v1max_sol = -(ac2*v11 - ac1*v12)
k1ac_v1max_sol = -ac2*v11 + ac1*v12
v1max_fun_expression = lambdify([variables], v1max_sol, "numpy")
k1ac_v1max_fun_expression = lambdify([variables], k1ac_v1max_sol, "numpy")
print("V1max Denominator (No enzyme data):", v1max_fun_expression(experimental_data))
print("K1ac Denominator (No enzyme data):", k1ac_v1max_fun_expression(experimental_data))

# symbolic expression for flux v1 w/ enzyme concentration data
k1cat_sol = -(ac1*v12*x31 - ac2*v11*x32)
k1cat_fun_expression = lambdify([variables], k1cat_sol, "numpy")
print("k1cat Denominator (w/ enzyme data):", k1cat_fun_expression(experimental_data))

k1ac_sol = ac1*v12*x31 - ac2*v11*x32
k1ac_fun_expression = lambdify([variables], k1ac_sol, "numpy")
print("K1ac Denominator (w/ enzyme data):", k1ac_fun_expression(experimental_data))

# symbolic expression for flux v2
v2max_sol = v22*x21 - v21*x22
v2max_fun_expression = lambdify([variables], v2max_sol, "numpy")

k2pep_sol = v22*x21 - v21*x22
k2pep_fun_expression = lambdify([variables], k2pep_sol, "numpy")
print("K2pep Denominator:", k2pep_fun_expression(experimental_data))