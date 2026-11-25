"""Owned child programme dialog; preserves parent grid, player and focus.

Callbacks queue intent. Only the parent's pump opens a child, with an exact
parent dialog identity check. Never close foreign modals or use Container.Update.
"""
import re,threading,time
from concurrent.futures import Future
import xbmc,xbmcgui,xbmcaddon
from localization import tr
_slots=threading.BoundedSemaphore(2)

def channel_row(channel):
 if isinstance(channel,dict):return dict(channel)
 return dict(channel.extra,sid=str(channel.extra.get('stream_id','')),name=channel.name,epg_channel_id=getattr(channel,'tvg_id',''))

def request(parent,channel,event=None):
 if getattr(parent,'_closed',False) or getattr(parent,'_leaving',False) or channel is None:return
 parent._programme_request46=(channel_row(channel),dict(event) if event else None)

def permitted(parent=None):
 try:dialog=int(xbmcgui.getCurrentWindowDialogId())
 except (AttributeError,RuntimeError,ValueError,TypeError):return False
 if dialog in (0,-1,9999):return True
 if parent is not None:
  owner=getattr(parent,'_owner69','')
  if owner and xbmcgui.Window(dialog).getProperty('XCMate.NativeOwner')==owner:return True
  if dialog==getattr(parent,'_native_dialog_id',None):return True
  nonce=getattr(parent,'_window_nonce',None)
  if nonce and xbmcgui.Window(dialog).getProperty('XtreamMate.NavigatorIdentity')==nonce:return True
 return False

def open_pending(parent):
 wanted=getattr(parent,'_programme_request46',None)
 if not wanted:return
 parent._programme_request46=None
 if parent._closed or getattr(parent,'_leaving',False):return
 if not permitted(parent):xbmcgui.Dialog().notification('XCMate',tr(36105));return
 return show(parent.portal,wanted[0],wanted[1],parent)

