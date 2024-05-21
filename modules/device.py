import modules.grpc as dish
import grpc
from yagrc import importer
import re

importer.add_lazy_packages(["spacex.api.device", "spacex.api.satellites.network"])
from spacex.api.device import dish_pb2 # type: ignore
from spacex.api.satellites.network import ut_disablement_codes_pb2 # type: ignore



def extract_alignment(raw_data):
    if raw_data.HasField('alignment_stats'):
        data = {
            'tilt_angle_deg': getattr(raw_data.alignment_stats, 'tilt_angle_deg', 0),
            'azimuth_deg': getattr(raw_data.alignment_stats, 'boresight_azimuth_deg', 0),
            'elevation_deg': getattr(raw_data.alignment_stats, 'boresight_elevation_deg', 0),
            'desired_azimuth_deg': getattr(raw_data.alignment_stats, 'desired_boresight_azimuth_deg', 0),
            'desired_elevation_deg': getattr(raw_data.alignment_stats, 'desired_boresight_elevation_deg', 0),
            'attitude_uncertainty_deg': getattr(raw_data.alignment_stats, 'attitude_uncertainty_deg', 0),
        }
        try:
            data['estimation_state'] = dish_pb2.AttitudeEstimationState.Name(raw_data.alignment_stats.attitude_estimation_state)
        except ValueError:
            data['estimation_state'] = 'UNKNOWN'
        
        return data
    return None

def extract_network(raw_data):
    data = {}
    data['cell_disabled'] = getattr(raw_data, 'is_cell_disabled', False)
    data['snr_persistently_low'] = getattr(raw_data, 'is_snr_persistently_low', False)
    data['snr_above_noisefloor'] = getattr(raw_data, 'is_snr_above_noisefloor', True)
    data['pop_ping_ms'] = getattr(raw_data, 'pop_ping_latency_ms', 0)
    data['pop_ping_drop_rate'] = getattr(raw_data, 'pop_ping_drop_rate', 0)
    data['seconds_to_non_empty_slot'] = getattr(raw_data, 'seconds_to_first_non_empty_slot', 0)
    data['throughtput'] = {}
    data['throughtput']['down_bps'] = getattr(raw_data, 'downlink_throughtput_bps', 0)
    data['throughtput']['up_bps'] = getattr(raw_data, 'uplink_throughtput_bps', 0)

    return data

def extract_alerts(raw_data):
    data = {}
    if raw_data.HasField('alerts'):
        for field in raw_data.alerts.DESCRIPTOR.fields:
            if getattr(raw_data.alerts, field.name, False):
                data[field.name] = True

        return data 
    return None

def extract_outage(raw_data):
    data = {}
    if raw_data.HasField('outage'):
        try:
            data['cause'] = dish_pb2.DishOutage.Cause.Name(raw_data.outage.cause)
        except ValueError:
            data['cause'] = 'UNKNOWN'
        data['start_ns'] = getattr(raw_data.outage, 'start_timestamp_ns', 0)
        data['duration_ns'] = getattr(raw_data.outage, 'duration_ns', 0)
        data['switched'] = getattr(raw_data.outage, 'did_switch', False)
        return data
    return None

def extract_info(raw_data):
    data = {}
    if raw_data.HasField('device_info') or raw_data.HasField('software_update_stats'):
        data['software'] = {}

    #extract device_info partially
    if raw_data.HasField('device_info'):
        data['id'] = getattr(raw_data.device_info, 'id', 'UNKNOWN')
        version = re.match('^[^\.]+', getattr(raw_data.device_info, 'software_version', 'UNKNOWN'))
        data['software']['version'] = 'UNKNOWN' if version == None else version.group()
        data['country'] = getattr(raw_data.device_info, 'country_code', '??')
    
    #extract update_stats
    if raw_data.HasField('software_update_stats'):
        try:
            state = dish_pb2.SoftwareUpdateState.Name(getattr(raw_data.software_update_stats, 'software_update_state', -1))
        except ValueError:
            state = 'UNKNOWN'
        data['software']['update_state'] = state
        data['software']['update_progress'] = getattr(raw_data.software_update_stats, 'software_update_progress', 0)

    #extract literals/enums
    try:
        data['disablement_code'] = ut_disablement_codes_pb2.UtDisablementCode.Name(getattr(raw_data, 'disablement_code', -1))
    except ValueError:
        data['disablement_code'] = 'UNKNOWN'

    try:
        data['service_class'] = dish_pb2.UserClassOfService.Name(getattr(raw_data, 'class_of_service', -1))
    except ValueError:
        data['service_class'] = 'UNKNOWN'

    try:
        data['mobility_class'] = dish_pb2.UserMobilityClass.Name(getattr(raw_data, 'mobility_class', -1))
    except ValueError:
        data['mobility_class'] = 'UNKNOWN'
    
    return data


def setup(setup):
    #resolve imports through gRPC reflection for current version
    channel = grpc.insecure_channel('192.168.100.1:9200')
    importer.resolve_lazy_imports(channel)

def collect(config):
    #Use get status as not all data are exposed in status_data()
    #Then extract the relevant metrics...
    #... and convert enums to string (OH GOD WHY)
    try:
        status = dish.get_status()
    except (grpc.RpcError, AttributeError, ValueError):
        return None
    
    data = {
        'alignment': extract_alignment(status),
        'network': extract_network(status),
        'alerts': extract_alerts(status),
        'outage': extract_outage(status),
        'info': extract_info(status)
    }

    #find keys with no value (None)
    to_delete = list()
    for key in data.keys():
        if data[key] == None:
            to_delete.append(key)
    #Delete them
    for key in to_delete:
        data.pop(key)

    if data:
        return data
    return None
    

# What do we extract from get_status?
# If you want to dig around and cahnge/add extracted data: `grpcurl -plaintext 192.168.100.1:9200 describe SpaceX.API.Device.DishGetStatusResponse`
# FIELD                                 Extracted? (note)                       Location of extraction  done?
# device_info                           YES, some (obj)                         info                    X            
# device_state                          NO (has only uptime in sec)             ----
# seconds_to_first_non_empty_slot       Maybe.. for polar/boot scenario?        network                 X
# pop_ping_drop_rate                    YES (float)                             network                 X
# obstruction_stats                     NO, dish.get_obstruction_map()          ----
# alerts                                YES (obj of bools)                      alerts                  X
# {downlink, uplink}_throughtput_bps    YES (float)                             network                 X
# pop_ping_latency_ms                   YES (float)                             network                 X
# stow_requested                        NO                                      ----
# boresight_{azimuth, elevation}_deg    NO, see alignemnt_stats                 ----
# outage                                YES (obj)                               outage                  X
# gps_stats                             NO, use dish.get_location()             ----
# ethernet_speed_mbps                   NO (no need)                            ----
# mobility_class                        YES (enum)                              info                    X
# is_snr_above_noise_floor              YES (bool)                              network                 X
# ready_states                          NO (dunno what they are)                ----
# class_of_service                      YES (enum)                              info                    X
# software_update_state                 NO, see software_update_stats           ----
# is_snr_persistently_low               YES (bool)                              network                 X
# has_actuators                         NO (inconsistent)                       ----
# disablement_code                      YES (enum)                              info                    X
# has_signed_calls                      NO (no need)                            ----
# software_update_stats                 YES (enum + float)                      info                    X
# alignment_stats                       YES                                     alignment               X
# initialization_duration_seconds       NO (no need)                            ----
# is_cell_disabled                      YES (bool)                              network                 X
# config                                NO (bools)                              ----