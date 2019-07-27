import datetime
import itertools
import logging
import os
import re
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from typing import List, Tuple, Optional, Dict

import requests
from bs4 import BeautifulSoup, Tag

from sources.download_helper import DownloadHelperService

FORMAT = '%(asctime)-15s %(levelname)s --- %(message)s'
logging.basicConfig(format=FORMAT, level=0)
logger = logging.getLogger(__name__)


class DownloadMyCourses:
    website_prefix = 'https://codewithmosh.com'
    req_session = requests.session()
    pool = ThreadPool()

    def __init__(self, course_name: str, first_course_url: str, helper: DownloadHelperService):
        self.course_name = course_name
        self.first_course_url = first_course_url
        self.helper = helper

    def start_download(self):
        logger.info('start_download')
        self.helper.prepare_course_folder(self.course_name)
        self.prepare_login_session()

        self.pool.map(self.download_items, self.prepare_download_items())
        self.pool.close()
        self.pool.join()

    def get_section_title_as_file_prefix(self, str1: str) -> str:
        no_time_info = re.sub(r'\(.+', '', str1)
        return re.sub('[-?!*<>|":/\']|\n', '', no_time_info).strip()

    def download_items(self, lecture_file_name_with_url: Tuple[str, str]):
        if lecture_file_name_with_url[1] != '':
            full_path: Path = Path(__file__).parent.parent / 'courses' / self.course_name / lecture_file_name_with_url[0]
            logger.info(f"starting download {full_path}")
            if not full_path.exists():
                full_path.write_bytes(self.req_session.get(lecture_file_name_with_url[1]).content)
                # with open(full_path.resolve(), 'wb') as f:
                #     f.write(self.req_session.get(lecture_file_name_with_url[1]).content)

    def prepare_download_items(self) -> List[Tuple[str, str]]:
        logger.info('prepare_download_items')
        r = self.req_session.get(self.first_course_url)

        lectures_with_file_name = self.get_lectures_with_file_name(r.text)
        lecture_page_url_prefix = self.get_lecture_page_url_prefix(r.text)

        def map_lecture_file_name_to_download_url(lecture: str, file_name: str) -> Optional[Tuple[str, str]]:
            r2 = self.req_session.get(f'{lecture_page_url_prefix}/{lecture}')
            if not r2.ok:
                logger.exception(f'status code: {r2.status_code} for lecture: {file_name}')
                return

            suffix, url = self.get_lecture_download_url(r2.text)
            result = file_name + suffix, url
            logger.info(f'{result[0]} === {result[1]}')
            return result

        return [map_lecture_file_name_to_download_url(k, v) for k, v in lectures_with_file_name.items()]

    def prepare_login_session(self):
        prefix = 'https://sso.teachable.com/secure/146684/users'

        auth_token = self.helper.get_token_string(
            self.req_session.get(f'{prefix}/sign_in?clean_login=true&reset_purchase_session=1')
        )

        logger.info(f'auth_token: {auth_token}')

        data = {
            'utf8': '&#x2713;',
            'authenticity_token': auth_token,
            'user[school_id]': '146684',
            'user[email]': os.environ['SITE_USER'],
            'user[password]': os.environ['SITE_PASSWORD'],
            'commit': 'Log In',
        }

        login_post = self.req_session.post(f'{prefix}/sign_in?flow_school_id=146684', data=data)
        if not login_post.ok:
            logger.error(f'status_code: {login_post.status_code}')
            logger.error(f'content: {login_post.content}')
            raise PermissionError('Fail to login')

    def get_all_sections_with_sequence_num_using_html(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'lxml')
        section_locks = soup.select('span.section-lock')
        return [self.get_section_title_tag(section_lock) for section_lock in section_locks]

    def get_section_title_tag(self, section_lock: Tag) -> str:
        return self.get_section_title_as_file_prefix(section_lock.next_sibling)

    def get_all_lectures_pages(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'lxml')
        link_items = soup.select('a.item')
        return [link_item['href'] for link_item in link_items]

    def get_lectures_with_file_name(self, html: str) -> Dict[str, str]:
        soup = BeautifulSoup(html, 'lxml')
        section_locks: List[Tag] = soup.select('span.section-lock')

        dual_list = [self.map_to_lecture_list(section_lock, idx) for idx, section_lock in enumerate(section_locks)]
        return dict(list(itertools.chain(*dual_list)))

    def map_to_lecture_list(self, section_lock: Tag, index: int) -> List[Tuple[str, str]]:
        title_as_file_prefix = self.get_section_title_as_file_prefix(section_lock.next_sibling)
        section_title_as_file_prefix = f'{index + 1:02d}_{title_as_file_prefix}'
        section_items = section_lock.parent.parent.select('li.section-item')

        def map_item_to_lecture(each_item: Tuple[int, Tag]) -> Tuple[str, str]:
            lecture_id = each_item[1]['data-lecture-id']
            lecture_name = self.get_section_title_as_file_prefix(each_item[1].select_one('.lecture-name').get_text())
            return lecture_id, f'{section_title_as_file_prefix}_{each_item[0] + 1:02d}_{lecture_name}'

        return list(map(map_item_to_lecture, enumerate(section_items)))

    def get_lecture_download_url(self, html: str) -> Tuple[str, str]:
        soup = BeautifulSoup(html, 'lxml')

        download = soup.select_one('a.download')
        if download is not None:
            url = download['href']
            suffix = download['data-x-origin-download-name'][-4:]
        else:
            url = ''
            suffix = ''
        return suffix, url

    def get_lecture_page_url_prefix(self, html: str) -> str:
        soup = BeautifulSoup(html, 'lxml')
        url = soup.find('meta', property='og:url')['content']
        return re.sub('lectures/.+', 'lectures', url)

    def get_lecture_name_and_page_url_map(self, html: str):
        soup = BeautifulSoup(html, 'lxml')

        def strip_name(str1: str) -> str:
            str1 = re.sub(r'\(.+', '', str1)
            return re.sub('[-?!*<>|":/\']|\n', '', str1).strip()

        course_sections = soup.select("div.lecture-sidebar .course-section")

        def get_section_name(idx: int, course_section: Tag) -> str:
            return strip_name(f"{idx + 1:02d}_{strip_name(course_section.select_one('.section-title').get_text())}")

        def get_lectures(course_section: Tag) -> List[Tuple[str, str]]:
            lectures = course_section.select(".item")
            return [(get_lecture_as_key(idx, lectures[idx]), lectures[idx]['href']) for idx in range(len(lectures))]

        def get_lecture_as_key(idx: int, lecture: Tag) -> str:
            return f"{idx + 1:02d}_{strip_name(lecture.get_text())}"

        sections_ = {get_section_name(idx, course_sections[idx]): get_lectures(course_sections[idx])
                     for idx in range(len(course_sections))}

        aa = [[(f"{k}_{each_v[0]}", each_v[1]) for each_v in v] for k, v in sections_.items()]

        chain = itertools.chain(*aa)
        return list(chain)
