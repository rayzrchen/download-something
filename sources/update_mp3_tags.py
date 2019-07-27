import logging
import re
from pathlib import Path
from typing import List

from mutagen.easyid3 import EasyID3

logger = logging.getLogger(__name__)


class UpdateMp3Tags:

    def __init__(self, music_folder_str: str):
        self.music_folder = Path(music_folder_str)

    def update_all_files(self):
        [self.update_each_file(mp3) for mp3 in self.music_folder.iterdir()]

    def update_each_file(self, mp3: Path):
        loaded = EasyID3(mp3.absolute())
        name_no_mp3 = mp3.name.replace('.mp3', '')
        name_split = name_no_mp3.split('-')
        title_artist = self.get_title_artist(name_split)

        loaded['title'] = title_artist[0]
        loaded['artist'] = title_artist[1]
        loaded['album'] = self.find_album(name_no_mp3, title_artist[1])

        loaded.save()

    def replace_name(self, old_name: str):
        return re.sub(r'(.+)(-.{11}\.mp3)', '\g<1>.mp3', old_name)

    def find_album(self, name: str, default_name: str):
        if name.find('(') > -1:
            strip = re.sub(r'.+\((.+?)\).*', '\g<1>', name).strip(' ')
            logger.info(strip)
            return strip
        else:
            return default_name

    def get_title_artist(self, name_split: List[str]):
        if len(name_split) == 2:
            return name_split[1], name_split[0]
        else:
            return name_split, name_split


if __name__ == '__main__':
    update_mp_tags = UpdateMp3Tags('')
    update_mp_tags.update_all_files()
