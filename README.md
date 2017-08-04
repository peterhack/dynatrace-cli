# Dynatrace CLI (Command Line Interface)
This Pyhton based CLI makes it easy to access the Dynatrace API (both SaaS and Managed). Besides accessing the underlying API the CLI also implements some DevOps specific use cases that allows you to automate Dynatrace into your DevOps Delivery Pipeline.

The CLI also caches queried data (Smartscape and Timeseries) on the local disk. This allows you to execute multiple queries against Smartscape without the roundtrip to the Dynatrace API. It also allows you to work "offline". The GitHub repo includes a cached version of our Dynatrace Demo environment API output. This allows you to explore and test most of the supported use cases without having access to a Dynatrace Tenant.

## Supported Use Cases:
* Query Smartscape entities by any property, e.G: Display Name, Technology Type, Tag, ...
* Query timeseries data for one or multiple entities and metric types
* (TBD) Access Dynatrace problem details and add comments
* (TBD) Push Custom Events (Deployments, Configuration Changes, Test Events, ...) to Dynatrace Entities
* (TBD) Push Custom Metrics

## Requirements:
* Pyhton Runtime: [Download](https://www.python.org/downloads/)
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
