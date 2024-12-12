import unittest
from unittest.mock import patch, mock_open, MagicMock
from hw2 import read_config, get_commit_tree, generate_plantuml_code, write_output, main

class TestHW2(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='[DEFAULT]\nvisualizer_path=/path/to/visualizer\nrepo_path=/path/to/repo\noutput_path=/path/to/output\n')
    def test_read_config(self, mock_file):
        config = read_config('dummy_path')
        expected_config = {
            'visualizer_path': '/path/to/visualizer',
            'repo_path': '/path/to/repo',
            'output_path': '/path/to/output'
        }
        self.assertEqual(config, expected_config)

    @patch('subprocess.run')
    def test_get_commit_tree(self, mock_run):
        # Настраиваем моки для команды git log и git diff-tree
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout='abc123 Commit message 1\nabc456 Commit message 2\n'),
            MagicMock(returncode=0, stdout='A\tfile1.txt\nM\tfile2.txt\nD\tfile3.txt\n'),
            MagicMock(returncode=0, stdout=''), 
        ]
        
        commit_info = get_commit_tree('/path/to/repo')
        
        expected_commit_info = {'abc123': {'message': 'Commit message 1', 'files': ['file1.txt', 'file2.txt', 'file3.txt'], 'actions': ['file1.txt (C)', 'file2.txt (R)', 'file3.txt (D)']}, 'abc456': {'message': 'Commit message 2', 'files': [], 'actions': []}}

        self.assertEqual(commit_info, expected_commit_info)

    def test_generate_plantuml_code(self):
        commit_info = {
            'abc123': {
                'message': 'Commit message 1',
                'files': ['file1.txt', 'file2.txt'],
                'actions': [
                    'file1.txt - Добавлен (C)',
                    'file2.txt - Изменён (R)'
                ]
            },
            'abc456': {
                'message': 'Commit message 2',
                'files': ['file3.txt'],
                'actions': [
                    'file3.txt - Удалён (D)'
                ]
            }
        }
        
        # Проверяем только структуру вывода без лишних деталей
        output = generate_plantuml_code(commit_info)
        
        self.assertIn('@startuml', output)
        self.assertIn('RECTANGLE', output)
        self.assertIn('Commit message 1', output)
        self.assertIn('Commit message 2', output)

    @patch('builtins.open', new_callable=mock_open)
    def test_write_output(self, mock_file):
        write_output('/path/to/output', 'test content')
        mock_file().write.assert_called_once_with('test content')

    @patch('hw2.read_config')
    @patch('hw2.get_commit_tree')
    @patch('hw2.generate_plantuml_code')
    @patch('hw2.write_output')
    def test_main(self, mock_write_output, mock_generate_plantuml_code, mock_get_commit_tree, mock_read_config):
        mock_read_config.return_value = {
            'visualizer_path': '/path/to/visualizer',
            'repo_path': '/path/to/repo',
            'output_path': '/path/to/output'
        }
        
        mock_get_commit_tree.return_value = {
            'abc123': {
                'message': 'Commit message 1',
                'files': ['file1.txt'],
                'actions': ['file1.txt - Добавлен (C)']
            },
            'abc456': {
                'message': 'Commit message 2',
                'files': [],
                'actions': []
            }
        }

        mock_generate_plantuml_code.return_value = '@startuml\n@enduml'

        main('dummy_config.ini')

        mock_read_config.assert_called_once_with('dummy_config.ini')
        mock_get_commit_tree.assert_called_once_with('/path/to/repo')
        mock_generate_plantuml_code.assert_called_once_with(mock_get_commit_tree.return_value)
        mock_write_output.assert_called_once_with('/path/to/output', '@startuml\n@enduml')

if __name__ == '__main__':
    unittest.main()
