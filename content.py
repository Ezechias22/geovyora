"""A deliberately small safe rich-content format. No executable HTML or raw embeds."""
import re
from urllib.parse import urlsplit
from db import one

def https_url(value):
    try:
        parsed=urlsplit(value)
        return value if parsed.scheme=='https' and parsed.netloc and not parsed.username and not parsed.password else None
    except ValueError:return None

def inline_parts(text):
    pattern=re.compile(r'\[([^\]\n]{1,200})\]\((https://[^\s)]{1,1500})\)');parts=[];last=0
    for match in pattern.finditer(text):
        if match.start()>last:parts.append({'text':text[last:match.start()],'url':None})
        url=https_url(match.group(2));parts.append({'text':match.group(1) if url else match.group(0),'url':url});last=match.end()
    if last<len(text):parts.append({'text':text[last:],'url':None})
    return parts

def body_blocks(body):
    blocks=[]
    for paragraph in re.split(r'\n\s*\n',body):
        text=paragraph.strip()
        if not text:continue
        if text.startswith('## '):blocks.append({'type':'heading','text':text[3:]});continue
        if text.startswith('> '):blocks.append({'type':'quote','text':text[2:]});continue
        image=re.fullmatch(r'!\[([^\]\n]{0,300})\]\((https://[^\s)]{1,1500})\)',text)
        if image and https_url(image.group(2)):
            blocks.append({'type':'image','caption':image.group(1),'url':image.group(2)});continue
        video=re.fullmatch(r'\[video:([a-z0-9-]{1,150})\]',text)
        if video:
            record=one("SELECT slug,title,playback_id FROM videos WHERE slug=? AND status='ready'",(video.group(1),))
            if record:blocks.append({'type':'video','video':record});continue
        blocks.append({'type':'paragraph','parts':inline_parts(text)})
    return blocks
