#!/usr/bin/env python

import multiprocessing
from ase.atoms import Atoms
try:
    print(kmc_model, dir(kmc_model))
    from kmc_model import base, lattice, proclist
except Exception, e:
    print('Could not find the kmc module. The kmc implements the actual')
    print('kmc model. This can be created from a kmos xml file using')
    print('kmos-export-program.')
    print(e)

    raise
try:
    import kmc_settings as settings
except:
    print('Could not find the settings file')
    print('The kmos_settings.py contains all changeable model parameters')
    print('and descriptions for the representation on screen.')

class KMC_Model(multiprocessing.Process):
    def __init__(self, image_queue=None,
                       parameter_queue=None,
                       signal_queue=None,
                       size=None, system_name='kmc_model'):
        super(KMC_Model, self).__init__()
        self.image_queue = image_queue
        self.parameter_queue = parameter_queue
        self.signal_queue = signal_queue
        self.size = int(settings.simulation_size) if size is None else int(size)
        proclist.init((self.size,)*int(lattice.model_dimension),
            system_name,
            lattice.default_layer,
            proclist.default_species)
        self.cell_size = np.dot(lattice.unit_cell_size, lattice.system_size)

        # prepare structures for TOF evaluation
        self.tofs = tofs = get_tof_names()
        self.tof_matrix = np.zeros((len(tofs),proclist.nr_of_proc))
        for process, tof_count in settings.tof_count.iteritems():
            process_nr = eval('proclist.%s' % process.lower())
            for tof, tof_factor in tof_count.iteritems():
                self.tof_matrix[tofs.index(tof), process_nr-1] += tof_factor

        # prepare procstat
        self.procstat = np.zeros((proclist.nr_of_proc,))
        self.time = 0.

        self.species_representation = []
        for species in sorted(settings.representations):
            if settings.representations[species].strip():
                self.species_representation.append(eval(settings.representations[species]))
            else:
                self.species_representation.append(Atoms())

        if len(settings.lattice_representation):
            self.lattice_representation = eval(
                settings.lattice_representation)[
                    lattice.default_layer]
        else:
            self.lattice_representation = Atoms()
        self.set_rate_constants(settings.parameters)

    def __del__(self):
        lattice.deallocate_system()

    def run(self):
        while True:
            for _ in xrange(50000):
                proclist.do_kmc_step()
            if not self.image_queue.full():
                atoms = self.get_atoms()
                # attach other quantities need to plot
                # to the atoms object and let it travel
                # piggy-back through the queue
                atoms.size = self.size
                self.image_queue.put(atoms)
            if not self.signal_queue.empty():
                signal = self.signal_queue.get()
                print('  ... model received %s' % signal)
                if signal.upper() == 'STOP':
                    self.terminate()
                elif signal.upper() == 'PAUSE':
                    while self.signal_queue.empty():
                        time.sleep(0.03)
                elif signal.upper() == 'RESET_TIME':
                    base.set_kmc_time(0.0)
                elif signal.upper() == 'START':
                    pass
            if not self.parameter_queue.empty():
                while not self.parameter_queue.empty():
                    parameters = self.parameter_queue.get()
                self.set_rate_constants(parameters)


    def set_rate_constants(self, parameters):
        """Tries to evaluate the supplied expression for a rate constant
        to a simple real number and sets it for the corresponding process.
        For the evaluation we draw on predefined natural constants, user defined
        parameters and mathematical functions
        """
        for proc in sorted(settings.rate_constants):
            rate_expr = settings.rate_constants[proc][0]
            rate_const = evaluate_rate_expression(rate_expr, parameters)

            try:
                base.set_rate_const(eval('proclist.%s' % proc.lower()), rate_const)
                print('%s: %.3e s^{-1}' % (proc, rate_const))
            except Exception as e:
                raise UserWarning("Could not set %s for process %s!\nException: %s" % (rate_expr, proc, e))
        print('-------------------')

    def get_atoms(self):
        atoms = ase.atoms.Atoms()
        atoms.calc = None
        atoms.set_cell(self.cell_size)
        atoms.kmc_time = base.get_kmc_time()
        atoms.kmc_step = base.get_kmc_step()
        for i in xrange(lattice.system_size[0]):
            for j in xrange(lattice.system_size[1]):
                for k in xrange(lattice.system_size[2]):
                    for n in xrange(1,1+lattice.spuck):
                        species = lattice.get_species([i,j,k,n])
                        if self.species_representation[species]:
                            atom = deepcopy(self.species_representation[species])
                            atom.translate(np.dot(lattice.unit_cell_size,
                            np.array([i,j,k]) + lattice.site_positions[n-1]))
                            atoms += atom
                    lattice_repr = deepcopy(self.lattice_representation)
                    lattice_repr.translate(np.dot(lattice.unit_cell_size,
                                np.array([i,j,k])))
                    atoms += lattice_repr

        # calculate TOF since last call
        atoms.procstat = np.zeros((proclist.nr_of_proc,))
        atoms.occupation = proclist.get_occupation()
        for i in range(proclist.nr_of_proc):
            atoms.procstat[i] = base.get_procstat(i+1)
        delta_t = (atoms.kmc_time - self.time)
        size = self.size**lattice.model_dimension
        if delta_t == 0. :
            print("Warning: numerical precision too low, to resolve time-steps")
            print('         Will reset kMC for next step')
            base.set_kmc_time(0.0)
            atoms.tof_data = np.zeros_like(self.tof_matrix[:,0])
        else:
            atoms.tof_data = np.dot(self.tof_matrix,  (atoms.procstat - self.procstat)/delta_t/size)

        # update trackers for next call
        self.procstat[:] = atoms.procstat
        self.time = atoms.kmc_time

        return atoms
