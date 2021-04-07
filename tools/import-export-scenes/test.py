import unittest
from import_export import *
class TestImport(unittest.TestCase):
    def test_obj_check_attr_ns_in_ns_list(self):
        obj = { 'namespace': 'public' }
        ns_config_dict = { 'public': None, 'ns1': { } }
        self.assertEqual(obj_check_attr(obj, 'namespace', ns_config_dict), True, "Should be True")

    def test_obj_check_attr_ns_not_in_ns_list(self):
        obj = { 'namespace': 'public' }
        ns_config_dict = { 'ns1': { } }
        self.assertEqual(obj_check_attr(obj, 'namespace', ns_config_dict), False, "Should be False")

    def test_obj_check_attr_ns_regex_true_no_skip(self):
        obj = { 'namespace': 'ns1' }
        ns_config_dict = { 'public': None, 'regex': { 'value': '.*', 'skip': False } }
        self.assertEqual(obj_check_attr(obj, 'namespace', ns_config_dict), True, "Should be True")

    def test_obj_check_attr_ns_regex_true_skip(self):
        obj = { 'namespace': 'ns1' }
        ns_config_dict = { 'public': None, 'regex': { 'value': '.*', 'skip': True } }
        self.assertEqual(obj_check_attr(obj, 'namespace', ns_config_dict), False, "Should be False")

    def test_check_list_ns_regex_true_no_skip(self):
        obj_list = [    { 'namespace': 'ns1' },
                        { 'namespace': 'ns2' },
                        { 'namespace': 'ns3' },
                        { 'namespace': 'public' },
                        { 'namespace': 'test' }]
        ns_config_dict = { 'public': None, 'regex': { 'value': 'ns*', 'skip': False } }
        res=[];
        expected=[True, True, True, True, False]
        for obj in obj_list:
            res.append(obj_check_attr(obj, 'namespace', ns_config_dict))
        self.assertEqual(res, expected, "Should match ns* and public")

    def test_check_list_ns_regex_true_skip(self):
        obj_list = [    { 'namespace': 'ns1' },
                        { 'namespace': 'ns2' },
                        { 'namespace': 'ns3' },
                        { 'namespace': 'public' },
                        { 'namespace': 'test' }]
        ns_config_dict = { 'public': None, 'regex': { 'value': 'ns*', 'skip': True } }
        res=[];
        expected=[False, False, False, True, False]
        for obj in obj_list:
            res.append(obj_check_attr(obj, 'namespace', ns_config_dict))
        self.assertEqual(res, expected, "Should skip ns* and test, match public")

    def test_check_list_ns_regex_true_skip_ns1(self):
        obj_list = [    { 'namespace': 'ns1' },
                        { 'namespace': 'ns2' },
                        { 'namespace': 'ns3' },
                        { 'namespace': 'public' },
                        { 'namespace': 'test' }]
        ns_config_dict = { 'public': None, 'ns1': None, 'regex': { 'value': 'ns*', 'skip': True } }
        res=[];
        expected=[True, False, False, True, False]
        for obj in obj_list:
            res.append(obj_check_attr(obj, 'namespace', ns_config_dict))
        self.assertEqual(res, expected, "Should match ns1 and public")

    def test_check_list_ns_regex_true_skip_undefined(self):
        obj_list = [    { 'namespace': 'ns1' },
                        { 'namespace': 'ns2' },
                        { 'namespace': 'ns3' },
                        { 'namespace': 'public' },
                        { 'namespace': 'test' }]
        ns_config_dict = { 'public': None, 'ns1': None, 'regex': { 'value': 'ns*' } }
        res=[];
        expected=[True, True, True, True, False]
        for obj in obj_list:
            res.append(obj_check_attr(obj, 'namespace', ns_config_dict))
        self.assertEqual(res, expected, "Should match ns* and public")

if __name__ == '__main__':
    unittest.main()
