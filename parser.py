import string

from bs4 import BeautifulSoup


class AdvertisementPageParser:
    def __init__(self):
        self.soup = None

    @property
    def _download_links(self):
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
    def _description(self):
        des = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > article > "
            "div.movie > div.m-content > div.row > div.col-12.order-3 > div > p"
        )
        if des:
            return des.text

    @property
    def _image_link(self):
        img_link = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_poster.col"
            "-auto.order-1.order-sm-2.pt-4.pr-sm-0.mx-auto > div > a > img"
        )
        if img_link:
            return img_link.get('src')

    @property
    def _page_title(self):
        name = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-title > h1 > a"
        )

        if name:
            english_name = ''.join([i for i in name.text if i in string.printable])
            return english_name.strip(' ')
        return 'sample'

    @property
    def _site(self):

        text = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-publisher > span.val > a"
        )
        if text:
            return text.text

    @property
    def _genres(self):
        gen = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-genres > span.val"
        )
        if gen:
            return gen.text

    @property
    def _movie_score_IMDB(self):
        score = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-sm.pl-"
            "sm-0.order-2.order-sm-1 > ul > li.imdb_row.d-flex.flex-wrap.align-items-"
            "center > span.val"
        )
        if score:
            return score.text.split(" ")[0]

    @property
    def _movie_score_RT(self):
        rt = self.soup.select_one(
            '#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > '
            'article > div.movie > div.m-content > div.row > div.m_info.col-'
            'sm.pl-sm-0.order-2.order-sm-1 > ul > li.meta_row.d-flex.flex-'
            'wrap.align-items-center > span.val.pt-1')
        if rt:
            return rt.text

    @property
    def _language(self):
        lan = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-lang.mt-1 > span.val"
        )
        if lan:
            return lan.text

    @property
    def _stars(self):
        star = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-stars > span.val"
        )
        if star:
            return star.text

    @property
    def _director(self):
        d = self.soup.select_one(
            "#page_content > div > div > div.row.mt-3 > div.col-lg.pl-lg-0 > "
            "article > div.movie > div.m-content > div.row > div.m_info.col-"
            "sm.pl-sm-0.order-2.order-sm-1 > ul > li.m-director > span.val"
        )
        if d:
            return d.text

    def parse(self, html_data, data):
        self.soup = BeautifulSoup(html_data, "html.parser")
        data_dict = {
            "_id": data["_id"], "link": data["link"],
            "name": self._page_title, 'img_links': self._image_link,
            "description": self._description, 'download_links': self._download_links,
            "site": self._site, "genres": self._genres, 'IMDB': self._movie_score_IMDB,
            "RT": self._movie_score_RT, 'language': self._language, "stars": self._stars,
            "director": self._director,
        }

        return data_dict

