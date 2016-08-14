from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.api.cloudshell_api import CloudShellAPISession
from collections import OrderedDict

def safefy(name_arge):
    def safefyName(creatfunction):
        def safecreate(*args,**kwargs):
            numbers = False
            name = kwargs[name_arge]
            i = 97
            while True:
                try:
                    return creatfunction(*args,**kwargs)
                except CloudShellAPIError as e:
                    if e.code == '114':
                        kwargs[name_arge] = name
                        if numbers:
                            kwargs[name_arge] += '_{0}'.format(str(i - 122))
                        else:
                            kwargs[name_arge] += '_{0}'.format(chr(i))
                    else:
                        raise
                if i == 122:
                    numbers = True
                i += 1
        return safecreate
    return safefyName

class SafeCloudShellAPISession(CloudShellAPISession):
    @safefy('resourceName')
    def CreateResource(self, resourceFamily='', resourceModel='', resourceName='', resourceAddress='',
                       folderFullPath='', parentResourceFullPath='', resourceDescription=''):
        """
            Adds a new resource.

            :param str resourceFamily: Specify the name of the resource family.
            :param str resourceModel: Specify the resource model.
            :param str resourceName: Specify the resource name.
            :param str resourceAddress: Specify the resource address.
            :param str folderFullPath: Specify the full folder name. Include the full path from the root to a specific folder, separated by slashes. For example: ResourceFamilyFolder/ResourceModelFolder.
            :param str parentResourceFullPath: Specify the full path from the root to a parent resource, separated by slashes. For example: Traffic Generators/Generic.
            :param str resourceDescription: Provide a short description to help identify the resource.

            :rtype: ResourceInfo
        """
        return self.generateAPIRequest(OrderedDict(
            [('method_name', 'CreateResource'), ('resourceFamily', resourceFamily), ('resourceModel', resourceModel),
             ('resourceName', resourceName), ('resourceAddress', resourceAddress), ('folderFullPath', folderFullPath),
             ('parentResourceFullPath', parentResourceFullPath), ('resourceDescription', resourceDescription)]))