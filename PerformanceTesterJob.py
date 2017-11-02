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

def printc(msg, color='black', sep=' ', end='\n'):
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
	print('{0}{1}{2}'.format(s,msg,e), sep=sep, end=end)

def run(cmd):
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out, err = p.communicate()
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
	def __init__(self, domain_size=[32, 32, 32], cpus=[2, 2, 2], timesteps=1000):
		self.domain_size = domain_size
		self.cpus = cpus
		self.timesteps = timesteps

		self.job_name = "E.{0}.{1}.{2}.{3}.{4}.{5}.{6}".format(self.domain_size[0], self.domain_size[1], self.domain_size[2], self.cpus[0], self.cpus[1], self.cpus[2], self.timesteps)

		self.total_cpu = numpy.prod(self.cpus)
		self.ppn = 20
		self.nodes = int(numpy.ceil(float(self.total_cpu)/float(self.ppn)))

		self.submit_file = "{0}.submit.sh".format(self.job_name)
		self.output_file = "{0}.out".format(self.job_name)

		self.timers_results = dict()

	def MakeSubmit(self):
		with open(self.submit_file, 'w') as f:
			f.write("")

			f.write("#!/bin/bash\n")
			f.write("#PBS -l nodes={0}:ppn={1}\n".format(self.nodes, self.ppn))
			f.write("#PBS -l walltime=01:00:00\n")
			f.write("##PBS -m abe\n")
			f.write("#PBS -N {0}\n".format(self.job_name))
			f.write("##PBS -j oe\n")
			f.write("#PBS -q batch\n")
			f.write("\n")
			f.write("# Initialization\n")
			f.write("set verbose\n")
			f.write("set echo\n")
			f.write("\n")
			f.write("# Go into case directory\n")
			f.write("cd $PBS_O_WORKDIR/\n")
			f.write("\n")
			f.write("# Run Eulag  in case directory\n")
			f.write("mpirun -n {0} -f $PBS_NODEFILE 2>&1 >{1}.out ./dwarf --sizex {2} --sizey {3} --sizez {4} --nprocx {5} --nprocy {6} --nprocz {7} --maxiteration {8}\n".format(self.total_cpu, self.job_name, self.domain_size[0], self.domain_size[1], self.domain_size[2], self.cpus[0], self.cpus[1], self.cpus[2], self.timesteps))


		f.close()
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