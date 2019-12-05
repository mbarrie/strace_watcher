import subprocess
import sys
import argparse
import os
import re
import shlex

parser = argparse.ArgumentParser(description='use Strace to figure out where file activity is happening')
parser.add_argument('--splunkpid', dest='splunkpid',nargs=1, required=True,
		help='the pid of the parent splunkd process')
parser.add_argument('--treedepth', dest='treedepth',nargs=1, required=True,help='how deep do you want to track in the file system hierarchy?')

args = parser.parse_args()

splunkpid=args.splunkpid[0]
treedepth=int(args.treedepth[0]) + 1
strace_string = "strace -f -p %s -y -e trace=open,close,read,write" %(splunkpid)
p = re.compile('\[pid\s+(\d+)\]\s+(read|write)\(\d+\<([^\>]+)\>.+\)\s=\s(\d+)', re.IGNORECASE)

def run_command(command):
	progress = 0
	write_count = 0
	read_count = 0
	open_count = 0
	close_count = 0
	total_ops = 0
	total_read_bytes = 0
	total_write_bytes = 0
	total_bytes = 0
	tree_list = {}
	process = subprocess.Popen(strace_string,shell=True , stderr=subprocess.PIPE)
	print "Streaming strace data..."
	try:
		while True:
			output = process.stderr.readline()
			if output == '' and process.poll() is not None:
				break
			if output:
				m = p.match(output)
				if m is not None:
					path = m.group(3).split("/",treedepth)
					path.pop(-1)
					path='/'.join(path)
					if len(path) < 1:
						continue
					if path not in tree_list:
						tree_list[path] = dict(write_count=0,total_ops=0,total_write_bytes=0,total_bytes=0,read_count=0,total_read_bytes=0)
					if m.group(2) == "write":
						tree_list[path]['write_count']=tree_list[path]['write_count'] + 1
						tree_list[path]['total_ops']+=1
						tree_list[path]['total_write_bytes']+=int(m.group(4))
						tree_list[path]['total_bytes']+=int(m.group(4))
					if m.group(2) == "read":			
						tree_list[path]['read_count']+=1
						tree_list[path]['total_ops']+=1
						tree_list[path]['total_read_bytes']+=int(m.group(4))
						tree_list[path]['total_bytes']+=int(m.group(4))
					#print "Action: %s path: %s bytes %s" %(m.group(2),m.group(3),m.group(4))
			if progress > 100:
				progress = 0
			else:
				progress+=1

			rc = process.poll()
	except KeyboardInterrupt:
		for path_name in tree_list:
			print "For path: %s  Stats: " %(path_name)
			print (tree_list[path_name])
	return rc

rc = run_command(strace_string)


# care about these things:
# counts of reads, writes, opens, cloes, total
# total bytes read, written anbd total by tree segemt

