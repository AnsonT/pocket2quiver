from peewee import Database
from pocket import Pocket, PocketException
from datetime import datetime

from .pocket_index import PocketIndex


class PocketDownloader(object):
  def __init__(self, consumer_key, access_token, db_path, exporter, all = False):
    assert(isinstance(consumer_key, str))
    assert(isinstance(access_token, str))

    self.consumer_key = consumer_key
    self.access_token = access_token
    self.exporter = exporter
    self.index = PocketIndex(db_path)
    self.all = all

  
  def fresh_bookmark(self, bookmark):
    if int(bookmark.get('status', 0)) == 2: #deleted
      return False

    downloaded = self.index.get_downloaded(bookmark['item_id'])
    if downloaded:
      bookmark['note_id'] = downloaded.note_id

    return self.all or \
          not downloaded or \
          int(downloaded.bookmarked_at.timestamp()) < int(bookmark['time_updated']) or \
          downloaded.downloaded_at < downloaded.bookmarked_at


  def download(self):
    since = self.index.downloaded_since()
    offset = 0
    count = 100
    resp_since = since
    p = Pocket(consumer_key = self.consumer_key, access_token = self.access_token)
    total = 0
    bookmarks = []
    while True:
      resp = p.retrieve(offset=offset, count=count, detailType='complete', state='all', sort='oldest', since=since)
      num_bookmarks = len(resp['list'])
      offset += num_bookmarks
      total += num_bookmarks
      if not num_bookmarks:
        break
      resp_since = resp['since']
      bookmarks = map(
        self._pocket_to_bookmark,
        filter(
          lambda bookmark: self.fresh_bookmark(bookmark),
          resp['list'].values()
        )
      )
      for bookmark in bookmarks:
        self.index.downloaded(bookmark) 
      print("Downloaded: ", total)
    # Pocket API appears to use Pacific time for timestamp.
    self.index.set_downloaded_since(resp_since)

  def export(self):
    for bookmark, note_id in self.index.unprocessed():
      try:
        bookmark['quiver']['note_id'] = note_id
        note_id = self.exporter.export(bookmark)
        self.index.processed(bookmark, note_id)
      except Exception as e:
        print("\nExport failed {}".format(bookmark['url']))
        
      

  def _pocket_to_bookmark(self, data):
    bookmark = {
      'url': data.get('given_url', data.get('resolved_url', '')),
      'title': data.get('resolved_title',  data.get('given_title', '')),
      'authors': [],
      'tags': list(data.get('tags', [])),
      'excerpt': data.get('excerpt', ''),
      'images': [],
      'videos': [],
      'saved_at': datetime.fromtimestamp(int(data['time_added'])),
      'updated_at': datetime.fromtimestamp(int(data['time_updated'])),
      'invalid_url': False,
      'pocket': {
        'item_id': data['item_id'],
        'resolved_url': data.get('resolved_url', ''),
      },
      'quiver': {
        'note_id': data.get('note_id', '')
      }
    }
    for author in data.get('authors', {}).values():
      bookmark['authors'].append( {'name': author['name'], 'url': author['url']})
    for raw_image in data.get('images', {}).values():
      image = {
        'caption': raw_image['caption'],
        'src': raw_image['src'],
        'credit': raw_image['credit']
      }
      bookmark['images'].append(image)
    return bookmark