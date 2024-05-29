import sys

sys.path.append(sys.path[0][:-6]) # FUCK YOU PYTHON

import conf
if(conf.ENABLE_PING_MOD_TESTS):
    import modules.ping as ping


    config = dict()
    config['targets'] = list()
    config['targets'].append('1.1.1.1')
    config['targets'].append('8.8.8.8')
    #config['targets'].append('csgate.cs.uni-sb.de')
    #config['targets'].append('2803:9810:3340:3297:226:22ff:fe99:5259')

    ping.setup(None)

    def test_full_ping(capsys):
        values = ping.collect(config)
        # with capsys.disabled():
        #     print(values)   
        for entry in values:
            assert entry['metadata']['target'] in config['targets']
            assert entry['rtt_ms'] >= 0