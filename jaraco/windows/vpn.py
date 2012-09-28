import os
from path import path

def params_to_lines(params):
	return ('{key}={value}\n' for key, value in params.iteritems())

def install_pptp(name, **params):
	"""
	"""
	# or consider using the API: http://msdn.microsoft.com/en-us/library/aa446739%28v=VS.85%29.aspx
	pbk_path = (path(os.environ['PROGRAMDATA'])
		/ 'Microsoft' / 'Network' / 'Connections' / 'pbk' / 'rasphone.pbk')
	pbk_path.dirname().makedirs_p()
	with open(pbk_path, 'a') as pbk:
		pbk.write('[{name}]\n'.format(name=name))
		pbk.writelines(params_to_lines(params))
		pbk.write('\n')
