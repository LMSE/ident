import numpy as np
import itertools as it


def parameter_based_processing(ident_details):
    """parameter-based classification of experimental datasets"""
    number_data, p = ident_details["boolean"].shape
    # p = np.cumsum([0] + parameters_per_flux).tolist()
    fp_list_keys = ['flux{}p{}'.format(f_index + 1, p_index + 1)
                    for f_index, p_limit in enumerate(ident_details["parameters"])
                    for p_index in range(0, p_limit)]
    fp_list_values = [[data_id for data_id in it.compress(range(0, number_data), list(ident_details["boolean"][:, parameter_id]))]
                      for parameter_id in range(0, p)]
    fp_list = dict(zip(fp_list_keys, fp_list_values))
    return fp_list


def data_based_processing(ident_details):
    """dataset dependent classification of parameters"""
    number_data, p = ident_details["boolean"].shape
    data_list_keys = ['dataset{}'.format(perturbation_id + 1) for perturbation_id in range(0, number_data)]
    data_list_values = [[parameter_id for parameter_id in it.compress(range(0, p), list(ident_details["boolean"][data_id, :]))]
                        for data_id in range(0, number_data)]
    data_list = dict(zip(data_list_keys, data_list_values))
    return data_list


def process_ident_data(ident_values, number_data):
    # create signed boolean array for identifiability
    signed_ident_values = np.sign(ident_values)
    ident_fun_val = []
    for id in range(0, number_data):
        ident_fun_val.append(signed_ident_values[id * 12:(id + 1) * 12, -1])
    p_list = [[p_id for p_id, val in enumerate(data_set) if val > 0] for data_set in ident_fun_val]
    p_list_boolean = [[True if parameter_id in list_1 else False for parameter_id in range(0, 12)] for list_1 in p_list]
    return p_list, np.array(p_list_boolean)


def get_all_indices(mother_list, value):
    current_value_id = []
    for i in it.compress(range(0, len(mother_list)),
                         [True if j_id == value else False for j_id in mother_list]):
        current_value_id.append(i)
    return current_value_id


def get_most_useful_dataset(ident_boolean_array):
    """get data identifying most parameters (most useful data set)"""
    # most useful dataset - based on number of parameter identified
    number_data, number_parameter = ident_boolean_array.shape
    identified_parameters = []  # np.zeros((number_data, 1))
    for idata in range(0, number_data):
        ip = [p_id for p_id in it.compress(range(0, number_parameter), ident_boolean_array[idata, :])]
        identified_parameters.append(len(ip))

    # get data identifying most parameters (most useful data set)
    max_useful_data = max(identified_parameters)
    max_data_id = get_all_indices(identified_parameters, max_useful_data)
    max_data = {"maximum": max_useful_data,
                "id": max_data_id,
                "parameters": identified_parameters}
    return max_data


def get_useful_data_info(ident_boolean_array, experiment_details, perturbation_details, data_needed):
    """get info all data sets that identify maximum number of parameters"""
    _, p = ident_boolean_array.shape
    # data_needed = max_data["id"]
    parameters_identified_by_max_data_id = []
    # get parameters identified by data_needed
    data_needed_id = 0
    for data_id in data_needed:
        # data_set_name = 'option {}'.format(data_needed_id + 1)
        # data_set_ident = [ident_parameter_name(i)
        #                   for i in it.compress(range(0, p), list(ident_boolean_array[data_id, :]))]
        data_set_ident_id = [i for i in it.compress(range(0, p), list(ident_boolean_array[data_id, :]))]
        # identify all experiments for given data set
        #perturbation_id = [int(i) for i in experiment_details["details"][data_id, range(0, 12, 4)].tolist()]
        perturbation_id = experiment_details["experiment_id"][data_id]
        # identify parameters perturbed by said experiment
        # perturbed_parameters = perturbation_details["indices"][perturbation_id, :]
        # perturbed_parameters = experiment_details["parameter_ids"][data_id]
        # get parameter names from parameter indices
        # perturbed_parameter_name = [(model_parameter_name(int(j[0])), j[1]) for j in perturbed_parameters.tolist()]
        info = {'id': data_id, 'parameter_ids':data_set_ident_id,
                'experiment_id':perturbation_id, 'ssid':experiment_details["ssid"][data_id]}
        parameters_identified_by_max_data_id.append(info)
        data_needed_id += 1
    #data_list = dict(parameters_identified_by_max_data_id)
    return parameters_identified_by_max_data_id


