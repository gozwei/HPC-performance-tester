import numpy
import subprocess
import sys
import os.path
from PerformanceTesterJob import Job, printc
import types
from tabulate081 import tabulate
from scipy import stats
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
				#plt.plot(self.uniq_total_cpus,min_times, color=self.domains_color[di])
				Q, W = -1, -1
				for q in range(len(self.uniq_total_cpus)):
					if min_times[q] > 0:
						for w in range(len(self.uniq_total_cpus)-1,0,-1):
							if min_times[w] > 0:
								if Q==-1 and W==-1:
									Q = q
									W = w + 1
									# print("Q, W", q, w)
								
				# print("Q, W", q, w)
				# plt.plot([self.uniq_total_cpus[Q], self.uniq_total_cpus[W]], [min_times[Q], min_times[Q]/(self.uniq_total_cpus[W]/self.uniq_total_cpus[Q])],'--', color=self.domains_color[di])
				# print(self.uniq_total_cpus[Q:W])
				# print(min_times[Q:W])

				x1, y1 = self.uniq_total_cpus[Q:W],min_times[Q:W]
				x2 = numpy.log(numpy.array(x1))
				y2 = numpy.log(numpy.array(y1))

				slope, intercept, r_value, p_value, std_err = stats.linregress(x2,y2)		
				#print("LS", slope, intercept, r_value, p_value, std_err)
				#plt.plot([x1[0], x1[-1]*16], [numpy.exp(x2[0]*slope+intercept), numpy.exp(numpy.log(x1[-1]*16)*slope+intercept)],'-.', color=self.domains_color[di])
				plt.plot([1, 1024*32], [numpy.exp(numpy.log(1)*slope+intercept), numpy.exp(numpy.log(1024*32)*slope+intercept)],'-.', color=self.domains_color[di])
				plt.axis((100,100000,0.0001,1))
			# print(self.uniq_total_cpus,min_times)
		if enable_plotting:
			# print("MakingPlot")

			plt.xlabel('Total number of cores',fontsize=16)
			plt.ylabel('Average time per iteration',fontsize=16)
			plt.legend()
			plt.grid()
			plt.savefig("nowy.png")
			# plt.show()

	def CpuConfigPlot(self):
		for ds in self.domains:
			name = 'cpu_{0}_{1}_{2}.png'.format(ds[0], ds[1], ds[2])
			title = 'Advection dwarf: global domain size {0} x {1} x {2}'.format(ds[0], ds[1], ds[2])

			JobsOK = []
			for J in self.Jobs:
				if J.domain_size == ds:
					if type(J.timers_results[self.timer]) is list:
						JobsOK.append(J)
			JobsOK.sort(key=lambda x: -float(x.timers_results[self.timer][4])/float(x.timers_results[self.timer][3]))
			JobsOK.sort(key=lambda x: -float(x.cpus[2]))
			JobsOK.sort(key=lambda x: float(x.total_cpu))
			y = []
			bestx = []
			besty = []
			labels=[]
			y2 = []
			x2=[]
			tcp =  0
			halo_size = []
			for J in JobsOK:
				tpts = float(J.timers_results[self.timer][4])/float(J.timers_results[self.timer][3])
				tptss = '{0:7.4f} s'.format(tpts)
				tptspc = tpts*J.total_cpu

				min_lptps = 1e10
				for K in JobsOK:
					
					if J.total_cpu == K.total_cpu:
						ltpts = float(K.timers_results[self.timer][4])/float(K.timers_results[self.timer][3])
						if ltpts < min_lptps:
							min_lptps = ltpts
				print(J.total_cpu, min_lptps)
				if tpts==min_lptps:
					bestx.append(len(y))
					besty.append(tpts)



				#print(numpy.prod(J.cpus), J.cpus[0], J.cpus[1], J.cpus[2],tptss)
				y.append(tpts)
				labels.append('{0} x {1} x {2}'.format(J.cpus[0],J.cpus[1],J.cpus[2]))
				if tcp != J.total_cpu:
					tcp = J.total_cpu
					y2.append(len(y)-1)
					x2.append(tcp)

				box = numpy.array(J.domain_size)/numpy.array(J.cpus)
				pp = (box[0]*box[1]+box[1]*box[2]+box[0]*box[2])*2
				ppt = pp*numpy.prod(J.cpus);
				# print(J.domain_size, J.cpus, box, pp, ppt)
				halo_size.append(ppt)


			
			x = range(len(y))

			print("CORR:", stats.pearsonr(y, halo_size))

			plt.clf()
			fig = plt.figure(figsize=(50,20))
			ax = fig.add_subplot(111)
			#ax.set_xscale("log", nonposx='clip')
			#ax.set_yscale("log", nonposy='clip')
			plt.plot(bestx,besty,'ro',ms=20)
			plt.plot(x,y,'.',ms=10)
			
			# for q in range(0,len(y2)-1):
			# 	s,e = y2[q], y2[q+1]
			# 	print("T", x2[q], s, e)
			# 	slope, intercept, r_value, p_value, std_err = stats.linregress(x[s:e],y[s:e])
			# 	print(slope, intercept, r_value, p_value, std_err)
			for a in range(len(y2)):
				plt.plot([y2[a]-.5, y2[a]-.5], [numpy.min(y), numpy.max(y)],'k--')
			plt.xticks(x, labels, rotation='vertical', fontsize=16)
			plt.grid()
			h = numpy.max(y)-numpy.min(y)
			plt.axis([-.5, len(y)+.5, numpy.min(y)-h/20, numpy.max(y)+h/20])
			plt.xlabel('MPI cartesian decomposition: nprocx * nprocy * nprocz', fontsize=28)
			plt.ylabel('Average time per MPDATA call', fontsize=28)
			plt.xticks(x, labels, rotation='vertical', fontsize=16)
			ax2 = plt.twinx()
			#ax2.set_yscale("log", nonposy='clip')
			#ax2.plot(x,numpy.array(halo_size),'sr')
			plt.title(title, fontsize=28)
			plt.savefig(name)
