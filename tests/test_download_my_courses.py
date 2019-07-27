import logging
import os
import unittest
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from unittest.mock import MagicMock

from sources.download_helper import DownloadHelper
from sources.download_my_course import DownloadMyCourses
from test_demo import FORMAT

logging.basicConfig(format=FORMAT, level=0)
logger = logging.getLogger(__name__)


class TestDownloadMyCourses(unittest.TestCase):

    def setUp(self) -> None:
        self.maxDiff = None
        self.download_my_courses = DownloadMyCourses('', '', DownloadHelper())

        def side_effect():
            print('download items')

        self.download_my_courses.download_items = MagicMock(side_effect=side_effect)

    def test_get_lecture_name_and_page_url_map(self):
        with open("test_html_file_2.html") as f:
            actual = self.download_my_courses.get_lecture_name_and_page_url_map(f.read().strip())

        print(actual)
        expect = [
            ("01_Getting Started_01_Welcome", "/courses/the-complete-node-js-course/lectures/4509750"),
            ("01_Getting Started_02_What is Node", "/courses/the-complete-node-js-course/lectures/4509035"),
            ("01_Getting Started_03_Node Architecture", "/courses/the-complete-node-js-course/lectures/4509036"),
            ("02_Node Module System_01_Introduction", "/courses/the-complete-node-js-course/lectures/4509169"),
            ("02_Node Module System_02_Global Object", "/courses/the-complete-node-js-course/lectures/4509174"),
        ]
        self.assertListEqual(expect, actual)

    def test_list_dict(self):
        s = ['a', 'b', 'c']
        zip1 = zip(range(len(s)), s)
        print(dict(zip1))

    def test_range(self):
        aaa = ['a', 'b']
        print(
            list(map(lambda item: f'{item[0]:02d} {item[1]}', enumerate(aaa)))
        )

        # [print(f'{idx:02d} {aaa[idx]}') for idx in range(len(aaa))]

    def test_get_all_sections_with_sequence_num(self):
        with open('test_html_file_1.html', encoding='utf8') as f:
            text = f.read()

        actual = self.download_my_courses.get_all_sections_with_sequence_num_using_html(text)
        expect = [
            'Getting Started',
            'Node Module System',
            'Node Package Manager',
            'Building RESTful APIs Using Express',
            'Express Advanced Topics',
            'Asynchronous JavaScript',
            'CRUD Operations Using Mongoose',
            'Mongo  Data Validation',
            'Mongoose Modeling Relationships between Connected Data',
            'Authentication and Authorization',
            'Handling and Logging Errors',
            'Unit Testing',
            'Integration Testing',
            'TestDriven Development',
            'Deployment'
        ]
        self.assertEqual(expect, actual)

    def test_get_lectures_with_file_name(self):
        text = (Path(__file__).parent / 'resources' / 'test_html_file_2.html').read_text()
        actual = self.download_my_courses.get_lectures_with_file_name(text)

        expect = {
            '4509750': '01_Getting Started_01_Welcome',
            '4509035': '01_Getting Started_02_What is Node',
            '4509036': '01_Getting Started_03_Node Architecture',
            '4509169': '02_Node Module System_01_Introduction',
            '4509174': '02_Node Module System_02_Global Object',
        }
        self.assertDictEqual(expect, actual)

    def test_list_to_map(self):
        a = dict([(i, i) for i in ['a', 'b']])

        print(a)

    def test_strip_except_alphanumeric(self):
        actual = self.download_my_courses.get_section_title_as_file_prefix('Getting Started (00:20)')
        expect = 'Getting Started'
        self.assertEqual(expect, actual)

        actual = self.download_my_courses.get_section_title_as_file_prefix(
            'Building RESTful API\'s Using Express (00:56)')
        expect = 'Building RESTful APIs Using Express'
        self.assertEqual(expect, actual)

        actual = self.download_my_courses.get_section_title_as_file_prefix(
            'Mongoose- Modeling Relationships between Connected Data (00:51)')
        expect = 'Mongoose Modeling Relationships between Connected Data'
        self.assertEqual(expect, actual)

    def test_get_lecture_page_url_prefix(self):
        text = (Path(__file__).parent / 'resources' / 'test_html_file_1.html').read_text()
        actual = self.download_my_courses.get_lecture_page_url_prefix(text)
        expect = 'https://codewithmosh.com/courses/293204/lectures'
        self.assertEqual(expect, actual)

    def test_get_each_lecture_download_info(self):
        text = (Path(__file__).parent / 'resources' / 'test_html_file_1.html').read_text()
        actual = self.download_my_courses.get_lecture_download_url(text)
        expect = ('.mp4', 'https://www.filepicker.io/api/file/1N9dD3plRdGGdB9N2hId')
        self.assertEqual(expect, actual)

    def test_download_items(self):
        self.download_my_courses.course_name = 'sql'
        self.download_my_courses.prepare_login_session()
        self.download_my_courses.download_items('01_Getting Started_01_Welcome.mp4',
                                                'https://www.filepicker.io/api/file/1N9dD3plRdGGdB9N2hId')

    def test_thread_pool(self):
        pool = ThreadPool()
        pool.map(self.temp1, [(1, 2), (3, 4)])
        pool.close()
        pool.join()

    def temp1(self, a):
        print('1- Welcome.mp4'[-4])

    def test_e2e_without_download(self):
        self.download_my_courses = DownloadMyCourses('nodejs',
                                                     'https://codewithmosh.com/courses/293204/lectures/4509750')
        self.download_my_courses.download_items = MagicMock(side_effect=print('download_items mock'))
        self.download_my_courses.start_download()

    def test_last_characters(self):
        print('1- Welcome.mp4'[-4:])

    def test_magic_mock(self):
        self.download_my_courses.download_items = MagicMock(side_effect=print('mock'))
        self.download_my_courses.download_items(('1', '1'))

    def test_env(self):
        [print(f'{k}, {v}') for k, v in sorted(os.environ.items())]

    def test_format_string(self):
        s = 1
        print(f'hello {s:02d}')

    def test_map_list(self):
        s1 = ['ok']

        print(s1 * 3)
        lll = ['a', 'b', 'c']
        # print(list(map(lambda s: s * 2, lll)))
        print(
            list(
                map(self.map_func, lll, range(len(lll)), s1 * 3)
            )
        )

    def test_list_general(self):
        print(list(range(1, 11)))

    def map_func(self, item, const, str1):
        return item + ' ' + str(const) + str1

    def test_main1(self):
        self.download_my_courses = DownloadMyCourses('java1',
                                                     'https://codewithmosh.com/courses/580597/lectures/10548877',
                                                     DownloadHelper())
        self.download_my_courses.start_download()

    def test_main2(self):
        self.download_my_courses = DownloadMyCourses('java2',
                                                     'https://codewithmosh.com/courses/606251/lectures/10953792',
                                                     DownloadHelper())
        self.download_my_courses.start_download()
