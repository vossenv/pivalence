from piveilance.config import Config
import yaml

def test_config():
    dict_a = {
        'a': 'b',
        'c': ['d', 'e'],
        'd': {'x': 't'},
        'e': {
            'a': [1, 2, '3'],
            'b1': {
                'a1': 'c1',
                'a2': ('a3', 'a4')
            }
        },
        'f': None
    }

    dict_b = {
        'x': {'y': 'z'},
        'a': 'bb',
        'c': ['dd', 'e'],
        'd': {'j': 'u'},
        'e': {

            'b1': {
                'a2': ('a3', 'a4')
            }
        },
        'f': {'g'}
    }

    r1 =  Config.merge_dict(dict_a, dict_b)

    Config.merge_dict(dict_a, dict_b, immutable=False)

    assert dict_a == r1 == {
        'a': 'bb',
        'c': ['dd', 'e'],
        'd': {
            'x': 't',
            'j': 'u'
        },
        'e': {
            'a': [1, 2, '3'],
            'b1': {
                'a1': 'c1',
                'a2': ('a3', 'a4')
            }
        },
        'f': {'g'},
        'x': {'y': 'z'}
    }

def test_complex():

    with open("complex_dict.yml") as config:
        complex = yaml.safe_load(config)

    with open("merge_config.yml") as config:
        merge = yaml.safe_load(config)

    with open('result.yml') as output:
        actual = yaml.safe_load(output)

    combined = Config.merge_dict(complex, merge)
    assert combined == actual

    # with open('temp.yml', 'w') as output:
    #     yaml.dump(combined, output)
    # print()


