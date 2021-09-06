#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 14:01:55 2021

@author: baris
"""


from pydentate import net_tunedrev, neuron_tools
from grid_model_new import grid_simulate
import shelve
import copy
import time
import numpy as np
import scipy.stats as stats
from pydentate_integrate_new import granule_simulate

start = time.time()

"""Setup"""
neuron_tools.load_compiled_mechanisms(path='/home/baris/pydentate/mechs/x86_64/libnrnmech.so')


"""Parameters"""
grid_seeds = [1,2]

# trajectories = [75]  # In cm
# trajectories = [74.5]
# trajectories = [74]
# trajectories = [73.5]
# trajectories = [73]
# trajectories = [72.5]
# trajectories = [72]
# trajectories = [71]
# trajectories = [70]
# trajectories = [69]
# trajectories = [68]
# trajectories = [67]
# trajectories = [66]
# trajectories = [65]
trajectories = [60]

p = 100*trajectories[0]-5000
poisson_seeds = np.arange(p,p+20,1)
poisson_seeds = list(poisson_seeds)


# shuffling = "non-shuffled"
shuffling = "shuffled"
# poisson_reseeding = True  # Controls seeding between trajectories
speed_cm = 20
dur_ms = 2000
rate_scale = 5
n_grid = 200
pp_weight = 9e-4
network_type = 'tuned'

parameters = {}
parameters = {'dur_ms': dur_ms,
              'pp_weight': pp_weight,
              'speed': speed_cm,
              'n_grid': n_grid,
              'rate_scale': rate_scale,
              'poisson_seeds': poisson_seeds}

print('grid', grid_seeds, 'poiss', poisson_seeds, 'traj', trajectories, 'dur', dur_ms)


for grid_seed in grid_seeds:
    output_path = f'{grid_seed}_{trajectories}_{poisson_seeds[0]}-{poisson_seeds[-1]}_{dur_ms}'
    storage = shelve.open(
        '/home/baris/results/grid-seed_trajectory_poisson-seeds_duration_shuffling_tuning_' + 
        output_path + '_' + shuffling + '_' + network_type, writeback=True)
    # storage = {'grid_spikes': {},
    #            'granule_spikes': {}}
    grid_spikes, _ = grid_simulate(trajs=trajectories,
                                            dur_ms=dur_ms,
                                            grid_seed=grid_seed,
                                            poiss_seeds=poisson_seeds,
                                            shuffle=shuffling,
                                            n_grid=n_grid,
                                            speed_cm=speed_cm,
                                            rate_scale=rate_scale)

    granule_spikes = {}
    for traj in trajectories:
        granule_spikes[traj] = {}
        for poisson_seed in poisson_seeds:
            granule_spikes[traj][poisson_seed] = {}
            granule_spikes_poiss = granule_simulate(grid_spikes[traj][poisson_seed],
                                              trajectory=traj,
                                              dur_ms=dur_ms, 
                                              poisson_seed=poisson_seed, 
                                              network_type=network_type, 
                                              grid_seed=grid_seed, 
                                              pp_weight=pp_weight)
            # grid_spikes[traj][poisson_seed] = grid_spikes_poiss[traj][poisson_seed]
            granule_spikes[traj][poisson_seed] = granule_spikes_poiss

    storage['grid_spikes'] = copy.deepcopy(grid_spikes)
    storage['granule_spikes'] = copy.deepcopy(granule_spikes)
    storage['parameters'] = parameters

storage.close()


output_name = f'{grid_seed}_{dur_ms}'
storage_path = '/home/baris/results/grid-seed_duration_shuffling_tuning_'
storage_name =  storage_path +  output_name + '_' + shuffling + '_' + network_type
collective_storage = shelve.open(storage_name, writeback=True)
traj_key = str(traj)
collective_storage[traj_key] = {}
collective_storage[traj_key]['grid_spikes'] = copy.deepcopy(grid_spikes[traj])
collective_storage[traj_key]['granule_spikes'] = copy.deepcopy(granule_spikes[traj])
collective_storage[traj_key]['parameters'] = parameters

collective_storage.close()

# "grid_seed_poisson_seed_reseeding-True"


stop = time.time()
time_sec = stop-start
time_min = time_sec/60
time_hour = time_min/60
print('time, ', time_sec, ' sec, ', time_min, ' min, ', time_hour, 'hour  ')