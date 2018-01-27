#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author: tsunc & zadmine
@software: PyCharm Community Edition
@time: 2018/1/27 18:10
"""

import  logging
import  paramiko
from watchdog.observers  import  Observer
from watchdog.events  import  PatternMatchingEventHandler

class SFTPClient(object):
	def __init__ (self, hostname, user, password, root, port=22):
		self.root = root
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(hostname = hostname, port=port,
						 username = user,  password=password)
		self.sftp = self.ssh.open_sftp()
		self.sftp.chdir(self.root)

	def create_dir(self, path):
		self.sftp.mkdir(path)

	def put(self, src, dst):
		self.sftp.rename(src, dst)

	def move(self, src, dst):
		self.sftp.rename(src, dst)

	def clost(self):
		self.ssh.close()


class BackupWatchEventHandler(PatternMatchingEventHandler):
	def __init__(self, sftp, patterns = None, ignore_patterns= None,
		         case_sensitive=False):
	    super(BackupWatchEventHandler, self).__init__(patterns=patterns,
	    											  ignore_patterns=ignore_patterns,
	    											  ignore_directories=False,
	    											  case_sensitive=case_sensitive)
	    self.sftp = sftp

	def on_created(self, event):
		if event.is_directory:
			self.sftp.create_dir(event.src_path)
		else:
			self.sftp.put(event.src_path, event.src_path)

	def on_modified(self, event):
		if not event.is_directory:
			self.sftp.put(event.src_path, event.src_path)

	def on_moved(self, event):
		self.sftp.move(event.src_path, event.dest_path)

	def on_any_event(self, event):
		logging.info('event {0} of {1}'.format(event.event_type, event.src_path))


if __name__=='__main__':
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)s - %(message)s',
						datefmt = '%Y-%m-%d %H-%M-%S')
	sftp = SFTPClient('192.168.21.22', 'pwd', 'client', '/tmp', '22')
	handler = BackupWatchEventHandler(sftp)
	observer = Observer()
	observer.schedule(handler, '.', recursive=True)
	observer.start()
	try:
		observer.join()
	except KeyboardInterrupt:
		observer.stop()
	observer.join()
	sftp.close()
  