def get_additional_data(ident_details, experiment_details, perturbation_details, unidentified_parameter_ids):
    """find data sets that identify parameters in unidentified set"""
    number_data, p = ident_details["boolean"].shape
    # get boolean for unidentified parameters
    unident_boolean = ident_details["boolean"][:, unidentified_parameter_ids]
    # work on this later
    # max_data = get_most_useful_dataset(unident_boolean)
    # if max_data["maximum"] > 1:
    #    selected_data_id = max_data["id"]
    #else:

    # get every single data set that identifies unidentified parameters
    data_ident = [[k for k in it.compress(range(0, number_data), list(unident_boolean[:, unid_p]))]
                  for unid_p in range(0, len(unidentified_parameter_ids))]
    # get other info for data sets in this list
    extra_data_details = []
    for list_elements in data_ident:
        if list_elements:
            data_list = get_useful_data_info(ident_details["boolean"],
                                             experiment_details,
                                             perturbation_details,
                                             list_elements)
            for dictionary in data_list:
                extra_data_details.append(dictionary)
        else:
            extra_data_details.append({})



    # collect common data ids in data_ident
    #for j_data_ident in data_ident:
    #for i_data in range(0, number_data):
    #   unidentifiable_parameters = [k for k in it.compress(range(0, p), list(np.logical_not(ident_details["boolean"][i_data, :])))]

    #    identified_parameters = [i for i in it.compress(range(0, p), list(ident_details["boolean"][i_data, :]))]
    #    identifiable_parameter_boolean = [True if un_id in identified_parameters
    #                                      else False
    #                                      for un_id in unidentified_parameter_ids]
    #    if any(identifiable_parameter_boolean):
    #        identifiable_parameter = [j
    #                                  for j in it.compress(unidentified_parameter_ids, identifiable_parameter_boolean)]
    #        extra_data_details.append({'data':i_data, 'parameter':identifiable_parameter})
    return extra_data_details


def calculate_experiment_combos(ident_details, experiment_details, perturbation_details, data_list):
    """choose additional data sets and consequently, experiments (if possible) to identify other parameters not
    identified by chosen data set(s)"""
    # get parameters identified by chosen data set
    number_data, p = ident_details["boolean"].shape
    new_combos = []
    new_combo_number = 0
    for chosen_data in data_list:
        # chosen_data = data_list[option_id]
        data_set_id = chosen_data["id"]
        # get parameters identified
        identified_parameters = [i for i in it.compress(range(0, p), list(ident_details["boolean"][data_set_id, :]))]
        # get unidentified parameters
        nonidentified_parameters = list(set(range(0, p)) - set(identified_parameters))

        # go through all data sets to identify indexes that identify unidentified parameters
        extra_data = get_additional_data(ident_details,
                                         experiment_details,
                                         perturbation_details,
                                         nonidentified_parameters)
        for extra_id, dict_id in enumerate(extra_data):
            if dict_id:
                new_option_name = 'combination {}'.format(new_combo_number + 1)
                new_option_composition = [chosen_data["id"], dict_id["id"]]
                new_option_experiment_id = [chosen_data["experiment_id"], dict_id["experiment_id"]]
                new_option_ssid = [chosen_data["ssid"], dict_id["ssid"]]
                new_options_parameter_ids = \
                    list(set(chosen_data["parameter_ids"]) | set(dict_id["parameter_ids"]))
                combo_info = {'id': new_option_composition, 'parameter_ids': new_options_parameter_ids,
                              'experiment_ids': new_option_experiment_id,
                              'ssid': new_option_ssid}
                new_combos.append(combo_info)
                new_combo_number += 1
    return new_combos


def get_top_useful_data(max_data):
    number_parameters_ided = max_data["parameters"]
    maximum_val = max(number_parameters_ided)
    all_current_values = []
    all_data_id = []
    current_value = maximum_val
    while current_value >= min(number_parameters_ided):
        current_value_id = get_all_indices(number_parameters_ided, current_value)
        all_data_id.append(current_value_id)
        all_current_values.append(current_value)
        current_value -= 1
    return all_current_values, all_data_id


