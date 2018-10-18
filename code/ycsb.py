import os
from functools import reduce

workload_num = 12

def generate_workload(project_path):
  distribution_attr = ['readproportion', 'updateproportion', 'insertproportion', 'scanproportion']
  distribution = [(0.48, 0.03, 0.47, 0.02), 
                  (0.05, 0.03, 0.90, 0.02), 
                  (0.90, 0.03, 0.05, 0.02), 
                  (0.25, 0.05, 0.25, 0.45), 
                  (0.05, 0.05, 0.45, 0.45), 
                  (0.45, 0.05, 0.05, 0.45), 
                  (0.25, 0.45, 0.25, 0.05), 
                  (0.05, 0.45, 0.45, 0.05), 
                  (0.45, 0.45, 0.05, 0.05), 
                  (0.03, 0.05, 0.02, 0.90), 
                  (0.03, 0.90, 0.02, 0.05), 
                  (0.03, 0.48, 0.02, 0.47)]

  attributes = {
    'recordcount': 1000000,
    'operationcount': 3000000,
    'workload': 'com.yahoo.ycsb.workloads.CoreWorkload',
    'readallfields': 'true',
    'requestdistribution': 'zipfian' # latest, uniform
  }
  for i in range(workload_num):
    dist = distribution[i]
    filename = project_path + 'workloads/workload' + str(i)
    f = open(filename, 'w')
    for k, v in attributes.items():
      f.write(k + '=' + str(v) + '\n')
    for j in range(len(distribution_attr)):
      f.write(distribution_attr[j] + '=' + str(dist[j]) + '\n')
    f.close()

def get_data(project_path):
  cmdlist = []

  for i in range(workload_num):
    cmd = project_path + 'bin/ycsb.sh load basic -P ' + project_path + 'workloads/workload' + str(i) + ' > ' + dirname + 'data' + str(i) + '_load.in'
    cmdlist.append(cmd)
    cmd = project_path + 'bin/ycsb.sh run basic -P ' + project_path + 'workloads/workload' + str(i) + ' > ' + dirname + 'data' + str(i) + '_run.in'
    cmdlist.append(cmd)

  for cmd in cmdlist:
    print('CMD:' + cmd)
    os.system(cmd)

def clean_data(dirname, prefix, suffix):
  cmdlist = []
  for i in range(workload_num):
    cmd1 = 'rm ' + dirname + prefix + str(i) + '_load' + suffix
    cmd2 = 'rm ' + dirname + prefix + str(i) + '_run' + suffix
    cmdlist.append(cmd1)
    cmdlist.append(cmd2)

  for cmd in cmdlist:
    print('CMD:' + cmd)
    os.system(cmd)


def read(in_filename, out_filename):
  replace_key = [':', ',', ';', '$']
  f = open(in_filename, 'r')
  lines = f.readlines()
  f.close()
  result = []
  for i, l in enumerate(lines):
    if l.startswith('INSERT') or l.startswith('UPDATE') or l.startswith('SCAN') or l.startswith('READ'):
      ls = l.split()
      nls = [ls[0], ls[2]]
      value = ''
      for j in range(3, len(ls)):
        value = value + ls[j] + ' '
      value = value.strip()
      for k in replace_key:
        value = value.replace(k, '0')
      nls.append(value)
      result.append(nls)
  f = open(out_filename, 'a')
  for i, l in enumerate(result):
    line = reduce(lambda x, w: x + '\t' + w, l, '').strip()
    f.write(line + '\n')
  f.close()

if __name__ == '__main__':
  project_path = 'lib/YCSB/'
  dirname = 'data/'
  prefix = 'data'
  suffix = '.in'
  print('GENERATE WORKLOAD')
  generate_workload(project_path)
  print('GET DATA')
  get_data(project_path)
  print('READ DATA')
  for i in range(workload_num):
    in_filename_load = dirname + prefix + str(i) + '_load' + suffix
    in_filename_run = dirname + prefix + str(i) + '_run' + suffix
    out_filename = dirname + prefix + str(i) + suffix
    if os.path.exists(out_filename):
      os.remove(out_filename)
    read(in_filename_load, out_filename)
    read(in_filename_run, out_filename)
  print('CLEAN DATA')
  clean_data(dirname, prefix, suffix)