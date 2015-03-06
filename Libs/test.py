import CHK

c = CHK.CHK()
c.load_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/scenario2.chk')

f = open('scenario2.txt','w')
for k,v in c.sections.iteritems():
	f.write(v.decompile() + '\n\n')
f.close()

c.save_file('test.chk')