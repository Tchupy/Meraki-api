from requests import request
from pprint import pprint
from config import TOKEN
from prettytable import PrettyTable
import json


def get_orga(org_name):
    api_url = "organizations"
    r = request("GET", base_url+api_url, headers=header)
    # get OrgID
    org_ID = ""
    for org in r.json():
        #if org['name'] == "OBS_SHOWROOM_OCWs":
        if org['name'] == org_name:
            org_ID = org['id']
    return org_ID

def get_network(net_name):
    # Get Network ID
    api_url = "organizations/" + org_ID + "/networks"
    r = request("GET", base_url+api_url, headers=header)
    net_ID = ""
    for network in r.json():
        #if network['name'] == "Massy OCWS - LABO":
        if network['name'] == net_name:
            net_ID = network['id']
    return net_ID


def print_devices(network_ID):
    # GET /networks/:networkId/devices
    api_url = "networks/" + network_ID + "/devices"
    r = request("GET", base_url+api_url, headers=header)
    # get devices Serial number
    device_tab = PrettyTable()
    device_tab.field_names = ['Model', 'Device Name', 'Serial Number']
    for device in r.json():
        device_tab.add_row([device['model'],device['name'],device['serial']])
    print(device_tab)
    return

def print_vlan(network_ID):
    # list all VLANs in a network
    # https://api.meraki.com/api/v1/networks/:networkId/appliance/vlans
    api_url = "networks/" + net_ID + "/appliance/vlans"
    r = request("GET", base_url+api_url, headers=header)
    vlan_tab = PrettyTable()
    vlan_tab.field_names = ['VLAN Id', 'VLAN Name', 'Subnet', 'IP']
    for vlan in r.json():
        vlan_tab.add_row([vlan['id'],vlan['name'],vlan['subnet'],vlan['applianceIp']])
    print(vlan_tab)
    input("continue...\n")
    return

def exist_network(network_id):
    # test if a network exists
    # GET/networks/{networkId}
    api_url = "networks/" + network_id
    r = request("GET", base_url + api_url, headers=header)
    if r.status_code == 200:
        # vlan exists
        return True
    elif r.status_code == 404:
        # vlan does not exist
        return False
    else:
        # error in request (authentication, url, etc..)
        # TODO
        return False

def exist_vlan(network_id,vlan_id):
    # test if a vlan exists
    # GET/networks/{networkId}/appliance/vlans/{vlanId}
    api_url = "networks/" + network_id + "/appliance/vlans/" + vlan_id
    r = request("GET", base_url + api_url, headers=header)
    if r.status_code == 200:
        # vlan exists
        return True
    elif r.status_code == 404:
        # vlan does not exist
        return False
    else:
        # error in request (authentication, url, etc..)
        # TODO
        return False

def delete_vlan(network_id,vlan_id):
    # delete a vlan from a network
    # DELETE/networks/{networkId}/appliance/vlans/{vlanId}
    if exist_vlan(network_id,vlan_id):
        api_url = "networks/" + network_id + "/appliance/vlans/" + vlan_id
        r = request("DELETE", base_url+api_url, headers=header)
        if r.status_code == 204:
            print("VLAN " + vlan_id + " has been removed")
            return 0
        else:
            print("VLAN " + vlan_id + "could not be removed. Does it exist ?")
            return 1
    else:
        print("VLAN " + vlan_id + "does not exist \n")

def add_vlan(network_id,vlan_id,vlan_name,vlan_subnet,vlan_ip):
    # add a vlan in a network
    # POST / networks / {networkId} / appliance / vlans
    if not exist_vlan(network_id,vlan_id):
        api_url = "networks/" + network_id + "/appliance/vlans"
        parameters = {
            'id': vlan_id,
            'name': vlan_name,
            'subnet': vlan_subnet,
            'applianceIp': vlan_ip
        }
        r = request("POST", base_url+api_url, headers=header, params=parameters)
        if r.status_code == 201:
            print("\t\tVLAN " + vlan_id + " has been added")
        else:
            print("\t\tVLAN " + vlan_id + " could not be added.")
    else:
        print("\t\tVLAN " + vlan_id + " could not be added. Does it already exist ?")

def bulk_add_vlan(filename):
    # VLAN creation from json file
    with open(filename) as vlan_file:
        vlan_json = json.load(vlan_file)

    for j_network in vlan_json:
        # try to create vlan for each networks
        if exist_network(j_network['network_id']):
            print("Processing network: " + j_network['network_id'])
            for j_vlan in j_network['vlans']:
                add_vlan(j_network['network_id'], j_vlan['id'],j_vlan['name'], j_vlan['subnet'], j_vlan['applianceIp'])
        else:
            print("Network: " + j_network['network_id'] + " is unknown\n")


def print_menu():       # Your menu design here
    print(15 * "-", "MENU", 15 * "-")
    print("1. Print devices list ")
    print("2. Print current VLAN list")
    print("3. Create a new VLAN  ")
    print("4. Create VLAN from file ")
    print("5. Delete a VLAN  ")
    print("9. Exit from the script ")
    print(73 * "-")

if __name__ == '__main__':
    base_url = "https://api-mp.meraki.com/api/v1/"
    header = {
        'X-Cisco-Meraki-API-Key': TOKEN
    }

    org_ID = get_orga("OBS_SHOWROOM_OCWs")
    net_ID = get_network("Massy OCWS - LABO")
    loop = True
    while loop:
        print_menu()
        choice = input("Enter your choise [1-9]: ")

        if choice == '1':
            print_devices(net_ID)
        elif choice == '2':
            print_vlan(net_ID)
        elif choice == '3':
            print("create VLAN")
            v_id = input("VLAN Id: ")
            v_name = input("VLAN name: ")
            v_subnet = input("VLAN subnet: ")
            v_ip = input("VLAN IP: ")
            print("VLAN to create: ")
            print("VLAN Id: " + v_id + "\nVLAN name: " + v_name + "\nVLAN subnet: " + v_subnet + "\nVLAN IP: " + v_ip)
            print("Is it correct ?")
            validate=input("[Y/n] ")
            if validate == "Y":
                add_vlan(net_ID, v_id, v_name, v_subnet, v_ip)
        elif choice == '4':
            # bulk creation of vlans
            print("\nCreation VLAN from file\n")
            file = input("Source File name: ")
            bulk_add_vlan(file)
        elif choice == '5':
            print("Delete VLAN")
            v_id = input("VLAN Id: ")
            print("Are you sure to want to delete VLAN " + v_id + " ?")
            validate = input("[Y/n] ")
            if validate == "Y":
                delete_vlan(net_ID,v_id)
            print_vlan(net_ID)
        elif choice == '9':
            print("Exiting..")
            loop = False
        else:
            print("Wrong input")