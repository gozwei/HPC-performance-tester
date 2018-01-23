import numpy
import subprocess
import sys
import os.path

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def printc(msg, color='black', end='\n'):
	s = ''
	e = ''
	if color == 'blue':
		s = bcolors.BOLD + bcolors.OKBLUE
		e = bcolors.ENDC
	elif color == 'violet':
		s = bcolors.BOLD + bcolors.HEADER
		e = bcolors.ENDC
	elif color == 'green':
		s = bcolors.BOLD + bcolors.OKGREEN
		e = bcolors.ENDC
	elif color == 'red':
		s = bcolors.BOLD + bcolors.FAIL
		e = bcolors.ENDC
	elif color == 'yellow':
		s = bcolors.BOLD + bcolors.WARNING
		e = bcolors.ENDC
	sys.stdout.write('{0}{1}{2}{3}'.format(s,msg,e,end))

def run(cmd, quiet=False):
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out, err = p.communicate()
	if not quiet:
		print(out.decode("utf-8").replace("\\n", "\n").strip())
		print(err.decode("utf-8").replace("\\n", "\n").strip())
	return (out, err)

def RemoveMultipleSpaces(str):
	while "  " in str:
		str = str.replace("  ", " ");
	return str

def GetStatsForTimer(J,name):
	if not os.path.isfile(J.output_file):
		return 0
	with open(J.output_file, 'r') as f:
		for line in f:
			line = line.strip()
			if name in line:
				stats = RemoveMultipleSpaces(line).split()
				if len(stats) == 7:
					return stats
	return 1


class Job():
	def __init__(self, domain_size=[32, 32, 32], cpus=[2, 2, 2], timesteps=1000, output_suffix='out', executable='', job_exec=''):
		self.domain_size = domain_size
		self.cpus = cpus
		self.timesteps = timesteps
		self.output_suffix = output_suffix
		self.job_name = "E.{0}.{1}.{2}.{3}.{4}.{5}.{6}.{7}".format(job_exec, self.domain_size[0], self.domain_size[1], self.domain_size[2], self.cpus[0], self.cpus[1], self.cpus[2], self.timesteps)

		self.total_cpu = numpy.prod(self.cpus)
		self.ppn = 20
		self.nodes = int(numpy.ceil(float(self.total_cpu)/float(self.ppn)))

		self.submit_file = "{0}.submit.sh".format(self.job_name)
		self.output_file = "{0}.{1}".format(self.job_name, self.output_suffix)

		self.timers_results = dict()
		self.executable = executable

	def MakeSubmit(self, template, part="all", mode="w", alternative_name=""):
		F = dict()
		F["executable"]		= self.executable
		F["nodes"] 			= self.nodes
		F["ppn"] 			= self.ppn
		F["job_id"] 		= self.job_name
		F["total_cpu"]		= self.total_cpu
		F["domain_size_x"]	= self.domain_size[0]
		F["domain_size_y"]	= self.domain_size[1]
		F["domain_size_z"]	= self.domain_size[2]
		F["cpu_x"]			= self.cpus[0]
		F["cpu_y"]			= self.cpus[1]
		F["cpu_z"]			= self.cpus[2]
		F["timesteps"]		= self.timesteps
		F["output_suffix"]	= self.output_suffix
		enable = True
		if part == "mpirun":
			enable = False
		if alternative_name == "":
			submit_file = self.submit_file
			F["job_name"] 		= self.job_name
		else:
			submit_file = alternative_name + ".submit.sh"
			F["job_name"] 		= alternative_name

		with open(submit_file, mode) as sf:
			with open(template, 'r') as tf:
				for line in tf:
					if line.strip() == "# RUN":
						if part == "head":
							enable = False
						elif part == "mpirun":
							enable = True
					if enable:
						for key in F:
							line = line.replace('{' + '{0}'.format(key) + '}', str(F[key]))
							#print("{{0}}".format(key), str(F[key]))
						sf.write(line)

		# with open(self.submit_file, 'w') as f:
		# 	f.write("")

		# 	f.write("#!/bin/bash\n")
		# 	f.write("#PBS -l nodes={0}:ppn={1}\n".format(self.nodes, self.ppn))
		# 	f.write("#PBS -l walltime=01:00:00\n")
		# 	f.write("##PBS -m abe\n")
		# 	f.write("#PBS -N {0}\n".format(self.job_name))
		# 	f.write("##PBS -j oe\n")
		# 	f.write("#PBS -q batch\n")
		# 	f.write("\n")
		# 	f.write("# Initialization\n")
		# 	f.write("set verbose\n")
		# 	f.write("set echo\n")
		# 	f.write("\n")
		# 	f.write("# Go into case directory\n")
		# 	f.write("cd $PBS_O_WORKDIR/\n")
		# 	f.write("\n")
		# 	f.write("# Run Eulag  in case directory\n")
		# 	f.write("mpirun -n {0} -f $PBS_NODEFILE 2>&1 >{1}.out ./dwarf --sizex {2} --sizey {3} --sizez {4} --nprocx {5} --nprocy {6} --nprocz {7} --maxiteration {8}\n".format(self.total_cpu, self.job_name, self.domain_size[0], self.domain_size[1], self.domain_size[2], self.cpus[0], self.cpus[1], self.cpus[2], self.timesteps))


		# f.close()
	def Submit(self):
		run("qsub {0}".format(self.submit_file))

	def ReadTimer(self, timer):
		self.timers_results[timer] = 0
		if not os.path.isfile(self.output_file):
			return 0
		with open(self.output_file, 'r') as f:
			for line in f:
				line = line.strip()
				if timer in line:
					stats = RemoveMultipleSpaces(line).split()
					if len(stats) == 7:
						self.timers_results[timer] = stats
						return 2
		return 1

	def Print(self):
		print(self.submit_file, self.total_cpu)

	def __lt__(self, other):
         return self.total_cpu < other.total_cpu