def show(portal,channel,event=None,parent=None,*,manual96=False):
 if not permitted(parent):xbmcgui.Dialog().notification('XCMate',tr(36105));return
 dialog=ProgrammeWindow46('XCMateProgramme46.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
 dialog.configure(portal,channel,event,parent);dialog._manual96=bool(manual96);dialog.run()
 if dialog._tune88 and parent is not None:
  if not __import__('programme_actions88').tune(parent,portal,channel):xbmcgui.Dialog().notification('XCMate','Sender kann aus dieser Ansicht momentan nicht umgeschaltet werden.')
 return dialog

class ProgrammeWindow46(xbmcgui.WindowXMLDialog):
 def configure(self,portal,channel,event=None,parent=None):
  self.portal,self.channel,self.selected,self.parent=portal,dict(channel),event,parent
  self._owner=threading.get_ident();self._closed=False;self._ready=False;self._shown=False;self._init_error69=False;self._read_deadline69=0
  self._retries85=0;self._retry_after85=0
  self._intent88=None;self._action88=None;self._tune88=False;self._timeline88=''
  self._hero_art={};self._poster_art={};self._next_art_intent=0
  self._detail_view_event={};self._extra_page=False;self._reference_images=('','')
  self._person_references=();self._next_person_intent=0
  self._cancel=threading.Event();self._future=None;self.event=None;self._art_signature=None;self._next=0;self._scroll46=0;self._art68={}
 def _gui(self):
  if threading.get_ident()!=self._owner:raise RuntimeError('PROGRAMME_OWNER_THREAD')
 @__import__('programme_lifecycle69').initialized
 def onInit(self):
  self._gui()
  if self._ready:return
  for cid in (104,105,107,108,110,114,115,116,120,121,129,130,142,143,144,145,146,1130):
   self.getControl(cid).setVisible(False)
  self._shown=True;self._ready=True;self.getControl(501).setLabel(tr(36101));self.getControl(101).setLabel(tr(36100))
  from menu_icons45 import icon
  self.getControl(881).setImage(icon('back',full=True));self.setFocusId(501)
  self._paint_facts(dict(self.selected or {},channel=self.channel.get('name','')))
  self.getControl(502).setLabel('Sendung merken');self.getControl(503).setLabel('Jetzt umschalten')
  self._start_read85()
 def _start_read85(self):
  if not _slots.acquire(blocking=False):return
  future=Future();self._future=future;self._read_deadline69=time.monotonic()+5
  def work():
   try:
    if not future.set_running_or_notify_cancel():return
    try:
     from programme_events46 import load,source_name
     from media_art import local_art,request as request_logos
     value=load(self.portal,self.channel,self.selected)
     value['_source_label100']=source_name(self.portal,value)
     value['_detail93']=True
     if self.selected and self.selected.get('_no_art_request68'):value['_no_art_request68']=True
     logos88=__import__('logo_manifest86').read(self.portal,[self.channel])
     verified_logo=logos88.get(str(self.channel.get('sid')),'')
     value['logo']=verified_logo or local_art(self.channel)['thumb'];request_logos([self.channel])
     from programme_art46 import cached
     from programme_requests68 import request
     value['_art68']=__import__('programme_preview67').shared(value) or cached(value)
     if not self._cancel.is_set():self._advertise_art(value,request)
     future.set_result(value)
    except Exception:future.set_exception(RuntimeError('PROGRAMME_READ_FAILED'))
   finally:_slots.release()
  try:threading.Thread(target=work,name='XCMate-programme-detail46',daemon=True).start()
  except (RuntimeError,MemoryError):_slots.release();self._future=None
 def _paint_facts(self,event):
  from presentation80 import text
  from programme_assets47 import station_image
  from programme_actions88 import xmltv_tmdb

  def label(cid,value):
   control=self.getControl(cid);control.setLabel(value);control.setVisible(bool(value))

  logo=event.get('logo','')
  real=station_image(logo)
  self.getControl(111).setImage(logo if real else '')
  self.getControl(111).setVisible(real)
  label(112,'' if real else text(event.get('channel')))
  label(101,text(event.get('title')))
  episode=event.get('subtitle') or event.get('episode_label')
  if not episode and event.get('season') and event.get('episode'):
   episode=tr(36103,event['season'],event['episode'])
  label(102,text(episode))
  facts=' · '.join(text(event[k]) for k in ('year','genre','age_rating','language') if event.get(k))
  label(106,facts)
  self.getControl(128).setVisible(bool(facts))
  source=event.get('_source_label100','')
  label(109,tr(32753)+' · '+source if source else '')
  self._detail_view_event=dict(event)
  self._art_signature=None
  ident,score,scope=xmltv_tmdb(event)
  self._paint_tmdb(ident,score,scope,bool(score))
  self._paint_cards()
  self._paint_time(event)

 def _paint_tmdb(self,ident,score,scope,brand):
  if score and scope:score+=' · '+scope
  self.getControl(129).setVisible(brand)
  self.getControl(129).setWidth(234 if score else 85)
  self.getControl(130).setVisible(brand)
  self.getControl(108).setLabel(score.removeprefix('TMDB '))
  self.getControl(108).setVisible(bool(score))
  self._detail_view_event.update(_tmdb_id=ident,_tmdb_rating=score)

 def _paint_cards(self):
  from presentation80 import text

  event=self._detail_view_event
  synopsis=text(event.get('description'))
  cast=event.get('cast')
  names=[text(name).strip() for name in cast if isinstance(name,str) and name.strip()] if isinstance(cast,list) else []
  channel_id=event.get('canonical')
  if event.get('source_key46')=='agent':
   origins=event.get('field_sources52') or {}
   for field in ('xmltv_tmdb_id','agent_art','xmltv_title_lang','xmltv_date'):
    origin=origins.get(field) or {}
    if origin.get('source')=='agent' and origin.get('channel'):
     channel_id=origin['channel'];break
  technical=[]
  for value,label in ((event.get('channel'),'Sender'),(event.get('_source_label100'),'EPG-Quelle'),
                      (channel_id,'EPG-Kanal-ID'),(event.get('xmltv_date'),'XMLTV-Datum'),(event.get('director'),'Regie')):
   if value:technical.append(label+'   '+text(value))
  title_language=event.get('xmltv_title_lang')
  metadata_language=not event.get('language') and isinstance(title_language,str) and re.fullmatch(r'[a-z]{2,3}(?:-[a-z0-9]{2,8}){0,3}',title_language)
  if metadata_language:technical.append('Metadaten-Sprache   '+title_language.upper())
  if self._detail_view_event.get('_tmdb_id'):
   technical.append('TMDB-ID   '+str(self._detail_view_event['_tmdb_id']))
  if self._detail_view_event.get('_tmdb_rating'):
   technical.append('Bewertung   '+self._detail_view_event['_tmdb_rating'])
  start,stop=(time.localtime(event[key]) if event.get(key) else None
              for key in ('start','stop'))
  exact_day=bool(start and stop and start[:3]==stop[:3])
  timestamp='%H:%M:%S' if exact_day else '%d.%m. %H:%M'
  times=[label+' '+time.strftime(timestamp, value) for label,value in
         (('Beginn',start),('Ende',stop)) if value]
  if times:technical.insert(0,'   ·   '.join(times))
  following=event.get('following46') or []
  preceding=event.get('preceding46')
  scheduled=bool(preceding or following)
  gaps=[]
  if event.get('title') and 0<event.get('start',0)<event.get('stop',0):
   roles=event.get('agent_art') or {}
   gaps=[label for key,label in (('season','Staffel'),('episode','Folge'),('director','Regie'))
         if not event.get(key)]
   if not (roles.get('episode_still') or event.get('_episode_picture')):gaps.append('Episodenbild')
   if roles.get('person') or roles.get('character'):gaps.append('Zuordnung der Personenfotos')
  backdrop,poster=self._reference_images
  people=self._person_references if self._extra_page else ()
  # The poster remains in the header; use its duplicate preview space for
  # the feed reference cards when they are available.
  if people and backdrop:poster=''
  left=678 if technical else 1184
  card_top=494 if synopsis else 370
  chips=[]
  x,y=70,card_top+40
  for name in names[:12]:
   width=min(244,max(88,26+len(name)*10))
   if x+width>48+left-22:x=70;y+=27
   if y+23>615:break
   chips.append((name,x,y,width))
   x+=width+7
  overflow=len(chips)<len(names)
  more=bool(scheduled or backdrop or poster or people or overflow or gaps)
  if not more:
   if self._extra_page:self.setFocusId(501)
   self._extra_page=False
  extra=self._extra_page
  self.getControl(504).setLabel('Zur Übersicht' if extra else
                               'Bildmaterial und Programm' if scheduled and (backdrop or poster or people) else 'Weitere Details')
  self.getControl(504).setVisible(more)
  back,bookmark,tune,more_button=(self.getControl(cid) for cid in (501,502,503,504))
  tune.setNavigation(tune,tune,bookmark,more_button if more else back)
  back.setNavigation(back,back,more_button if more else tune,bookmark)

  show_plot=bool(synopsis) and not extra
  show_cast=bool(names) and not extra
  show_technical=bool(technical) and not extra
  for cid in (117,118,103):self.getControl(cid).setVisible(show_plot)
  for cid in (119,123):self.getControl(cid).setVisible(show_cast)
  for cid in (125,126,127):self.getControl(cid).setVisible(show_technical)

  plot_height=113 if names else 240
  plot=self.getControl(117);plot.setWidth(left);plot.setHeight(plot_height)
  box=self.getControl(103);box.setWidth(left-44);box.setHeight(plot_height-56);box.setText(synopsis)
  card=self.getControl(119);card.setPosition(48,card_top);card.setWidth(left)
  card.setHeight(122 if synopsis else 240)
  self.getControl(123).setPosition(70,card_top+11)
  fact_x=742 if synopsis or names else 48
  fact_width=490 if synopsis or names else 1184
  for cid,dx,dy in ((125,0,0),(126,22,12),(127,22,45)):
   control=self.getControl(cid);control.setPosition(fact_x+dx,370+dy)
   control.setWidth(fact_width-2*dx)
  technical_body=self.getControl(127)
  technical_body.setHeight(190 if metadata_language else 177)
  technical_body.setText('\n'.join(technical))

  for i in range(12):
   chip,label=(self.getControl(cid+i) for cid in (700,720))
   if i<len(chips):
    name,x,y,width=chips[i]
    chip.setPosition(x,y);chip.setWidth(width)
    label.setPosition(x+8,y-2);label.setWidth(width-16);label.setLabel(name)
   chip.setVisible(show_cast and i<len(chips))
   label.setVisible(show_cast and i<len(chips))

  show_schedule=extra and bool(scheduled or overflow)
  show_images=extra and bool(backdrop or poster or people)
  for cid in (132,133,134):self.getControl(cid).setVisible(show_schedule)
  for cid in (135,136):self.getControl(cid).setVisible(show_images)
  self.getControl(133).setLabel('[B]TV-Programm um diese Ausstrahlung[/B]' if scheduled else '[B]Mitwirkende[/B]')
  selected=bool(scheduled and event.get('title') and event.get('start'))
  self.getControl(137).setVisible(show_schedule and selected)
  self.getControl(138).setVisible(show_schedule and selected)
  def line(row):
   start=time.strftime('%H:%M',time.localtime(row['start']))
   stop='–'+time.strftime('%H:%M',time.localtime(row['stop'])) if row.get('stop') else ''
   return start+stop+'   '+text(row['title'])

  previous=self.getControl(144)
  previous.setVisible(show_schedule and bool(preceding))
  if preceding:previous.setLabel(line(preceding))
  highlight_y=445 if preceding else 416
  self.getControl(137).setPosition(70,highlight_y)
  self.getControl(138).setPosition(84,highlight_y+3)
  if selected:self.getControl(138).setLabel(line(event))
  schedule=[line(row) for row in following]
  if overflow:
   schedule.extend(('', 'Mitwirkende', ', '.join(names)) if scheduled else (', '.join(names),))
  schedule_width=678 if show_images else 1184
  for cid,margin in ((132,0),(134,22),(137,22),(138,36),(144,22)):
   self.getControl(cid).setWidth(schedule_width-2*margin)
  body=self.getControl(134)
  body_y=highlight_y+40 if selected else 420
  body.setPosition(70,body_y)
  body.setHeight((546 if gaps else 604)-body_y)
  body.setText('\n'.join(schedule))
  gap_x=70
  gap_y=548 if show_schedule else 386
  gap_width=(schedule_width-44 if show_schedule else 634 if show_images else 1140)
  for cid,dy in ((142,0),(143,26)):
   control=self.getControl(cid)
   control.setPosition(gap_x,gap_y+dy);control.setWidth(gap_width)
   control.setVisible(extra and bool(gaps))
  self.getControl(143).setText(' · '.join(gaps))

  split_images=show_schedule or bool(gaps)
  image_x=742 if split_images else 48
  image_width=490 if split_images else 1184
  self.getControl(135).setPosition(image_x,370)
  self.getControl(135).setWidth(image_width)
  self.getControl(136).setPosition(image_x+22,382)
  portrait_width=min(122,(image_width-62)//4)
  portrait_left=image_x+image_width-22-len(people)*(portrait_width+6)+6
  main_width=portrait_left-image_x-28 if people else image_width-44
  first=self.getControl(140);first.setPosition(image_x+22,421)
  poster_width=min(139,main_width)
  backdrop_width=(282 if split_images else image_width-190) if poster else main_width
  first.setWidth(backdrop_width)
  second=self.getControl(141);second.setWidth(poster_width)
  poster_left=image_x+22+main_width-poster_width if people else image_x+image_width-172
  second.setPosition(poster_left if backdrop else image_x+22,421)
  for image,uri in ((first,backdrop),(second,poster)):
   image.setImage(uri);image.setVisible(show_images and bool(uri))
  caption=self.getControl(145)
  caption.setPosition(image_x+22,580);caption.setWidth(backdrop_width)
  caption.setLabel('Hintergrundbild / Hero');caption.setVisible(show_images and bool(people and backdrop))
  self._paint_person_cards(people,portrait_left,portrait_width)

 def _paint_person_cards(self,people,left,width):
  for index,cid in enumerate((150,154)):
   image,source,assignment,card,state=(self.getControl(n) for n in (cid,cid+1,cid+2,cid+3,148+index))
   if index>=len(people):
    image.setImage('')
    for control in (image,source,assignment,card,state):control.setVisible(False)
    continue
   uri,credit,role=people[index]
   for control,y in ((image,422),(source,536),(card,416),(state,468)):
    control.setPosition(left,y);control.setWidth(width);control.setVisible(True)
   image.setHeight(114)
   image.setImage(uri);image.setVisible(bool(uri))
   source.setLabel(('Foto' if role=='person' else 'Figur')+' · '+credit)
   assignment.setPosition(left+6,558);assignment.setWidth(width-12);assignment.setHeight(48)
   assignment.setText('Nicht zugeordnet');assignment.setVisible(True)
   state.setLabel('Lädt …');state.setVisible(not uri)
   left+=width+6

 def _read_person_cards(self,result,request):
  from agent_programme100 import PERSON_VIEWS,person_candidates
  from programme_deadline80 import WAITING
  from programme_image69 import reference
  from programme_mapping85 import current

  if not self._extra_page:return ()
  mapping=current(self.event)
  if mapping and mapping.get('hidden'):return ()
  now=time.monotonic()
  offer=now>=self._next_person_intent
  if offer:self._next_person_intent=now+5
  cards=[]
  for view,candidate in zip(PERSON_VIEWS,person_candidates(self.event)):
   event=dict(self.event,_art_view499=view)
   art=result(event)
   uri=reference(art,event)
   status=art.get('code')
   if not uri and offer:request(event,priority=True)
   if uri or not status or status in WAITING:
    cards.append((uri,candidate['attribution'],candidate['role81']))
  return tuple(cards)

 def _paint_time(self,event):
  stamp,percent=__import__('programme_actions88').timeline(event)
  if stamp:
   stamp=time.strftime('%d.%m.%Y · ',time.localtime(event['start']))+stamp
  if stamp!=self._timeline88:
   self.getControl(107).setLabel(stamp);self._timeline88=stamp
  self.getControl(107).setVisible(bool(stamp))
  current=bool(stamp and event['start']<=time.time()<event['stop'])
  for cid in (120,121):self.getControl(cid).setVisible(current)
  if current:self.getControl(121).setWidth(max(1,int(520*percent/100)))

 @staticmethod
 def _advertise_art(event,request):
  request(event,priority=True)
  art=event.get('agent_art') or {}
  if art.get('backdrop'):request(dict(event,_art_view499='hero'),priority=True)
  if art.get('poster'):request(dict(event,_art_view499='card'),priority=False)

 def _paint_art(self,art,hero,poster):
  from programme_actions88 import rating,tmdb_source,tmdb_id,xmltv_tmdb
  from programme_image69 import eligible

  def image(value,view=None):
   event=dict(self.event,_art_view499=view) if view else self.event
   return value.get('image','') if not value.get('provisional85') and eligible(value,event) else ''

  hero_image=image(hero,'hero')
  poster_image=image(poster,'card')
  detail_image=image(art)
  confirmed=__import__('agent_programme100').manual(art)
  ready=detail_image if confirmed and art.get('role81')!='poster' else hero_image
  if not ready and art.get('role81')!='poster':ready=detail_image
  cover=poster_image if poster.get('role81')=='poster' else ''
  if (confirmed or not cover) and art.get('role81')=='poster':cover=detail_image
  if cover==ready:cover=''
  primary=art if confirmed and detail_image else hero if hero_image else poster if cover and cover==poster_image and not ready else art
  source=primary.get('source','') if ready or cover else ''
  visible_poster=poster if cover and cover==poster_image else {}
  score_source=source
  score=rating(primary)
  if not score and visible_poster:
   score=rating(visible_poster)
   if score:score_source=visible_poster.get('source')
  score_scope={'tmdb_movie':'Film','tmdb_series':'Serie','tmdb_episode':'Folge'}.get(score_source)
  if not score_scope:score=''
  feed_id,feed_score,feed_scope=xmltv_tmdb(self._detail_view_event)
  if feed_score:score,score_scope=feed_score,feed_scope
  brand=bool(score) or tmdb_source(source) or tmdb_source(visible_poster.get('source'))
  art_id=(tmdb_id(primary) or tmdb_id(visible_poster)) if ready or cover else None
  verified_id=feed_id or art_id
  poster_source=(poster if cover==poster_image else art).get('source','') if cover else ''
  episode_picture=bool(ready and ready==detail_image and (art.get('role81')=='episode_still'
                       or art.get('image_scope57')=='episode'))
  series_picture=bool(ready and primary.get('image_scope57')=='series_fallback')
  signature=(ready,cover,source,score,score_scope,brand,verified_id,poster_source,episode_picture,
             series_picture,self._person_references)
  if signature==self._art_signature:return
  self._art_signature=signature
  for cid,uri in ((110,ready),(114,cover)):
   control=self.getControl(cid);control.setImage(uri);control.setVisible(bool(uri))
  for cid in (115,116):self.getControl(cid).setVisible(bool(ready))
  self.getControl(1130).setVisible(bool(cover))
  self._paint_tmdb(verified_id,score,score_scope,brand)
  names={'provider_event':'Anbieter','xmltv_event':'XMLTV','agent_xmltv':'XMLTV',
         'tvmaze_series':'TVMaze','tvmaze_episode':'TVMaze','agent_tvmaze':'TVMaze',
         'user_local86':'Manuell'}
  image_source='TMDB' if tmdb_source(source) else names.get(source,'')
  picture_label='Serienbild (kein Episodenbild)' if series_picture else 'Bild'
  self.getControl(105).setLabel(picture_label+' · '+image_source if image_source else '')
  self.getControl(105).setVisible(bool(image_source))
  poster_attribution='TMDB' if tmdb_source(poster_source) else names.get(poster_source,'')
  self.getControl(146).setLabel('Poster · '+poster_attribution if poster_attribution else '')
  self.getControl(146).setVisible(bool(poster_attribution))
  self._detail_view_event['_episode_picture']=episode_picture
  self._reference_images=(ready,cover)
  self._paint_cards()
  __import__('programme_pipeline77').note(self.event,'RENDER_CONTROL',
      'IMAGE_REQUESTED' if ready or cover else 'SOURCE_MISSING',
      control=110,visible=bool(ready or cover))

 def pump(self):
  self._gui()
  if self._closed:return
  if __import__('programme_lifecycle69').pulse(self):return
  if self.parent is not None and self.parent._closed:self.close();return
  if self._intent88=='bookmark' and self.event and self._action88 is None and _slots.acquire(blocking=False):
   self._intent88=None;future88=Future();self._action88=future88;event88=dict(self.event)
   def save88():
    try:
     if future88.set_running_or_notify_cancel():
      try:future88.set_result(__import__('programme_actions88').bookmark(event88,self._cancel.is_set))
      except Exception:future88.set_exception(OSError('BOOKMARK_FAILED'))
    finally:_slots.release()
   try:threading.Thread(target=save88,name='XCMate-programme-bookmark88',daemon=True).start()
   except RuntimeError:_slots.release();self._action88=None
  if self._action88 is not None and self._action88.done():
   try:
    added88=self._action88.result();self.getControl(502).setLabel('Nicht mehr merken' if added88 else 'Sendung merken')
    if added88:xbmcgui.Dialog().notification('XCMate',tr(33116))
   except Exception:xbmcgui.Dialog().notification('XCMate','Merkliste konnte nicht gespeichert werden.')
   self._action88=None
  if getattr(self,'_series_menu85',False):
   self._series_menu85=False
   if __import__('work_manager86').open(self):
    self._art68={};self._art_signature=None;self._next=0
    if self.event:__import__('programme_requests68').request(self.event,priority=True)
   return
  if self._future is not None and not self._future.done() and time.monotonic()>self._read_deadline69:
   self._cancel.set();self._future.cancel();self._future=None
   __import__('programme_lifecycle69').mark(self,'READ_TIMEOUT')
  if self._future is not None and self._future.done():
   future=self._future;self._future=None
   try:self.event=future.result()
   except Exception:__import__('programme_lifecycle69').mark(self,'READ_FAILED')
   else:
    if getattr(self,'_manual96',False):self._series_menu85=True;self._manual96=False
    self._art68=self.event.pop('_art68',{})
    self._paint_facts(self.event)
  if self.event and time.monotonic()>=self._next:
   self._next=time.monotonic()+.5
   from programme_image69 import eligible
   from programme_lastgood80 import choose
   from programme_requests68 import request,result

   art=choose(self.event,result(self.event,self._art68),self._art68) or {}
   if eligible(art,self.event):self._art68=dict(art)
   roles=self.event.get('agent_art') or {}
   for role,view,field in (('backdrop','hero','_hero_art'),('poster','card','_poster_art')):
    if roles.get(role):
     event_view=dict(self.event,_art_view499=view)
     prior=getattr(self,field)
     setattr(self,field,choose(event_view,result(event_view,prior),prior) or {})
   if art.get('source') in (None,'','placeholder') and time.monotonic()>=self._next_art_intent:
    self._next_art_intent=time.monotonic()+5
    self._advertise_art(self.event,request)
   self._person_references=self._read_person_cards(result,request)
   self._paint_art(art,self._hero_art,self._poster_art)
   self._paint_time(self.event)
 def run(self):
  self._gui();monitor=xbmc.Monitor();start=time.monotonic()
  try:
   if not permitted(self.parent):return
   self.show()
   while not self._closed:
    if self._init_error69:break
    if self._ready:self.pump()
    elif time.monotonic()-start>10:break
    if monitor.waitForAbort(.05):break
  finally:self.close()
 def onAction(self,action):
  self._gui()
  key=action.getId()
  if key==117 or key==1 and self.getFocusId()==501:self._series_menu85=True
  elif key in (9,10,92):self.close()
  elif key in (3,4,5,6):
   self._scroll46=max(0,min(512,self._scroll46+(-1 if key==3 else 1 if key==4 else -10 if key==5 else 10)))
   self.getControl(134 if self._extra_page else 103).scroll(self._scroll46)
   if not self._extra_page:self.getControl(127).scroll(self._scroll46)
 def onClick(self,cid):
  self._gui()
  if cid==501:self.close()
  elif cid==504:
   self._extra_page=not self._extra_page;self._scroll46=0
   self._person_references=();self._next_person_intent=0;self._next=0
   self._paint_cards()
  elif cid==502 and self.event and self._action88 is None:self._intent88='bookmark'
  elif cid==503 and not self._tune88 and not __import__('station_rows88').header(self.channel):self._tune88=True;self.close()
 def close(self):
  self._gui()
  if self._closed:return
  self._closed=True;self._cancel.set()
  if self._art68.get('asset88'):__import__('decoded_assets88').release(self._art68['asset88'])
  __import__('programme_lifecycle69').mark(self,'CLOSE')
  __import__('programme_lifecycle69').unregister(self)
  if self._future:self._future.cancel()
  if self._action88:self._action88.cancel()
  if self._shown:super().close()

def launch_standalone(portal,channel,selected=None):
 """Serialize root dispatches; wait briefly for natural modal release only.

This runs in the plugin interpreter, never in a parent's GUI callback. Parent
children use the exact parent identity path instead and retain its owner lease.
"""
 from window_navigation import ownership
 with ownership() as acquired:
  if not acquired:xbmcgui.Dialog().notification('XCMate',tr(36105));return
  deadline=time.monotonic()+2;monitor=xbmc.Monitor()
  while not permitted():
   if time.monotonic()>=deadline or monitor.waitForAbort(.05):
    xbmcgui.Dialog().notification('XCMate',tr(36105));return
  return show(portal,channel,selected)


def route(router,portal):
 from boot_diagnostics import finish_directory
 if router._handle>=0:finish_directory(router,succeeded=False,cacheToDisc=False)
 if not portal:return
 try:
  params=router._params
  from library_index import Reader
  channel=Reader(portal['id']).get('live',str(params.get('sid','')))
  if not channel:return
  selected=dict(start=int(params.get('start',0)),stop=int(params.get('stop',0)),key=str(params.get('event','')),source_key46=str(params.get('source',''))[:128])
  dialog88=launch_standalone(portal,channel,selected if selected['start'] else None)
  if dialog88 and dialog88._tune88:
   from guide_playback import request,handoff,player_state
   handoff(router,portal,request(portal,channel,player_state()))
  return dialog88
 except (ValueError,TypeError):xbmcgui.Dialog().notification('XCMate',tr(36107))
