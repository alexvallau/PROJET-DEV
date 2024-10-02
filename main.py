from flask import Flask, jsonify, render_template, request
from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, nextCmd, getCmd
import threading
import time
import json
import os
import random

app = Flask(__name__)
data_file = 'data.json'
data = []
snmp_target = '192.168.2.108'  # Replace with the target IP address
snmp_community = 'public'  # Replace with the SNMP community string
snmp_oid = '1.3.6.1.2.1.2.2.1.10.2'  # OID for ifOutOctets for the first interface




def returnRandom():
    return random.randint(1,100000000)

def createJsonFile(hostname,ipAddress,numberOfInterfaces, communityString, OID):
    random = returnRandom()
    strRandom = str(random)
    filePath = r'C:\\Users\Arizzi Alexandre\\Documents\Apprentissage\\TRI\\Master 2\\Projet Developpement\\devicesConfiguration'
    fileName = strRandom+'.json'
    fileDataPath = r'C:\\Users\Arizzi Alexandre\\Documents\Apprentissage\\TRI\\Master 2\\Projet Developpement\\devicesJsonData'

    jsonModel= {'hostname':hostname,
                'ipAddress':ipAddress,
                'numberOfInterfaces':numberOfInterfaces,
                'communityString':communityString,
                'OID':OID
                }
    
    #création du fichier de configuration
    with open(os.path.join(filePath,fileName), 'w') as json_file:
        json.dump(jsonModel, json_file)
    #création du fichier de données

    with open(os.path.join(fileDataPath, fileName), 'w') as json_file2:
        json.dump([], json_file2)
    print(jsonModel)   

def load_data():
    global data
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            data = json.load(file)

def save_data():
    with open(data_file, 'w') as file:
        json.dump(data, file)

def collect_data():
    previous_value = None
    while True:
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(snmp_community),
                   UdpTransportTarget((snmp_target, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(snmp_oid)))
        )

        if error_indication:
            print(error_indication)
        elif error_status:
            print('%s at %s' % (error_status.prettyPrint(),
                                error_index and var_binds[int(error_index) - 1][0] or '?'))
        else:
            for var_bind in var_binds:
                current_value = int(var_bind[1])
                if previous_value is not None:
                    speed = (current_value - previous_value)/5   # Convert to bits per second
                    data.append(speed)
                    if len(data) > 2592000:  # Keep only the last 30 days (1 minute of data if collected every second)
                        data.pop(0)
                    save_data()
                previous_value = current_value
        time.sleep(5)


@app.route('/data')
def get_data():
    return jsonify(data)

@app.route('/add')
def create_Device():
    return render_template('addDevice.html')

@app.route('/submitDevice', methods=['POST'])
def submit_Device():
    data = request.form
    hostname = request.form['hostname']
    numberOfInterfaces = request.form['numInterfaces']
    ipAddress= request.form['ipAddress']
    snmp_community = request.form['community']
    snmp_oid = request.form['oid']
    print(hostname+numberOfInterfaces+ipAddress)
    createJsonFile(hostname,ipAddress,numberOfInterfaces,snmp_community,snmp_oid)
    return 'Device added'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    load_data()
    threading.Thread(target=collect_data, daemon=True).start()
    app.run(debug=True)