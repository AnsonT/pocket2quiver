from readability import Document
import requests
import html2text
import re
import time

_html2text = html2text.HTML2Text()


def get_summary(bookmark):
  url = bookmark['url']
  content = ''
  try:
    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    response = requests.get(url, headers=headers, timeout=5)
    if re.match( r'text/html', response.headers.get('Content-Type','')):
      doc = Document(response.text)
      content = _html2text.handle(doc.summary())
    else:
        print('\nSkipped summary {} {}'.format(url, response.headers.get('Content-Type','')))
  except Exception as e:
    content = str(e)
  return content
