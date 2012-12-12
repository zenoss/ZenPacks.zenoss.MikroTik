##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.DataCollector.plugins.CollectorPlugin \
    import SnmpPlugin, GetMap, GetTableMap

from Products.DataCollector.plugins.DataMaps import MultiArgs, ObjectMap


class MikroTik(SnmpPlugin):
    snmpGetMap = GetMap({
        '.1.3.6.1.2.1.1.1.0': 'sysDescr',
        '.1.3.6.1.4.1.14988.1.1.4.1.0': 'mtxrLicSoftwareId',
        '.1.3.6.1.4.1.14988.1.1.4.4.0': 'mtxrLicVersion',
        })

    snmpGetTableMaps = (
        GetTableMap('hrStorageTable', '1.3.6.1.2.1.25.2.3.1', {
            '.3': 'hrStorageDescr',
            '.4': 'hrStorageAllocationUnits',
            '.5': 'hrStorageSize',
            }),
        )

    def process(self, device, results, log):
        log.info('processing %s for device %s', self.name(), device.id)

        model = results[0].get('sysDescr', '').replace('RouterOS', '').strip()
        serial_number = results[0].get('mtxrLicSoftwareId', '')
        os = 'RouterOS %s' % results[0].get('mtxrLicVersion', '')
        os = os.strip()

        device_om = ObjectMap()

        hw_om = ObjectMap(compname='hw', data={
            'setProductKey': MultiArgs(model, 'MikroTik'),
            'serialNumber': serial_number,
            })

        os_om = ObjectMap(compname='os', data={
            'setProductKey': MultiArgs(os, 'MikroTik'),
            'totalSwap': 0,
            })

        for snmpindex, row in results[1].get('hrStorageTable', {}).items():
            if 'memory' not in row.get('hrStorageDescr'):
                continue

            device_om.snmpindex_dct = {
                '1.3.6.1.2.1.25.2.3.1.6': snmpindex.strip('.'),
                }

            units = int(row.get('hrStorageAllocationUnits', 1024))

            if 'hrStorageSize' in row:
                hw_om.totalMemory = int(row['hrStorageSize']) * units

        return [device_om, hw_om, os_om]
