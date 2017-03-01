#!/usr/bin/env python3
from datetime import datetime
from subprocess import Popen, PIPE

def status_qubes():
	try:
		with Popen(['qvm-ls', '--raw-data', 'name', 'on', ], stdout=PIPE) as f:
			count = len([l for l in f.stdout.readlines() if l.strip()[-1] == 42])
		return '"name":"qubes","full_text":"{} Qubes"'.format(count)
	except:
		pass

def status_net(netvm='sys-net'):
	try:
		with Popen(['qvm-run', '--pass-io', netvm, 'ip route',  ], stdout=PIPE) as f:
			dev = [l.split()[4] for l in f.stdout.readlines() if l.split()[0]==b'default']
		if not dev:
			color = '#ff0000'
			dev = 'None'
			ip = '-'
			ssid = '-'
		else:
			color = '#00ff00'
			dev = str(dev[0], 'ascii')
			# 'qvm-run', '--pass-io', netvm, 'ip -o -f inet addr',
			with Popen(['qvm-run', '--pass-io', netvm, 'ifconfig {}'.format(dev),  ], stdout=PIPE) as f:
				ip = str([l.split() for l in f.stdout.readlines()][1][1], 'ascii')
			if dev.startswith('wl'):
				# 'qvm-run', '--pass-io', netvm, 'iwconfig {}'.format(dev),
				with Popen(['qvm-run', '--pass-io', netvm, 'iwconfig {}'.format(dev),  ], stdout=PIPE) as f:
					ssid = str([l.split() for l in f.stdout.readlines()][0][3], 'ascii').split(':')[1][1:-1]
			else:
				ssid = '-'
		return '"name":"net","full_text":"{}: {} ({})","color":"{}"'.format(dev, ip, ssid, color)
	except:
		pass

def status_disk():
	try:
		with Popen(['df', '--output=pcent', '/', ], stdout=PIPE) as f:
			pcent = int(f.stdout.read().strip().split()[1][:-1])
		if pcent > 85:
			color = '#ff0000'
		else:
			color = '#00ff00'
		return '"name":"disk","full_text":"Disk use: {}%","color":"{}"'.format(pcent, color, )
	except:
		pass

def status_bat():
	try:
		with open('/sys/class/power_supply/BAT0/charge_now') as f:
			charge_now = int(f.readline().strip())
		with open('/sys/class/power_supply/BAT0/charge_full') as f:
			charge_full = int(f.readline().strip())
		with open('/sys/class/power_supply/BAT0/charge_full_design') as f:
			charge_full_design = int(f.readline().strip())
		with open('/sys/class/power_supply/AC/online') as f:
			online = int(f.readline().strip())
		if online:
			if charge_now < charge_full:
				status_chr = chr(9650)
			else:
				status_chr = chr(9632)
		else:
			status_chr = chr(9660)
		status_num = int(charge_now / charge_full * 100)
		if status_num <= 30:
			color = '#ff0000'
		else:
			color = '#00ff00'
		return '"name":"bat","full_text":"BAT {}{}%","color":"{}"'.format(status_chr, status_num, color, )
	except:
		pass

def status_load():
	try:
		with Popen(['uptime', ], stdout=PIPE) as f:
			load = float(f.stdout.read().strip().split()[-3][:4])
		if load > 3.0:
			color = '#ff0000'
		else:
			color = '#00ff00'
		return '"name":"load","full_text":"Load: {}","color":"{}"'.format(load, color)
	except:
		pass

def status_cpu():
	try:
		cpu = 0.0
		with Popen(['xentop', '-i', '2', '-b', ], stdout=PIPE) as f:
			for l in f.stdout.readlines():
				l = l.strip().split()[3]
				try:
					cpu += float(l)
				except:
					pass
		if cpu > 60.0:
			color = '#ff0000'
		else:
			color = '#00ff00'
		return '"name":"cpu","full_text":"CPU: {:.1f}%","color":"{}"'.format(cpu, color)
	except:
		pass

def status_time():
	try:
		return '"name":"time","full_text":"{}","color":"{}"'.format(datetime.now().strftime("%Y-%m-%d %H:%M, %a [%V]"), '#ee9900', )
	except:
		pass

if __name__ == '__main__':
	print(',[{{{}}}]'.format('},{'.join([s for s in (
		status_qubes(),
		status_net(),
		#status_net('work'),
		status_disk(),
		status_cpu(),
		status_bat(),
		status_time(),
		) if s])))
