import sys
import random
import string
import re
from collections import defaultdict
from commons import *

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "usage: " + sys.argv[0] + " Test.csv"
		sys.exit()

	testfile = sys.argv[1]
	inter = load_intersection('data/intersection.csv')

	g = open('data/TestRest.csv', 'w')
	with open(testfile, 'r') as f:
		f.readline() #skip first
		for line in f:
			parts = line.lower().strip(' ').strip('\n').strip('"').split('","', 2)
			if len(parts) < 3: continue
			idd, title, rest = parts
			if idd not in inter:
				g.write(line)
	g.close()

if __name__ == '__main2__':
	if len(sys.argv) < 3:
		print "usage: " + sys.argv[0] + " Train.csv Test.csv"
		sys.exit()

	trainfile = sys.argv[1]
	testfile = sys.argv[2]

	c = 0
	trainhash = dict()
	with open(trainfile, 'r') as f:
		f.readline() #skip first
		for line in f:
			parts = line.lower().strip(' ').strip('\n').strip('"').split('","', 2)
			if len(parts) < 3: continue
			idd, title, rest = parts
			comma = rest.rfind(',')
			body, giventags = rest[:comma-1], rest[comma+2:]

			trainhash[title+body[:8]+body[-8:]] = giventags
			c += 1
			if c % 1000000 == 0:
				print c

	id_tags = dict()
	with open(testfile, 'r') as f:
		f.readline() #skip first
		for line in f:
			parts = line.lower().strip(' ').strip('\n').strip('"').split('","', 2)
			if len(parts) < 3: continue
			idd, title, rest = parts
			comma = rest.rfind(',')
			body = rest[:comma-1]

			bodyhash = title + body[:8] + body[-8:]
			if bodyhash in trainhash:
				id_tags[idd] = trainhash[bodyhash]

	with open('data/intersection.csv', 'w') as g:
		for idd, tags in sorted(id_tags.items()):
			g.write('{},"{}"\n'.format(idd, tags))

