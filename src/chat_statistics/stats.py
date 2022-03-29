import json
from pathlib import Path
from typing import Union

import arabic_reshaper
from hazm import Normalizer
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """Generates a chat statistics from a telegram chat json file
    """
    def __init__(self, chat_json: Union[str, Path]):
        """Args:
            chat_json (Union[str, Path]): path to telegram export json file
        """

        # load chat data
        logger.info(f'loading chat data from {chat_json}')
        with open(chat_json) as f:
            self.chat_data = json.load(f)

        self.normalizer = Normalizer()

        # load stopwords
        logger.info(f'loading stopwords from {DATA_DIR}/stopwords.txt')
        with open(Path(DATA_DIR) / 'stopwords.txt') as f:
            stopwords = f.readlines()
        stopwords = set(map(str.strip, stopwords))
        self.stopwords = set(map(self.normalizer.normalize, stopwords))

    def generate_word_cloud(self,
                            output_dir: Union[str, Path],
                            width=1200,
                            height=1200,
                            max_font_size=300,
                            background_color='white'):
        """generates a word cloud from the chat data

        Args:
            output_dir (Union[str, Path]): path to output directory for word
            cloud image
            width (int, optional): width of word cloud image.
            Defaults to 1200.
            height (int, optional): height of word cloud image.
            Defaults to 1200.
            max_font_size (int, optional): max font for words in word cloud.
            Defaults to 300.
            background_color (str, optional): background color of wordcloud
            image.
            Defaults to 'white'.
        """

        text_content = ''

        logger.info('Loading text content...')
        for msg in self.chat_data['messages']:
            content = msg['text']
            if(type(content) is str):
                text_content += f" {str(content).strip()}"

        # normalize, reshape for final word cloud
        text_content = arabic_reshaper.reshape(text_content)
        text_content = self.normalizer.normalize(text_content)

        # generate word cloud
        logger.info('Generating word cloud...')
        word_cloud = WordCloud(
            width=width,
            height=height,
            max_font_size=max_font_size,
            font_path=str(DATA_DIR) +
            '/font/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf',
            background_color=background_color,
            stopwords=self.stopwords
            ).generate(text_content)

        logger.info(f'Saving word cloud to {output_dir}')
        word_cloud.to_file(str(output_dir)+'/wordcloud.png')


if __name__ == '__main__':
    chat_stats = ChatStatistics(chat_json=DATA_DIR / 'online.json')
    chat_stats.generate_word_cloud(output_dir=DATA_DIR)
    print('DONE!')
