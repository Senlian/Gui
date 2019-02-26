# -*- coding:utf-8 -*-
import psutil
import sys

def getpid(processName,number):
	pids=psutil.pids()
	i=1
	for pid in pids:
		
		p = psutil.Process(pid)
		if p.name() == processName:
			if i==int(number):
				return pid
				i+=1
			else :
				i+=1
				continue
	
if  __name__ =="__main__":

	if "rss"==sys.argv[1]:
		pid=getpid(sys.argv[2],sys.argv[3])		
		p = psutil.Process(pid)
		a= p.memory_info()
		print a.rss
	elif "vms"==sys.argv[1]:
		pid=getpid(sys.argv[2],sys.argv[3])		
		p = psutil.Process(pid)
		a= p.memory_info()
		print a.vms
	elif "percent"==sys.argv[1]:
		pid=getpid(sys.argv[2],sys.argv[3])		
		p = psutil.Process(pid)
		percent=p.memory_percent()
		print percent
	elif "cpu_user"==sys.argv[1]:
		pid=getpid(sys.argv[2],sys.argv[3])		
		p = psutil.Process(pid)
		cpu=p.cpu_times()
		print cpu.user
	elif "cpu_system"==sys.argv[1]:
		pid=getpid(sys.argv[2],sys.argv[3])		
		p = psutil.Process(pid)
		cpu=p.cpu_times()
		print cpu.system
		
	elif "cpu_percent" ==sys.argv[1]:
		pid=getpid(sys.argv[2],sys.argv[3])
		p = psutil.Process(pid)
		#print pid
		cpu=p.cpu_percent(interval=1)
		#/psutil.cpu_count()
		#print psutil.cpu_count()
		print cpu
	elif "mem_usd" == sys.argv[1]:
		mem = psutil.virtual_memory()
		print mem.percent
	else:
		print "pless chanshu"
