import glob
import os
import random
import re
import string

import requests
from bs4 import BeautifulSoup
from furl import furl
from hstest.check_result import CheckResult
from hstest.stage_test import StageTest
from hstest.test_case import TestCase
from hstest import WrongAnswer


class NatureScraper:
    def tag_leading_to_view_article(self, tag):
        return tag.has_attr("data-track-action") and tag["data-track-action"] == "view article"

    def tag_containing_atricle_type(self, tag):
        return tag.name == "span" and tag.has_attr("data-test") and tag["data-test"] == "article.type"

    def tag_containing_article_title(self, tag):
        return tag.name == "h1" and ("article" in tag["class"][0] and "title" in tag["class"][0])

    def get_article_links_of_type(self, url, article_type="News"):
        origin_url = furl(url).origin
        try:
            articles_resp = requests.get(url)
        except Exception:
            raise WrongAnswer("An error occurred when tests tried to connect to the Internet page.\n"
                              "Please, try again.")
        soup = BeautifulSoup(articles_resp.text, "html.parser")
        articles = soup.find_all(self.tag_containing_atricle_type)
        articles = list(filter(lambda x: x.text.strip() == article_type, articles))
        return [
            furl(origin_url).add(path=x.find_parent("article").find(self.tag_leading_to_view_article).get("href")).url \
            for x in articles]

    def get_article_title_and_content(self, url):
        try:
            article = requests.get(url)
        except Exception:
            raise WrongAnswer("An error occurred when tests tried to connect to the Internet page.\n"
                              "Please, try again.")
        soup = BeautifulSoup(article.text, "html.parser")
        title = soup.find(self.tag_containing_article_title)
        content = soup.find("p", {"class": "article__teaser"})
        if title and content:
            return title.text.strip(), content.text.strip()
        else:
            return title, content


class WebScraperTest(StageTest):
    def generate(self):
        txt_files = glob.glob("*.txt")
        for filename in txt_files:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
        return [TestCase(time_limit=0)]

    def check(self, reply, attach=None):
        scraper = NatureScraper()
        txt_files = glob.glob("*.txt")
        url = 'https://www.nature.com/nature/articles?sort=PubDate&year=2020&page=3'
        article_links = scraper.get_article_links_of_type(url)
        if len(txt_files) != len(article_links):
            return CheckResult.wrong("A wrong number of files with articles was found. \n"
                                     "{0} files were found, {1} files were expected.".format(len(txt_files),
                                                                                             len(article_links)))

        if not article_links:
            return CheckResult.correct()
        title, content = None, None
        while not title or not content:
            article_n = random.randint(0, len(article_links) - 1)
            title, content = scraper.get_article_title_and_content(article_links[article_n])
            if not title or not content:
                article_links.pop(article_n)
                if not article_links:
                    return CheckResult.correct()
        title = f"{title.translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')}.txt"
        print(title)
        if not os.path.exists(title):
            return CheckResult.wrong("A file with the name \"{0}\" was not found.\n"
                                     "Make sure you remove punctuation and \nreplace the whitespaces with underscores in the titles.".format(
                title))
        with open(title, "rb") as f:
            try:
                file_content = f.read().decode('utf-8').strip()
            except UnicodeDecodeError:
                return CheckResult.wrong("An error occurred when tests tried to read the file \"{0}\"\n"
                                         "Please, make sure you save your file in binary format \n"
                                         "and encode the saved data using utf-8 encoding.".format(title))
        file_content = re.sub('[\r\n]', '', file_content)
        content = re.sub('[\r\n]', '', content)
        if content in file_content:
            return CheckResult.correct()
        else:
            return CheckResult.wrong("Some of the files do not contain the expected article's body. \n"
                                     "The tests expected the following article:\n"
                                     f"\"{content}\"\n"
                                     f"However, the following text was found in the file {title}:\n"
                                     f"\"{file_content}\"")


if __name__ == '__main__':
    WebScraperTest().run_tests()
