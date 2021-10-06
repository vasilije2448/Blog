import os
import sys
import pypandoc
import bs4
import yaml
from shutil import copy, copytree

MD_POSTS_PATH = 'posts'
HTML_POSTS_PATH = 'dist'
AUDIO_PATH = 'audio'

def main():
    if not os.path.exists(HTML_POSTS_PATH):
        os.makedirs(HTML_POSTS_PATH)
    copy('style.css', os.path.join(HTML_POSTS_PATH, 'style.css'))
    copytree(AUDIO_PATH, HTML_POSTS_PATH, dirs_exist_ok=True)
    generate_posts()
    create_home_page()


def generate_posts():
    l = []
    for root, subdirs, files in os.walk(MD_POSTS_PATH):
        for filename in files:
            md_file_path = os.path.join(MD_POSTS_PATH, filename)
            html_file_path = os.path.join(HTML_POSTS_PATH, filename[0:-3]+'.html')
            output = pypandoc.convert_file(source_file=md_file_path, format='md',
                                           to='html5',
                                           extra_args=['--template='+os.path.join('templates','post_template.html'),
                                                       '--include-before-body='+os.path.join('templates','navbar.html')],
                                           outputfile = html_file_path)
            metadata_dict = get_metadata_dict(md_file_path)
            if 'title' in metadata_dict:
                add_title_metadata_to_html(html_file_path, metadata_dict['title'])
            else:
                add_title_metadata_to_html(html_file_path, 'Without Title')

            if 'audio' in metadata_dict:
                add_audio_to_html(html_file_path, metadata_dict['audio'])
def create_home_page():
    with open(os.path.join(HTML_POSTS_PATH, 'index.html')) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, features='html.parser')
        for root, subdirs, files in os.walk(MD_POSTS_PATH):
            for filename in files:
                if filename in ['about.md', 'index.md']:
                    continue
                filename_html = filename[0:-3]+'.html'
                new_h3 = soup.new_tag('h3')
                new_a = soup.new_tag('a', href=filename_html)
                t = extract_title(os.path.join(HTML_POSTS_PATH, filename_html))
                new_a.string = extract_title(os.path.join(HTML_POSTS_PATH, filename_html))
                new_h3.append(new_a)
                soup.find('main').append(new_h3)
        with open(os.path.join(HTML_POSTS_PATH, 'index.html'), 'w') as file:
            file.write(str(soup))


def extract_title(file_path):
    with open(file_path) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, features='html.parser')
        return soup.find('meta', attrs={'name':'title'})['content']

def get_metadata_dict(md_file_path):
    with open(md_file_path) as inf:
        post_md = inf.read()
        s = post_md.split('---')
        if len(s) < 3 or post_md[0:3] != '---':
            return dict()
        return yaml.safe_load(s[1])

def add_title_metadata_to_html(html_file_path, title):
    with open(html_file_path) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, features='html.parser')
        head = soup.find('head')
        title_meta = bs4.BeautifulSoup('<meta name="title" content="' + title + '"/>',
                                       features='html.parser')
        head.append(title_meta)
        with open(os.path.join(html_file_path), 'w') as file:
            file.write(str(soup))

def add_audio_to_html(html_file_path, audio_file_name):
    with open(html_file_path) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, features='html.parser')
        a = bs4.BeautifulSoup("""
                                <audio controls preload="none">
                                <source src="""+audio_file_name+"""
                                "type="audio/mpeg">
                                </audio>
                              """, features='html.parser')
        soup.find('h1').insert_after(a)
    with open(html_file_path, 'w') as file:
        file.write(str(soup))

if __name__ == '__main__':
    main()
