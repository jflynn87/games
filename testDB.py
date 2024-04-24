#connect to mysql db
# import MySQLdb
# import sshtunnel
# import subprocess



# sshtunnel.SSH_TIMEOUT = 5.0
# sshtunnel.TUNNEL_TIMEOUT = 5.0

# with sshtunnel.SSHTunnelForwarder(
#     ('ssh.pythonanywhere.com'),
#     ssh_username='jflynn87', ssh_password='hawks123',
#     remote_bind_address=('jflynn87.mysql.pythonanywhere-services.com', 3306)
# ) as tunnel:
#     connection = MySQLdb.connect(
#         user='jflynn87',
#         passwd='games2018',
#         host='127.0.0.1', port=tunnel.local_bind_port,
#         db='jflynn87$orig_games',
#     )
#     #mycursor = connection.cursor()
#     #mycursor.execute("Show tables;")
#     #myresult = mycursor.fetchall()
#     #for x in myresult:
#     #    print(x)
#     #connection.close()
#     f = open('zfile.sql', 'wb')
#     #cmd = "mysqldump --user=jflynn87 --port=3306 --password=games2018 jflynn87$orig_games".format(**locals())
#     cmd = "ssh -t jflynn87@ssh.pythonanywhere.com mysqldump --user=jflynn87 --port=3306 --password=games2018 jflynn87$orig_games".format(**locals())
#     p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     p.communicate(input='hawks123\n')
#     for line in p.stdout.readlines():
#         f.write(line)
#     #with open('zfile.sql','w') as output:
#         #c = subprocess.Popen(cmd,
#         #                 stdout=output, shell=True)

#!/usr/bin/python

# Run with:
#   python hello.py cameron
#   python hello.py


# import modules used here -- sys is a very standard one
import sys
import subprocess
import getpass
import ConfigParser
import os
import pexpect
import datetime
# from subprocess import Popen, PIPE, STDOUT

# Gather our code in a main() function
def main():

  # print 'Number of arguments: ', len(sys.argv)
  config = ConfigParser.ConfigParser()
  config.read('dump.cfg')

  for db in config.sections():
    if config.getboolean(db, 'active'):
      print config.items(db)
      host = config.get(db, 'host')
      database = config.get(db, 'host')
      user = config.get(db, 'user')
      if not os.path.exists(host):
        os.mkdir(host)
      dump_file = open(host + '/' + database + '_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.sql.gz', "w")
      subprocess.Popen(['ssh', host, 'mysqldump -u\'' + user + '\' -p \'' + database + '\' | gzip -3 -c'], stdin=subprocess.PIPE, stdout=dump_file)
      # subprocess.Popen(['echo', 'MamaIkilledher'+user], stdout=dump_file)
      # mkdir -p "$MYSQLDUMP_HOST" && ssh $MYSQLDUMP_HOST "mysqldump -u'$MYSQLDUMP_USER' -p '$MYSQLDUMP_DB' | gzip -3 -c" > "$MYSQLDUMP_HOST/${MYSQLDUMP_DB}_`date +%Y%m%d_%H%M%S`.sql.gz"
      dump_file.close();

  sys.exit(0)

  host = sys.argv[1]
  database = sys.argv[2]
  # while 1:
  #   try:
  #     line = sys.stdin.readline()
  #   except KeyboardInterrupt:
  #     break

  #   if not line:
  #     break
  #   # ssh aap-dev "mysqldump -uroot -p altech_autopage | gzip -3 -c" > altech_autopage_`date +%Y%m%d_%H%M%S`.sql.gz
  #   print line.strip()
  filename = database+"_"+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+".sql.gz"
  dumpfile = open(filename, 'w')
  # p = Popen(['grep', 'f'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
  # subprocess.call(['ls', '-l'], stdout=dumpfile)
  passs = getpass.getpass("Key password: ")
  p = subprocess.Popen(["ssh", host, "mysqldump -uroot -p "+database+" | gzip -3 -c"], stdin=subprocess.PIPE, stdout=dumpfile, preexec_fn=os.setsid)
  # p.communicate(input=passs+'\ntwo\nthree\nfour\nfive\nsix\n')[0]
  # p.communicate(input=passs)[0]
  print passs
  p.stdin.write(passs+"\n")
  # subprocess.call(["ssh", "aap-dev", "mysqldump -uroot -p'"+passs+"' altech_autopage | gzip -3 -c"], stdout=dumpfile)

def ssh_command (user, host, password, command):
    """This runs a command on the remote host. This could also be done with the
    pxssh class, but this demonstrates what that class does at a simpler level.
    This returns a pexpect.spawn object. This handles the case when you try to
    connect to a new host and ssh asks you if you want to accept the public key
    fingerprint and continue connecting. """

    ssh_newkey = 'Are you sure you want to continue connecting'
    child = pexpect.spawn('ssh -l %s %s %s'%(user, host, command))
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
    if i == 0: # Timeout
        print 'ERROR!'
        print 'SSH could not login. Here is what SSH said:'
        print child.before, child.after
        return None
    if i == 1: # SSH does not have the public key. Just accept it.
        child.sendline ('yes')
        child.expect ('password: ')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0: # Timeout
            print 'ERROR!'
            print 'SSH could not login. Here is what SSH said:'
            print child.before, child.after
            return None       
    child.sendline(password)
    return child

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()        