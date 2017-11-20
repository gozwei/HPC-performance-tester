#!/bin/bash
#PBS -l nodes={nodes}:ppn={ppn}
#PBS -l walltime=01:00:00
##PBS -m abe
#PBS -N {job_name}
##PBS -j oe
#PBS -q batch

# Initialization
set verbose
set echo

# Go into case directory
cd $PBS_O_WORKDIR/

# Run Eulag  in case directory
echo "START: {job_name}" > {job_name}.{output_suffix}
# RUN
echo "{job_id}" >> {job_name}.{output_suffix}
mpirun -n {total_cpu} -f $PBS_NODEFILE 2>&1 >> {job_name}.{output_suffix} {executable} --sizex {domain_size_x} --sizey {domain_size_y} --sizez {domain_size_z} --nprocx {cpu_x} --nprocy {cpu_y} --nprocz {cpu_z} --maxiteration {timesteps}
