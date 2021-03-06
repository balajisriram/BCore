from verlib import NormalizedVersion as Ver
import numpy as np

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class Criterion(object):

    def __init__(self, name='Unknown'):
        self.name = name
        self.ver = Ver('0.0.1')

    def __repr__(self):
        return "Criterion object"

    def check_criterion(self, **kwargs):
        return False


class NumTrialsDoneCriterion(Criterion):
    """
        NUMTRIALDONECRITERION - graduate after 'n' trials are done. Note: because it works on compiled_record and because
        compiled_records are created after checking for graduation, current trial's data will not be available before
        checking for graduation.
    """

    def __init__(self, num_trials=100, num_trials_mode='global', name='Unknown'):
        super(NumTrialsDoneCriterion, self).__init__(name)
        self.ver = Ver('0.0.1')
        self.num_trials = num_trials
        self.num_trials_mode = num_trials_mode

    def __repr__(self):
        return "NumTrialsDoneCriterion object, n:%d mode:%s", (self.num_trials, self.num_trials_mode)

    def check_criterion(self, compiled_record, trial_record, **kwargs):
        # trial_number = np.append(np.asarray(compiled_record['trial_number']),np.asarray(trial_record['trial_number']))
        # current_step = np.append(np.asarray(compiled_record['current_step']),np.asarray(trial_record['current_step']))
        # protocol_name = np.append(np.asarray(compiled_record['protocol_name']),np.asarray(trial_record['protocol_name']))
        # protocol_ver = np.append(np.asarray(compiled_record['protocol_version_number']),np.asarray(trial_record['protocol_version_number']))
        trial_number = np.asarray(compiled_record['trial_number'])
        current_step = np.asarray(compiled_record['current_step'])
        protocol_name = np.asarray(compiled_record['protocol_name'])
        protocol_ver = np.asarray(compiled_record['protocol_version_number'])
        # filter out trial_numbers for current protocol_name and protocol_ver
        current_step = current_step[np.bitwise_and(protocol_name==protocol_name[-1],protocol_ver==protocol_ver[-1])]
        trial_number = trial_number[np.bitwise_and(protocol_name==protocol_name[-1],protocol_ver==protocol_ver[-1])]

        # print('current_step:',current_step)
        # print('current_step[-1]:',trial_record['current_step'])
        # print('current_step==current_step[-1]',current_step==trial_record['current_step'])

        # filter out trial_numbers where step==current_step
        # print('trial_number::',trial_number)
        temp = trial_number[current_step==trial_record['current_step']]
        # print('temp_pre:',temp)
        # print(np.asarray([-1]))
        # print(np.asarray([trial_record['trial_number']]))
        temp = np.append(np.append(np.asarray([-1]),temp),np.asarray([trial_record['trial_number']]))
        # print('temp::',temp)
        if self.num_trials_mode == 'consecutive':
            jumps = np.array(np.where(np.diff(temp)!=1)) # jumps in trial number
            try:
                tr_for_current_sequence = temp[jumps[0,-1]+1]
                nT = trial_record['trial_number'] - tr_for_current_sequence +1
            except IndexError:
                nT = 0
        else:  # 'global'
            nT = np.sum(current_step==current_step[-1])
        # print('nT::',nT)
        if nT >= self.num_trials:
            graduate = True
        else:
            graduate = False
        print("NUMTRIALSDONECRITERION:CHECK_CRITERION::graduate=%s, nT=%d" % (graduate, nT))
        return graduate


class PerformanceCriterion(Criterion):

    def __init__(self, pct_correct=0.8, num_trials=200, num_trials_mode='global', name='Unknown'):
        super(PerformanceCriterion, self).__init__(name)
        self.ver = Ver('0.0.1')
        self.pct_correct = pct_correct
        self.num_trials = num_trials
        self.num_trials_mode = num_trials_mode

    def __repr__(self):
        return "PerformanceCriterion object, (%s in %s trials, mode:%s)", (self.pct_correct, self.num_trials, self.num_trials_mode)


    def check_criterion(self, compiled_record, trial_record, **kwargs):
        trial_number = np.asarray(compiled_record['trial_number'])
        current_step = np.asarray(compiled_record['current_step'])
        correct = np.asarray(compiled_record['correct'])
        protocol_name = np.asarray(compiled_record['protocol_name'])
        protocol_ver = np.asarray(compiled_record['protocol_version_number'])

        # filter out trial_numbers for current protocol_name and protocol_ver
        current_step = current_step[np.bitwise_and(protocol_name==protocol_name[-1],protocol_ver==protocol_ver[-1])]
        trial_number = trial_number[np.bitwise_and(protocol_name==protocol_name[-1],protocol_ver==protocol_ver[-1])]
        correct = correct[np.bitwise_and(protocol_name==protocol_name[-1],protocol_ver==protocol_ver[-1])]

        if self.num_trials_mode == 'consecutive':
            jumps = np.where(np.diff(trial_number)!=1) # jumps in trial number
            if not jumps[0]:
                which_trials = trial_number
            else:
                which_trials = trial_number[jump[0][-1]:] # from the last jump
        else:
            which_trials = trial_number

        if np.size(which_trials)<self.num_trials:
            graduate = False # dont graduate if the number of trials less than num required
        else:
            which_trials = which_trials[-self.num_trials:]
            filter =  np.isin(trial_number,which_trials)
            correct = correct[filter]
            perf = np.sum(correct)/np.size(correct)
            if perf >self.pct_correct:
                graduate = True
            else:
                graduate = False

        return graduate


class RateCriterion(Criterion):

    def __init__(self, trials_per_minute=10, consecutive_minutes=5, name='Unknown'):
        super(PerformanceCriterion, self).__init__(name)
        self.ver = Ver('0.0.1')
        self.trials_per_minute = trials_per_minute
        self.consecutive_minutes = consecutive_minutes

    def __repr__(self):
        return "RateCriterion object, (%s trials/minute for %s minutes)", (self.trials_per_minute, self.consecutive_minutes)

    def check_criterion(self, compiled_record, trial_record, station, **kwargs):
        Graduate = False
        raise NotImplementedError()
        return graduate


class RepeatIndefinitely(Criterion):

    def __init__(self, name='Unknown'):
        self.ver = Ver('0.0.1')
        super(RepeatIndefinitely, self).__init__(name)

    def __repr__(self):
        return "RepeatIndefinitely object"

    def check_criterion(self, **kwargs):
        return False
