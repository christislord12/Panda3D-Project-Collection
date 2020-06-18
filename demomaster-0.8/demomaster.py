from pandac.PandaModules import loadPrcFileData, ConfigVariableBool
import os, sys, demobase
import dynamicimporter

if __name__ == '__main__':
    # Import Psyco if available
    if True:
        try:
            import psyco
            psyco.full()
            print "psyco found"
        except ImportError:
            pass

    os.chdir(sys.path[0])
    # Usage: demomaster.py [basic-shader-only (t/f)] [multi-threaded (t/f)] [Use wx (t/f)] [Appname]
    # using multithread may have problem on Windows
    params = len(sys.argv)
    fuseWxApp = True
    fmultithread = False
    fbasicshaderonly = True
    demoname = None
    if params > 1:
        fbasicshaderonly = (sys.argv[1] == "t")
        if params > 2:
            fmultithread = (sys.argv[2] == "t")
            if params > 3:
                fuseWxApp = (sys.argv[3] == "t")
                if params > 4:
                    demoname = sys.argv[4]

    if not fbasicshaderonly:
        loadPrcFileData("", "basic-shaders-only #f")

    if fuseWxApp:
        # try to import the wx libraries
        try:
            import wx, wx.aui
        except:
            fuseWxApp = False
            print "wxPython not available ?"

    import demomain
    importer = dynamicimporter.DynamicImporter()
    importer.compileAll()
    ok,demolist = importer.ImportCompiledObjects(demobase.DemoBase, demoname)
    if len(demolist) == 0:
        print "No application founded"
        sys.exit()
    if not fuseWxApp:
        room = demomain.Container(fmultithread, demolist, None)
    else:
        demomain.start(fmultithread, demolist)
    run()