def data_usefulness_percentage(ident_details):
    """get percentage of data identifying n, n-1, n-2, ... number of parameters. n is the maximum number of
    parameters identified by a data set"""
    number_data, _ = ident_details["boolean"].shape
    # most useful dataset - based on number of parameter identified
    max_data = get_most_useful_dataset(ident_details["boolean"])

    # get top n, n-1, n-2, .... parameters identifying data sets
    number_parameters_identified, data_id = get_top_useful_data(max_data)

    # percentage of datasets identifying x number of parameters
    percentage_of_total = []
    for i, j_parameter_identified in enumerate(number_parameters_identified):
        number_data_identifying_j = len(data_id[i])
        percentage_of_total.append(float(number_data_identifying_j) / float(number_data) * 100)
    data_usefulness = {'number_parameters_ided': number_parameters_identified,
                       'index': data_id,
                       'percentage': percentage_of_total}
    return data_usefulness


def flux_parameter_plot_data(original_data, case=1):
    all_boolean_p_id = []
    for len_pos, i_list in enumerate(original_data):
        for i_data in i_list:
            boolean_p_id = [True if j_p in i_data["parameter_ids"] else False for j_p in range(0, 12)]
            all_boolean_p_id.append(boolean_p_id)
    number_data, number_p = np.array(all_boolean_p_id).shape
    all_boolean_p_id = [list(j_p) for j_p in np.transpose(np.array(all_boolean_p_id))]
    if case == 1:
        # get total data identifying each parameter
        all_boolean_p_id_sum = [sum(j_list) for j_list in all_boolean_p_id]
        all_boolean_p_id_fraction = [float(sum(j_list))*100/number_data for j_list in all_boolean_p_id]
        return all_boolean_p_id_sum, all_boolean_p_id_fraction, all_boolean_p_id
    elif case == 2:
        all_boolean_e_id = []
        for len_pos, i_list in enumerate(original_data):
            for i_data in i_list:
                # experiments done
                boolean_e_id = [True if j_p in i_data["experiment_id"] else False for j_p in range(0, 18)]
                all_boolean_e_id.append(boolean_e_id)
        # all_boolean_e_id = [list(j_p) for j_p in np.transpose(np.array(all_boolean_e_id))]
        # get total for each experiment in each identifying data set
        # all_boolean_e_id = [sum(k_list) for k_list in all_boolean_e_id]
        return all_boolean_p_id, all_boolean_e_id
    else:
        return []


def parameter_plot_data_per_sample(original_data, case=1):
    number_of_samples = len(original_data)
    all_sample_total_p = []
    all_sample_fraction_p = []
    all_sample_all_p_boolean = []
    for i_sample_ident_data in original_data:
        total_p, fraction_p, all_p_boolean = flux_parameter_plot_data(i_sample_ident_data, case)
        all_sample_total_p.append(total_p)
        all_sample_fraction_p.append(fraction_p)
        all_sample_all_p_boolean.append(all_p_boolean)

    # collect data from all samples and calculate means and standard deviations for each parameter
    all_sample_total_means = list(np.mean(np.array(all_sample_total_p), axis=0))
    all_sample_total_std = list(np.std(np.array(all_sample_total_p), axis=0))
    all_sample_fraction_means = list(np.mean(np.array(all_sample_fraction_p), axis=0))
    all_sample_fraction_std = list(np.std(np.array(all_sample_fraction_p), axis=0))
    all_sample_totals = {'means': all_sample_total_means, 'std': all_sample_total_std}
    all_sample_fractions = {'means': all_sample_fraction_means, 'std': all_sample_fraction_std}
    for j_sample in range(0, number_of_samples):
        pass
    return all_sample_totals, all_sample_fractions, all_sample_all_p_boolean


