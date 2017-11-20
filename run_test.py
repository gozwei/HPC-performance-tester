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
T.SetTimer("mpdatm_LAM")
T.AddDomain( 512,  256, 128, color='#800000', symbol='o')
T.AddDomain(1024,  512, 128, color='#000080', symbol='s')
T.AddDomain(2048, 1024, 128, color='#008000', symbol='*')
T.SetCpuConfig([2,4,8,16,32,64,128], [2,4,8,16,32,64], [1,2,4,8,16,32])
T.AddIterations(32,2000,10)
#T.AddIterations(64,1800,1000)
T.SetTemplate('GRAD.tpl')
T.SetOutputSuffix("logout")
T.SetExecutable('./dwarf')
T.GenerateJobs()

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
