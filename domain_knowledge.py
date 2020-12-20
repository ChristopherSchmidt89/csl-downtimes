import csv
import pandas as pd

filename = './edges.csv'

variable_class_dict = {
	'cz':'config',
	'cx':'config',
	'cy':'config',
	'mspeed':'measure',
	'mnumber':'measure',
	's1':'stop',
	's2':'stop',
	'o1':'operational',
	'o2':'operational',
}

def read_edges(filename):
	edges = []
	with open(filename, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)
		for line in reader:
			edges.append((line[0],line[1]))
	return edges

def apply_rules(edges):
	marked_edges = set()
	for e in edges:
		### apply rule 1
		if (e[0][-2:] == '_c' and e[1][-2:] == '_e' and (e[1],e[0]) in edges):
			marked_edges.add(e)
		### apply rule 2
		if (variable_class_dict[e[0][:-2]] =='config' and
			variable_class_dict[e[1][:-2]] !='config' and (e[1],e[0]) in edges):
			marked_edges.add(e)

	return marked_edges

def write_violations(rule_violations, filename):
	with open('./'+filename+'.csv', 'w') as file:
		for v in rule_violations:
			file.write('"'+v[0]+'","'+v[1]+'"\n')

if __name__ == '__main__':
	edges = read_edges(filename)
	rule_violations = apply_rules(edges)
	write_violations(rule_violations, 'rule_violations')