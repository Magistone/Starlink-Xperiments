import sys

sys.path.append(sys.path[0][:-6]) # FUCK YOU PYTHON

import conf

if conf.ENABLE_TRACEROUTE_MOD_TESTS:
    import modules.traceroute as trace


    config = dict()
    config['targets'] = list()
    config['targets'].append('1.1.1.1')
    config['targets'].append('8.8.8.8')
    config['targets'].append('csgate.cs.uni-sb.de')
    #config['targets'].append('2803:9810:3340:3297:226:22ff:fe99:5259')

    trace.setup(None)

    def test_full_trace():
        return
        print("Hi")
        values = trace.collect(config)
        print("Bye")
        for key in values.keys():
            assert key in config['targets']