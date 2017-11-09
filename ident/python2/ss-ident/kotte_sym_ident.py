import numpy as np
from generate_noisy_data import generate_noisy_data
from generate_noisy_data import run_noisy_parameter_perturbation
from kotte_model import establish_kotte_flux_identifiability
from kotte_model import arrange_experimental_data

# generate noisy experimental data for testing identifiability
y0 = np.array([5, 1, 1])
all_options_exp_1 = []
all_options_exp_2 = []
all_options_exp_3 = []
# default parameter values
cvode_options = ('Newton', 'Adams', 1e-8, 1e-8, 100)
ode_paramater_values = np.array([.1, .1, 4e6, .1, .3, 1.1, .45, 2, .25, .2, 1, 1, 1, .1])

# get initial noisy system steady state
initial_options = (cvode_options, ode_paramater_values)
noisy_initial_ss, _, _, _ = generate_noisy_data(y0, initial_options, 1)

# all parameter perturbations
parameter_perturbation = [(14, 0), (14, 4), (14, 9),
                          (11, .1), (11, .5), (11, 1), (11, -.1), (11, -.5),
                          (12, .1), (12, .5), (12, 1), (12, -.1), (12, -.5),
                          (13, .1), (13, .5), (13, 1), (13, -.1), (13, -.5)]
perturbation_options = {'ode_parameters':ode_paramater_values, 'cvode_options':cvode_options}
noisy_ss, noisy_dynamic, perturbed_parameter_values = \
    run_noisy_parameter_perturbation(parameter_perturbation, noisy_initial_ss[0], perturbation_options)

noisy_exp_xss = []
noisy_exp_fss = []
for ss_values in noisy_ss:
    noisy_exp_xss.append(ss_values[0])
    noisy_exp_fss.append(ss_values[1])

# experimental data based on order of inputs for lambdify expressions
exp_flux_index = np.array([0, 3, 2, 4])
# get combinations of experimental datasets
experimental_datasets = \
    arrange_experimental_data(noisy_exp_xss, noisy_exp_fss, perturbed_parameter_values, exp_flux_index)

# identifiability for all kotte fluxes
perturbation_list, identifiability_value_signs = establish_kotte_flux_identifiability(experimental_datasets[0:10])
print('Perturbations allowing identifiability:\n')
print 'Flux 1 Parameter 1\n{}\nFlux 1 Parameter 2\n{}\nFlux 1 Parameter 3\n{}\nFlux 1 Parameter 4\n{}\n'.\
    format(perturbation_list[0][0], perturbation_list[0][1], perturbation_list[0][2], perturbation_list[0][3])
print 'Flux 2 Parameter 1\n{}\nFlux 2 Parameter 2\n{}\n'.format(perturbation_list[1][0], perturbation_list[1][1])
print 'Flux 3 Parameter 1\n{}\nFlux 3 Parameter 2\n{}\nFlux 3 Parameter 3\n{}\n' \
      'Flux 3 Parameter 4\n{}\nFlux 3 Parameter 5\n{}\nFlux 3 Parameter 6\n{}\n'.\
    format(perturbation_list[2][0], perturbation_list[2][1], perturbation_list[2][2],
           perturbation_list[2][3], perturbation_list[2][4], perturbation_list[2][5])
#print('Flux 1 Identifiability:\n')
#for index in range(1, 100):
#    print flux1[0][index, :], flux1[1][index, :], flux1[2][index, :]
#print('Flux 2 Identifiability:\n')
#for index in range(1, 100):
#    print flux2[0][index, :], flux2[1][index, :], flux2[2][index, :]
#print('Flux 3 Identifiability:\n')
#for index in range(1, 100):
#    print flux3[0][index, :], flux3[1][index, :], flux3[2][index, :]

# clear workspace (removes all module names and objects)
# import sys
# sys.modules[__name__].__dict__.clear()