# Pocket2Quiver

Download bookmarks from Pocket, and export into Quiver notebook.
Bookmarked content is downloaded, summarized by [readability-lxml](https://github.com/predatell/python-readability-lxml) and converted to markedown [html2text](https://github.com/Alir3z4/html2text/).

* First run will setup Pocket authentication and Quiver notebook
* Subsequent runs will get Pocket updates, and continue unprocessed exports 

```
Usage:
  python -m pocket2quiver [--notebook=<notebook>] [--library=<library>] [--consumer-key=<key>] [--access-token=<token>] [-a]
  pocket2quiver -y [--all]
  pocket2quiver -i | --interactive
  pocket2quiver -h | --help
  pocket2quiver -v | --version

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
```
Install:
- python setup.py install

This is work in progress:
- Only compiled in Python 3.5.2
- Progress index stored in ~/.pocket2quiver/ to support incremental updates


Quiver export based on:
https://gist.github.com/kspeeckaert/934a8308a4ec09e2e0756a313a915622


