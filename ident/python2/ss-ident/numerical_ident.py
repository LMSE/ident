import casadi as casadi


def v3_ck_numerical_problem(chosen_data):
    """fun to calculate objectives and constraints for numerical identification of v3
    using convenience kinetics"""

    number_data = len(chosen_data)
    # symbolic variables for use with casadi
    v3max = casadi.SX.sym("v3max")
    k3fdp = casadi.SX.sym("k3fdp")
    k3pep = casadi.SX.sym("k3pep")
    error = casadi.SX.sym("error", number_data)

    all_constraints = []
    for i_data_id, i_data in enumerate(chosen_data):
        _, pep, fdp, _, _, _, v3, _, _, _ = list(i_data)

        # flux equation for each experiment i_data in chosen_data
        fdp_sat = fdp / k3fdp
        pep_sat = pep / k3pep
        nr_3 = v3max * fdp_sat
        dr_3 = 1 + fdp_sat
        regulation_activate = 1 / (1 + 1 / pep_sat)
        flux_3 = regulation_activate * nr_3 / dr_3
        # formulate constraint for each experimental data set
        all_constraints.append(flux_3 - v3 - error[i_data_id])

    # create casadi array of constraints
    constraints = casadi.vertcat(*all_constraints)

    # create complete casadi objective fun
    objective = error[0]**2
    for i_error_id in range(1, number_data):
        objective += error[i_error_id]**2

    # get complete set of all optimization variables vertcat([parameters, error])
    x = casadi.vertcat(*[v3max, k3fdp, k3pep, error])

    nlp = {'x': x, 'f': objective, 'g': constraints}

    return nlp


def v3_numerical_problem(chosen_data):
    """fun to calculate objectives and constraints for numerical identification of v3
        using MWC kinetics"""

    number_data = len(chosen_data)
    # symbolic variables for use with casadi
    v3max = casadi.SX.sym("v3max")
    k3fdp = casadi.SX.sym("k3fdp")
    k3pep = casadi.SX.sym("k3pep")
    l3fdp = casadi.SX.sym("l3fdp")
    error = casadi.SX.sym("error", number_data)

    # fdp_sat = 1 + y[1] / K3fdp
    # pep_sat = 1 + y[0] / K3pep
    # flux_3 = V3max * (fdp_sat - 1) * (fdp_sat ** 3) / (fdp_sat ** 4 + L3fdp * (pep_sat ** (-4)))

    all_constraints = []
    for i_data_id, i_data in enumerate(chosen_data):
        _, pep, fdp, _, _, _, v3, _, _, _ = list(i_data)

        # flux equation for each experiment i_data in chosen_data
        fdp_sat = 1 + fdp / k3fdp
        pep_sat = 1 + pep / k3pep
        nr_3 = v3max * (fdp_sat - 1) * (fdp_sat**3)
        dr_3 = (fdp_sat ** 4 + l3fdp * 1e6 * pep_sat ** (-4))
        flux_3 = nr_3 / dr_3
        # formulate constraint for each experimental data set
        all_constraints.append(flux_3 - v3 - error[i_data_id])

    # create casadi array of constraints
    constraints = casadi.vertcat(*all_constraints)

    # create complete casadi objective fun
    objective = error[0] ** 2
    for i_error_id in range(1, number_data):
        objective += error[i_error_id] ** 2

    # get complete set of all optimization variables vertcat([parameters, error])
    x = casadi.vertcat(*[v3max, k3fdp, k3pep, l3fdp, error])

    nlp = {'x': x, 'f': objective, 'g': constraints}

    return nlp


def solve_numerical_nlp(chosen_fun, chosen_data, opt_problem_details, optim_options={}):
    """solve nlp for determining parameter values numerically"""
    # formulate nlp
    nlp = chosen_fun(chosen_data)

    # NLP solver options
    if optim_options:
        solver = optim_options["solver"]
        opts = optim_options["opts"]
    else:
        solver = "ipopt"
        opts = {"ipopt.tol": 1e-12}
        # solver = "sqpmethod"
        # opts = {"qpsol": "qpoases"}

    # Allocate an NLP solver and buffer
    solver = casadi.nlpsol("solver", solver, nlp, opts)

    # Solve the problem
    res = solver(**opt_problem_details)

    # Print the optimal cost
    print("optimal cost: ", float(res["f"]))

    # Print the optimal solution
    xopt = res["x"]
    print("optimal solution: ", xopt)
    print("dual solution (x) = ", res["lam_x"])
    print("dual solution (g) = ", res["lam_g"])

    return res


def identify_all_data_sets(experimental_data, chosen_fun, x0, optim_options={}):
    if chosen_fun == 0:
        ident_fun = v3_ck_numerical_problem
        # Initial condition
        arg = {"lbx": 6 * [0],
               "ubx": [2, 1, 1, .1, .1, .1],
               "lbg": 3 * [0],
               "ubg": 3 * [0]}
    elif chosen_fun == 1:
        ident_fun = v3_numerical_problem
        arg = {"lbx": 8 * [0],
               "ubx": [2, 1, 1, 5, .1, .1, .1, .1],
               "lbg": 4 * [0],
               "ubg": 4 * [0]}
    else:
        ident_fun = []
        arg = {}
    arg["x0"] = x0

    number_data_sets = len(experimental_data)
    all_data_solutions = []
    for i_data_id, i_data in enumerate(experimental_data):
        print("Performing Identifiability Analysis on Data set {} of {}".format(i_data_id+1, number_data_sets))
        if ident_fun:
            sol = solve_numerical_nlp(chosen_fun=ident_fun, chosen_data=i_data, opt_problem_details=arg,
                                      optim_options=optim_options)
        else:
            sol = []
        all_data_solutions.append(sol)
        print("Identifiability analysis on data set {} of {} complete".format(i_data_id+1, number_data_sets))
    return all_data_solutions
