from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import InitCommandContext, ResourceCommandContext
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from auxiliary import SafeCloudShellAPISession
import time



class QaTestingScriptsDriver (ResourceDriverInterface):

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """

        pass


    def CreateTopologyWithNApps(self,context,n, topology_name, app_name):

        # cast input to appropriate type
        n = int(n)

        api_session = self._api_session(context)
        res_id = api_session.CreateImmediateReservation('Apps', api_session.username, 5).Reservation.Id
        for i in range(n):
            api_session.AddAppToReservation(res_id, str(app_name))
        api_session.SaveReservationAsTopology(res_id, '', str(topology_name))
        api_session.EndReservation(res_id)
        return topology_name

    def RemoveAllResources(self,context,res_id):
        api_session = self._api_session(context)
        reservation = api_session.GetReservationDetails(res_id).ReservationDescription
        for resource in reservation.Resources:
            api_session.RemoveResourcesFromReservation(res_id, [resource.Name])

    def KillAllReservations(self,context):
        api_session =self._api_session(context)
        current = api_session.GetCurrentReservations(api_session.username)
        current_reservation_id = context.reservation.reservation_id
        if len(current.Reservations) == 0:
            return 'there were no live reservations'
        else:
            for res in current.Reservations:
                if res.Id != current_reservation_id:
                    api_session.EndReservation(res.Id)
            return 'Killed %d resevations' % len(current.Reservations)

    def CreateConnectedBridges(self,context,numberBridges=2, numberPorts=10, folderName='Bridges', panelName='The Panel',
                               bridgeName='Bridge', override=False):

        # cast input to appropriate type
        numberBridges = int(numberBridges)
        numberPorts = int (numberPorts)
        override = override == 'True'

        api_session = self._api_session(context)
        safe_session = self._safe_session(context)
        session = api_session
        if override:
            test = False
            for item in api_session.GetFolderContent().ContentArray:
                if item.Name == folderName and item.Type == 'Folder':
                    test = True
                    break
            if test:
                api_session.DeleteFolder(folderName)
        else:
            session = safe_session

        api_session.CreateFolder(folderName)
        panel = session.CreateResource('PatchPanel', 'Generic PatchPanel', resourceName=panelName,
                                       resourceAddress='Panelia', folderFullPath=folderName)
        api_session.UpdateResourceDriver(panel.Name, 'Patch Panel Driver')
        for i in range(numberBridges):
            bridge = session.CreateResource('Bridge', 'Bridge Generic Model', resourceName=bridgeName + str(i + 1),
                                            resourceAddress='Brigerabia ' + str(i + 1), folderFullPath=folderName)
            for j in range(numberPorts):
                num = numberPorts * i + j + 1
                port = api_session.CreateResource('Bridge Port', 'Bridge Port Generic Model', 'Port' + str(j),
                                                  'Brigeportia ' + str(num), folderName, bridge.Name)
                jack = api_session.CreateResource('Panel Jack', 'Generic Jack', 'Jack' + str(num),
                                                  'Jackville ' + str(num),
                                                  folderName, panel.Name)
                api_session.UpdatePhysicalConnection(port.Name, jack.Name)

    def CreateUsers(self,context):

        api_session = self._api_session(context)
        Westcost = {'Odd Future': ['Tyler the Creator', 'Earl sweatshirt', 'Domo Genesis'],
                    'Alternative': ['Childish Gambino', 'Flying Lotus'],
                    'Death Row': ['Tupac Shakur', 'Snoop Dog', 'Dr. Dre']}
        Eastcoast = {'Wu Tang': ['RZA', 'Ghostface Killa', "Ol' Dirty Basterd"],
                     'Mock Southern': ['Bobby Shmurda', 'Di$igner'],
                     'Old School Masters': ['Biggie', 'Big Pun', 'Diddy', 'JayZ']}
        DirtySouth = {'Outkast': ['Andre3000', 'BigBoi'], 'New Atlanta': ['Young Thug', 'Future', 'Travi$ scott'],
                      'Trap Lords': ['T.I', 'Young Jeezy', 'Gucci Maine']}
        allDomains = {'Westcost': Westcost, 'Eastcoast': Eastcoast, 'DirtySouth': DirtySouth}
        kindOfUsers = ['External', 'Regular', 'DomainAdmin']

        for domain in allDomains:
            api_session.AddNewDomain(domain)
            index = 0
            for group in allDomains[domain]:
                api_session.AddNewGroup(group, '', kindOfUsers[index % 3])
                api_session.AddGroupsToDomain(domain, [group])
                index += 1
                for user in allDomains[domain][group]:
                    api_session.AddNewUser(user, 'admin', 'fake@quali.com', True)
                    api_session.AddUsersToGroup([user], group)

    def CreatevCenter(self,context,vmLocation,name='VMware vCenter'):

        api_session = self._api_session(context)
        attributes = {'User': 'Automation', 'Password': 'qs@L0cal', 'Default Datacenter': 'QualiSB',
                      'VM Storage': 'eric ds cluster', 'Holding Network': 'Anetwork', 'VM Location': vmLocation,
                      'Default dvSwitch': 'dvSwitch', 'VM Cluster': 'QualiSB Cluster', 'VM Resource Pool': 'LiverPool',
                      'Shutdown Method': 'hard', 'Execution Server Selector': '',
                      'OVF Tool Path': 'C:\Program Files (x86)\VMware\VMware Workstation\OVFTool\ovftool.exe',
                      'Reserved Networks': ''}
        family = 'Cloud Provider'
        model = 'VMware vCenter'
        address = '192.168.42.110'
        driver = 'VCenter Shell Driver'
        vcenter = api_session.CreateResource(family, model, name, address)
        for attribute in attributes:
            api_session.SetAttributeValue(vcenter.Name, attribute, attributes[attribute])
        api_session.UpdateResourceDriver(name, driver)


    def CreateManyReservations(self,context,topology, name=None, num=10, duration=5, delta=None,owner='admin',
                               offset=0):

        # cast input to appropriate type
        num = int(num)
        duration = int(duration)
        offset = int(offset)
        if delta == 'None':
            delta = duration
        if name == 'None':
            name = topology

        api_session = self._api_session(context)
        offset *= 60
        duration *= 60
        delta *= 60
        fail = 0
        t = time.time() + offset
        for i in range(num):
            try:
                res = api_session.CreateTopologyReservation(reservationName=name + '_' + str(i), owner=owner,
                                                            startTime=self.FormatTime(t),
                                                            endTime=self.FormatTime(t + duration), topologyFullPath=topology)
            except CloudShellAPIError as e:
                fail += 1
                print str(i) + ': ' + self.FormatTime(t, time.localtime)

            t += delta
        if fail > 0:
            print '%i function calls have failed' % fail
            print e

    def DeleteAllReservations(self,context):

        api_session = self._api_session(context)
        current_reservation_id = context.reservation.reservation_id
        now = time.time()
        for res in api_session.GetScheduledReservations(self.FormatTime(now), self.FormatTime(now + 604800)).Reservations:
            if res.Id != current_reservation_id:
                api_session.DeleteReservation(res.Id)

    def CreateConnectedChassis(self,context,numberChassis=2, numberBlades=2, numberPorts=10, override=False, panelName='Panel',
                               chassisName='Chassis', folderName='Chassis'):

        # cast input to appropriate type
        numberChassis = int(numberChassis)
        numberBlades = int(numberBlades)
        numberPorts = int(numberPorts)
        override = override == 'True'

        api_session = self._api_session(context)
        safe_session = self._safe_session(context)
        session = api_session
        if override:
            test = False
            for item in api_session.GetFolderContent().ContentArray:
                if item.Name == folderName and item.Type == 'Folder':
                    test = True
                    break
            if test:
                api_session.DeleteFolder(folderName)
        else:
            session = safe_session

        api_session.CreateFolder(folderName)
        panel = session.CreateResource('PatchPanel', 'Generic PatchPanel', resourceName=panelName,
                                       resourceAddress='Panelia', folderFullPath=folderName)
        api_session.UpdateResourceDriver(panel.Name, 'Patch Panel Driver')
        for i in range(numberChassis):
            chassis = session.CreateResource('Generic Chassis', 'Generic Chassis Model',
                                             resourceName=chassisName + str(i + 1),
                                             resourceAddress='Chassistan ' + str(i + 1), folderFullPath=folderName)
            for j in range(numberBlades):
                blade = api_session.CreateResource('Generic Blade', 'Generic Blade Model', 'Blade' + str(j + 1),
                                                   'Bladnitrova ' + str(j + 1), folderName, chassis.Name)
                for k in range(numberPorts):
                    num = i * numberBlades * numberPorts + j * numberPorts + k + 1
                    port = api_session.CreateResource('Generic Port', 'Generic Ethernet Port', 'Port' + str(k + 1),
                                                      'Portlandia ' + str(k + 1), folderName, blade.Name)
                    jack = api_session.CreateResource('Panel Jack', 'Generic Jack', 'Jack' + str(num),
                                                      'Jackville ' + str(num),
                                                      folderName, panel.Name)
                    api_session.UpdatePhysicalConnection(port.Name, jack.Name)

    def _api_session(self, context):
        '''

        :param ResourceCommandContext context: the context the command runs on
        :rtype CloudShellAPISession
        '''
        return CloudShellAPISession(host=context.connectivity.server_address,
                                    token_id=context.connectivity.admin_auth_token,
                                    domain=context.reservation.domain)

    def _safe_session(self, context):
        '''

        :param ResourceCommandContext context: the context the command runs on
        :rtype SafeCloudShellAPISession
        '''

        return SafeCloudShellAPISession(host=context.connectivity.server_address,
                                        token_id=context.connectivity.admin_auth_token,
                                        domain=context.reservation.domain)

    def FormatTime(self, t, func=time.gmtime):
        return time.strftime("%m/%d/%Y %H:%M", func(t))





