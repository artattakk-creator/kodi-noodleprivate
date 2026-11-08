"""Keep every .81 cold assertion; read complete, unique screenshot receipts."""
from pathlib import Path
import io,uuid
source82=Path('/root/base-post81.py').read_text()
source82=source82.replace("picture=Path('/root/home75-cold79-'+kind+'.png')", "canonical82=Path('/root/home75-cold79-'+kind+'.png')\n picture=Path('/root/home75-cold79-'+kind+'-'+uuid.uuid4().hex+'.png')")
source82=source82.replace("with Image.open(picture) as im:im.load();rgb=im.convert('RGB').resize((1920,1080))", "raw82=picture.read_bytes()\n   with Image.open(io.BytesIO(raw82)) as im:im.load();rgb=im.convert('RGB').resize((1920,1080))")
source82=source82.replace('except (OSError,ValueError):continue','except (OSError,ValueError,SyntaxError):continue')
source82=source82.replace("if max(abs(a-b) for a,b in zip(rgb.getpixel((800,150)),color))<=8:break", "if max(abs(a-b) for a,b in zip(rgb.getpixel((800,150)),color))<=8:\n   canonical82.write_bytes(raw82)\n   break")
exec(compile(source82,'native-cold82','exec'),globals())
