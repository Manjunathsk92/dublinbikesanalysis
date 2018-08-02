from subprocess import call
for i in range(0,60):

    call(['python','test_models.py',str(i)])


