# Required Libraries
import sys
import io
import re
import os
import json
import datetime
import operator
import urllib
import requests

# Constants
API_ENDPOINT_APPLICATIONS = "/api/v1/entity/applications"
API_ENDPOINT_SERVICES = "/api/v1/entity/services"
API_ENDPOINT_PROCESS_GROUPS = "/api/v1/entity/infrastructure/process-groups"
API_ENDPOINT_HOSTS = "/api/v1/entity/infrastructure/hosts"
API_ENDPOINT_TIMESERIES = "/api/v1/timeseries"
API_ENDPOINT_EVENTS = "/api/v1/events"

# Configuration is read from config file if exists. If you want to go back to default simply delete the config file
dtconfigfilename = os.path.dirname(os.path.abspath(__file__)) + "\\" + "dtconfig.txt"
config = {
    "tenanthost"  : "smpljson",   # "hci34192.live.dynatrace.com" # this would be the configuration for a specific Dynatrace SaaS Tenant
    "apitoken"    : "smpltoken",  # YOUR API TOKEN, generated with Dynatrace
    "cacheupdate" : -1            # -1 = NEVER, 0=ALWAYS, X=After X seconds
}

def getAuthenticationHeader():
    return {"Authorization" : "Api-Token " + config["apitoken"]}

def getRequestUrl(apiEndpoint, queryString):
    requestUrl = "https://" + config["tenanthost"] + apiEndpoint;
    if(queryString is not None and len(queryString) > 0):
        requestUrl += "?" + queryString
    return requestUrl

def getCacheFilename(apiEndpoint, queryString):
    fullCacheFilename = os.path.dirname(os.path.abspath(__file__)) + "\\" + config["tenanthost"].replace(".", "_") + "\\" + apiEndpoint.replace("/","_")
    if(queryString is not None and len(queryString) > 0):
        fullCacheFilename += "\\" + urllib.parse.unquote(queryString);
    fullCacheFilename += ".json"

    return fullCacheFilename

class NameValue:
    def __init__(self, defaultName, defaultValue):
        self.name = defaultName

        # we allow values to be object lists - so we simply load it as JSON
        if(defaultValue.startswith("[") and defaultValue.endswith("]")):
            json.load(defaultValue)
        else:
            self.value = defaultValue

# helper functions
def parseNameValue(nameValue, defaultName, defaultValue):
    "Allowed strings are: justvalue, name=value, [value1,value2], name=[value1,value2]"

    # first we check for None and just return defaultName, defaultValue
    if(nameValue is None):
        return NameValue(defaultName, defaultValue)

    # now we check for name=value pair or just value
    equalSign = nameValue.find("=")
    if(equalSign < 0):
        return NameValue(defaultName, nameValue)

    partitions = nameValue.partition("=")
    return NameValue(partitions[0], partitions[2])

def queryDynatraceAPI(isGet, apiEndpoint, queryString, postBody):
    # we first validate if we have the file in cache
    fullCacheFilename = getCacheFilename(apiEndpoint, queryString)
    readFromCache = False
    if(os.path.isfile(fullCacheFilename)):
        cacheupdate = config["cacheupdate"]
        if(cacheupdate == -1):
            readFromCache = True
        if(cacheupdate > 0):
            now = datetime.datetime.now()
            lastModified = datetime.datetime.fromtimestamp(os.path.getmtime(fullCacheFilename))
            if((now - lastModified).seconds < cacheupdate):
                readFromCache = True

    jsonContent = None
    if readFromCache:
        with open(fullCacheFilename) as json_data:
            jsonContent = json.load(json_data)
    else:
        myResponse = requests.get(getRequestUrl(apiEndpoint, queryString), headers=getAuthenticationHeader(), verify=True)
        print("Request to Dynatrace API ended with: " + str(myResponse.status_code))

        # For successful API call, response code will be 200 (OK)
        if(myResponse.ok):
            jsonContent = json.loads(myResponse.text)

            # lets ensure the directory is there
            directory = os.path.dirname(fullCacheFilename)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # now lets save the content to the cache as well
            with open(fullCacheFilename, "w+") as output_file:
                json.dump(jsonContent, output_file)

    return jsonContent

