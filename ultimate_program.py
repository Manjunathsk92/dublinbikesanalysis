







from subprocess import call
text = open('ultimate_program.py','r').read()
print(text)
call(['killall','python'])
