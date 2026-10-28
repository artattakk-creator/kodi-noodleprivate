"""Verified local manager previews, including offline existing manual choices."""
import os


def local_bytes(pid,path):
    from media_overrides43 import paths
    from programme_art46 import root
    from media_sources43 import SourceError,MAX_IMAGE,validate_image
    folder,_=paths(pid)
    allowed=(str(folder/'images'),root())
    if (not isinstance(path,str) or os.path.dirname(path) not in allowed
            or os.path.islink(path) or os.path.islink(os.path.dirname(path))):raise SourceError('LOCAL_FILE_REQUIRED')
    with open(path,'rb') as stream:data=stream.read(MAX_IMAGE+1)
    validate_image(data)
    return data


def candidates(pid,item):
    from media_sources43 import provider
    from media_overrides43 import cached_art
    values=[]
    for role,path in cached_art(item).items():
        if role in ('poster','fanart'):
            values.append(dict(source='local',url='',local_path48=path,name='Gespeichert · '+('Poster' if role=='poster' else 'Hintergrund'),role=role,attribution='Eigene gespeicherte Auswahl · offline',metadata={}))
    return (values+provider(item.get('_provider43',item)))[:24]
