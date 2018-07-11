from peewee import *
from peewee import Database
from playhouse.sqlite_ext import SqliteDatabase
from peewee import DateTimeField
from playhouse.kv import KeyValue
import yaml
from datetime import datetime

_null_date = datetime.utcfromtimestamp(0)
db = SqliteDatabase(None)

yaml.SafeLoader.add_constructor("tag:yaml.org,2002:python/unicode", lambda loader, node: node.value)

class Bookmark(Model):
  pocket_id = CharField(unique=True)
  note_id = CharField(null=True)
  bookmarked_at = DateTimeField(default=_null_date)
  downloaded_at = DateTimeField(default=_null_date)
  processed_at = DateTimeField(default=_null_date)
  bookmark = TextField(null=True)

  class Meta:
    database = db

class PocketIndex(object):
  def __init__(self, db_path):
    db.init(db_path)
    db.create_tables([Bookmark], safe=True)
    self.jkv = KeyValue(database=db)


  def get_downloaded(self, pocket_id):
    try:
      bookmark = Bookmark.get(pocket_id=pocket_id)
      return bookmark
    except DoesNotExist:
      return None

  def downloaded(self, bookmark):
    pocket_id = bookmark['pocket']['item_id']
    bookmarked_at = bookmark['updated_at']
    bookmark, created = Bookmark.get_or_create(pocket_id=pocket_id,
      defaults={
        'pocket_id': pocket_id,
        'note_id': '',
        'bookmarked_at': bookmarked_at,
        'downloaded_at': datetime.utcnow(),
        'processed_at': _null_date,
        'bookmark': yaml.dump(bookmark, default_flow_style = False, allow_unicode = True)
      })
    if bookmark.bookmarked_at < bookmarked_at:
      bookmark.bookmark = bookmark
      bookmark.bookmarked_at = bookmarked_at
      bookmark.save()
    return bookmark, created

  def unprocessed(self):
    return map(
        lambda bookmark: (yaml.safe_load(bookmark.bookmark), bookmark.note_id),
        Bookmark.select().where(Bookmark.processed_at < Bookmark.downloaded_at).order_by(Bookmark.processed_at))

  def processed(self, bookmark, note_id):
    bookmark = Bookmark.get(pocket_id=bookmark['pocket']['item_id'])
    bookmark.processed_at = datetime.utcnow()
    bookmark.note_id = note_id
    bookmark.save()
    return bookmark

  def downloaded_since(self):
    return self.jkv.get('downloaded_since', 0)
  
  def set_downloaded_since(self, since):
    self.jkv['downloaded_since'] = float(since)

    