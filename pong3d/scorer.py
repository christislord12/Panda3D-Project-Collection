# -*- coding: utf-8 -*-
""" Scoreboard module

@author: fabius
@copyright: fabius@2010
@license: GCTA give credit to (the) authors
@version: 0.1
@date: 2010-05
@contact: astelix (U{panda3d forums<http://www.panda3d.org/forums/profile.php?mode=viewprofile&u=752>})
@status: eternal WIP

@note: il modo di fare clamp forse non va bene: poni il caso si vuole tenere 100 scores ma visualizzarne, a un certo momento, solo 10 e poi tutti e 100

@todo: la parte in remoto
"""
#import hashlib, urllib

class scorer(object):
  """ A class to keep scores
  """
  def __init__(self, filename="scores.csv", clamp=100):
    """
    @param clamp: clamp the score list to clamp elements
    """
    self._scoreboard=[]
    self._filename=filename
    self._clamp=clamp
    self._loadscores()
  #----------------------------------------------------------------------
  #
  def putscore(self, player, score):
    self._scoreboard.append((int(score), player.lower()))
    self._scoreboard=self.getscores()
    try: fd=open(self._filename, "w+")
    except: print "[putscore:error] can't write scorefile '%s'"%self._filename
    else:
      fd.write(
        "\n".join(
          ["%d;%s"%(item) for item in self._scoreboard[:self._clamp]]
        )
      )
      fd.close()
  #----------------------------------------------------------------------
  #
  def getscores(self):
    self._scoreboard.sort()
    self._scoreboard.reverse()
    return self._scoreboard[:self._clamp]

  #----------------------------------------------------------------------
  #
  def _loadscores(self):
    try: fd=open(self._filename, "r")
    except: print "[_loadscores:warning] scorefile does not exist"
    else:
      self._scoreboard=[]
      for line in fd.readlines():
        s=line.strip().split(';')
        self._scoreboard.append((int(s[0]), s[1]))
      fd.close()

#=========================================================================
#
if __name__ == "__main__":
  """ usage test """
  import random, rndname
  sb=scorer(filename='scoretest.csv', clamp=10)
  for idx in range(10):
    name=rndname.generate()
    for i in range(random.choice([1,1,1,2,2,3])):
      score=random.randint(1, 15)
      sb.putscore(name, score)
  scoreboard=sb.getscores()

  print "\n\nshowin scores:"
  i=0
  for item in scoreboard:
    i+=1
    print "%03d) %05d - %-20s."%(i,item[0],item[1])
