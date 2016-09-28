import json
import uuid
from os import path, mkdir

from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

import html2text
import requests

import yaml

from .summarize_content import get_summary

# Download the images and generate UUIDs
def localize_images(resource_path, img_tags):

    for img_tag in img_tags:
      try:
        url = img_tag['src']
        r = requests.get(url)
        
        # Define the extension and the new filename
        img_ext = Path(urlparse(url).path).suffix
        img_name = '{}{}'.format(uuid.uuid4().hex.upper(),
                                 img_ext)
        img_filename = Path(resource_path, img_name)
        
        with open(str(img_filename), 'wb') as f:
            f.write(r.content)
        
        # Convert the original URL to a Quiver URL
        img_tag['src'] = 'quiver-image-url/{}'.format(img_name)
      except Exception as e:
        print("Failed to localize {}".format(url))


# Write content.json
def write_content(note_path, bookmark, note_text):
    note_title = bookmark['title'] 
    qvr_content = {}
    qvr_content['title'] = note_title
    qvr_content['cells'] = []

    summary = '{}\n\n> {}\n'.format(
      bookmark['url'],
      bookmark['excerpt']
    )

    cell = {'type': 'markdown',
            'data': summary }
    qvr_content['cells'].append(cell)

    cell = {'type': 'markdown', 
            'data': '---\n'+note_text}
    qvr_content['cells'].append(cell)

    cell = {'type': 'code',
            'language': 'yaml',
            'data': yaml.dump(bookmark) }

    qvr_content['cells'].append(cell)
    with open(str(Path(note_path, 'content.json')), 'w') as f:
        f.write(json.dumps(qvr_content))


# Write meta.json
def write_meta(note_path, bookmark, note_uuid):
    timestamp = int(datetime.timestamp(datetime.now()))
    note_title = bookmark['title']

    qvr_meta = {}
    qvr_meta['title'] = note_title
    qvr_meta['uuid'] = note_uuid
    qvr_meta['created_at'] = int(bookmark['updated_at'].timestamp())
    qvr_meta['updated_at'] = timestamp
    qvr_meta['tags'] = bookmark['tags'] + ['Pocket']

    with open(str(Path(note_path, 'meta.json')), 'w') as f:
        f.write(json.dumps(qvr_meta))


def write_bookmark_to_quiver(notebook, note_id, bookmark, content):
  

  # Create the folders
  paths = {}
  paths['notebook'] = notebook
  paths['note'] = Path(paths['notebook'], '{}.qvnote'.format(note_id))
  paths['resources'] = Path(paths['note'], 'resources')
  paths['resources'].mkdir(parents=True, exist_ok=True)
  
  # Replace the original links by the quiver links
  localize_images(paths['resources'], bookmark['images'])

  write_content(paths['note'], 
                bookmark,
                content)

  write_meta(paths['note'], 
                bookmark,
                note_id)


def ensure_notebook(library, notebook):
  if not path.exists(library):
    # create library
    pass
  notebook_path = path.join(library, notebook+'.qvnotebook')
  if not path.exists(notebook_path):
    meta = {
      'name': 'bookmarks',
      'uuid': notebook
    }
    mkdir(notebook_path)
    with open(str(Path(notebook_path, 'meta.json')), 'w') as f:
        f.write(json.dumps(meta))


class QuiverExporter(object):
  def __init__(self, library, notebook):
    self.library = library
    self.notebook = notebook
    ensure_notebook(self.library, self.notebook)

  def export(self, bookmark):
    print('+', end='', flush=True)

    content = get_summary(bookmark)

    print('\b.', end='', flush=True)
    note_id = bookmark['quiver']['note_id'] or str(uuid.uuid4()).upper()
    bookmark['quiver']['note_id'] = note_id
    notebook_path = path.join(self.library, self.notebook+'.qvnotebook')
    write_bookmark_to_quiver(notebook_path, note_id, bookmark, content)
    return note_id
