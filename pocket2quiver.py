#!/usr/bin/env python
"""Pocket 2 Quiver

Usage:
  pocket2quiver.py [--notebook=<notebook>] [--library=<library>] [--consumer-key=<key>] [--access-token=<token>] [-a]
  pocket2quiver.py -y [--all]
  pocket2quiver.py -e | --export
  pocket2quiver.py -i | --interactive
  pocket2quiver.py -h | --help
  pocket2quiver.py -v | --version

Options:
  -h --help                Show this screen
  -v --version             Show version
  -i --interactive         Enter interactive mode
  -y                       Execute immediately
  -a --all                 Download all
  -n --notebook=<notebook> Quiver notebook
  -l --library=<library>   Quiver library
  --consumer-key=<key>     Pocket consumer key    
  --access-token=<token>   Pocket access token

"""


from docopt import docopt
from prompt_toolkit.validation import Validator, ValidationError 
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import PathCompleter
from peewee import *
from playhouse.sqlite_ext import SqliteDatabase
from playhouse.fields import DateTimeField
from playhouse.kv import JSONKeyStore
from pocket_downloader import PocketDownloader
from quiver_export import QuiverExporter
from os.path import expanduser, exists, join, splitext, abspath, split
from os import makedirs
import re
import sys

db_path = expanduser(join('~', '.pocket2quiver'))
if not exists(db_path):
  makedirs(db_path)

db_file = join(db_path, 'pocket.db')
db = SqliteDatabase(db_file)
db.connect()
jkv = JSONKeyStore(database=db)


class NotEmptyValidator(Validator):
  def __init__(self, error="Cannot be empty"):
    self.error = error

  def validate(self, document):
    if not document.text:
      raise ValidationError(message=self.error)

class RegExValidator(Validator):
  def __init__(self, r, allow_empty=False):
    self.r = r
    self.allow_empty = allow_empty

  def validate(self, document):
    if not self.allow_empty and not document.text:
      raise ValidationError(message="cannot be empty")
    if not re.match(self.r, document.text):
      raise ValidationError(message="invalid input")


def prompt_yn(message, default=True):
  yn = prompt(message=message, validator=RegExValidator(r'[YyNn]?', allow_empty=True))
  if not yn:
    return default
  if yn == 'y' or yn == 'Y':
    return True
  return False

def prompt_if_none(arguments, key, key_desc, force_prompt=False, completer=None):
  value = arguments[key] or jkv.get(key, None)
  if not value or force_prompt:
    value = prompt(message=key_desc+": ", validator=NotEmptyValidator(error=key_desc+' required'), completer=completer)
  jkv[key] = value
  return value

class has_extension(object):
  def __init__(self, extension):
    self.extension = extension
  
  def __call__(self, file):
    if not self.extension:
      return True
    root, ext = splitext(file)
    head, tail = split(root)
    if tail.startswith('.'):
      return False
    if not ext:
      return True
    return ext == self.extension
    

def prompt_path_if_none(arguments, key, key_desc, force_prompt=False, extension=""):
  value = arguments[key] or jkv.get(key, None)
  if not value or force_prompt:
    confirm = False
    while not confirm:
      confirm = True
      value = prompt(
        message=key_desc+": ", 
        validator=NotEmptyValidator(error=key_desc+' required'), 
        completer=PathCompleter(
          expanduser=True,
          file_filter=has_extension(extension) ))
      value = abspath(expanduser(value))
      root, ext = splitext(value)
      value = root + extension
      print(value)
      if not exists(value):
        confirm = prompt_yn('Create {}? (Y/n): '.format(value))
  jkv[key] = value
  return value



if __name__ == '__main__':
  arguments = docopt(__doc__, version='pocket2quiver 0.1')

  force_prompt = arguments['--interactive']
  library = prompt_path_if_none(arguments, '--library', 'Quiver library', force_prompt=force_prompt, extension=".qvlibrary")
  notebook = prompt_if_none(arguments, '--notebook', 'Quiver notebook', force_prompt=force_prompt)
  consumer_key = prompt_if_none(arguments, '--consumer-key', 'Pocket consumer key', force_prompt=force_prompt)
  access_token = prompt_if_none(arguments, '--access-token', 'Pocket access token', force_prompt=force_prompt)

  print("Quiver Library: {}".format(library))
  print("Quiver Notebook: {}".format(notebook))  


  #if not prompt_yn('Download (Y/n): '):
  #  exit()

  all = arguments['--all']
  q = QuiverExporter(library, notebook)
  p = PocketDownloader(consumer_key, access_token, db_file, q, all=all)
  print('downloading...')
  p.download()
  p.export()

  