def dataset_with_experiment(data_exp, exp_id):
    # get datasets in which experiment exp_id is used
    # number_data = len(data_exp)
    try:
        lst_data_id = [[j_data for j_data, j_expt_used in enumerate(data_exp) if k_exp_id in j_expt_used]
                       for k_exp_id in exp_id]
    except TypeError:
        lst_data_id = [j_data for j_data, j_expt_used in enumerate(data_exp) if exp_id in j_expt_used]
    # covert boolean array to list
    # data_exp_boolean = data_exp["boolean"]
    # lst_parameter = [list(j_p) for j_p in list(np.transpose(data_exp_boolean))]
    # data_id = [[id for id, val in enumerate(lst_parameter[j_p]) if val] for j_p in range(0, 12)]
    # try:
    #     data_with_exp = [[k_p_set for k_p_id, k_p_set in enumerate(data_id) if k_p_id == j_exp_id] for j_exp_id in exp_id]
    # except TypeError:
    #     data_with_exp = [k_p_set for k_p_id, k_p_set in enumerate(data_id) if k_p_id == exp_id]
    return lst_data_id


def experiments_in_ident_data(data_p_boolean, data_exp, exp_types, data_id):
    """get all data sets that identify parameter j and get different types of experiments in these data sets"""
    number_of_experiments_per_data = 3
    number_exp_types = len(exp_types)
    data_identifying_p = []
    exp_data_parameter_info = []
    for j_p, data_set_boolean in enumerate(data_p_boolean):
        data_identifying_parameter_j = [j_data for j_data, value in enumerate(data_set_boolean) if value]
        data_identifying_p.append(data_identifying_parameter_j)
        chosen_data_experiments = [j_data_set for data_set_id, j_data_set in enumerate(data_exp["experiment_id"])
                                   if data_set_id in data_identifying_parameter_j]
        chosen_data_experiments = np.array(chosen_data_experiments)
        # get number of experiments of each type at each position
        exp_types_classification = []
        for i_exp_type in exp_types:
            try:
                pos_based_lst = [[chosen_data_experiments[:, iexp] == np.array(j_exp_id) for j_exp_id in i_exp_type]
                                 for iexp in range(0, number_of_experiments_per_data)]
            except IndexError:
                pos_based_lst = []
            exp_types_classification.append(pos_based_lst)
        # get experiment type numbers and percentages within data set at each position
        total_identifying_experiments = chosen_data_experiments.shape[0]
        counter_exp_type = 0
        print('Parameter {}'.format(j_p))
        exp_type_all_pos_info = []
        for j_exp_type, exp_id in zip(exp_types_classification, exp_types):
            all_exp_types_info = []
            for i_pos, i_exp_pos in enumerate(j_exp_type):
                all_pos_info = []
                # print('Experiment Position in Data sets {}'.format(i_pos))
                for k_exp_at_i_exp_pos_in_j_exp_type, k_exp in zip(i_exp_pos, exp_id):
                    total_number_of_k_exp_at_i_pos_in_j_exp_type = sum(k_exp_at_i_exp_pos_in_j_exp_type)
                    percentage_of_k_exp_at_i_pos_in_j_exp_type = \
                        float(sum(k_exp_at_i_exp_pos_in_j_exp_type))/float(total_identifying_experiments)
                    info = {'type':counter_exp_type, 'id':k_exp,
                            'occurrence':total_number_of_k_exp_at_i_pos_in_j_exp_type,
                            'occurrence percentage':percentage_of_k_exp_at_i_pos_in_j_exp_type,
                            'position':i_pos}
                    all_pos_info.append(info)
                    pass
                # all_pos_info.append(all_pos_info)
                all_exp_types_info.append(all_pos_info)
            counter_exp_type += 1
            exp_type_all_pos_info.append(all_exp_types_info)
        exp_data_parameter_info.append(exp_type_all_pos_info)
    return exp_data_parameter_info


def experiments_per_sample_for_ident(all_sample_p_boolean, data_exp, exp_types, data_id):
    """cycle through each sample of data sets to identify different experiments in
    each data set identifying each experiment"""
    number_of_samples = len(all_sample_p_boolean)
    all_sample_exp_parameter_info = []
    for j_sample, j_sample_boolean in enumerate(all_sample_p_boolean):
        exp_data_parameter_info = experiments_in_ident_data(j_sample_boolean, data_exp[j_sample], exp_types, data_id)
        all_sample_exp_parameter_info.append(exp_data_parameter_info)
    return all_sample_exp_parameter_info


