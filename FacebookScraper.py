from bs4 import BeautifulSoup
from FacebookRenderEngine import RenderEngine
import json
import time


class Scraper:
    def __init__(self, username, password):
        self.__render_engine = RenderEngine(username, password)

    def close(self):
        self.__render_engine.close_engine()

    def __extract_comment_data(self, data_block, parent_id):
        comment_data = {'comment_id': data_block.get('data-uniqueid'), 'comment_author': '',
                        'comment_message': 'Graphical Emoji', 'comment_like_link': '',
                        'parent_id': parent_id,
                        'num_of_replies': 0, 'reply_username_list': [], 'comment_time': ''}
        comment_block = data_block.find('div', class_='_2b04')
        # extract author
        comment_data['comment_author'] = comment_block.find('div', class_='_2b05') \
            .find('a') \
            .get('href') \
            .split('?')[0].replace('/', '')
        # extract comment like link
        comment_data['comment_like_link'] = "https://www.facebook.com" + \
                                            comment_block.find('a', class_='_14v8').get('href')
        # extract comment message
        comment_message_tag = comment_block.find('div', class_='_14v5') \
            .find('div', {'data-sigil': "comment-body"})
        if comment_message_tag is not None:
            comment_data['comment_message'] = comment_message_tag.text
        # extract comment time
        comment_time_tag = comment_block.find('abbr', class_='_4ghv _2b0a')
        if comment_time_tag is not None:
            comment_data['comment_time'] = comment_time_tag.text
        return comment_data

    def __get_local_time_from_epoch(self, epoch_time):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(epoch_time)))

    def __get_type_of_post(self, post_block):
        if post_block.find('a', class_='_39pi') is not None:
            return 'Photo'
        if post_block.find('a', class_='_39pi _26ih') is not None:
            return 'Photo'
        if post_block.find('i', class_='img _lt3 _4s0y') is not None:
            return 'Video'
        if post_block.find('a', class_='touchable _4qxt') is not None:
            return 'Link'
        return 'Text'

    def get_post_list(self, page_title):
        html_source = self.__render_engine.render_posts_of_page(page_title)
        post_data_template = {'page_id': '', 'post_id': '', 'post_type': '', 'post_published': '',
                              'num_shares': 0, 'num_comments': 0}
        post_data_list = []
        soup = BeautifulSoup(html_source, 'html.parser')
        list_post_tag = soup.find_all('div', class_='_3w7e')
        for post_tag in list_post_tag:
            post_data = post_data_template.copy()

            # extract page_id, post_id, post_published_time
            article_tag = post_tag.find('article', class_='_55wo _5rgr _5gh8 async_like')
            json_data = json.loads(article_tag.get('data-ft'))
            post_data['page_id'] = json_data['page_id']
            post_data['post_id'] = json_data['top_level_post_id']
            post_context = json_data['page_insights'][post_data['page_id']]['post_context']
            post_data['post_published'] = self.__get_local_time_from_epoch(
                post_context['publish_time'])
            post_data['post_type'] = self.__get_type_of_post(post_tag)

            # extract number of shares and comments
            share_comment_tags = post_tag.find_all('span', class_='_1j-c')
            for share_comment_tag in share_comment_tags:
                share_comments_data = share_comment_tag.text.split()
                if 'share' in share_comments_data[1]:
                    post_data['num_shares'] = share_comments_data[0]
                elif 'comment' in share_comments_data[1]:
                    post_data['num_comments'] = share_comments_data[0]
            post_data_list.append(post_data.copy())
        return post_data_list

    def get_post_details(self, post_link):
        html_source = self.__render_engine.render_web_page(post_link)
        post_details = {'post_message': '', 'post_like_link': '', 'post_share_link': ''}
        soup = BeautifulSoup(html_source, 'html.parser')

        # get post message
        post_message_tag = soup.find('div', class_='_5rgt _5nk5')
        if post_message_tag is not None:
            post_details['post_message'] = post_message_tag.text

        # get post reactions link
        post_reactions_tag = soup.find('div', class_='_52jh _5ton _45m7')
        if post_reactions_tag is not None:
            post_details['post_like_link'] = "https://m.facebook.com{}".format(post_reactions_tag.find('a').get('href'))

        # get post shares link
        post_shares_tag = soup.find('div', class_='_43lx _55wr')
        if post_shares_tag is not None:
            post_shares_link = post_shares_tag.find('a').get('href')
            if "https://m.facebook.com/ufi/reaction/profile/" not in post_shares_link:
                # /browse/shares?id=246585629427087&__tn__=-R
                share_id = post_shares_link.split("id=")[1].split('&')[0]
                post_shares_link = "https://www.facebook.com/shares/view?id=" + share_id
            post_details['post_share_link'] = post_shares_link
        return post_details

    def get_reactions_count(self, post_like_link):
        reactions = {
            'All': 0,
            'Like': 0, 'Wow': 0, 'Love': 0, 'Haha': 0, 'Sad': 0, 'Angry': 0,
        }
        html_source = self.__render_engine.render_web_page(post_like_link)
        soup = BeautifulSoup(html_source, 'html.parser')

        # get total number of reactions
        num_reactions_tag = soup.find(lambda tag: tag.name == 'span' and tag.get('class') == ['_5p-9'])
        if num_reactions_tag is not None:
            reactions_data = num_reactions_tag.text.split()
            reactions[reactions_data[0].strip()] = reactions_data[1]

        # get count of each reaction types
        tags_reactions_type = soup.find_all('span', class_='_5p-9 _5p-l')
        for tag_reactions_type in tags_reactions_type:
            reactions_data = tag_reactions_type.get('aria-label')
            reactions_data = reactions_data.split()
            reactions[reactions_data[-1].strip()] = reactions_data[0]
        if reactions['All'] == 0:
            for val in reactions.values():
                if val != 0:
                    reactions['All'] = val
                    break
        return reactions

    def get_liked_user_list(self, like_link):
        html_source = self.__render_engine.render_like_link_of_post(like_link)
        soup = BeautifulSoup(html_source, 'html.parser')
        user_tags = soup.find_all('div', class_='_5j0e fsl fwb fcb')
        liked_user_list = []
        for user_tag in user_tags:
            user_a_tag = user_tag.find('a', href=True)
            if user_a_tag is not None:
                user_id = user_a_tag.get('data-hovercard').split('?')[1].split('=')[1].split('&')[0]
                liked_user_list.append(user_id)
        return liked_user_list

    def get_shared_user_list(self, share_link, find_share_link_of_share):
        share_data_template = {
            'user_id': 0, "like_link": '', 'share_link': '', 'published_time': 0
        }
        share_data_list = []
        html_source = self.__render_engine.render_share_link_of_post(share_link)
        soup = BeautifulSoup(html_source, 'html.parser')
        share_blocks = soup.find_all('div', class_='_3ccb')
        for share_block in share_blocks:
            share_data = share_data_template.copy()
            # Extract shared user ID
            shared_user_tag = share_block.find('div', class_='_6a _5u5j _6b')
            user_id = shared_user_tag.find('a', class_='profileLink').get('data-hovercard') \
                .split('?')[1].split('=')[1].split('&')[0]
            share_data['user_id'] = user_id

            # Extract Like Link on this Share Block
            share_block_like_tag = share_block.find('a', class_='_2x4v')
            if share_block_like_tag is not None:
                share_block_like_link = "https://www.facebook.com{}".format(share_block_like_tag.get('href'))
                share_data['like_link'] = share_block_like_link

            # Extract Share Link on this Share Block
            if find_share_link_of_share:
                share_block_share_tag = share_block.find('a', class_='UFIShareLink')
            else:
                share_block_share_tag = share_block.find('a', class_='_ipm _2x0m')
            if share_block_share_tag is not None:
                share_block_share_link = share_block_share_tag.get('href')
                share_data['share_link'] = share_block_share_link

            # Extract post shared time
            share_data['published_time'] = self.__get_local_time_from_epoch(
                share_block.find('abbr', class_='_5ptz').get('data-utime'))

            share_data_list.append(share_data)
        return share_data_list

    def get_user_data(self, username, options):
        user_network = []
        html_source = self.__render_engine.render_user_data(username, options)
        soup = BeautifulSoup(html_source, 'html.parser')
        friends = soup.find_all('div', class_='fsl fwb fcb')
        for friend in friends:
            user_tag = friend.find('a', href=True)
            if user_tag is not None:
                link = user_tag.get('href')
                if options == "network":
                    if "friends_tab" in link:
                        user = user_tag.get('data-hovercard').split('?')[1].split('=')[1].split('&')[0]
                        user_network.append(user)
                elif options == "liked_pages":
                    user = user_tag.get('data-hovercard').split('?')[1].split('=')[1].split('&')[0]
                    user_network.append(user)
                else:
                    raise Exception
        return user_network

    def get_post_comments_data(self, page_id, post_id):
        comment_data_list = []
        html_source = self.__render_engine.render_post_comments(page_id, post_id)
        soup = BeautifulSoup(html_source, 'html.parser')
        comment_blocks = soup.find_all('div', {'class': '_2a_i', 'data-sigil': 'comment'})
        for comment_block in comment_blocks:
            # get parent comment_data
            parent_comment_data = self.__extract_comment_data(comment_block, '')
            reply_blocks = comment_block.find_all('div', class_='_2a_i')
            parent_comment_data['num_of_replies'] = len(reply_blocks)
            for reply_block in reply_blocks:
                # get reply comment_data
                reply_comment_data = self.__extract_comment_data(reply_block, parent_comment_data['comment_id'])
                parent_comment_data['reply_username_list'].append(
                    reply_comment_data['comment_author'])
                comment_data_list.append(reply_comment_data)
            comment_data_list.append(parent_comment_data)
        # for comment_data in comment_data_list:
        #     print("get_post_comments_data", comment_data)
        return comment_data_list

    def get_user_id_from_username(self, username):
        user_id = ''
        html_source = self.__render_engine.render_user_profile(username)
        soup = BeautifulSoup(html_source, 'html.parser')
        about_link_tag = soup.find('a', {'class': '_6-6', 'data-tab-key': 'about'})
        if about_link_tag is not None:
            # href="https://www.facebook.com/sathwikbubby.n/about?lst=100000059386771%3A100005452500591%3A1531374722"
            user_id = about_link_tag.get('href').split("%3A")[1]
        return user_id

    def get_username_from_user_id(self, user_id):
        username_link = self.__render_engine.render_get_username_from_user_id(user_id)
        # https://www.facebook.com/mathsdada
        return username_link.split("https://www.facebook.com/")[1]

    def get_page_data(self, page_id):
        data = {'page_likes': '', 'page_followers': ''}
        page_link = "https://m.facebook.com/{}".format(page_id)
        html_source = self.__render_engine.render_facebook_page(page_link)
        soup = BeautifulSoup(html_source, 'html.parser')
        for item in soup.find_all('div', class_='_59k _2rgt _1j-f _2rgt _2rgt'):
            if "people like this" in item.text:
                data['page_likes'] = item.text.split("people like this")[0].strip()
            if "people follow this" in item.text:
                data['page_followers'] = item.text.split("people follow this")[0].strip()
        return data