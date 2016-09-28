from readability import Document
import requests
import html2text
import re

_html2text = html2text.HTML2Text()


def get_summary(bookmark):
  url = bookmark['url']
  content = ''
  try:
    response = requests.get(url)
    if re.match( r'text/html', response.headers.get('Content-Type','')):
      doc = Document(response.text)
      content = _html2text.handle(doc.summary())
    else:
        print('\nSkipped summary {} {}'.format(url, response.headers.get('Content-Type','')))
  except Exception as e:
    content = str(e)
  return content