def experiment_position_based_info(experiments_identifying_each_parameter, number_of_experiments_per_data=3):
    all_parameter_position_based_info = []
    for p_parameter, p_info in enumerate(experiments_identifying_each_parameter):
        all_pos_ids = []
        all_pos_occurrence = []
        all_pos_total_occurrence = []
        all_pos_occurrence_percentage = []
        all_pos_total_occurrence_percentage = []
        for j_pos in range(0, number_of_experiments_per_data):
            j_pos_ids = []
            j_pos_occurrence = []
            j_pos_total_occurrence = []
            j_pos_occurrence_percentage = []
            j_pos_total_occurrence_percentage = []
            for i_exp_type, i_type_info in enumerate(p_info):
                try:
                    type_based_info = i_type_info[j_pos]
                except IndexError:
                    type_based_info = i_type_info
                j_pos_ids.append([j_type_info["id"]
                                  for j_type_info in type_based_info])
                j_pos_occurrence.append([j_type_info["occurrence"]
                                         for j_type_info in type_based_info])
                j_pos_total_occurrence.append(sum([j_type_info["occurrence"]
                                                   for j_type_info in type_based_info]))
                j_pos_occurrence_percentage.append([j_type_info["occurrence percentage"]
                                                    for j_type_info in type_based_info])
                j_pos_total_occurrence_percentage.append(sum([j_type_info["occurrence percentage"]
                                                              for j_type_info in type_based_info]))
            all_pos_ids.append(j_pos_ids)
            all_pos_occurrence.append(j_pos_occurrence)
            all_pos_total_occurrence.append(j_pos_total_occurrence)
            all_pos_occurrence_percentage.append(j_pos_occurrence_percentage)
            all_pos_total_occurrence_percentage.append(j_pos_total_occurrence_percentage)
        all_parameter_position_based_info.append({"id": all_pos_ids,
                                                  "occurrence": all_pos_occurrence,
                                                  "occurrence percentage": all_pos_occurrence_percentage,
                                                  "occurrence total": all_pos_total_occurrence,
                                                  "occurrence total percentage": all_pos_total_occurrence_percentage})

    return all_parameter_position_based_info


def experiment_position_based_info_per_sample(experiments_identifying_each_parameter, number_of_experiments_per_data=3):
    number_of_samples = len(experiments_identifying_each_parameter)
    for j_sample_exp in experiments_identifying_each_parameter:
        all_parameter_position_based_info = \
            experiment_position_based_info(j_sample_exp, number_of_experiments_per_data)
        pass
    return None


def experiment_type_based_info(experiments_identifying_each_parameter):
    all_parameter_type_based_info = []
    for p_parameter, p_info in enumerate(experiments_identifying_each_parameter):
        all_exp_type = []
        for i_exp_type, i_type_info in enumerate(p_info):
            all_pos = []
            for j_pos, j_pos_info in enumerate(i_type_info):
                all_ids = [iter_j_pos_info["id"] for iter_j_pos_info in j_pos_info]
                all_occurrence = [iter_j_pos_info["occurrence"] for iter_j_pos_info in j_pos_info]
                all_occurrence_percentage = [iter_j_pos_info["occurrence percentage"] for iter_j_pos_info in j_pos_info]
                all_type = [iter_j_pos_info["type"] for iter_j_pos_info in j_pos_info]
                if all([True if type_iter == i_exp_type else False for type_iter in all_type]):
                    all_type = i_exp_type
                all_position = [iter_j_pos_info["position"] for iter_j_pos_info in j_pos_info]
                if all([True if pos_iter == j_pos else False for pos_iter in all_position]):
                    all_position = j_pos
                all_pos.append({"id": all_ids, "occurrence": all_occurrence,
                                "occurrence percentage": all_occurrence_percentage,
                                "type": all_type,
                                "position": all_position})
                pass
            all_exp_type.append(all_pos)
        all_parameter_type_based_info.append(all_exp_type)

    return all_parameter_type_based_info


