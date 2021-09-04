import os

i = int(os.environ.get('SETUP_RAN', '0'))
i += 1
os.environ['SETUP_RAN'] = str(i)
