#!/bin/bash
#SBATCH --account=slmet
#SBATCH --nodes={nodes}
#SBATCH --ntasks={total_cpu}
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=8
#SBATCH --output={job_name}.{output_suffix}
#SBATCH --error={job_name}.{output_suffix}
#SBATCH --time=00:14:59
#SBATCH --partition=dc-cpu-devel

# Initialization

UCX_LOG_LEVEL=error
export UCX_LOG_LEVEL
export OMP_NUM_THREADS=8
# Run Eulag  in case directory
echo "START: {job_name}" > {job_name}.{output_suffix}
# RUN
echo "{job_id}" >> {job_name}.{output_suffix}
read -s -t 2
srun --hint=multithread --distribution=*:*:cyclic -n {total_cpu} {executable} --sizex {domain_size_x} --sizey {domain_size_y} --sizez {domain_size_z} --nprocx {cpu_x} --nprocy {cpu_y} --nprocz {cpu_z} --maxiteration {timesteps}
