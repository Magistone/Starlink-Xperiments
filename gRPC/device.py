from spacex.api.device import dish_pb2, device_pb2, device_pb2_grpc

REQUEST_TIMEOUT = 10


def getStuff(channel):
    stub = device_pb2_grpc.DeviceStub(channel=channel)
    response = stub.Handle(device_pb2.Request(get_status={}), timeout = REQUEST_TIMEOUT)
    print(response)

# with grpc.insecure_channel("192.168.100.1:9200") as channel:
#     getStuff(channel)

# get_status, get_location, get_next_id, get_device_info

print(device_pb2.Request(dish_get_context={}))