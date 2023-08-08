from flask import Flask, Markup, render_template
from collections import defaultdict
import requests
import json
from types import SimpleNamespace
app = Flask(__name__)

# POST https://micron.jamfcloud.com/uapi/auth/tokens
# Authorization: Basic TestAPIAdmin CrashB0y$!

# GET https://micron.jamfcloud.com/api/preview/computers
# Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdXRoZW50aWNhdGVkLWFwcCI6IkdFTkVSSUMiLCJhdXRoZW50aWNhdGlvbi10eXBlIjoiTERBUCIsImdyb3VwcyI6W10sInN1YmplY3QtdHlwZSI6IkpTU19VU0VSX0lEIiwidG9rZW4tdXVpZCI6ImYzMmQyMGVjLTZmNjItNDM0NS04ZGMwLWQ4YzdjMTU0YjZkYyIsImxkYXAtc2VydmVyLWlkIjotMSwic3ViIjoiODIiLCJleHAiOjE2MzUwMDA0MzZ9.tGlLatMiUiJ9b9cmK2TJyBeUdkOoh0gp4NKGXrF33_c


@app.route('/')
def home():
    # return render_template("application.html")
    return getOs()


@app.route('/os')
def getOs():
    auth_url = 'https://micron.jamfcloud.com/uapi/auth/tokens'
    auth_resp = requests.post(auth_url, auth=("TestAPIAdmin", "CrashB0y$!"),headers={
                              "Accept": "application/json", "Content-Type": "application/json",'Authorization': 'Basic TestAPIAdmin CrashB0y$!'})
    auth_data = json.loads(
        auth_resp.text, object_hook=lambda d: SimpleNamespace(**d))

    token = auth_data.token

    computers_preview_url = 'https://micron.jamfcloud.com/api/preview/computers'
    querystring = {"page":"0","size":"100","pagesize":"100","page-size":"1000"}
    computers_preview_resp = requests.get(computers_preview_url, headers={
        "Accept": "application/json", "Content-Type": "application/json", 'Authorization': 'Bearer ' + token},params=querystring)

    computers_preview_data = json.loads(
        computers_preview_resp.text, object_hook=lambda d: SimpleNamespace(**d))
    
    print(computers_preview_data.results)
    return render_template('os.html', computers_data=computers_preview_data.results)

@app.route('/zoom')
def random():
    return appname("zoom.us.app")


@app.route('/users')
def listUsers():

    computers_url = "https://micron.jamfcloud.com/JSSResource/computers"
    computers_response = requests.get(computers_url, auth=("TestAPIAdmin", "CrashB0y$!"), headers={
        "Accept": "application/json", "Content-Type": "application/json"})

    computersjson = json.loads(
        computers_response.text, object_hook=lambda d: SimpleNamespace(**d))

    return render_template('users.html', computers=computersjson.computers)


@app.route('/app/<appname>')
def appname(appname):
    vipusers_url = "https://micron.jamfcloud.com/JSSResource/computergroups/name/VIP Users"
    applications_url = "https://micron.jamfcloud.com/JSSResource/computerapplications/application/{}".format(
        appname)
    computers_url = "https://micron.jamfcloud.com/JSSResource/computers"
    response = requests.get(applications_url, auth=("TestAPIAdmin", "CrashB0y$!"),
                            headers={"Accept": "application/json", "Content-Type": "application/json"})

    data = json.loads(
        response.text, object_hook=lambda d: SimpleNamespace(**d))
    # print(data.computer_applications.versions)
    versions = []
    usersAndVersions = []
    for version in data.computer_applications.versions:
        versionObj = {}
        versionObj['name'] = appname
        versionObj['version'] = version.number
        versionObj['users_count'] = len(version.computers)
        versions.append(versionObj)
    versions = sorted(versions, key=lambda k: k['users_count'], reverse=True)

    uniqueIds = set()

    for version in data.computer_applications.versions:
        for computer in version.computers:
            versionObj = {}
            uniqueIds.add(computer.id)
            versionObj['id'] = computer.id
            versionObj['name'] = computer.name
            versionObj['version'] = version.number
            usersAndVersions.append(versionObj)

    vipusers_response = requests.get(vipusers_url, auth=("TestAPIAdmin", "CrashB0y$!"), headers={
                                     "Accept": "application/json", "Content-Type": "application/json"})

    vipdata = json.loads(vipusers_response.text,
                         object_hook=lambda d: SimpleNamespace(**d))
    vipIds = []
    for computer in vipdata.computer_group.computers:
        vipIds.append(computer.id)

    vipUserObjs = []
    for versionObj in usersAndVersions:
        # print("&&&&&&&&&",versionObj,versionObj['id'])
        if versionObj['id'] in vipIds:
            vipUserObjs.append(versionObj)

    tmp = defaultdict(list)

    for vipUserObj in vipUserObjs:
        #         {'4.6.7 (18176.0301)': [15], '5.1.1 (28575.0629)': [666, 607], '5.2.2 (45106.0831)': [22, 277], '5.4.3 (58887.1115)':
        # [719], '5.6.1 (560)': [725, 597, 392, 541, 425, 268, 734, 272, 835, 736, 446, 427, 713, 334]})
        tmp[vipUserObj['version']].append(vipUserObj['id'])

    vipUsersVersionsCount = []
    for kv in tmp.items():
        print(kv)
        tObj = {}
        tObj['name'] = appname
        tObj['version'] = kv[0]
        tObj['users_count'] = len(kv[1])
        vipUsersVersionsCount.append(tObj)

    vipUsersVersionsCount = sorted(
        vipUsersVersionsCount, key=lambda k: k['users_count'], reverse=True)
    print(vipUsersVersionsCount, vipUserObjs)

    computers_response = requests.get(computers_url, auth=("TestAPIAdmin", "CrashB0y$!"), headers={
                                      "Accept": "application/json", "Content-Type": "application/json"})
    print("*********", type(response.text))
    print(computers_response)

    computers = json.loads(computers_response.text,
                           object_hook=lambda d: SimpleNamespace(**d))

    print('********************************************************')
    print(appname, versions)
    # print('********************************************************')
    # print(usersAndVersions)
    # print('********************************************************')
    # print(vipIds)
    print('********************************************************')
    # print(vipUsers, len(vipUsers))
    # print(tmp,vipUsersVersionsCount)
    # return appname
    return render_template('application.html', title=appname, max=500, labels=versions, values=versions, vipdata=vipUsersVersionsCount, vipusers=vipUserObjs, users=usersAndVersions, totalUsers=len(uniqueIds), computers=computers.computers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
