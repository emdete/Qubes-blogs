#!/usr/bin/env python3
from datetime import datetime
from subprocess import Popen, PIPE
from json import dumps

def status_qubes(color='#00ff00'):
	try:
		with Popen(['qvm-ls', '--raw-data', 'name', 'on', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			count = len([l for l in f.stdout.readlines() if l.strip()[-1] == 42])
		return '"name":"qubes","full_text":"{} Qubes","color":"{}"'.format(count, color)
	except:
		return '"name":"qubes","full_text":"qubes","color":"#ff0000"'

def status_qubes_net(netvm='sys-net', color='#00ff00'):
	try:
		with Popen(['qvm-run', '--passeio', netvm, 'ip route', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			dev = [l.split()[4] for l in f.stdout.readlines() if l.split()[0]==b'default']
		if not dev:
			color = '#ff0000'
			dev = 'None'
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
		return '"name":"net","full_text":"{}: {} ({})","color":"{}"'.format(dev, ip, ssid, color)
	except:
		return '"name":"net","full_text":"net","color":"#ff0000"'

def status_net(color='#00ff00'):
	try:
		dev = None
		with Popen(['ip', 'route', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			for l in f.stdout.readlines():
				l = l.split()
				if l[0] == b'default':
					p = l.index(b'dev')
					dev = l[p+1]
		if not dev:
			color = '#ff0000'
			dev = 'lo'
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
		return '"name":"net","full_text":"{}: {} ({})","color":"{}"'.format(dev, ip, ssid, color)
	except:
		return '"name":"net","full_text":"net","color":"#ff0000"'

def status_disk(color='#00ff00'):
	try:
		with Popen(['df', '--output=pcent', '/rw', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			pcent = int(f.stdout.read().strip().split()[1][:-1])
		if pcent > 85:
			color = '#ff0000'
		return '"name":"sdd","full_text":"sdd: {}%","color":"{}"'.format(pcent, color, )
	except:
		return '"name":"sdd","full_text":"sdd","color":"#ff0000"'

def status_bat(color='#00ff00'):
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
			color = '#ff0000'
		return '"name":"bat","full_text":"bat: {}{}%","color":"{}"'.format(status_chr, capacity, color, )
	except:
		return '"name":"bat","full_text":"bat","color":"#ff0000"'

def status_load(color='#00ff00'):
	try:
		with Popen(['uptime', ], stdout=PIPE, env=dict(LANG='C', )) as f:
			load = float(f.stdout.read().strip().split()[-3][:4])
		if load > 3.0:
			color = '#ff0000'
		return '"name":"load","full_text":"load: {}","color":"{}"'.format(load, color)
	except:
		return '"name":"load","full_text":"load","color":"#ff0000"'

def status_xen_cpu(color='#00ff00'):
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
			color = '#ff0000'
		return '"name":"cpu","full_text":"cpu: {:.1f}%","color":"{}"'.format(cpu, color)
	except:
		return '"name":"cpu","full_text":"cpu","color":"#ff0000"'

def status_temp(color='#00ff00'):
	try:
		with open('/sys/devices/platform/coretemp.0/hwmon/hwmon1/temp1_input') as f:
			temp = int(f.readline().strip()) // 1000
		return '"name":"temp","full_text":"temp: {}°","color":"{}"'.format(temp, color, )
	except:
		return '"name":"temp","full_text":"temp","color":"#ff0000"'

def status_brightness(color='#00ff00'):
	try:
		with open('/sys/devices/pci0000:00/0000:00:02.0/backlight/acpi_video0/max_brightness') as f:
			max_brightness = int(f.readline().strip())
		with open('/sys/devices/pci0000:00/0000:00:02.0/backlight/acpi_video0/actual_brightness') as f:
			actual_brightness = int(f.readline().strip())
		brightness = int((actual_brightness / (max_brightness+1)) * 10)
		return '"name":"brightness","full_text":"brightness: {}☼","color":"{}"'.format(brightness, color, )
	except:
		return '"name":"brightness","full_text":"brightness","color":"#ff0000"'

def status_volume(color='#00ff00'):
	try:
		volume = '?'
		if False:
			with Popen(['pactl', 'list', 'sinks', ], stdout=PIPE, env=dict(LANG='C', )) as f:
				for l in f.readlines():
					'Description', 'Volume', 'Mute'
		return '"name":"volume","full_text":"volume: {}♬","color":"{}"'.format(volume, color, )
	except:
		return '"name":"volume","full_text":"volume","color":"#ff0000"'

def status_time(color='#bbbbbb'):
	try:
		return '"name":"time","full_text":"{}","color":"{}"'.format(datetime.now().strftime("%Y-%m-%d %H:%M, %a [%V]"), color, )
	except:
		return '"name":"time","full_text":"time","color":"#ff0000"'

if __name__ == '__main__':
	print(',[{{{}}}]'.format('},{'.join([s for s in (
		status_net(),
		status_disk(),
		status_load(),
		status_temp(),
		status_bat(),
		status_brightness(),
		status_volume(),
		status_time(),
		) if s])))
