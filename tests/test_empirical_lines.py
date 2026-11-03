import csv
from pathlib import Path
import tempfile
import unittest
from scripts.empirical_lines import select,render

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/evidence/copilot-integrity-20261103/figures/historical-runs.csv'


class LineFigureTests(unittest.TestCase):
    def rows(self):
        with SOURCE.open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))

    def test_all_six_arms_each_have_five_ordered_points(self):
        points=select(self.rows());self.assertEqual(len(points),30)
        for arm in {r['arm'] for r in points}:self.assertEqual([r['rep'] for r in points if r['arm']==arm],[1,2,3,4,5])
        with self.assertRaises(ValueError):select(points[:-1])
        with self.assertRaises(ValueError):select(points+[points[0]])
        bad=[dict(p) for p in points];bad[0]['total_tokens']+=1
        with self.assertRaises(ValueError):select(bad)

    def test_line_figures_have_real_ticks_six_series_and_no_learning_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            render(self.rows(),Path(directory),'0'*64)
            for name in ('combined-cents-tokens.svg','combined-cents-seconds.svg'):
                text=(Path(directory)/name).read_text()
                self.assertEqual(text.count('<polyline '),6)
                self.assertIn('not a learning curve',text)
                self.assertIn('Independent repetition index',text)
            self.assertIn('100,000',(Path(directory)/'combined-cents-tokens.svg').read_text())
