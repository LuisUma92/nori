import os
from os.path import isdir
from pathlib import Path
from appdirs import user_config_dir

import logging
from daemonize import Daemonize
import click

import inkscapefigures as inkfig
from inkscapefigures.picker import pick
from inkscapefigures.rofi import rofi
from inotify.adapters import select

# Loading logger
logging.basicConfig()
log = logging.getLogger('nori')

#loading User config folder
user_dir = Path(user_config_dir("nori","LuisUmana"))
if not user_dir.is_dir():
    user_dir.mkdir()

#loading current root files
root_file = user_dir / 'root'
if not root_file.is_file():
    root_file.touch()

def getRoot():
    return [root for root in root_file.read_text().split('\n') if root != '']

def add_root(path):
    path = str(path)
    roots = getRoot()
    if path in roots:
        return None
    roots.append(path)
    root_file.write_text('\n'.join(roots))

# definition of config
config = user_dir / 'config.py'

# LaTeX citation format
def latex_citation(citeKey,note,verbatim=False):
    if verbatim:
        note = '``'+note+"''"
    note = note+rf"\cite{{{citeKey}}}"
    return note

# main definition
@click.group()
def cli():
    pass

@click.command()
@click.option('--daemon/--no-daemon', default=True)
def watch(daemon):
    """
    Watches for figures.
    """
    # if platform.system() == 'Linux':
    watcher_cmd = watch_daemon_inotify

    if daemon:
        daemon = Daemonize(app='NoRI',
                           pid='/tmp/norigures.pid',
                           action=watcher_cmd)
        daemon.start()
        log.info("Watching notes.")
    else:
        log.info("Watching notes.")
        watcher_cmd()

def watch_daemon_inotify():
    import inotify.adapters
    from inotify.constants import IN_CLOSE_WRITE

    while True:
        roots = getRoot()

        # Watch the file with contains the paths to watch
        # When this file changes, we update the watches.
        i = inotify.adapters.Inotify()
        i.add_watch(str(root_file), mask=IN_CLOSE_WRITE)

        # Watch the actual figure directories
        log.info('Watching directories: ' + ', '.join(getRoot()))
        for root in roots:
            try:
                i.add_watch(root,mask=IN_CLOSE_WRITE)
            except Exception:
                log.debug('Could not add root {}'.format(root))


@cli.command()
@click.argument(
    'root',
    default=os.getcwd(),
    type=click.Path(exists=False,file_okay=False,dir_okay=True)
)
def insert(root):
    '''
        Search and insert notes
    '''
    summDir =  Path(root).absolute()
    if not summDir.exists():
        summDir.mkdir()
    add_root(summDir)

    summaries = summDir.glob('*.yaml')
    summaries = sorted(summaries, key=lambda f: f.stat().st_mtime, reverse=True)

    files = [inkfig.main.beautify(f.stem) for f in summaries]
    key, index, selected = pick(files)
    print(key, index, selected)


if __name__ == "__main__":
    cli()
