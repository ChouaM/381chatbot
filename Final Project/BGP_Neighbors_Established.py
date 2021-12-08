import time
import json

# To build the table at the end
from tabulate import tabulate

# Genie import
from genie.conf import Genie
from genie.abstract import Lookup

# import the genie libs
from genie.libs import ops # noqa

# Parser import
from genie.libs.parser.iosxe.show_interface import ShowIpInterfaceBrief

# Import Genie Conf
from genie.libs.conf.interface import Interface

class BGP_Neighbors_Established():

    def setup(self, testbed):
        genie_testbed = Genie.init(testbed)
        self.device_list = []
        str = ""
        for device in genie_testbed.devices.values():
            try:
                device.connect()
            except Exception as e:
                print("Failed to establish connection to '{}'".format(
                    device.name))
                str += "\nFailed to establish connection to "+ device.name

            self.device_list.append(device)

        return str


    def learn_bgp(self):
        self.all_bgp_sessions = {}
        str = ""
        for dev in self.device_list:
            print("Gathering BGP Information from {}".format(
                dev.name))
            abstract = Lookup.from_device(dev)
            bgp = abstract.ops.bgp.bgp.Bgp(dev)
            bgp.learn()
            if hasattr(bgp, 'info'):
                #print(bgp.info)
                self.all_bgp_sessions[dev.name] = bgp.info
                #print("BGP on %s looks good!" % dev.name)
            else:
                print("Failed to learn BGP info from device %s" % dev.name, 
                            goto=['common_cleanup'])
                str += "Failed to learn BGP info from device" + dev.name
                
        return str

    def check_bgp(self):

        failed_dict = {}
        mega_tabular = []
        text=""
        for device, bgp in self.all_bgp_sessions.items():

            # may need to change based on BGP config
            vrfs_dict = bgp['instance']['default']['vrf']

            for vrf_name, vrf_dict in vrfs_dict.items():

                # If no neighbor for default VRF, then set the neighbors value to {}
                neighbors = vrf_dict.get('neighbor', {})
                for nbr, props in neighbors.items():
                    state = props.get('session_state')
                    if state:
                        #create a table 
                        tr = []
                        tr.append(vrf_name)
                        tr.append(nbr)
                        tr.append(state)
                        if state.lower() == 'established':
                            tr.append('Passed')
                        else:
                            failed_dict[device] = {}
                            failed_dict[device][nbr] = props
                            tr.append('Failed')

                        mega_tabular.append(tr)

                print("Device {d} Table:\n".format(d=device))
                text+="\n"+"Device {d} Table:\n".format(d=device)
                print(tabulate(mega_tabular,
                                  headers=['VRF', 'Peer',
                                           'State', 'Pass/Fail'],
                                  tablefmt='github'))
                text+= tabulate(mega_tabular,
                                  headers=['VRF', 'Peer',
                                           'State', 'Pass/Fail'],
                                  tablefmt='grid')

        if failed_dict:
            print(json.dumps(failed_dict, indent=3))
            print("Testbed has BGP Neighbors that are not established")

        else:
            print("All BGP Neighbors are established")

        return text

if __name__ == "__main__":
    # test functions
    bgp = BGP_Neighbors_Established()
    bgp.setup('testbed/routers.yml')
    bgp.learn_bgp()
    bgp.check_bgp()