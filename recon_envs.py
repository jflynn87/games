from pip._internal.utils.misc import get_installed_distributions
import pprint

def get_env_file():
    d = {}
    for package in get_installed_distributions():
        #print (package, vars(package))
        d[package.project_name] = {'ver': package.version}

    return d

def get_requirements_file():
    d = {}
    f = open("requirements.txt", "r")
    for line in f.readlines():
        if len(line.split('==')) > 1:
            d[line.split('==')[0].strip()] = {'ver': line.split('==')[1].strip()}
        else:
            print (line)

    return d

def recon():
    env = get_env_file()
    req = get_requirements_file()

    for k, v in req.items():
        if not env.get(k):
            print ('package not in env', k)
        elif env.get(k).get('ver') != v.get('ver'):
            print ('ver mismatch', k, v, env.get(k))
        else:
            print ("OK", k)
    return

print (recon())