from liquid_tags.mdx_liquid_tags import LiquidTags
import requests
from bs4 import BeautifulSoup
import os
import json
from jinja2 import Template
import bleach

@LiquidTags.register('linkarchive')
def linkarchive(preprocessor, tag, markup):

  path = preprocessor.configs.getConfig('PATH')
  pelican_dir = os.path.split(path)[0]
  cache_dir = os.path.join(pelican_dir, "archive_cache")
  cache = {}
  with open(os.path.join(cache_dir, "cache_file.json")) as f:
    cache = json.load(f) 

  entry = {}
  if markup not in cache:
    session = requests.Session()
    session.headers.update({'User-Agent': 'Custom user agent'})
    result = session.get(markup)
    print(result.status_code)
    if result.status_code == 200:
      c = result.content
      soup = BeautifulSoup(c)
      title_el = soup.find("meta",  property="og:title")
      desc_el = soup.find("meta",  property="og:description")
      img_el = soup.find("meta",  property="og:image")
      url_el = soup.find("meta",  property="og:url")
      entry["title"] = bleach.clean(title_el["content"])
      entry["desc"] = bleach.clean(desc_el["content"])
      entry["img"] = bleach.clean(img_el["content"])
      entry["url"] = bleach.clean(url_el["content"])
    else:
      entry["title"] = ""
      entry["desc"] = ""
      entry["img"] = ""
      entry["url"] = markup
    cache[markup] = entry
    with open(os.path.join(cache_dir, "cache_file.json"), "w") as f:
     json.dump(cache, f, indent=4, sort_keys=True) 
    
  else:
    entry = cache[markup]

  title = entry["title"]
  desc = entry["desc"]
  img = entry["img"]
  url = entry["url"]
    
  #print(title)
  #print(desc)
  #print(img)
  #print(url)

  basetemplate = '''
<div class="col-md-12 lp-posted">
  <div class="col-sm-12 lp-posted-image">
   <img src="{{img}}">
  </div>
  <a href="{{url}}" target="_blank">
    <div class="lp-posted-wrap col-sm-12">
      <div class="col-sm-12 lp-posted-title">{{title}}</div>
      <div class="col-sm-12 lp-posted-canonical-url">{{url}}</div>
      <div class="col-sm-12 lp-posted-description">{{desc}}</div>
    </div>
  </a>
</div>
'''
  template = Template(basetemplate)
  final =  template.render(title=title, desc=desc, img=img, url=url)
  #print(final)
  return final

from liquid_tags import register