class KeySearch:
    # key allows a regular keyname but also a format of [keylistname/][context:][key][?valuekey] - example: tags/AWS:Name
    # some examples of allowed key names
    # - displayName=.*easyTravel                   -> match on value displayName=.*easyTravel
    # - tags/AWS:Name=.*host.*                     -> match parent list=tags, context=AWS,key=Name and value=.*host.*
    # - tags/Name=.*host.*                         -> match parent list=tags, key=Name and value=.*host.*
    # - tags/context#AWS:key#Name=value#.*host.*   -> match parent list=tags, context=AWS,key=Name and value=.*host.*
    def __init__(self, key):
        self.keylistname = None         # name of list in case we match on a list, e.g: tags
        self.contextvalue = None        # value of the context, e.g: AWS
        self.contextkeyname = None      # name of the context key fiels, e.g: context
        self.keyvalue = None            # value of the key field, e.g: Name
        self.keykeyname = None          # name of the key key field, e.g: key
        self.value = None               # value of the value field, e.g: some value
        self.valuekeyname = "value"     # name of the name key field, e.g: value

        parts = key.partition("/")
        if(parts[1] == "/"):
            self.keylistname = parts[0]      # tags
            key = parts[2]                   # AWS:Name

        parts = key.partition("?")
        if(parts[1] == "?"):
            self.valuekeyname = parts[2]
            key = parts[0]

        if(len(key) > 0):
            parts = key.partition(":")
            if(parts[1] == ":"):
                self.contextvalue = parts[0]     # AWS
                self.contextkeyname = "context"
                self.keyvalue = parts[2]         # Name
                self.keykeyname = "key"
            else:
                if(self.keylistname is not None):
                    self.keyvalue = parts[0]
                    self.keyname = "key"
                else:
                    self.valuekeyname = parts[0]

        # now we validate if any of the three parameters where defined with keyname#keyvalue
        if(self.contextvalue is not None):
            parts = self.contextvalue.partition("#")
            if(parts[1] == "#"):
                self.contextkeyname = parts[0]
                self.contextvalue = parts[2]

        if(self.keyvalue is not None):        
            parts = self.keyvalue.partition("#")
            if(parts[1] == "#"):
                self.keykeyname = parts[0]
                self.keyvalue = parts[2]

    def isTagSearch():
        return self.keylistname is not None

def getAttributeFromFirstMatch(attributeName, objectlist):
    "Iterates through a list of objects and returns first occurence of attributeName"
    for object in objectlist:
        try:
            attributeValue = object[attributeName]
            if(attributeValue is not None):
                return attributeValue
        except KeyError:
            x=1
    
    return "OBJECT DOESNT HAVE KEY " + attributeName

def jsonFindValuesByKey(jsonContent, key, matchValue, returnKey):
    "Traverses through the jsonContent object. Searches for the request key and returns the returnKey in case matchValue matches"
    return jsonFindValuesByKeyEx(jsonContent, key, matchValue, returnKey, None, None)

def jsonFindValuesByKeyEx(jsonContent, key, matchValue, returnKey, parentJsonNodename, parentJsonContent):
    "INTERNAL helper function for jsonFindValuesByKeyEx"
    if((key is not None) and (type(key) == str)):
        key = KeySearch(key)

    # we convert the regular match string to a compilied regex. we do it right here so we only have to do it once
    if((matchValue is not None) and (type(matchValue) == str)):
        try:
            matchValue = re.compile(matchValue)
        except:
            print(matchValue + " is NOT VALID regular expression")
            sys.exit(1)

    # our final result list
    result = []
    if type(jsonContent) == str:
        jsonContent = json.loads(jsonContent)

    if type(jsonContent) is dict:
        # Only look into this dictionary if the parent node is what we want to find or if we dont care about the parent node name
        # when looking at a dictionary we either return when we found the first key match - or if we have two key matches in case KeySearch wants to search for Context and Name
        foundValueMatch = None
        foundContextMatch = key.contextvalue is None
        foundKeyMatch = key.keyvalue is None
        for jsonkey in jsonContent:
            # 1: We found the key and it is a list
            if ((type(jsonContent[jsonkey]) is list) and (jsonkey == key.keyvalue)):
                # if we found the key and it is a list we make sure that one list item matches
                if(matchValue is None):
                    foundKeyValueMatch = True
                else:
                    for listItem in jsonContent[jsonkey]:
                        if(matchValue.match(listItem)):
                            foundKeyValueMatch = True

                if foundKeyValueMatch is not None:
                    foundKeyValueMatch = getAttributeFromFirstMatch(returnKey, [jsonContent, parentJsonContent])
            
            # 2: we have a list (that doesnt match the key) and a dictionary (we dont care about matching keys as this is currently not supporrted)
            elif type(jsonContent[jsonkey]) in (list, dict):
                subResult = jsonFindValuesByKeyEx(jsonContent[jsonkey], key, matchValue, returnKey, jsonkey, jsonContent)
                if(len(subResult) > 0):
                    result.extend(subResult)

            # 3: we have a matching key on a regular value
            elif jsonkey == key.valuekeyname:
                # if we found the rigth key check if the value matches
                if(matchValue is None):
                    foundValueMatch = jsonContent[jsonkey]
                else:
                    if(matchValue.match(jsonContent[jsonkey])):
                        foundValueMatch = getAttributeFromFirstMatch(returnKey, [jsonContent, parentJsonContent])

            # 4: we have a matching context key in case user searches for context, e.g. in a tag
            elif (key.contextvalue is not None) and (jsonkey == key.contextkeyname):
                foundContextMatch = key.contextvalue == jsonContent[jsonkey]

            # 5: we have a matching key key in case user searches for context, e.g. in a tag
            elif (key.keyvalue is not None) and (jsonkey == key.keykeyname):
                foundKeyMatch = key.keyvalue == jsonContent[jsonkey]

        # if we iterated through a whole dictionary and found a matching value and, if necessary, matching context and key then we are good
        if (key.keylistname is None) or (key.keylistname == parentJsonNodename):
            if((foundValueMatch is not None) and foundContextMatch and foundKeyMatch):
                result.append(foundValueMatch)

    elif type(jsonContent) is list:
        for item in jsonContent:
            if type(item) in (list, dict):
                subResult = jsonFindValuesByKeyEx(item, key, matchValue, returnKey, parentJsonNodename, parentJsonContent)
                if(len(subResult) > 0):
                    result.extend(subResult)
    return result

