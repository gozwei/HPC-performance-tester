import numpy
import subprocess
import sys
import os.path
# import matplotlib as mpl
# mpl.use('Agg')
# import matplotlib.pyplot as plt
from PerformanceTester import Tester



T = Tester()
T.SetTimer("mpdatm_LAM")
T.AddDomain( 512,  256, 128, color='#800000', symbol='o')
T.AddDomain(1024,  512, 128, color='#000080', symbol='s')
T.AddDomain(2048, 1024, 128, color='#008000', symbol='*')
T.SetCpuConfig([2,4,8,16,32,64], [2,4,8,16,32,64], [1,2,4,8])
T.AddIterations(0,64,250)
T.AddIterations(64,1800,1000)
T.SetTemplate('GRAD.tpl')
T.SetOutputSuffix("out")
T.SetExecutable('./dwarf')
T.GenerateJobs()

if sys.argv[1] == "dryrun":
	T.MakeSubmits()

if sys.argv[1] == "run":
	T.MakeSubmits()
	T.SubmitAll()

if sys.argv[1] == "test":
	T.ReadJobTimers()
	T.ProcessStats()
	T.CpuConfigPlot()

exit()