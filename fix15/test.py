import unittest
import fix15
import io
import unittest.mock
import fix15.__main__

test_file = \
"""id,firstname,lastname,accountid
00300000053jhOc,john,smith,00100006gG70oPa
003000A694fjJ21,allison,brown,001000000043463
0030000bB09fQt9,thomas,tomlinson,001000004FfoA00
003000000044000,hannah,anderson,001000000000001
003000000npQ9vB,sarah,white,00100006gG70oPa"""
test_file_converted = \
"""id,firstname,lastname,accountid
00300000053jhOcAAI,john,smith,00100006gG70oPaAQI
003000A694fjJ21ACE,allison,brown,001000000043463AAA
0030000bB09fQt9AIE,thomas,tomlinson,001000004FfoA00AQE
003000000044000AAA,hannah,anderson,001000000000001AAA
003000000npQ9vBAAS,sarah,white,00100006gG70oPaAQI"""

class test_fix15(unittest.TestCase):
    def test_to18_realids(self):
        known_good_ids = {
            '01Q36000000RXX5': '01Q36000000RXX5EAO',
            '005360000016xkG': '005360000016xkGAAQ',
            '01I36000002zD9R': '01I36000002zD9REAU',
            '0013600001ohPTp': '0013600001ohPTpAAM',
            '0033600001gyv5B': '0033600001gyv5BAAQ'
        }

        for id_15 in known_good_ids:
            self.assertEqual(known_good_ids[id_15], fix15.to18(id_15))
            self.assertEqual(fix15.to18(id_15), fix15.to18(fix15.to18(id_15)))
    
    def test_to18_bad_input(self):
        self.assertEqual('', fix15.to18(''))
        with self.assertRaises(ValueError):
            fix15.to18('test')

    def test_process_file_index_mode(self):
        input_file = io.StringIO(test_file)
        output_file = io.StringIO(newline=None)

        fix15.process_file(input_file, output_file, [0, 3], skip_headers=True)

        self.assertEqual(test_file_converted.strip(), output_file.getvalue().strip())

    def test_process_file_column_mode(self):
        input_file = io.StringIO(test_file)
        output_file = io.StringIO(newline=None)

        fix15.process_file(input_file, output_file, ['id', 'accountid'])

        self.assertEqual(test_file_converted.strip(), output_file.getvalue().strip())

    def test_process_file_index_mode_no_skip_header(self):
        input_file = io.StringIO(test_file)
        output_file = io.StringIO(newline=None)

        with self.assertRaises(ValueError):
            fix15.process_file(input_file, output_file, [0, 3], skip_headers=False)

    def test_process_file_progress(self):
        input_file = io.StringIO(test_file)
        output_file = io.StringIO(newline=None)
        called_n = 0

        def p(b):
            nonlocal called_n
            self.assertTrue(b > 0 and b < len(test_file))
            called_n += 1

        fix15.process_file(input_file, output_file, ['id', 'accountid'], progress=p)

        self.assertEqual(5, called_n)
    
    def test_command_line(self):
        input_file = io.StringIO(test_file)
        output_file = io.StringIO(newline=None)

        with unittest.mock.patch('sys.argv', ['fix15', '-c', 'id', '-c', 'accountid']):
            with unittest.mock.patch('sys.stdin', input_file):
                with unittest.mock.patch('sys.stdout', output_file):
                    fix15.__main__.main()

        self.assertEqual(test_file_converted.strip(), output_file.getvalue().strip())


if __name__ == '__main__':
    unittest.main()