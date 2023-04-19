import string

from bs4 import BeautifulSoup


class AdvertisementPageParser:
    def __init__(self):
        self.soup = None

    @property
    def download_links(self):
        urls = None
        try:
            urls = self.soup.select_one(
                "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 >"
                " article > div.movie > div.m-content > div.m_content"
            ).find_all('a')
        except:
            pass

        if urls:
            links = []
            for link in urls:
                text = "".join([i for i in link.text if i in string.printable])
                link = link.get('href')
                if not link.startswith("https://subscene.com/subtitles/"):
                    links.append(link)
            if links:
                return links
        return None

    @property
    def description(self):
        des = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > article > "
            "div.movie > div.m-content > div.row > div.col-12.order-3 > div > p"
        )
        if des:
            return des.text

    @property
    def image_link(self):
        img_link = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_poster.col"
            "-auto.order-1.order-sm-2.pt-4.pr-sm-0.mx-auto > div > a > img"
        )
        if img_link:
            return img_link.get('src')

    @property
    def page_title(self):
        name = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-title > h1 > a"
        )

        if name:
            english_name = ''.join([i for i in name.text if i in string.printable])
            return english_name.strip(' ')
        return 'sample'

    @property
    def site(self):

        text = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-publisher > span.val > a"
        )
        if text:
            return text.text

    @property
    def genres(self):
        gen = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-genres > span.val"
        )
        if gen:
            return gen.text

    @property
    def movie_score_IMDB(self):
        score = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-sm.pl-"
            "sm-0.order-2.order-sm-1 > ul > li.imdb_row.d-flex.flex-wrap.align-items-"
            "center > span.val"
        )
        if score:
            return score.text.split(" ")[0]

    @property
    def movie_score_RT(self):
        rt = self.soup.select_one(
            '#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > '
            'article > div.movie > div.m-content > div.row > div.m_info.col-'
            'sm.pl-sm-0.order-2.order-sm-1 > ul > li.meta_row.d-flex.flex-'
            'wrap.align-items-center > span.val.pt-1')
        if rt:
            return rt.text

    @property
    def language(self):
        lan = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-lang.mt-1 > span.val"
        )
        if lan:
            return lan.text

    @property
    def stars(self):
        star = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-stars > span.val"
        )
        if star:
            return star.text

    @property
    def director(self):
        d = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-director > span.val"
        )
        if d:
            return d.text

    def parse(self, html_data, link):
        self.soup = BeautifulSoup(html_data, "html.parser")
        data_dict = {
            "_id": link[1], "movie_information_link": link[0],
            "name": self.page_title, 'img_links': self.image_link,
            "description": self.description, 'download_links': self.download_links,
            "site": self.site, "genres": self.genres, 'IMDB': self.movie_score_IMDB,
            "RT": self.movie_score_RT, 'language': self.language, "stars": self.stars,
            "director": self.director,
        }

        return data_dict