def mainX():
    pass
    # readConfig()
    # saveConfig()
    # queryDynatraceAPI(False, API_ENDPOINT_APPLICATIONS, "", "")
    # doEntity(False, ["dtcli", "ent","app"])
    # doEntity(False, ["dtcli", "ent","host","tags/AWS:Name=et-demo.*", "displayName"])
    # doEntity(False, ["dtcli", "ent","host","tags/AWS:Category?value=DEMOABILITY", "displayName"])
    # doEntity(False, ["dtcli", "ent","host","tags/AWS:Name=.*", "value"])
    # doEntity(False, ["dtcli", "ent","host","tags/AWS:Name=.*", "entityId"])
    # doEntity(False, ["dtcli", "ent", "srv", "agentTechnologyType=JAVA", "displayName"])
    # doEntity(False, ["dtcli", "ent", "srv", "serviceTechnologyTypes=ASP.NET", "displayName"])
    # doEntity(False, ["dtcli", "ent", "srv", "serviceTechnologyTypes=ASP.NET", "entityId"])
    # doEntity(False, ["dtcli", "ent", "pg", "key=customizable", "entityId"])
    # doEntity(False, ["dtcli", "ent", "pg", "key=se-day", "displayName"])
    # doEntity(False, ["dtcli", "ent", "pg", "javaMainClasses=.*Bootstrap.*"])
    # doEntity(False, ["dtcli", "ent", "pg", "cloudFoundryAppNames=.*"])
    # doEntity(False, ["dtcli", "ent", "host", "ipAddresses=54\.86\..*"])
    # doEntity(False, ["dtcli", "ent", "pg", "softwareTechnologies/?type=TOMCAT"])

def main():
    readConfig()
    command = "usagae"
    doHelp = False
    if len(sys.argv) > 1:
        command = sys.argv[1]
    if command == "help":
        doHelp = True
        if len(sys.argv) > 2:
            command = sys.argv[2]
        else:
            command = "usage"

    if command == "ent" :
        doEntity(doHelp, sys.argv)
    elif command == "ts" :
        doTimeseries(doHelp, sys.argv)
    elif command == "config" :
        doConfig(doHelp, sys.argv)
    elif command == "prob" :
        doProblem(doHelp, sys.argv)
    elif command == "evt" :
        doEvent(doHelp, sys.argv)
    else :
        doUsage(sys.argv)
    exit

def readConfig():
    "Is reading stored configuration from the disk"
    global config
    if os.path.exists(dtconfigfilename):
        with open(dtconfigfilename) as json_data:
            config = json.load(json_data)

def saveConfig():
    "Stores configuration to disk"
    with open(dtconfigfilename, 'w') as outfile:
        json.dump(config, outfile)        

def doUsage(args):
    "Just printing Usage"
    print("Usage: Dynatrace Command Line Interface")
    print("dtcli <command> <options>")
    print("Valid commands include ent=entities, ts=timerseries, prob=problems, evt=events")
    print("To configure access token and Dynatrace REST Endpoint use command 'config'")
    print("For more information on a command use: dtcli help <command>")

