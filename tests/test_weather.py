import sys

sys.path.append(sys.path[0][:-6]) # FUCK YOU PYTHON

import conf
if (conf.DISH_ON_NETWORK):
    import modules.weather as w

    def test_weather():
        w.setup(None)
        data = w.collect({'user_agent': 'starlinkXperiments/dev privateemail@gmail.com'})
        assert(data.get('temperature_C') != None)
        assert(data.get('cloud_fraction_area_%') != None)
        assert(data.get('precipitation_amount_mm') != None)