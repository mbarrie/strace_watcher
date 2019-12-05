# strace_watcher
Tool for using strace to figure out where splunkd is writing and reading


Example:
python strace_cleaner.py --splunkpid 3262 --treedepth 4

Treedepth is at what level you want to collect stats, so for example in an indexer where splunk is installed in /opt/splunk, a treedepth of 4 means you'd track at the level of /opt/splunk/*/*.   A higher tree depth would give more granular results.  For shorter paths like /proc it should hopefully just ignore them.

splunkpid should be the current pid of the parent splunk process, although it could also be a child pid like a super broken search.
