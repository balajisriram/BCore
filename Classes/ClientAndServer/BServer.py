import os

from BCore import getBaseDirectory, getIPAddr


class BServer:
    """
        BSERVER  keeps track of all the stations that it commands,
        which subjects are allowed in which station and data storage locations.
            serverID            : string Identifier
            serverDataPath      : allowed data storage location
            serverIP            : IPV4 value
            stations            : list of stations
            subjects            : list of subjects
            assignments         : dictionary with keys being subjectID
                                and values being list of stationIDs
            revisionControl     : dictionary with access to details about
                                the repository
    """

    def __init__(server, **kwargs):
        if len(kwargs) == 0:
            # use standard location for path
            server = os.path.join(
                getBaseDirectory(), 'BServerData', 'database')
        elif len(kwargs) == 1 and 'BServerPath' in kwargs:
            pass
            #server = load
        if (
            len(kwargs) > 2) or (
                'serverID' not in kwargs) or (
                    'serverDataPath' not in kwargs):
            raise ValueError(
                'No more than 2 arguments to BServer\
                (''serverID'' and ''serverDataPath'') for initialization')
        server.version = '0.0.1'  # Feb 5, 2014
        server.serverID = kwargs['serverID']
        server.serverDataPath = kwargs['serverDataPath']
        server.serverIP = getIPAddr()
        server.log = []
        server.stations = []
        server.subjects = []
        server.assignments = {}
        server.database = []

    def _setupPaths(server):
        # create 'BServerData'
        os.path.mkdir(os.path.join(getBaseDirectory, 'BServerData'))
        # create 'ServerData','Stations','PermanentTrialRecordStore' in
        # BServerData
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'ServerData'))
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'StationData'))
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'TrialData'))
        # create 'replacedDBs' in 'ServerData'
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'ServerData', 'replacedDBs'))
        # create 'Full' and 'Compiled' in 'TrialData'
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'TrialData', 'Full'))
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'TrialData', 'Compiled'))

    def addStation(server, newStation):
        if newStation.stationID in server.getStationIDs():
            raise ValueError('Station IDs have to be unique')
        server.stations.append(newStation)

    def addSubject(server, newSubject, newAssignment):
        if newSubject in server.subjects:
            raise ValueError('Cannot add replica of subjects to BServer')
        if not(any(newAssignment in server.getStationIDs())):
            raise ValueError('Cannot add new subject to non existent stations')
        server.subjects.append(newSubject)
        server.assignment[newSubject.subjectID] = newAssignment

    def changeAssignment(server, subject, newAssignment):
        if subject not in server.subjects:
            raise ValueError('Cannot change assignment on a subject \
            that is not on Bserver')
        if not(any(newAssignment in server.getStationIDs())):
            raise ValueError('Cannot assign subject to non existent stations')
        server.assignment[subject.subjectID] = newAssignment

    def getStationIDs(server):
        stationIDs = []
        for station in server.stations:
            stationIDs.append(station.stationID)
        return stationIDs

    def getSubjectIDs(server):
        subjectIDs = []
        for subject in server.subjects:
            subjectIDs.append(subject.subjectID)
        return subjectIDs

if __name__ == "__main__":
    print("here")
