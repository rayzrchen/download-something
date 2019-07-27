import logging
from abc import ABC, abstractmethod
from pathlib import Path

from bs4 import BeautifulSoup
from requests import Response

FORMAT = '%(asctime)-15s %(levelname)s --- %(message)s'
logging.basicConfig(format=FORMAT, level=0)
logger = logging.getLogger(__name__)


class DownloadHelperService(ABC):
    @abstractmethod
    def prepare_course_folder(self, course_name: str):
        pass

    @abstractmethod
    def get_token_string(self, resp: Response) -> str:
        pass


class DownloadHelper(DownloadHelperService):

    def get_token_string(self, resp: Response) -> str:
        if not resp.ok:
            raise ValueError("Error while getting the auth token")
        soup = BeautifulSoup(resp.text, 'lxml')
        return soup.find('input', {'name': 'authenticity_token'})['value']

    def prepare_course_folder(self, course_name: str):
        course_folder: Path = Path(__file__).parent.parent / 'courses' / course_name
        logger.info(course_folder.resolve())
        if not course_folder.exists():
            course_folder.mkdir(exist_ok=True)
