# Starlink toolset for measurements
This toolset is designed to be used as a platform to easily collect metrics about starlink and its network performance.
This toolset was developed as a Bachelor Thesis At Saarland university under the supervision of Dependable Systems Chair.

## Requirements
Orchestrator: python >=3.10, IPv6 working or a tunnel to machine with IPv6

Nodes behind starlink: IPv6 working

## Included modules
All parameters are required unless stated otherwise

### IP
Collects Current IPv4 and IPv6 address

Module specific parameters:
- `None`
- Recommended period: 15s (= once per starlink widow)

### Traceroute
Collects traceroute against a list of targets.

For each target, returns a `dict` where keys correspond to hop distance and values contain `address` and `rtt_ms` fields. Only single packet is sent per hop

Module specific parameters:
- `targets: list[str]`: List of targets against which to run traceroute. Each string can be any of the following types `IPv4`, `IPv6`, `FQDN`. Mixing is allowed

### Ping
Collects ping against a list of targets

For each target returns an object with `rtt_ms` property. This property is average of 3 packets sent with 5ms gaps. If the reply comes from a different host or the target is FQDN additionally contains `address` property specyfying the IP address

Module specific parameters:
- `targets: list[str]`: List of targets agaisnt which to collect ping (rtt) data. Each string can be any of the following types `IPv4`, `IPv6`, `FQDN`. Mixing is allowed

### Weather
Collects weather data locally - precipitation and cloud coverage.
This module uses MET weather API, please familirize yourself with their [TOS](https://developer.yr.no/doc/TermsOfService/) before using the module.
In case your region is not covered you will have to find a different provider and/or write a custom version.

Module specific parameters:
- `user_agent: str`: Must conform to MET Weather API requirements
- Starlink dish configuration: Location enabled. The script queries the dish for GPS coordinates during the setup period. After setup, location can be disabled.

> [!CAUTION]
> MET API has rate limits and requires a valid `user_agent`. Not following their guidelines can result in the inability to collect data

### Space Weather
Collects space weather data on [NOAA Scale](https://www.spaceweather.gov/noaa-scales-explanation)
Underlying metrics (e.g. proton flux, k-index) are historically available on [spaceweather.gov](https://spaceweather.gov)
Module specific parameters:
- `None`

## Writing your own modules
The process to creating your own module if pretty straightforward:

You need to include 2 methods: `setup(conf_s)` and `collect(conf_c)`

The `setup` method is designed to run one-time preparition that depends on some external factors. A good example might be getting location from the dish for weather collection, or any expensive calls that do not need to be called with each data collection. Should you need to pass it some parameters via a playbook, they will be part of the `conf_s` object
Returns `void`.

The `collect` method is called every collection cycle exactly once. Parameters that are needed for every collection should be passed through the `conf_c` object.
This method returns a `dict()` with collected data. The data will be stored in the same key-value format. 

> [!NOTE]
> The scheduler takes care of injecting timestamp into the collected data object