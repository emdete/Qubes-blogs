#!/usr/bin/env python3
from datetime import datetime
from subprocess import Popen, PIPE
from json import dumps

C_NORMAL = '#00dd00'
C_FATAL = '#ff0000'
C_WARN = '#ffff00'

def status_qubes(name='qubes', color=C_NORMAL):
	full_text = name
	try:
		with Popen(['qvm-ls', '--raw-data', 'name', 'on', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			count = len([l for l in f.stdout.readlines() if l.strip()[-1] == 42])
		full_text = '{} Qubes'.format(count)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_qubes_net(name='qubes-net', netvm='sys-net', color=C_NORMAL):
	full_text = name
	try:
		with Popen(['qvm-run', '--passeio', netvm, 'ip route', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			dev = [l.split()[4] for l in f.stdout.readlines() if l.split()[0]==b'default']
		if not dev:
			color = C_WARN
			ip = '-'
			ssid = '-'
		else:
			dev = str(dev[0], 'ascii')
			# 'qvm-run', '--pass-io', netvm, 'ip -o -f inet addr',
			with Popen(['qvm-run', '--pass-io', netvm, 'ifconfig {}'.format(dev), ], stdout=PIPE, env=dict(LANG='C', )) as f:
				ip = str([l.split() for l in f.stdout.readlines()][1][1], 'ascii')
			if dev.startswith('wl'):
				# 'qvm-run', '--pass-io', netvm, 'iwconfig {}'.format(dev),
				with Popen(['qvm-run', '--pass-io', netvm, 'iwconfig {}'.format(dev), ], stdout=PIPE, env=dict(LANG='C', )) as f:
					ssid = str([l.split() for l in f.stdout.readlines()][0][3], 'ascii').split(':')[1][1:-1]
			else:
				ssid = '-'
		full_text = '{}: {} ({})'.format(dev, ip, ssid)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_net(name='net', color=C_NORMAL):
	full_text = name
	try:
		dev = None
		with Popen(['ip', 'route', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			for l in f.stdout.readlines():
				l = l.split()
				if l[0] == b'default':
					p = l.index(b'dev')
					dev = l[p+1]
		if not dev:
			color = C_WARN
			ip = '-'
			ssid = '-'
		else:
			dev = str(dev, 'ascii')
			with Popen(['ip', '-oneline', '-family', 'inet', 'addr', 'show', 'dev', dev, ], stdout=PIPE, env=dict(LANG='C', )) as f:
				ip = str([l.split() for l in f.stdout.readlines()][0][3], 'ascii')
			if dev.startswith('wl'):
				with Popen(['wpa_cli', '-i', dev, 'status' ], stdout=PIPE, env=dict(LANG='C', )) as f:
					ssid = str([l.strip().split(b'=')[1] for l in f.stdout.readlines() if l.startswith(b'ssid=')][0], 'ascii')
			else:
				ssid = '-'
		full_text = '{}: {} ({})'.format(dev, ip, ssid)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_disk(name='ssd', color=C_NORMAL):
	full_text = name
	try:
		with Popen(['df', '--output=pcent', '/rw', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			pcent = int(f.stdout.read().strip().split()[1][:-1])
		if pcent > 90:
			color = C_WARN
		full_text = 'ssd: {}%'.format(pcent)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_bat(name='bat', color=C_NORMAL):
	full_text = name
	try:
		if True: # relative to capacity
			with open('/sys/class/power_supply/BAT0/capacity') as f:
				capacity = int(f.readline().strip())
		else: # relative to design:
			with open('/sys/class/power_supply/BAT0/charge_now') as f:
				charge_now = int(f.readline().strip())
			with open('/sys/class/power_supply/BAT0/charge_full') as f:
				charge_full = int(f.readline().strip())
			with open('/sys/class/power_supply/BAT0/charge_full_design') as f:
				charge_full_design = int(f.readline().strip())
			capacity = int(charge_now / charge_full_design * 100)
		with open('/sys/class/power_supply/AC/online') as f:
			online = int(f.readline().strip())
		if online:
			if capacity < 100:
				status_chr = chr(9650)
			else:
				status_chr = chr(9632)
		else:
			status_chr = chr(9660)
		if capacity <= 30:
			color = C_WARN
		full_text = 'bat: {}{}%'.format(status_chr, capacity)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_load(name='load', color=C_NORMAL):
	full_text = name
	try:
		with Popen(['uptime', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			load = float(f.stdout.read().strip().split()[-3][:4])
		if load > 3.0:
			color = C_WARN
		full_text = 'load: {}'.format(load)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_xen_cpu(name='cpu', color=C_NORMAL):
	full_text = name
	try:
		cpu = 0.0
		with Popen(['xentop', '-i', '2', '-b', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			for l in f.stdout.readlines():
				l = l.strip().split()[3]
				try:
					cpu += float(l)
				except:
					pass
		if cpu > 60.0:
			color = C_FATAL
		full_text = 'cpu: {:.1f}%'.format(cpu)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_temp(name='temp', color=C_NORMAL):
	full_text = name
	try:
		with open('/sys/devices/platform/coretemp.0/hwmon/hwmon1/temp1_input') as f:
			temp = int(f.readline().strip()) // 1000
		if temp > 80:
			color = C_WARN
		full_text = 'temp: {}°'.format(temp)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_brightness(name='brightness', color=C_NORMAL):
	full_text = name
	try:
		with open('/sys/devices/pci0000:00/0000:00:02.0/backlight/acpi_video0/max_brightness') as f:
			max_brightness = int(f.readline().strip())
		with open('/sys/devices/pci0000:00/0000:00:02.0/backlight/acpi_video0/actual_brightness') as f:
			actual_brightness = int(f.readline().strip())
		brightness = int((actual_brightness / (max_brightness+1)) * 10)
		if brightness < 2:
			color = C_WARN
		full_text = 'brightness: {}☼'.format(brightness, color, )
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_volume(name='volume', color=C_NORMAL):
	full_text = name
	try:
		volume = '?'
		if False:
			with Popen(['pactl', 'list', 'sinks', ], stdout=PIPE, env=dict(LANG='C', )) as f:
				for l in f.readlines():
					'Description', 'Volume', 'Mute'
		full_text = 'volume: {}♬'.format(volume)
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

def status_time(name='time', color='#dddddd'):
	full_text = name
	try:
		full_text = datetime.now().strftime("%Y-%m-%d %H:%M, %a [%V]")
	except:
		color = C_FATAL
	return dict(name=name, full_text=full_text, color=color, )

if __name__ == '__main__':
	print(dumps((
		status_net(),
		status_disk(),
		status_load(),
		status_temp(),
		status_bat(),
		status_brightness(),
		status_volume(),
		status_time(),
		)))