def data_for_plots(original_data, case=1):
    if case==1:
        all_boolean_p_id = []
        for len_pos, i_list in enumerate(original_data):
            for i_data in i_list:
                boolean_p_id = [True if j_p in i_data["parameter_ids"] else False for j_p in range(0, 12)]
                all_boolean_p_id.append(boolean_p_id)
        all_boolean_p_id = [list(j_p) for j_p in np.transpose(np.array(all_boolean_p_id))]
        # get total data identifying each parameter
        all_boolean_p_id = [sum(j_list) for j_list in all_boolean_p_id]
        return all_boolean_p_id
    elif case==2:
        all_boolean_p_id = []
        all_boolean_e_id = []
        all_boolean_e_pos_id = []
        for len_pos, i_list in enumerate(original_data):
            for i_data in i_list:
                # parameters identified
                boolean_p_id = [True if j_p in i_data["parameter_ids"] else False for j_p in range(0, 12)]
                all_boolean_p_id.append(boolean_p_id)
                # experiments done
                boolean_e_id = [True if j_p in i_data["experiment_id"] else False for j_p in range(0, 18)]
                all_boolean_e_id.append(boolean_e_id)
                # experiments done based on position in data set
                boolean_e_pos_id = [[True if j_p == i_data["experiment_id"][j_pos] else False
                                     for j_p in range(0, 18)]
                                    for j_pos in range(0, 3)]
                all_boolean_e_pos_id.append(boolean_e_pos_id)

        # get each part in a 3 part experiment separately
        all_seg_data = []
        for iseg in range(0, 3):
            iseg_data = []
            for idata in all_boolean_e_pos_id:
                iseg_data.append(idata[iseg])
            all_seg_data.append(iseg_data)

        all_segment_experiment_data = []
        for jseg in range(0, len(all_seg_data)):
            exp_seg_id = []
            data_seg_id = []
            exp_seg_p_id = []
            for data_set_index, value in enumerate(all_seg_data[jseg]):
                exp_seg_id.append([j_exp for j_exp, bool_value in enumerate(value) if bool_value][0])
                data_seg_id.append(data_set_index)
                exp_seg_p_id.append([k_p for k_p, bool_val in enumerate(all_boolean_p_id[data_set_index]) if bool_val])
            complete_info = {'experiment_id':exp_seg_id,
                             'data_id':data_seg_id,
                             'parameter_id':exp_seg_p_id}
            all_segment_experiment_data.append(complete_info)



        all_boolean_p_id = [list(k_p) for k_p in np.transpose(np.array(all_boolean_p_id))]

        # get experiment-parameter relationship
        boolean_p_id_array = np.array(all_boolean_p_id)
        boolean_e_id_array = np.array(all_boolean_e_id)
        all_data_set_for_exp = []
        # get data sets for each experiment
        for i_exp in range(0, 18):
            data_set_for_exp = [i for i, val in enumerate(list(boolean_e_id_array[:, i_exp])) if val]
            # parameters identified by each data set in data_set_exp
            parameter_data_exp = [j for j, val in enumerate(list(boolean_p_id_array[:, data_set_for_exp]))]



        # all_boolean_e_id = [list(j_p) for j_p in np.transpose(np.array(all_boolean_e_id))]
        # get total for each experiment in each identifying data set
        # all_boolean_e_id = [sum(k_list) for k_list in all_boolean_e_id]
        return all_boolean_p_id, all_boolean_e_id
    else:
        return []


def useful_experiments(original_data):
    """get most and least useful experiments based on identifiable and non-identifiable datasets"""
    all_boolean_p_id, all_boolean_e_id = data_for_plots(original_data, 2)
    all_parameter_exp_id = []
    for j_p in all_boolean_p_id:
        # get data set for each parameter
        data_id = [i for i, val in enumerate(j_p) if val]
        # get experiments for data in data_id
        exp_id = [[j for j, val in enumerate(all_boolean_e_id[i]) if val] for i in data_id]
        exp_id = np.array(exp_id)
        exp_lst = []
        try:
            for j_exp in range(0, exp_id.shape[1]):
                exp_lst.append(list(np.unique(exp_id[:, j_exp])))
        except IndexError:
            for _ in range(0, 3):
                exp_lst.append([])
        all_exp_total_per_pos = []
        for i_pos, k_exp_pos in enumerate(exp_lst):
            total_each_exp_per_pos = []
            for exp_number in k_exp_pos:
                y = sum([[True if exp_number == i else False for i in j][i_pos] for j in exp_id])
                total_each_exp_per_pos.append(y)
            all_exp_total_per_pos.append(total_each_exp_per_pos)
        all_parameter_exp_id.append({'unique': exp_lst,
                                     'occurrence': all_exp_total_per_pos})

    # classify data based on experiments - get parameters identified by each experiment
    number_experiment_required = 3
    exp_used_pos = [[] for _ in xrange(number_experiment_required)]
    for len_pos, i_list in enumerate(original_data):
        for i_data in i_list:
            parameter_ided = i_data["parameter_ids"]
            experiments_used = i_data["experiment_id"]

            p_ided = i_data["parameter_ids"]

    return all_parameter_exp_id


