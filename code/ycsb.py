import os
import numpy as np
from functools import reduce

distribution_attr = ['operationcount', 'readproportion', 'updateproportion', 'insertproportion', 'scanproportion']
distribution = [(200000, 0.50, 0.50, 0.00, 0.00),  # 0  a 50% read 50% update
                (200000, 0.95, 0.05, 0.00, 0.00),  # 1  b 90% read 10% update
                (200000, 0.05, 0.95, 0.00, 0.00),  # 2    10% read 90% update
                (200000, 1.00, 0.00, 0.00, 0.00),  # 3  c 100% read
                (200000, 0.50, 0.50, 0.00, 0.00),  # 4    50% read 50% insert
                (200000, 0.95, 0.00, 0.05, 0.00),  # 5    90% read 10% insert
                (200000, 0.05, 0.00, 0.95, 0.00),  # 6    10% read 90% insert
                (100000, 0.00, 1.00, 0.00, 0.01),  # 7    50% scan 50% update
                (100000, 0.00, 0.50, 0.00, 0.01),  # 8    90% scan 10% update
                (150000, 0.00, 1.90, 0.00, 0.001), # 9    10% scan 90% update
                (1000, 0.00, 0.00, 0.00, 1.00),    # 10   100% scan
                (100000, 0.00, 0.00, 1.00, 0.01),  # 11   50% scan 50% insert
                (100000, 0.00, 0.00, 0.50, 0.01),  # 12 e 90% scan 10% insert
                (150000, 0.00, 0.00, 1.90, 0.001), # 13 e 10% scan 90% insert
                (100000, 1.00, 0.00, 0.00, 0.01),  # 14   50% scan 50% read
                (200000, 0.00, 0.00, 1.00, 0.00),  # 15   100% insert
                (200000, 0.00, 0.50, 0.50, 0.00)]  # 16   50% insert 50% update

attributes = {
  'recordcount': 50000,
  'workload': 'com.yahoo.ycsb.workloads.CoreWorkload',
  'readallfields': 'true',
  'requestdistribution': 'zipfian' # latest, uniform
}
workload_num = len(distribution)
value_len_max = 1000

def generate_workload(project_path):
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

def clean_data(project_path, dirname, prefix, suffix):
  cmdlist = []
  for i in range(workload_num):
    cmd1 = 'rm ' + dirname + prefix + str(i) + '_load' + suffix
    cmd2 = 'rm ' + dirname + prefix + str(i) + '_run' + suffix
    cmd3 = 'rm ' + project_path + 'workloads/workload' + str(i)
    cmdlist.append(cmd1)
    cmdlist.append(cmd2)
    cmdlist.append(cmd3)

  for cmd in cmdlist:
    print('CMD:' + cmd)
    os.system(cmd)

def shuffle(arr):
  np.random.shuffle(arr)

def read(in_filename, out_filename):
  print('Process ' + in_filename)
  replace_key = [':', ',', ';', '$', ' ', '\t']
  f = open(in_filename, 'r')
  lines = f.readlines()
  f.close()
  result = []
  for i, l in enumerate(lines):
    if l.startswith('INSERT') or l.startswith('UPDATE') or l.startswith('SCAN') or l.startswith('READ'):
      ls = l.split()
      op = ls[0]
      key = ls[2][4:]
      if op == 'SCAN':
        st = 4
      else:
        st = 3
      value = ''
      for j in range(st, len(ls)):
        value = value + ls[j] + ' '
      value = value.strip()
      for k in replace_key:
        value = value.replace(k, '0')
      # value = value[:value_len_max]
      if op == 'SCAN':
        suffix = ls[3]
        value = key[:len(key) - len(suffix)]
        for s in suffix:
          value = value + s
        if int(key) > int(value):
          t = key
          key = value
          value = t
      result.append([op, key, value])
  shuffle(result)
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
  clean_data(project_path, dirname, prefix, suffix)
