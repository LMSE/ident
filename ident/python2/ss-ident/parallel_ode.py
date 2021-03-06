from mpi4py import MPI
from mpi_master_slave import Master, Slave
from mpi_master_slave import WorkQueue
from simulate_ode import simulate_ode
import numpy as np


class ParallelOde(object):
    """Class running multiple ode simulations by assigning jobs to different slaves
    until all the work is done"""

    def __init__(self, slaves):
        # when creating the Master we tell it what slaves it can handle
        self.master = Master(slaves)
        # WorkQueue is a convenient class that run slaves on a tasks queue
        self.work_queue = WorkQueue(self.master)

    def terminate_slaves(self):
        """
        Call this to make all slaves exit their run loop
        """
        self.master.terminate_slaves()

    def __add_next_task(self, ode_rhs_fun, flux_fun, t_final, parameters, ode_opts, initial_value=(), value_id=()):
        """
        create tasks and add it to the work queue
        Every task has specific arguments
        """
        # set ode rhs function, initial condition and parameters
        data = {'ode_fun': ode_rhs_fun, 'y0': initial_value, 'id': value_id,
                'ode_sys_opts': parameters, 'ode_opts': ode_opts,
                't_final': t_final, 'flux_fun': flux_fun}
        # add data to work queue
        self.work_queue.add_work(data)

    def run_i_value(self, ode_rhs_fun, flux_fun, ode_sys_opts, initial_values, t_final, ode_opts, experiment_id):
        """
        This is the core where I keep starting slaves
        as long as there is work to do
        """

        # let's prepare our work queue. This can be built at initialization time
        # but it can also be added later as more work become available
        #
        for j_experiment_id, j_value in zip(experiment_id, initial_values):
            self.__add_next_task(ode_rhs_fun=ode_rhs_fun, flux_fun=flux_fun, t_final=t_final, parameters=ode_sys_opts, ode_opts=ode_opts,
                                 initial_value=j_value, value_id=j_experiment_id)

        # Keeep starting slaves as long as there is work to do
        all_boolean = []
        all_tout = []
        all_yout = []
        all_y0_id = []
        while not self.work_queue.done():
            # give more work to do to each idle slave (if any)
            self.work_queue.do_work()
            # reclaim returned data from completed slaves
            for slave_return_data in self.work_queue.get_completed_work():
                y0_id, done, time_course, y_result = slave_return_data
                # import pdb; pdb.set_trace()
                all_boolean.append(done)
                all_tout.append(time_course)
                all_yout.append(y_result)
                all_y0_id.append(y0_id)

                if done:
                    print('Master: slave finished its task returning: %s)' % str(y0_id))
            # sleep some time
            # time.sleep(0.3)
        results = {'time': all_tout, 'y': all_yout, 'id': all_y0_id, 'boolean': all_boolean}
        return results

    def run_i_parameter(self, ode_rhs_fun, flux_fun, ode_sys_opts, initial_value, t_final, ode_opts, experiment_id):
        """
        This is the core where I keep starting slaves
        as long as there is work to do
        """
        # let's prepare our work queue. This can be built at initialization time
        # but it can also be added later as more work become available
        #
        for j_experiment_id, j_parameter in zip(experiment_id, ode_sys_opts):
            self.__add_next_task(ode_rhs_fun=ode_rhs_fun, flux_fun=flux_fun, t_final=t_final, parameters=j_parameter, ode_opts=ode_opts,
                                 initial_value=initial_value, value_id=j_experiment_id)

        # Keeep starting slaves as long as there is work to do
        all_boolean = []
        all_tout = []
        all_yout = []
        all_y0_id = []
        all_flux = []
        while not self.work_queue.done():
            # give more work to do to each idle slave (if any)
            self.work_queue.do_work()
            # reclaim returned data from completed slaves
            for slave_return_data in self.work_queue.get_completed_work():
                y0_id, done, time_course, y_result, flux = slave_return_data
                # import pdb; pdb.set_trace()
                all_boolean.append(done)
                all_tout.append(time_course)
                all_yout.append(y_result)
                all_y0_id.append(y0_id)
                all_flux.append(flux)

                if done:
                    print('Master: slave finished its task returning: %s)' % str(y0_id))
            # sleep some time
            # time.sleep(0.3)
        results = {'time': all_tout, 'y': all_yout, 'id': all_y0_id, 'boolean': all_boolean, 'flux': all_flux}
        return results


class MySlave(Slave):
    """
    A slave process extends Slave class, overrides the 'do_work' method
    and calls 'Slave.run'. The Master will do the rest
    In this example we have different tasks but instead of creating a Slave for
    each type of taks we create only one class that can handle any type of work.
    This avoids having idle processes if, at certain times of the execution, there
    is only a particular type of work to do but the Master doesn't have the right
    slave for that task.
    """

    def __init__(self):
        super(MySlave, self).__init__()

    def do_work(self, data):
        """do work method overrides Slave.do_work() and defines work
        to be done by every slave"""
        # boolean variable set to determine whether work on slave was completed on not
        done = False

        # define explicit assimulo problem
        rhs_fun = data['ode_fun']
        y_initial = data['y0']
        y0_id = data['id']
        ode_opts = data['ode_opts']
        ode_sys_opts = data['ode_sys_opts']
        t_final = data['t_final']
        all_options = [ode_opts, ode_sys_opts]
        time_course, y_result, _, _ = simulate_ode(rhs_fun, y_initial, tf=t_final, opts=all_options)

        # calculate flux
        flux_fun = data['flux_fun']
        flux = np.array(list(map(lambda x: flux_fun(x, ode_sys_opts), y_result)))

        rank = MPI.COMM_WORLD.Get_rank()
        name = MPI.Get_processor_name()

        print('  Slave %s rank %d executing task %s' % (name, rank, y0_id))

        if len(time_course) and len(y_result):
            done = True

        if done:
            return y0_id, done, time_course, y_result, flux
        else:
            return y0_id, done, [], [], []


def setup_parallel_ode(ode_rhs_fun, flux_fun, parameters, y0, t_final, experiment_id, ode_opts=(),
                       i_value_opt=1, parameter_opt=0):
    if not ode_opts:
        ode_opts = {'iter': 'Newton', 'discr': 'Adams', 'atol': 1e-10, 'rtol': 1e-10,
                    'time_points': 200, 'display_progress': True, 'verbosity': 30}
    name = MPI.Get_processor_name()
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()

    sim_result = {}
    print('I am  %s rank %d (total %d)' % (name, rank, size))
    if rank == 0:  # Master
        ode_job = ParallelOde(slaves=range(1, size))
        # import pdb;pdb.set_trace()
        if i_value_opt:
            sim_result = ode_job.run_i_value(ode_rhs_fun=ode_rhs_fun, flux_fun=flux_fun, t_final=t_final, ode_sys_opts=parameters,
                                             ode_opts=ode_opts, initial_values=y0, experiment_id=experiment_id)
        elif parameter_opt:
            sim_result = ode_job.run_i_parameter(ode_rhs_fun=ode_rhs_fun, flux_fun=flux_fun, t_final=t_final, ode_sys_opts=parameters,
                                                 ode_opts=ode_opts, initial_value=y0, experiment_id=experiment_id)
        ode_job.terminate_slaves()
    else:  # Any slave
        MySlave().run()

    # rearrange results based on order of parameters/initial values
    # import pdb;pdb.set_trace()
    return sim_result
