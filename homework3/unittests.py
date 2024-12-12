import unittest
from hw3 import remove_comments, parse_arrays, parse_constants, evaluate_expressions  # Замените your_module на имя вашего файла

class TestConfigTool(unittest.TestCase):

    def test_remove_comments(self):
        input_text = """{{!-- Это многострочный комментарий --}}
        def myConst = 42
        """
        expected_output = "def myConst = 42"
        self.assertEqual(remove_comments(input_text), expected_output)

    def test_parse_arrays(self):
        input_text = "myArray = [ 1; 2; 3; 4]"
        expected_arrays = {
            'array_0': ['1', '2', '3', '4']
        }
        arrays, remaining_text = parse_arrays(input_text)
        self.assertEqual(arrays, expected_arrays)
        self.assertEqual(remaining_text.strip(), "myArray = array_0")

    def test_parse_constants(self):
        input_text = """def myConst = 42
                        def myString = @"This is string"
                     """
        expected_constants = {
            'myConst': '42',
            'myString': '@"This is string"'
        }
        constants = parse_constants(input_text)
        self.assertEqual(constants, expected_constants)

    def test_evaluate_expressions(self):
        constants = {
            'myConst': '42',
            'myString': '@"This is string"'
        }
        input_text = "Value: $(myConst), String: $(myString)"
        expected_output = "Value: 42, String: @\"This is string\""
        
        result = evaluate_expressions(input_text, constants)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
