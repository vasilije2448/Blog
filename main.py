import os
import sys
import pypandoc
import bs4
from shutil import copy

MD_POSTS_PATH = 'posts'
HTML_POSTS_PATH = 'dist'

def main():
    if not os.path.exists(HTML_POSTS_PATH):
        os.makedirs(HTML_POSTS_PATH)
    copy('style.css', os.path.join(HTML_POSTS_PATH, 'style.css'))
    generate_posts()
    create_home_page()


def generate_posts():
    l = []
    for root, subdirs, files in os.walk(MD_POSTS_PATH):
        for filename in files:
            p = os.path.join(MD_POSTS_PATH, filename)
            output = pypandoc.convert_file(source_file=p, format='md',
                                           to='html5',
                                           extra_args=['--template='+os.path.join('templates','post_template.html'),
                                                       '--include-before-body='+os.path.join('templates','navbar.html')],
                                           outputfile = os.path.join(HTML_POSTS_PATH,filename[0:-3]+'.html'))
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
                new_a.string = extract_title(os.path.join(HTML_POSTS_PATH, filename_html))
                new_h3.append(new_a)
                soup.find('main').append(new_h3)
        with open(os.path.join(HTML_POSTS_PATH, 'index.html'), 'w') as file:
            file.write(str(soup))


def extract_title(file_path):
    with open(file_path) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, features='html.parser')
        # Assumes first h1 is the title. This needs to be improved.
        first_h1 = soup.find('h1')
        if first_h1 is None:
            return 'Without title'
        else:
            return first_h1.string
                
if __name__ == '__main__':
    main()
