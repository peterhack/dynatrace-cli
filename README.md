# Dynatrace CLI (Command Line Interface)
This Python based CLI makes it easy to access the Dynatrace API (both SaaS and Managed). Besides accessing the underlying API the CLI also implements some DevOps specific use cases that allows you to automate Dynatrace into your DevOps Delivery Pipeline.

The CLI also caches queried data (Smartscape and Timeseries) on the local disk. This allows you to execute multiple queries against Smartscape without the roundtrip to the Dynatrace API. It also allows you to work "offline". The GitHub repo includes a cached version of our Dynatrace Demo environment API output. This allows you to explore and test most of the supported use cases without having access to a Dynatrace Tenant.

## Supported Use Cases:
* Query Smartscape entities by any property, e.G: Display Name, Technology Type, Tag, ...
* Query timeseries data for one or multiple entities and metric types
* (TBD) Access Dynatrace problem details and add comments
* (TBD) Push Custom Events (Deployments, Configuration Changes, Test Events, ...) to Dynatrace Entities
* (TBD) Push Custom Metrics

## Requirements:
* Python Runtime: [Download](https://www.python.org/downloads/)
* Dynatrace Tenant: [Get your Saas Trial Tenant](http://bit.ly/dtsaastrial)

## Examples
The CLI assumes the following commands
py dtcli.py <command> <options>
<command>: 
* config: configure dynatrace tenant, token and cache strategy
* ent: query entities: app(lication), srv (services, pg (process groups), host
* ts: list availabbly metric types and query timeseries data
* prob: access problem information
* evt: push and access custom events, e.g: deployments
* dql: Dynatrace Query Language: a more convenient way to query timeseries data for certain entities ina  single command line
<option> 

## Examples: Query Entities
```
> py dtcli.py ent app .*easyTravel.*
['MOBILE_APPLICATION-752C288D59734C79']

> py dtcli.py ent srv JourneyService
['SERVICE-CDEB60C48DE58E80', 'SERVICE-97EA6CCFEC367EC5', 'SERVICE-A9E9962F2DE6F4BC']

> py dtcli.py ent host tags/AWS:Category?value=DEMOABILITY
['HOST-F5D85B7DCDD8A93C', 'HOST-54AA0D8B5401A1C2', 'HOST-A02BF7E1B9ADA36D', 'HOST-7453A7E317FCF4AF', 'HOST-76FAA6DC0347DA12', 'HOST-6B659DFBAC76F491', 'HOST-7344649A8D974E74', 'HOST-EA50C80CC9354652', 'HOS
T-DE6F9EC80D4D7C58', 'HOST-0788564003D72AEF', 'HOST-1E64E15558B9486B', 'HOST-E662F28EFFC7D77D']

> py dtcli.py ent host tags/AWS:Name=.* value
['et-demo-1-win1', 'et-demo-1-win2', 'et-demo-1-lnx6', 'et-demo-1-lnx7', 'et-demo-1-lnx2', 'et-demo-1-lnx3', 'et-demo-1-lnx4', 'et-demo-1-lnx5', 'et-demo-1-win3', 'et-demo-1-lnx1', 'et-demo-1-win4', 'et-de
mo-1-lnx8']

> py dtcli.py ent srv serviceTechnologyTypes=ASP.NET discoveredName
['dotNetBackend_easyTravel_x64:9010', 'dotNetFrontend_easyTravel_x64:9000', 'eT-demo1-weather-express', 'eT-demo1-weather-service-restify']

> py dtcli.py ent app .\*easyTravel.\* displayName
['easyTravel Demo']

> py dtcli.py ent app .\*easyTravel.\* entityId
['MOBILE_APPLICATION-752C288D59734C79']
```

## Examples: Query Timeseries
```
> py dtcli.py ts list .*response.*
['ruxit.jmx.appserver.jetty:responsesBytesTotal', 'com.dynatrace.builtin:servicemethod.requestspermin', 'com.dynatrace.builtin:servicemethod.responsetime']

> py dtcli.py ts list .*response.* displayName
['responsesBytesTotal', 'Method response time', 'Method response time']

> py dtcli.py ts list dimensions=APPLICATION
['com.dynatrace.builtin:app.errorcount', 'com.dynatrace.builtin:app.jserrorsduringuseractions', 'com.dynatrace.builtin:app.jserrorswithoutuseractions', 'com.dynatrace.builtin:app.useractionduration', 'com.
dynatrace.builtin:app.useractionsperminute', 'com.dynatrace.builtin:appmethod.errorcount', 'com.dynatrace.builtin:appmethod.useractionduration', 'com.dynatrace.builtin:appmethod.useractionsperminute']

> py dtcli.py ts describe com.dynatrace.builtin:appmethod.useractionsperminute
{'displayName': 'com.dynatrace.builtin:appmethod.useractionsperminute', 'types': [], 'unit': 'count/min', 'timeseriesId': 'com.dynatrace.builtin:appmethod.useractionsperminute', 'aggregationTypes': ['COUNT
'], 'filter': 'BUILTIN', 'dimensions': ['APPLICATION_METHOD']}

> py dtcli.py ts query com.dynatrace.builtin:appmethod.useractionsperminute[count%hour]
{'APPLICATION_METHOD-0A1EF133D2225DE3': {'unit': 'count/min', 'dataPoints': [[1501779420000, 9.0], [1501779480000, 5.0], [1501779540000, 4.0], [1501779600000, 5.0], [1501779660000, 8.0], [1501779720000, 4.
0], [1501779780000, 3.0], [1501779840000, 5.0], [1501779900000, 4.0], [1501779960000, 7.0], .........

> py dtcli.py ts query com.dynatrace.builtin:app.useractionduration[avg%hour] APPLICATION-F5E7AEA0AB971DB1
{'APPLICATION-F5E7AEA0AB971DB1': {'timeseriesId': 'com.dynatrace.builtin:app.useractionduration', 'dataPoints': [[1501779960000, 4474862.904109589], [1501780020000, 6921639.344262295], [1501780080000, 4273
398.5], [1501780140000, 5725744.966442953], [1501780200000, 4575715.764705882], [1501780260000, 6323631.719298245], [1501780320000, 4294378.218487395], [1501780380000, .......

```

## Examples: Dynatrace Query Language
```
> py dtcli.py dql app www.easytravel.com app.useractions[count%hour],app.useractionduration[avg%hour]
[{'APPLICATION-F5E7AEA0AB971DB1': {'entityDisplayName': 'www.easytravel.com', 'timeseriesId': 'com.dynatrace.builtin:app.useractions', 'dataPoints': [[1501788420000, 103.0], [1501788480000, 143.0], [150178
8540000, 130.0], [1501788600000, 143.0], [1501788660000, 120.0], [1501788720000, 156.0], [1501788780000, 118.0], [1501788840000, 102.0], [1501788900000, 106.0], [1501788960000, 70.0], [1501789020000, 110.0
], [1501789080000, 115.0], [1501789140000, 145.0], [1501789200000, 139.0], [1501789260000, 137.0], [1501789320000, 115.0], [1501789380000, 140.0], [1501789440000, 98.0], [1501789500000, 105.0], [1501789560
000, 141.0], [1501789620000, 112.0], [1501789680000, 123.0], [1501789740000, 123.0], [1501789800000, 144.0], [1501789860000, 118.0], [1501789920000, 128.0], [1501789980000, 118.0], [1501790040000, 86.0], [

> py dtcli.py dql appmethod .*Book.* appmethod.useractionduration[avg%hour]
[{'APPLICATION_METHOD-6ED7F83A1EF195DC': {'dataPoints': [[1501792560000, 985400.0], [1501792620000, 605600.0], [1501792680000, 2759333.3333333335], [1501792740000, 445333.3333333333], [1501792800000, 54000
0.0], [1501792860000, 3709000.0], [1501792920000, 727200.0], [1501792980000, 1670800.0], [1501793040000, 791666.6666666666], [1501793100000, 372200.0], [1501793160000, 1700500.0], [1501793220000, 636285.71
42857143], [1501793280000, 989250.0], [1501793340000, 1517000.0], [1501793400000, 872250.0], [1501793460000, 893750.0], [1501793520000, 358333.3333333333], [1501793580000, 324000.0], [1501793640000, 953000 ...

```
