import numpy
import subprocess
import sys
import os.path
# import matplotlib as mpl
# mpl.use('Agg')
# import matplotlib.pyplot as plt
from PerformanceTester import Tester


mode = "group" # or "single"
T = Tester()
#T.SetTimer("diff_fckflxdv")
T.SetTimer("timeloop")
#T.AddDomain( 64, 64, 64, color='#800000')
T.AddDomain( 512,512, 128, color='#008000')

T.AddIterations(0,1500,1)
#T.AddIterations(64,1800,1000)
T.SetTemplate('JURECADChybrid.tpl')
T.SetOutputSuffix("logout")
T.AddExecutable('./comprconvecapp', 'comprconvecapp', symbol='o')
#T.AddExecutable('./test_002.out', 'test_002', symbol='s')
#T.AddExecutable('./test_003.out', 'test_003', symbol='*')


#T.SetCpuConfig([2,4,8,16,32,64,128], [2,4,8,16,32,64], [1,2,4])
T.SetCpuConfig([4,8], [4,8], [1,2])
T.GenerateJobs()


#T.GenerateJobsTotalCPU(128,16,16,4)
#T.GenerateJobsTotalCPU(256,16,16,4)



if sys.argv[1] == "dryrun":
	if mode == "single":
		T.MakeSubmits()
	elif mode == "group":
		T.MakeGroupSubmits()


if sys.argv[1] == "run":
	if mode == "single":
		T.MakeSubmits()
		T.SubmitAll()
	elif mode == "group":
		T.MakeGroupSubmits()
		T.SubmitGroupAll()

if sys.argv[1] == "test":
	if mode == "single":
		T.ReadJobTimers()
	elif mode == "group":
		T.ReadGroupJobTimers()
	T.ProcessStats()
	T.CpuConfigPlot()

exit()
