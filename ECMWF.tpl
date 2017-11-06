#!/bin/bash
#PBS -V
#PBS -N {job_name}
#PBS -j oe
#PBS -l EC_total_tasks={total_cpu}
#PBS -l EC_threads_per_task=1
#PBS -l EC_hyperthreads=1
#PBS -l EC_memory_per_task=1GB
#PBS -l walltime=00:05:00
#PBS -q np

# Initialization
set verbose
set echo

# Go into case directory
cd $PBS_O_WORKDIR/
pwd 
# Run Eulag  in case directory
aprun -n{total_cpu} -f $PBS_NODEFILE 2>&1 >{job_name}.{output_suffix} {executable} --sizex {domain_size_x} --sizey {domain_size_y} --sizez {domain_size_z} --nprocx {cpu_x} --nprocy {cpu_y} --nprocz {cpu_z} --maxiteration {timesteps}