def process_info(ident_details, experiment_details, perturbation_details):
    print("Process information From Identifiability Analysis.....\n")
    number_data, p = ident_details["boolean"].shape

    # get data identification percentages to classify utility of data sets
    data_usefulness = data_usefulness_percentage(ident_details)

    # get info all the aforementioned data sets
    original_data = []
    combination_data = []
    for i_data in range(0, len(data_usefulness["number_parameters_ided"])):
        # get all info on all data sets present in useful data from above
        temp_list = get_useful_data_info(ident_details["boolean"],
                                         experiment_details,
                                         perturbation_details,
                                         data_usefulness["index"][i_data])
        original_data.append(temp_list)

        # choose additional data sets and consequently, experiments (if possible) to identify other parameters not
        # identified by chosen data set(s)
        new_combos = calculate_experiment_combos(ident_details,
                                                 experiment_details,
                                                 perturbation_details,
                                                 temp_list)
        combination_data.append(new_combos)

    # print total individual data sets required and combinations found
    number_original_data = 0
    number_combination_data = 0
    for list_pos, i_data in enumerate(original_data):
        # original data sets
        print('Original Data sets that can detect {} parameters: {}'.
              format(data_usefulness["number_parameters_ided"][list_pos], len(i_data)))
        number_original_data += len(i_data)
        # combination data sets
        print('Combination Data sets for more parameters: {}'.format(len(combination_data[list_pos])))
        number_combination_data += len(combination_data[list_pos])

    # decide which experiments to perform for each parameter based on above calculations

    # most easily identifieable parameter - based on frequency of identification
    identifying_data = [] # np.zeros((number_parameter, 1))
    for iparameter in range(0, p):
        idata = [data_id for data_id in it.compress(range(0, number_data), ident_details["boolean"][:, iparameter])]
        identifying_data.append(len(idata))

    # get parameters identified by most data sets (most identifiable parameter)
    max_identified = max(identifying_data)
    max_parameter_id = [identifying_data.index(max(identifying_data))]
    for iparameter, number_identifying_data in enumerate(identifying_data):
        if number_identifying_data == max_identified and iparameter not in max_parameter_id:
            max_parameter_id.append(iparameter)
        elif number_identifying_data > max_identified:
            max_identified = number_identifying_data
            max_parameter_id = [iparameter]
    max_parameter = {"maximum": max_identified,
                     "id": max_parameter_id,
                     "data": identifying_data}
    # ident_parameter_names = ident_parameter_name(range(0, 12))
    print("Information Processing Complete\n")
    return data_usefulness, original_data, combination_data, max_parameter


def process_info_sample(ident_details, experiment_details, perturbation_details):
    number_of_samples = len(ident_details)
    all_sample_data_list = []
    all_sample_original_data = []
    all_sample_combo_data = []
    all_sample_max_parameter = []
    for j_sample, j_sample_ident_details in enumerate(ident_details):
        print("Processing identifiability data for sample {}".format(j_sample))
        data_list, original_ident_data, combo_ident_data, max_parameter = \
            process_info(j_sample_ident_details, experiment_details[j_sample], perturbation_details)
        all_sample_data_list.append(data_list)
        all_sample_original_data.append(original_ident_data)
        all_sample_combo_data.append(combo_ident_data)
        all_sample_max_parameter.append(max_parameter)
    return all_sample_data_list, all_sample_original_data, all_sample_combo_data, all_sample_max_parameter
