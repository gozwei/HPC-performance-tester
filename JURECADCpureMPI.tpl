#!/bin/bash
#SBATCH --account=slmet
#SBATCH --nodes={nodes}
#SBATCH --ntasks={total_cpu}
##SBATCH --ntasks-per-node={ppn}
#SBATCH --cpus-per-task=1
#SBATCH --output={job_name}.{output_suffix}
#SBATCH --error={job_name}.{output_suffix}
#SBATCH --time=00:14:59
#SBATCH --partition=dc-cpu-devel

# Initialization

UCX_LOG_LEVEL=error
export UCX_LOG_LEVEL
export OMP_NUM_THREADS=1
# Run Eulag  in case directory
echo "START: {job_name}" > {job_name}.{output_suffix}
# RUN
echo "{job_id}" >> {job_name}.{output_suffix}
read -s -t 2
srun --hint=nomultithread  {executable} --sizex {domain_size_x} --sizey {domain_size_y} --sizez {domain_size_z} --nprocx {cpu_x} --nprocy {cpu_y} --nprocz {cpu_z} --maxiteration {timesteps}
