import logging
import unittest
from datetime import datetime
from pathlib import Path

FORMAT = '%(asctime)-15s %(levelname)s --- %(message)s'
logging.basicConfig(format=FORMAT, level=0)
logger = logging.getLogger(__name__)


def convert_utc_time_str_to_utc_timestamp(utc_time_str: str) -> int:
    gap = (datetime.now() - datetime.utcnow()).seconds
    return int(datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S').timestamp() + gap) * 1000


def convert_utc_timestamp_to_utc_time_str(utc_timestamp: int) -> str:
    utcfromtimestamp = datetime.utcfromtimestamp(utc_timestamp / 1000)
    return utcfromtimestamp.strftime('%Y-%m-%dT%H:%M:%S')


class TestDemo(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_is_upper(self):
        self.assertEqual('Foo'.isupper(), False)
        self.assertEqual('FOO'.isupper(), True)

    def test_path(self):
        test_file: Path = Path(__file__).parent / 'resources' / 'test_html_file_1.html'
        self.assertTrue(test_file.exists())

    def test_time_stamp(self):
        input_time_str = '2019-06-18T01:02:03'
        timestamp = convert_utc_time_str_to_utc_timestamp(input_time_str)
        logger.info(timestamp)
        self.assertEqual(input_time_str, convert_utc_timestamp_to_utc_time_str(timestamp))


if __name__ == '__main__':
    unittest.main()
