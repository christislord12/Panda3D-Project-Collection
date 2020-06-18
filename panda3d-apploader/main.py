from panda3d.core import VirtualFileSystem
from panda3d.core import Multifile
from panda3d.core import Filename
from direct.showbase import VFSImporter
from panda3d.core import *
print(ConfigVariableString("model-path"))
from panda3d.core import loadPrcFileData
import sys
from direct.stdpy import file, glob
import os
if sys.version_info >= (3, 0):
    import builtins
else:
    import __builtin__ as builtins


multifileRoot = str(ExecutionEnvironment.getCwd())
sys.path.append(multifileRoot)
ExecutionEnvironment.setEnvironmentVariable("MAIN_DIR", Filename(multifileRoot).toOsSpecific())
getModelPath().appendDirectory(multifileRoot)
trueFileIO = False
if not trueFileIO:
        # Replace the builtin open and file symbols so user code will get
        # our versions by default, which can open and read files out of
        # the multifile.
        builtins.open = file.open
        if sys.version_info < (3, 0):
                builtins.file = file.open
                builtins.execfile = file.execfile
        os.listdir = file.listdir
        os.walk = file.walk
        os.path.join = file.join
        os.path.isfile = file.isfile
        os.path.isdir = file.isdir
        os.path.exists = file.exists
        os.path.lexists = file.lexists
        os.path.getmtime = file.getmtime
        os.path.getsize = file.getsize
        sys.modules['glob'] = glob
vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("app.p3d"), multifileRoot, VirtualFileSystem.MFReadOnly)
VFSImporter.register()
VFSImporter.reloadSharedPackages()
loadPrcFileData('', 'default-model-extension .bam')
dirName = Filename(multifileRoot).toOsSpecific()
importer = VFSImporter.VFSImporter(dirName)
loaderr = importer.find_module('__main__')
mainModule = loaderr.load_module('__main__')
#import Pinball

