import numpy
import subprocess
import sys
import os.path
from PerformanceTesterJob import Job, printc
import types
from tabulate081 import tabulate
enable_plotting = True
try:
	import matplotlib as mpl
	mpl.use('Agg')
	import matplotlib.pyplot as plt
except:
	enable_plotting = False


class Tester():
	def __init__(self):
		self.Jobs = [];
		self.cx = []
		self.cy = []
		self.cz = []

		self.timer = ''
		self.domains = []
		self.domains_color = []
		self.domains_symbol = []
		self.template = ''
		self.iterations = []
		self.output_suffix = ''
		self.executable = ''

		self.uniq_total_cpus = []
	def SetTimer(self, timer):
		self.timer = timer

	def SetTemplate(self, template):
		self.template = template

	def SetExecutable(self, executable):
		self.executable = executable

	def SetOutputSuffix(self, output_suffix):
		self.output_suffix = output_suffix


	def SetCpuConfig(self, cx, cy, cz):
		self.cx = cx
		self.cy = cy
		self.cz = cz

	def AddDomain(self, dx, dy, dz, color='#000000', symbol='o'):
		self.domains.append([dx,dy,dz])
		self.domains_color.append(color)
		self.domains_symbol.append(symbol)

	def AddIterations(self, cpu_from, cpu_to, iterations):
		self.iterations.append([cpu_from, cpu_to, iterations])

	def GenerateJobs(self):
		utc = set()
		for x in self.cx:
			for y in self.cy:
				for z in self.cz: 
					utc.add(numpy.prod([x,y,z]))
					for iteration in self.iterations:
						if numpy.prod([x,y,z]) > iteration[0] and numpy.prod([x,y,z]) <= iteration[1]:
							for d in self.domains:
								self.Jobs.append(Job(d, [x,y,z], iteration[2], output_suffix=self.output_suffix, executable=self.executable))
					# if numpy.prod([x,y,z]) >= 64 and numpy.prod([x,y,z]) <= 1600:
					# 	for d in self.domains:
					# 		self.Jobs.append(Job(d, [x,y,z], 1000))
					# elif numpy.prod([x,y,z]) < 64:
					# 	for d in self.domains:
					# 		self.Jobs.append(Job(d, [x,y,z], 250))

		self.Jobs.sort()
		self.uniq_total_cpus = list(utc)
		self.uniq_total_cpus.sort()

	def MakeSubmits(self):
		for J in self.Jobs:
			J.MakeSubmit(self.template)
			print('Prepared submit for job', J.job_name)

	def SubmitAll(self):
		for J in self.Jobs:
			J.Submit()

	def ReadJobTimers(self):
		for J in self.Jobs:
			J.ReadTimer(self.timer)

	def ProcessStats(self):
		if enable_plotting:
			fig = plt.figure()
			ax = fig.add_subplot(111)
			ax.set_xscale("log", nonposx='clip')
			ax.set_yscale("log", nonposy='clip')
		for di in range(len(self.domains)):
			d = self.domains[di]
			min_times = numpy.empty(len(self.uniq_total_cpus))
			min_times[:] = numpy.NAN

			printc('\nProcessing Domain {0}'.format(str(d)), 'blue')
			for ci in range(len(self.uniq_total_cpus)):
				c = self.uniq_total_cpus[ci]
				JobsOK = []
				JobsNK = []
				printc('\tProcessing cpu config {0}'.format(str(c)), 'violet')
				T = []
				for J in self.Jobs:
					if J.total_cpu == c and J.domain_size == d:
						if type(J.timers_results[self.timer]) is list:
							JobsOK.append(J)
						else:
							JobsNK.append(J)
				JobsOK.sort(key=lambda x: float(x.timers_results[self.timer][4])/float(x.timers_results[self.timer][3]))
				if len(JobsOK) > 0:
					min_times[ci] = float(JobsOK[0].timers_results[self.timer][4])/float(JobsOK[0].timers_results[self.timer][3])
				for J in JobsOK:
					# printc('\t\tOK:', 'green', end=" ")
					tpts = float(J.timers_results[self.timer][4])/float(J.timers_results[self.timer][3])
					tptss = '{0:7.4f} s'.format(tpts)
					tptsp = '{0:5.2f} x'.format(((tpts/min_times[ci])))
					tptspc = '{0:10.7f} s'.format(tpts*J.total_cpu)
					# print(J.job_name,'\t', tpts)
					ds = '{0} x {1} x {2}'.format(J.domain_size[0],J.domain_size[1],J.domain_size[2])
					T.append(['OK', ds, J.cpus[0], J.cpus[1], J.cpus[2], J.timesteps, tptss, tptsp,tptspc])
				for J in JobsNK:
					# printc('\t\tFAIL:', 'red', end=" ")
					# print(J.job_name,'\t', J.timers_results)
					ds = '{0} x {1} x {2}'.format(J.domain_size[0],J.domain_size[1],J.domain_size[2])

					T.append(['FAIL', ds, J.cpus[0], J.cpus[1], J.cpus[2], '-', '-', '-','-'])
				header=['result', 'domain size', 'cpu x', 'cpu y', 'cpu z', 'timesteps', 'time / iter', 'to fastest', 'time / iter / core']
				if len(T) > 0:
					print('\t\t'+tabulate(T, headers=header, tablefmt="fancy_grid").replace('\n','\n\t\t'))
			if enable_plotting:
				plt.plot(self.uniq_total_cpus,min_times,self.domains_symbol[di], color=self.domains_color[di],label=str(self.domains[di]),ms=10)
				plt.plot(self.uniq_total_cpus,min_times, color=self.domains_color[di])
			# print(self.uniq_total_cpus,min_times)
		if enable_plotting:
			print("MakingPlot")
			plt.xlabel('Total number of cores')
			plt.ylabel('Average time per iteration')
			plt.legend()
			plt.savefig("nowy.png")
			# plt.show()

