import csv
import pandas as pd

filename = './synthetic_data.csv'
def last(l):
	return l[-1]
def count(l):
	return len(l)
def binary(l):
	return 1 if len(l) > 0 else 0
def mean(l):
	return sum(l)/len(l)
aggregation_dict = {'config':last,
					'operational':count,
					'stop':binary,
					'measure':mean,
					'default':count}

### Note, for simplicity we use a fixed dictionary in our example
### Other options are to use location or indications from the
### message dscription or message_id, to provide an automatic
### mapping of variables to classes
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

class LogMessage:
	def __init__(self, time, sub_id, msg_id, location=None,
				param=None, msg_desc=None):
		self.time 					= time
		self.sub_id 				= sub_id
		self.message_id 			= msg_id
		self.location				= location
		self.parameter_value		= param
		self.message_description	= msg_desc

def parse(filename):
	logMessages = []
	with open(filename, 'r') as f:
		reader = csv.reader(f)
		for line in reader:
			logMessages.append(LogMessage(line[2],line[1],
								line[0],line[3].split('=')[1] if line[3] else line[3],
								float(line[4].split(':')[1]) if line[4] else line[4],
								line[5]))
	return logMessages

def write_to_csv(observations, filename):
	with open('./'+filename+'.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile, observations[0].keys())
		writer.writeheader()
		for l in observations:
			writer.writerow(l)


def get_time_frames(logMessages):
	### Note for simplicity we assume sorted log messages by time
	tf = []
	tf_ramp_up = []
	tf_exec = []
	curTaskStart = None
	curSubTaskStart = None
	taskConfigured = False
	for m in logMessages:
		# bc be ee
		if m.message_id == 'bc':
			curTaskStart = m.time
			curSubTaskStart = m.time
		elif m.message_id == 'be':
			tf_ramp_up.append((curSubTaskStart,m.time))
			curSubTaskStart = m.time
		elif m.message_id == 'ee':
			tf_exec.append((curSubTaskStart,m.time))
			tf.append((curTaskStart,m.time))

	return (tf, tf_ramp_up, tf_exec)

def map_log_messages_to_observation(logMessages, message_ids, timeFrames):
	mapped_messages = []

	mm_dict = {}
	for mid in message_ids[0]:
		mm_dict[mid] = []
	tf_index = 0
	for m in logMessages:
		if m.message_id in ['bc','be','ee']:
			continue
		if m.time < timeFrames[0][0][0]:
			## prior to first time frame
			continue
		if m.time > timeFrames[0][tf_index][1]:
			## get next time frame
			tf_index+=1
			mapped_messages.append(mm_dict)
			mm_dict = {}
			for mid in message_ids[0]:
				mm_dict[mid] = []
		if m.time > timeFrames[0][-1][1]:
			## after last time frame
			break
		if m.time < timeFrames[0][tf_index][0]:
			continue
		if m.time <= timeFrames[1][tf_index][1]:
			## belong to ramp-up phase
			mm_dict[m.message_id+'_c'].append(m.parameter_value) if m.parameter_value else mm_dict[m.message_id+'_c'].append(1)
		else:
			## belong to execution phase
			mm_dict[m.message_id+'_e'].append(m.parameter_value) if m.parameter_value else mm_dict[m.message_id+'_e'].append(1)
	mapped_messages.append(mm_dict)
	return(mapped_messages)	

def get_distinct_message_ids(logMessages, timeFrames):
	### Note we assume both ordered logMessages and ordered timeframes
	message_ids_c = set([])
	message_ids_e = set([])
	tf_index = 0
	for m in logMessages:
		if m.message_id in ['bc','be','ee']:
			continue
		if m.time > timeFrames[0][-1][1]:
			## after last time frame
			break		
		if m.time > timeFrames[0][tf_index][1]:
			## get next time frame
			tf_index+=1
		## message occurs before time frame
		if m.time < timeFrames[0][tf_index][0]:
			continue
		if m.time <= timeFrames[1][tf_index][1]:
			## belong to ramp-up phase
			message_ids_c.add(m.message_id+'_c')
		else:
			## belong to execution phase
			message_ids_e.add(m.message_id+'_e')

	return (message_ids_c.union(message_ids_e), message_ids_c, message_ids_e)

def apply_transformation_rules(mapped_messages):
	observations = []
	for obs in mapped_messages:
		observation = {}
		for var in obs.keys():
			if len(obs[var]) == 0:
				observation[var] = 0
			elif len(obs[var]) == 1:
				observation[var] = obs[var][0]
			else:
				if var[:-2] in variable_class_dict.keys():
					observation[var] = aggregation_dict[variable_class_dict[var[:-2]]](obs[var])
				else:
					### rely on default
					observation[var] = aggregation_dict['default'](obs[var])
		observations.append(observation)
	return observations

def discretize(filename):
	df = pd.read_csv('./'+filename+'.csv')
	for k in variable_class_dict.keys():
		if variable_class_dict[k] == 'measure':
			df[k+'_c'] = pd.cut(df[k+'_c'], bins=5, labels=False)
			df[k+'_e'] = pd.cut(df[k+'_e'], bins=5, labels=False)
	df.to_csv(filename+'_disc.csv',index=False)

if __name__ == '__main__':
	logMessages = parse(filename)
	timeFrames = get_time_frames(logMessages)
	message_ids = get_distinct_message_ids(logMessages, timeFrames)
	mapped_messages = map_log_messages_to_observation(logMessages, message_ids, timeFrames)
	observations = apply_transformation_rules(mapped_messages)
	write_to_csv(observations, 'observations')
	discretize('observations')
	