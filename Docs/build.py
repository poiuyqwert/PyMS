PyMS = (1,2,1) * 2
import PyMSUtils, re
infoheaderstart = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<title>%%s [PyMS v%s.%s.%s by poiuy_qwert]</title>
<link rel="stylesheet" type="text/css" href="styles.css"/>
</style>
</head>
<body>
<br><br>
<table align="center" width="80%%%%" height="150px" cellspacing="1">
	<tr>
		<td class="blue" align="center" valign="middle" colspan="3">
			<strong>PyMS</strong><br>
			v%s.%s.%s<br><br>
			By: poiuy_qwert</td>
	</tr>
	<tr height="1">
		<td class="bblue" width="25%%%%">
			<ol>
""" % PyMS
infoheadermid = """			</ol>
		</td>
		<td class="lblue" valign="top">
			<a name="top" class="header">%s</a><br><br>
			%s
			<ol>
"""
files = PyMSUtils.odict()
files['Introduction'] = ['','intro.html']
files['PyGRP'] = ['v3.8','PyGRP.html']
files['PyPAL'] = ['v1.5','PyPAL.html']
files['PyLO'] = ['v1.6','PyLO.html']
files['PyTBL'] = ['v1.7','PyTBL.html']
files['PyTRG'] = ['v2.6','PyTRG.html']
files['PyDAT'] = ['v1.11','PyDAT.html']
files['PyGOT'] = ['v1.2','PyGOT.html']
files['PyAI'] = ['v2.4','PyAI.html']
files['PyICE'] = ['v1.8','PyICE.html']
files['PyFNT'] = ['v1.2','PyFNT.html']
files['PyTILE'] = ['v1.3','PyTILE.html']
files['PyPCX'] = ['v1.0','PyPCX.html']
files['PyMPQ'] = ['v1.0','PyMPQ.html']

def escape(s):
	return s.replace('<','&lt;').replace('>','&gt;')

def tags(s):
	return re.sub('(?<!http:)//(.+?)//', '<i>\\1</i>', \
			re.sub('~\\Z', '<br>', \
			re.sub('__(.+?)__', '<b>\\1</b>', \
			re.sub('\[(\\S+)	(.+?)\]', '<a href="\\1">\\2</a>', escape(s))))).replace('\\n','<br>')

compile = ['intro','pygrp','pypal','pylo','pytbl','pytrg','pydat','pygot','pyai','pyice','pyfnt','pytile','pypcx','pympq']
for c in compile:
	comp = ''
	subheader = False
	closelist = False
	optlist = False
	lastheader = False
	pre = 0
	for n,l in enumerate(open('%s.txt' % c,'r')):
		l = l.rstrip('\n')
		if n == 0:
			out = open(l,'w')
		elif n == 1:
			name = l
			out.write(infoheaderstart % name)
			for n,d in files.iteritems():
				print '%s - %s' % (name, '%s %s' % (n,d[0]))
				if name.split(' ')[0] == n:
					out.write('				<li><b>%s</b>\n' % name)
				else:
					out.write('				<li><a class="tree" href="%s">%s %s</a>\n' % (d[1],n,d[0]))
		elif n == 2:
			out.write(infoheadermid % (name,tags(l)))
		elif optlist:
			if l == ']':
				comp += '</table>\n'
				optlist = False
			else:
				v = list(tags(p) for p in l.split('	'))
				if len(v) == 4:
					if v[3]:
						v[2] += ' <b>Default: %s</b>' % v[3]
					else:
						v[2] += ' <b>Default</b>'
				comp += """	<tr>
		<td class="lblue"><b>%s</b></td>
		<td class="lblue"><b>%s</b></td>
		<td>%s</td>
	</tr>
""" % tuple(v[:3])
		elif pre:
			if l == '>':
				comp += """</pre>
		</td>
	</tr>
</table>
"""
				pre = 0
			else:
				if pre > 1:
					comp += '\n'
				comp += escape(l)
				pre = 2
		else:
			if l.startswith('		'):
				if not subheader:
					subheader = True
					out.write('			<ol>\n')
				if not lastheader:
					comp += '<br><br>'
					lastheader = False
				txt,ref = l[2:].split('	')
				out.write('				<li><a href="#%s">%s</a>\n' % (ref,txt))
				comp += '<a name="%s" class="subheader">%s</a><a href="#top" class="top">^</a><br><br>\n' % (ref,txt)
			elif l.startswith('	'):
				if subheader:
					out.write('			</ol>\n')
					subheader = False
				txt,ref = l[1:].split('	')
				out.write('				<li><a href="#%s">%s</a>\n' % (ref,txt))
				comp += '<br><br><a name="%s" class="header">%s</a><a href="#top" class="top">^</a><br><br>\n' % (ref,txt)
				lastheader = True
			elif l == '+u':
				comp += '</ul>\n'
				lastheader = False
			elif l == '+o':
				comp += '</ol>\n'
				lastheader = False
			elif l.startswith('+'):
				if closelist:
					comp += '</ul>\n'
				comp += '<b>%s</b>\n<ul>\n' % tags(l[1:])
				closelist = True
				lastheader = False
			elif l.startswith(' -'):
				comp += '	<li>%s\n' % tags(l[2:])
				lastheader = False
			elif l == ' +u':
				comp += '<ul>\n'
				lastheader = False
			elif l == ' +o':
				comp += '<ol>\n'
				lastheader = False
			elif l == '[':
				comp += """<table width="100%%">
	<tr>
		<td class="blue" width="10%%"><b>Option</b></td>
		<td class="blue" width="15%%"><b>Long Option</b></td>
		<td class="blue"><b>Description</b></td>
	</tr>
"""
				optlist = True
				lastheader = False
			elif l.startswith('<'):
				comp += """<table align="center" width="95%%" class="pre">
	<tr>
		<td class="pblue"><b>%s</b></td>
	</tr>
	<tr>
		<td class="pre">
			<pre>""" % l[1:]
				pre = 1
				lastheader = False
			elif l.startswith('{'):
				fs = l[1:].split('	')
				prev = ''
				if fs[0]:
					prev = '<a class="nav" href="%s">&#171; %s</a></td>' % (files[fs[0]][1], fs[0])
				next = ''
				if fs[1]:
					next = '<a class="nav" href="%s">%s &#187;</a>' % (files[fs[1]][1], fs[1])
				if subheader:
					out.write('			</ol>\n')
				out.write("""			</ol>
		</td>
	</tr>
</table>\n""" + comp + """<br><br><br><br>
<table align="center" width="80%%"  cellspacing="1">
	<tr>
		<td class="blue" width="20%%">%s</td>
		<td class="blue" align="center"><a class="nav" href="#top">%s</a></td>
		<td class="blue" width="20%%" align="right">%s</td>
	</tr>
</table>
</body>
</html>""" % (prev, name.split(' ')[0], next))
				out.close()
				break
			else:
				comp += tags(l) + '<br>\n'

raw_input()