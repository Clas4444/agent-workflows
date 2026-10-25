import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'.github/skills/loop-table/scripts/table_check.py'


class TableHelperTests(unittest.TestCase):
    def table(self, root, rows, bom=False):
        stream=io.StringIO(newline='');csv.writer(stream).writerows(rows)
        path=root/'input.csv';path.write_bytes((b'\xef\xbb\xbf' if bom else b'')+stream.getvalue().encode('utf-8'))
        return path

    def run_helper(self, mode, path, *args):
        return subprocess.run([sys.executable,str(HELPER),mode,str(path),*args],
                              capture_output=True,text=True,encoding='utf-8',timeout=20)

    def test_units_decimals_ids_formulas_and_missing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path=self.table(Path(directory),[['id','kind','amount','currency','note'],
                ['001','Travel','10.10','USD','train, city'],['002','Travel','0.20','USD','=SUM(A1:A2)'],
                ['003','Travel','5.00','EUR','meeting'],['004','Food','','USD','missing']],bom=True)
            before=path.read_bytes()
            inspect=self.run_helper('inspect',path);self.assertEqual(inspect.returncode,0,inspect.stderr)
            data=json.loads(inspect.stdout);self.assertEqual(data['row_count'],4)
            self.assertEqual(data['formula_like_text'],[{'record':2,'column':'note'}])
            strict=self.run_helper('aggregate',path,'--value','amount','--group','kind','--unit','currency')
            self.assertEqual(strict.returncode,1)
            self.assertEqual(strict.stdout,'')
            result=self.run_helper('aggregate',path,'--value','amount','--group','kind','--unit','currency','--allow-missing')
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads(result.stdout);self.assertFalse(data['complete'])
            sums={(row['group'],row['unit']):row['known_value_sum'] for row in data['subtotals']}
            self.assertEqual(sums,{('Travel','USD'):'10.30',('Travel','EUR'):'5.00',('Food','USD'):None})
            self.assertEqual(data['missing_value_records'],[4])
            self.assertEqual(path.read_bytes(),before)

    def test_extreme_scales_sum_without_rounding_away_small_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path=self.table(Path(directory),[['value'],['12345678901234567890.10'],['0.0000000000000000000001']])
            result=self.run_helper('aggregate',path,'--value','value','--unit-label','count')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['subtotals'][0]['known_value_sum'],
                             '12345678901234567890.1000000000000000000001')

    def test_duplicate_headers_ragged_rows_and_non_decimal_values_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for rows in ([['ID',' id '],['a','b']],[['a','b'],['only-one']],
                         [['value'],['NaN']],[['value'],['1e3']],[['value'],['1,234']]):
                path=self.table(root,rows);before=path.read_bytes()
                result=self.run_helper('aggregate',path,'--value','value','--unit-label','count')
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(result.stdout,'')
                self.assertEqual(path.read_bytes(),before)

    def test_no_unit_policy_no_silent_mixing_and_different_input_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for first,second,expected in [('7.75','2.25','10.00'),('-2.00','0.50','-1.50')]:
                path=self.table(root,[['value','unit'],[first,'USD'],[second,'USD']])
                self.assertEqual(self.run_helper('aggregate',path,'--value','value').returncode,1)
                result=self.run_helper('aggregate',path,'--value','value','--unit','unit')
                self.assertEqual(json.loads(result.stdout)['subtotals'][0]['known_value_sum'],expected)

    def test_row_limit_and_multiline_quoted_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path=self.table(Path(directory),[['id','text'],['001','line one\nline two'],['002','next']])
            self.assertEqual(self.run_helper('inspect',path,'--max-rows','1').returncode,1)
            result=self.run_helper('inspect',path)
            self.assertEqual(json.loads(result.stdout)['row_count'],2)
