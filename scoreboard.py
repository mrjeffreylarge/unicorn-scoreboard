#!/usr/bin/env python

import requests
import operator
import math
import time
import numpy as np
import unicornhat as uh
from datetime import datetime, timedelta

def main():
  api_base = 'https://yourteam.beanstalkapp.com/api/changesets.json'
  username = ''
  key = ''  
# 30 max so do page
  params = {'per_page': '30', 'page': 1}

  scores = {}
  display_scores = {}
  users = [ ]
  # start everyone at 9
  for user in users:
    scores[user] = 0

  do_request = True

  print 'Getting scores...'

  while do_request:
    # build request
    req = requests.get(api_base, auth=(username, key), params=params, timeout=2000)

    changesets = req.json()
    i = 0
    for change in changesets:
      rev = change['revision_cache']
      if in_last_day(parse_tz(rev['time'])):
        # weed out non players
        if rev['email'] in users:
          scores[rev['email']] += 1 # yay one point
      else:
        do_request = False
        break
      # do_request = False
    params['page'] += 1

  winner_count = max(scores.values())

  for player in scores:
    # scores are percentage of highest score, based on rounding down on 25%
    display_scores[player] = int(math.floor(float(scores[player]) / float(winner_count) * 100.00 / 25.00))

  # draw_scores(display_scores)
  visualize_scores(dict(display_scores))
  light_scores(dict(display_scores))

# no timezone offset...
def parse_tz(date):
  date_format = '%Y/%m/%d %H:%M:%S'
  stamp = datetime.strptime(date[:19], date_format);
  offset_dir = date[20]
  offset_hrs = date[21:23]
  offset_min = date[23:]

  if offset_dir == '-':
    stamp -= timedelta(hours=int(offset_hrs), minutes=int(offset_min))
  elif offset_dir == '+':
    stamp += timedelta(hours=int(offset_hrs), minutes=int(offset_min))
  return stamp

def in_last_day(date):
  return (datetime.now() - date).days < 1

def light_scores(s):
  uh.set_layout(uh.PHAT)
  uh.brightness(0.5)
  pos = 0
  for score in s:
    for i in range(4):
      if s[score] > 0:
        # orangish to green
        uh.set_pixel(pos, (s[score] - 1), (255 - (s[score] * 51)), ((51 * s[score]) + 51), 0)
      s[score] -= 1
    pos += 1
  uh.show()
  time.sleep(60)

def visualize_scores(s):
  a = []
  b = []
  for score in s:
    for i in range(5):
      if i == 0:
        a.append(score[:5])
      else:
        if s[score] > 0:
          a.append('O')
        else:
          a.append(' ')
        s[score] -= 1
    b.append(a)
    a = []
  c = np.array(b)
  print c

if __name__ == '__main__':
  main()

