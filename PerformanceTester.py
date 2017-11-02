import numpy
import subprocess
import sys
import os.path
from PerformanceTesterJob import Job, printc
import types
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

class Tester():
	def __init__(self):
		self.Jobs = [];
		self.cx = [2]#[2,4,8,16,32,64]
		self.cy = [4]#[2,4,8,16,32,64]
		self.cz = [1,2,4,8]

		self.timer = ''
		self.domains = []
		self.domains_color = []
		self.domains_symbol = []

		self.uniq_total_cpus = []
	def SetTimer(self, timer):
		self.timer = timer
	def AddDomain(self, dx, dy, dz, color='#000000', symbol='o'):
		self.domains.append([dx,dy,dz])
		self.domains_color.append(color)
		self.domains_symbol.append(symbol)

	def GenerateJobs(self):
		utc = set()
		for x in self.cx:
			for y in self.cy:
				for z in self.cz: 
					utc.add(numpy.prod([x,y,z]))
					if numpy.prod([x,y,z]) >= 64 and numpy.prod([x,y,z]) <= 1600:
						for d in self.domains:
							self.Jobs.append(Job(d, [x,y,z], 100))
					elif numpy.prod([x,y,z]) < 64:
						for d in self.domains:
							self.Jobs.append(Job(d, [x,y,z], 25))

		self.Jobs.sort()
		self.uniq_total_cpus = list(utc)
		self.uniq_total_cpus.sort()

	def MakeSubmits(self):
		for J in self.Jobs:
			J.MakeSubmit()
			print('Prepared submit for job', J.job_name)

	def SubmitAll(self):
		for J in self.Jobs:
			J.Submit()

	def ReadJobTimers(self):
		for J in self.Jobs:
			J.ReadTimer(self.timer)

	def ProcessStats(self):
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
					printc('\t\tOK:', 'green', end=" ")
					print(J.job_name,'\t', float(J.timers_results[self.timer][4])/float(J.timers_results[self.timer][3]))
				for J in JobsNK:
					printc('\t\tFAIL:', 'red', end=" ")
					print(J.job_name,'\t', J.timers_results)

			plt.plot(self.uniq_total_cpus,min_times,self.domains_symbol[di], color=self.domains_color[di],label=str(self.domains[di]),ms=10)
			plt.plot(self.uniq_total_cpus,min_times, color=self.domains_color[di])
			# print(self.uniq_total_cpus,min_times)
		print("MakingPlot")
		plt.xlabel('Total number of cores')
		plt.ylabel('Average time per iteration')
		plt.legend()
		plt.savefig("nowy.png")
		plt.show()

