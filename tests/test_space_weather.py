import sys

sys.path.append(sys.path[0][:-6]) # FUCK YOU PYTHON

import modules.space_weather as sw

def test_sw(capsys): 
    sw.setup(None)
    data = sw.collect(None)

    assert(data.get('R') != None)
    assert(data.get('S') != None)
    assert(data.get('G') != None)