def doEntity(doHelp, args):
    "Allows you to query information about entities"
    if doHelp:
        print("dtcli ent <type> <query> <resulttag>")
        print("type: app | srv | pg | host")
        print("Examples:")
        print("===================")
        print("dtcli ent app .*easyTravel.*")
        print("dtcli ent srv myfrontend")
        print("dtcli ent host tag/AWS:Name=et-demo-1-win1")
        print("dtcli ent host tag/Name=.*demo.*")
        print("dtcli ent srv serviceTechnologyTypes=ASP.NET discoveredName")
        print("dtcli ent app .*easyTravel.* displayName")
    else:
        entityTypes = ["app","srv","pg","host"]
        entityEndpoints = [API_ENDPOINT_APPLICATIONS, API_ENDPOINT_SERVICES, API_ENDPOINT_PROCESS_GROUPS, API_ENDPOINT_HOSTS]
        if (len(args) <= 2) or not operator.contains(entityTypes, args[2]):
            # Didnt provide the correct parameters - show help!
            doEntity(True, args)
        else:
            # As the Dynatrace API currently doesnt suppot all the filtering that we want to provide through this CLI we have to parse the response and filter in our script
            apiEndpoint = operator.getitem(entityEndpoints, operator.indexOf(entityTypes, args[2]))
            jsonContent = queryDynatraceAPI(True, apiEndpoint, "", "")

            if len(args) > 3:
                nameValue = parseNameValue(args[3], "displayName", "")
                resultTag = "entityId"
                if(len(args) > 4):
                    resultTag = args[4]
                elements = jsonFindValuesByKey(jsonContent, nameValue.name, nameValue.value, resultTag)
            else:
                elements = jsonFindValuesByKey(jsonContent, "displayName", None, None)
            print(elements)

def doTimeseries(doHelp, args):
    "Allows you to query information about entities"
    if doHelp:
        print("dtcli ts <action> <options>")
        print("action: list | query | push")
        print("options for list: (optional)*name*")
        print("options for query: [tsid1,tsid2,...] ([entid1,entid2,...])")
        print("options for push: TODO")
        print("Examples:")
        print("===================")
        print("dtcli ts list")
        print("dtcli ts list *ResponseTime*")
        print("dtcli ts query [jmx.tomcat.jdbc.pool:Active]")
        print("dtcli ts query [jmx.tomcat.jdbc.pool:Active] [ENTITY-XYZ,ENTITY-ABC]")
    else:
        actionTypes = ["list","query","push"]
        action = None
        if (len(args) <= 2) or not operator.contains(actionTypes, args[2]):
            # Didnt provide the correct parameters - show help!
            doTimeseries(True, args)
        else:
            action = operator.indexOf(actionTypes, args[2])

        if action == 0:   # list
            jsonContent = queryDynatraceAPI(True, API_ENDPOINT_TIMESERIES, "", "")
            if len(args) > 3:
                elements = jsonFindValuesByKey(jsonContent, "displayName", args[3], "timeseriesId")
            else:
                elements = jsonFindValuesByKey(jsonContent, "displayName", None, None)
            print(elements)
        elif action == 1: # query
            # build the query string for the timeseries id
            if(len(args) > 3):
                timeseriesId = args[3]
                jsonContent = queryDynatraceAPI(True, API_ENDPOINT_TIMESERIES, "timeseriesId=" + timeseriesId + "&relativeTime=hour&aggregationType=avg", "")
        
            print("TODO: implement ts query")
        elif action == 2: # push
            print("TODO: implement ts push")
        else:
            doTimeseries(True, args)

def doConfig(doHelp, args):
    if doHelp or len(args) < 4:
        print("You can set the following configuration options")
        print("apitoken <dynatracetoken>")
        print("tenanthost <http://yourdynatraceserver>")
        print("cacheupdate -1 (only use cache), 0 (=never use cache), X (=update cache in X Minutes)")
        print("Examples")
        print("==============")
        print("dtapi config apitoken ABCEDEFASDF tenanthost myurl.live.dynatrace.com cacheupdate 5")
        print("==============")
        print("Current Dynatrace Tenant: " + config["tenanthost"])
    else:
        global config
        i = 2
        while i+2 <= len(args):
            configName = args[i]
            configValue = args[i+1]
            if configName == "apitoken":
                config["apitoken"] = configValue
            elif configName == "tenanthost":
                config["tenanthost"] = configValue
            elif configName == "cacheupdate":
                config["cacheupdate"] = configValue
            else:
                print("Configuration element '" + configName + "' not valid")
                doConfig(True, args)
                i = len(args)
            i = i+2

        saveConfig()

def doProblem(doHelp, args):
    print("TODO: problem")

def doEvent(doHelp, args):
    print("TODO Event")

def getProcessGroups():
    # todo: error handling ...
    myResponse = requests.get(url, headers=authHeader, verify=True)
    print (myResponse.status_code)

    # For successful API call, response code will be 200 (OK)
    if(myResponse.ok):
        jData = json.loads(myResponse.text)

        print("The response contains {0} properties".format(len(jData)))
        print("\n")
        for key in jData:
            print (key + " : " + jData[key])
    else:
  # If response code is not ok (200), print the resulting http error code with description
        myResponse.raise_for_status()

if __name__ == "__main__": main()