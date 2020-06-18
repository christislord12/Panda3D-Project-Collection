import compileall, glob, inspect, pyclbr
import os, sys,traceback
import demobase
class DynamicImporter():
    def __init__(self):
        self.modules = []
        self.output = ""

    def restoreRedirect(self):
        sys.stderr = self.originalerr
        sys.stdout = self.originalout

    def setRedirect(self):
        self.output = ""
        self.originalout = sys.stdout
        self.originalerr = sys.stderr
        sys.stderr = self
        sys.stdout = self

    def write(self, s):
        self.output += s

    def compileAll(self, dir=".", fForce=False):
        compileall.compile_dir(dir,force=fForce,maxlevels=4)

    def ImportCompiledObjects(self, lookingForClass, classname, quitOnError=True):
        ok = True
        result = []
        filelist = glob.glob("*/*.pyc")
        for file in filelist:
            #print inspect.getmodulename(file)
            l = file.rfind(os.sep)
            path = file[0:l]
            modulename = file[l+1:-4]
            sys.path.append(path)
            sys.path.append("%s%s..%sshare" % (path,os.sep,os.sep))
            try:
                #print pyclbr.readmodule(eval(file))

##                classes = pyclbr.readmodule(modulename)
##                for classname in classes:
##                    print classname
##                    for super in classes[classname].super:
##                        if isinstance(super, pyclbr.Class):
##                            print super.name
##                        else:
##                            print super
                mod = __import__(modulename)
                classes = inspect.getmembers(mod, inspect.isclass)
                for classinfo in classes:
                    c,v = classinfo
                    if issubclass(v, lookingForClass) and (classname == None or c == classname) and v != lookingForClass and v.__doc__ != None:
                        #print "adding", c
                        result.append([path, mod, v])
            except:
                print "Error in module"
                traceback.print_exc(file=sys.stdout)
                if quitOnError:
                    sys.exit()
                ok = False
            sys.path = sys.path[:-2]
        print "Compile result", ok
        return ok,result

if __name__ == "__main__":
    # testing
    d = DynamicImporter()
    d.compileAll()
    d.ImportCompiledObjects(demobase.DemoBase)
