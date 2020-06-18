import  wx
import os
#------------------------------------------------------------------
#
def messagebox(message, style="", parent=None):
  dlg=wx.MessageDialog(
    parent, message, "",
    style=style or (wx.OK| wx.ICON_INFORMATION)
  )
  r=dlg.ShowModal()
  dlg.Destroy()
#------------------------------------------------------------------
#
def errorbox(message, parent=None):
  messagebox(message, style=wx.OK| wx.ICON_ERROR, parent=parent)
#------------------------------------------------------------------
#
def questionbox(message, parent=None):
  dlg=wx.MessageDialog(parent, message, "", wx.YES_NO | wx.ICON_QUESTION)
  r=dlg.ShowModal()
  dlg.Destroy()
  return r == wx.ID_YES
#------------------------------------------------------------------
def textbox(message, default='', parent=None):
  r=""
  dialog=wx.TextEntryDialog(
    parent, message, defaultValue=default, style=wx.OK|wx.CANCEL
  )
  if dialog.ShowModal() == wx.ID_OK: r=dialog.GetValue()
  dialog.Destroy()
  return r
#------------------------------------------------------------------
#
def fileDialog(
    message="Choose a file", start=os.getcwd(), wildcard="*",
    style="", parent=None
):
  '''start could be a default dirname or a default filename'''
  path=""
  if os.path.isdir(start):
    ddir=start
    dfile=""
  else:
    ddir=os.path.dirname(start)
    dfile=os.path.basename(start)
  dlg=wx.FileDialog(
    parent, message=message, defaultDir=ddir,
    defaultFile=dfile, wildcard=wildcard,
    style=style or (wx.FD_OPEN| wx.FD_FILE_MUST_EXIST)
  )
  if dlg.ShowModal() == wx.ID_OK: path=dlg.GetPath()
  dlg.Destroy()
  return path
#------------------------------------------------------------------
#
def openFileDialog(
  message="Open File", start=os.getcwd(), wildcard="*", parent=None
):
  return fileDialog(message=message, start=start, wildcard=wildcard,
    parent=parent
  )
#------------------------------------------------------------------
#
def saveFileDialog(
    message="Save File As", start=os.getcwd(), parent=None
):
  return fileDialog(
    message=message, start=start, style=wx.FD_SAVE, parent=parent
  )
#------------------------------------------------------------------
#
def get_folder_list(starting_point, patterns='*', extfilter=[]):
  '''
  Crea una folder list innestata di files dalla struttura di folder partendo dall posizioe specificata.
  NB: il dizionario e' composto da tanti dict nested ognuno dei quali contiene la struttura verticale di un branch di folders coi suoi sottobranch e relative leaves (i files .py) - quando si arriva a una leaf se ne memorizza il percorso completo che servira' in seguito nell'app.
  es:
  { 'rootnode':
    {'subnode_1':
      {
        'subnode_1_1':
        {
          subnode_1_1_fileleaf_1:path_1,
          ...,
          subnode_1_1_fileleaf_n:path_n,
        },
        'subnode_1_2':
        {
          subnode_1_2_fileleaf_1:path_1,
          ...,
          subnode_1_2_fileleaf_n:path_n,
        }
      }
    }
  }
  '''
  treelist={}
  root, start=os.path.split(starting_point)
  os.chdir(root)
  for x in walktree(root=start, patterns=patterns, single_level=False, yield_folders=True):
    x=os.path.normpath(x)
    pst=treelist
    for node in x.split(os.sep):
      if node[0] not in ['_','~']:
        nodename,nodeext=os.path.splitext(node)
        if nodeext in extfilter:
          node=nodename
          pst[node]=x
        else:
          if not pst.has_key(node): pst[node]={}
          pst=pst[node]
      else: break
  return treelist
#------------------------------------------------------------------
#
def walktree(root, patterns='*', single_level=False, yield_folders=False):
  '''
  by: Robin Parmar, Alex Martelli
  from: Python Cookbook 2nd edition
  '''
  import os, fnmatch
  # Expand patterns from semicolon-separated string to list
  patterns = patterns.split(';')
  for path, subdirs, files in os.walk(root):
    if yield_folders:
      files.extend(subdirs)
    files.sort( )
    for name in files:
      for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
          yield os.path.join(path, name)
          break
    if single_level: break
