# Starlink toolset for measurements
This toolset is designed to be used as a platform to easily collect metrics about starlink network performance.
Alternatively, if you are a non-researcher, you can use this for network monitoring.
This toolset was developed as a Bachelor Thesis At Saarland university under the supervision of Dependable Systems Chair.

## Installation
### Prerequisites
 - Linux Based Machine: machine on a network that is connected to the dish. Due to docker on widnows implementation some scripts would not work (you're welcome to try).
 - All scripts that query the dish directly expect to find it on the static `192.168.100.1` IP. Note: this IP works in bypass mode as well, although you might need to add a static route to your router
 - Docker installed. See [docs](https://docs.docker.com/get-docker/)
 - IPv6 enabled in Docker. See [docs](https://docs.docker.com/config/daemon/ipv6/). No need to create a network yourself, docker compose takes care of that. Feel free to change the subnet according to IPv6 specification, should you need to.
### Installation
 - The package comes with a script that builds all the required containers.
 - Make sure Docker is running
 - run `build.sh`, this will invoke a script that builds all the containers
 - CONFIGURE TARGETS ????? TODO!!!
 - After the script finishes and you have configured targets, run `docker compose up` from the root of this directory. Optionally, add `-d` flag to run in the background

## GRPC tools
Partially based on [sparky8512's tools](https://github.com/sparky8512/starlink-grpc-tools), custom implementation
### server
The starlink dish is always at `192.168.0.1` and has grpc server reflection enabled on port `9200`.
Since that is the case, you can query the server for formats of messages and generate the proto files required for querying using [grpcurl](https://github.com/fullstorydev/grpcurl).
Example commands:
`grpcurl -plaintext 192.168.100.1:9200 list` - Lists all service
`grpcurl -plaintext 192.168.100.1:9200 describe SpaceX.API.Device.Device` - Describe a service/message
To list all possible requests run the above command with `SpaceX.API.Device.Request` target. (Or response for responses respectively)
You can also describe each of the messages. Note that a lot of them are empty, i.e they don't require any data to be sent along.
### generating protobuf
(NOT NEEDED, repository already contains required files)
See [starlink-grpc-tools wiki](https://github.com/sparky8512/starlink-grpc-tools/wiki/gRPC-Protocol-Modules#using-extract_protosetpy)

## Network tools
Basic metrics collected about the network behavior
### Ping
Sends ICMP ping packets to specified hosts with specified interval.
### Traceroute
Runs traceroute against specified host with specified interval.
The recommended frequency is 1 (=once every satelite window)

## Other collected metrics
WARNING: Physics ahead
Since communication uses parts of the electromagnetic spectrum, it is not resistant to nature. 
Starlink uses Ku-band and Ka-band for their satellite communication. This band is susceptible to weather conditions hence 2 additional metrics are connected.
### Weather data
We consifer sufficient to collect sky data - clear sky/cloudy/thunderstorm/rain (snow or other precipitation) as it affects the performace.
It is unlikely to see full disconnects, performance will only be degraded.
The effect of thunderstorms is unknown
### Space Weather data
This project was done about a year before predicted solar maximum in [July 2025](https://www.swpc.noaa.gov/products/solar-cycle-progression), albeit we haven't witnessed powerful enough GeoMagnetic storms or solar flares to draw any conclusion how it affects network performance. 
Given Ionosphere altitude and starlink orbital shell altitude, we hypotezize that we would need to see an event of magnitude that is at least G3 or R3 or S3. [NOAA scales](https://www.swpc.noaa.gov/noaa-scales-explanation)

## Customization
Write your own scripts for things you want to collect in whatever language you want to.
To add your metrics to this toolset follow the following:
 - Push the metrics to `InfluxDB:xxxx` with `DB=starlink` TODO!!!
 - create a Docker container from your "data collector"
 - add it to the provided `Docker-compose.yml` file. 
 - include the network interface in configuration that all the other containers share to be able to reach the DB
 - HOW TO READ THE INFLUX TOKEN ????