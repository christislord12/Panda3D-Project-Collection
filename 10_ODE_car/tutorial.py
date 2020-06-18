# -*- coding: utf_8 -*-
from direct.directbase import DirectStart
from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup
from pandac.PandaModules import OdeBody, OdeMass, OdeBoxGeom, OdePlaneGeom, OdeCylinderGeom, OdeSphereGeom
from pandac.PandaModules import OdeJointGroup,OdeJoint,OdeHinge2Joint
from pandac.PandaModules import BitMask32, CardMaker, Vec4, Quat, Point3, Vec3
from random import randint, random
from direct.showbase import DirectObject 
from CameraHandler import CameraHandler
from pandac.PandaModules import Texture, TextureStage 
import math
from pandac.PandaModules import AmbientLight, PointLight

class World():
    def __init__(self):
        #Общее освещение
        self.ambientLight = render.attachNewNode( AmbientLight( "ambientLight" ) )
        self.ambientLight.node().setColor( Vec4( .8, .8, .8, 1 ) )
        #Точечный источник
        self.PointLight = camera.attachNewNode( PointLight( "PointLight" ) )
        self.PointLight.node().setColor( Vec4( 0.8, 0.8, 0.8, 1 ) )
        self.PointLight.node().setAttenuation( Vec3( .1, 0.04, 0.0 ) ) 
            
        #Говорим, что нужно освещать рендер
        render.setLight( self.ambientLight )
        render.setLight( self.PointLight )
       
        #Установка нашего физического мира
        self.world = OdeWorld()
        self.world.setGravity(0, 0, -9.81)
        #Поверхности для столкновений
        #Теперь их у нас два типа - для колёс (1) и для всего остального (0)
        #Параметры подбираются опытным путём. Описание есть в Reference
        self.world.initSurfaceTable(2)
        self.world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
        self.world.setSurfaceEntry(0, 1, 1.0, 0.0, 9.1, 0.9, 0.00001, 100, 0.002)
        

        #Создание пространства ОДЕ и добавление контактной группы для хранения
        #соединений, возникших при столкновении
        self.space = OdeSimpleSpace()
        self.space.setAutoCollideWorld(self.world)
        self.contactgroup = OdeJointGroup()
        self.space.setAutoCollideJointGroup(self.contactgroup)

        #Загружаем бокс
        box = loader.loadModel("box")
        #и текстуру к нему
        tex = loader.loadTexture('box.png')
        ts = TextureStage('ts')
        #назначаем тип текстуры - в данном случае на неё должен 
        #будет влиять диффузный цвет объекта
        ts.setMode(TextureStage.MModulate)
        box.setTexture(ts,tex)
        #список боксов
        self.boxes = []
        #генерим случайные боксы
        for i in range(randint(50, 100)):
            #генерируем размеры
            sx=random()+0.5
            sy=random()+0.5
            sz=random()+0.5
            #создаём копию загруженного ранее бокса
            #и сразу реперентим его в корневой узел - делаем видимым
            boxNP = box.copyTo(render)
            #устанавливаем случайным образом позицию
            boxNP.setPos(randint(-30, 30), randint(-30, 30), 10 + random())
            #цвет
            boxNP.setColor(random()*2, random()*2, random()*2, 1)
            #и ориентацию в пространстве
            boxNP.setHpr(randint(-45, 45), randint(-45, 45), randint(-45, 45))
            #устанавливаем размер сгенеренный ранее
            boxNP.setScale(sx,sy,sz)
            #С визуальной составляющей всё -
            #теперь создадим и настроим для наших боксов
            #физическое тело. Это что б дать знать ОДЕ как
            #применять к ним силы, какая у них масса, где центр масс и т.д.
            boxBody = OdeBody(self.world)
            M = OdeMass()
            M.setBox(150, 1, 1, 1)
            boxBody.setMass(M)
            #и синхронизируем их положение с нашими визуальными телами
            boxBody.setPosition(boxNP.getPos(render))
            boxBody.setQuaternion(boxNP.getQuat(render))
            #настроим физическую геометрию для наших физических тел
            #т.е. дадим ОДЕ знать каким образом они должны сталкиваться
            boxGeom = OdeBoxGeom(self.space, sx,sy,sz)
            #присвоим физической геометрии созданное ранее физическое тело
            boxGeom.setBody(boxBody)
            #Замечание:физическое тело и геометрия никак не связаны 
            #с наши визуальным кубиком, который мы создали ранее. 
            #Не стоит их путать.
            #В завершение, внесём наше физическое и визуальное тело в список
            #это потребуется в дальнейшем что б их синхронизировать
            self.boxes.append((boxNP, boxBody))

        #Небольшая визуализация для поверхности, на которую будут сыпаться кубики
        self.cm = CardMaker("ground")
        self.cm.setFrame(-50, 50, -50, 50)
        self.ground = render.attachNewNode(self.cm.generate())
        self.ground.setPos(0, 0, 0); self.ground.lookAt(0, 0, -2)
        self.ground.setTexture(ts,tex)
        self.groundGeom = OdePlaneGeom(self.space, Vec4(0, 0, 1, 0))
        #Устанавливаем позицию камеры
        base.disableMouse()
        base.camera.setPos(40, 40, 20)
        base.camera.lookAt(0, 0, 0)
        #регистрируем задание на обновление физической симуляции
        taskMgr.doMethodLater(0.5, self.simulationTask, "Physics Simulation")
      
        self.car=Car(self.world,self.space)
        #процедура нашей физической симуляции
    def simulationTask(self,task):
        cc=self.space.autoCollide() #Устанавливаем контактные соединения на  автомат
        #Запускаем шаг симуляции за время последнего рендеринга
        # на всякий случай делаем проверку что б наш шаг небыл слишком большим
        #иначе при "прихватывании" получим взрыв - наши тела разлетятся во все стороны
        dt=globalClock.getDt()*2
        if dt>0.05:
            dt=0.05
        self.world.quickStep(dt)
        #Синхронизируем визуальные тела панды с физическими ОДЕ
        for np, body in self.boxes:
            np.setPos(render, body.getPosition())
            np.setQuat(render,Quat(body.getQuaternion()))
        self.contactgroup.empty() #Очищаем контакты перед следующим шагом симуляции
        self.car.Sync()
        return task.cont

#Класс машины
class Car():
    def __init__(self,world,space):
        self.world=world
        self.space=space
        self.camH=CameraHandler() #импортируем управление камерой
        self.camH.moveByMouse=False 
        self.camH.camDist=60
        self.turn=False #переменные для обработки поворота колёс
        self.turnspeed=0.0
        self.turnangle=0.0
        self.box = loader.loadModel("box")#корпус машины - настравается аналогично кубикам
        self.box.setZ(2.5)
        self.box.setY(-16)
        self.box.setScale(2,4,1) 
        self.box.setColor(0.5,0.5,0.5)       
        self.box.reparentTo(render)
        self.body=OdeBody(self.world)
        M = OdeMass()
        M.setBox(140, 2, 4, 0.5)
        self.body.setMass(M)
        self.body.setPosition(self.box.getPos(render))
        self.bodyGeom = OdeBoxGeom(self.space, 2,4,1)
        self.bodyGeom.setBody(self.body)          
        self.joints=[] #соединения
        self.wheelsbody=[] #тело колёс
        self.wheelsgeom=[] #геометрия колёс
        self.wheels=[]     #визуальное представление колёс
        for i in range(4):
            #настраиваем физические параметры колеса
            self.wheelsbody.append(OdeBody(self.world))
            M = OdeMass()
            M.setCylinder(260,2,1, 0.4)
            self.wheelsbody[i].setMass(M)
            self.wheelsbody[i].setQuaternion(Quat(0.7,0,0.7,0))
            self.wheelsgeom.append(OdeCylinderGeom(self.space, 1,0.4))
            self.wheelsgeom[i].setBody(self.wheelsbody[i]) 
            self.space.setSurfaceType(self.wheelsgeom[i],1)            
            #добавляем соединение hinge2 - специально предназначенное 
            #для случая с колёсами
            self.joints.append(OdeHinge2Joint(self.world))
            self.joints[i].attachBodies(self.body,self.wheelsbody[i])
            #минимальный и максимальный угол, в пределах которого
            #болтается колесо. У нас оно не должно болтаться, поэтому
            #ставим его одинаковым
            self.joints[i].setParamHiStop(0, 0.0)
            self.joints[i].setParamLoStop(0, 0.0)
            #параметр уменьшения ошибок в подвеске
            self.joints[i].setParamSuspensionERP(0, 1)
            #смешивание сил - в данном случае влияет на 
            #жёсткость подвески
            self.joints[i].setParamSuspensionCFM(0, 0.001)            
            #параметр сглаживания рывков при приложении компенсирующих сил
            self.joints[i].setParamFudgeFactor(0,0.1)
            #оси соединения - одна вертикально, одна горизонтально
            self.joints[i].setAxis1(0,0,1)
            self.joints[i].setAxis2(1,0,0)            
            #визуальная модель
            self.wheels.append(loader.loadModelCopy("wheel"))
            self.wheels[i].setColor(0.5,0.5,0.5)
            self.wheels[i].setScale(1,1,2)
            self.wheels[i].reparentTo(render)            
        #устанавливаем наши колёса в исходое положение
        self.wheelsbody[0].setPosition(-1.8,-14,2)
        self.wheelsbody[1].setPosition(-1.8,-18,2)
        self.wheelsbody[2].setPosition(1.8,-14,2)
        self.wheelsbody[3].setPosition(1.8,-18,2)
        #устанавливаем центы соединений колёс с корпусом
        self.joints[0].setAnchor(Vec3(-1.1,-14,2))    
        self.joints[1].setAnchor(Vec3(-1.1,-18,2))
        self.joints[2].setAnchor(Vec3(1.1,-14,2))
        self.joints[3].setAnchor(Vec3(1.1,-18,2))
        
        #регистрируем реакцию на нажатия клавишь и задачу управления машиной
        base.accept('w', self.Accel,[-15])
        base.accept('w-up', self.Accel,[0])
        base.accept('s', self.Accel,[15])
        base.accept('s-up', self.Accel,[0]) 
        base.accept('d', self.Turn,[True,0.01])       
        base.accept('a', self.Turn,[True,-0.01])       
        base.accept('d-up', self.Turn,[False,0.01])       
        base.accept('a-up', self.Turn,[False,-0.01])
        taskMgr.add(self.TurnTask,"Rule Car")               
    #фнкция придания колёсам скорости
    def Accel(self,aspect):
        #привод на все 4
        for i in range(4):
            #устанавливаем скорость вращения
            self.joints[i].setParamVel(1,aspect)
            #и силу с которой мы пытаемся достичь этой скорости
            if aspect==0:
                self.joints[i].setParamFMax(1, 500)
            else:
                self.joints[i].setParamFMax(1, 2500)    
    #поворот колёс (просто присовоение необходимых переменных)    
    def Turn(self,enabled,aspect):
        self.turn=enabled
        self.turnspeed=aspect
    #сам поворот осуществляется здесь
    def TurnTask(self,task):
        #считаем
        if not self.turn:
            if self.turnangle>0:
                self.turnspeed=-0.01
            if self.turnangle<0:    
                self.turnspeed=0.01
        self.turnangle=self.turnangle+self.turnspeed
        if self.turnangle>0.3:
            self.turnangle=0.3
        if self.turnangle<-0.3:
            self.turnangle=-0.3    
        # и устанавливаем передним колёсам нужный угол
        self.joints[1].setParamHiStop(0, self.turnangle)
        self.joints[1].setParamLoStop(0, self.turnangle)        
        self.joints[3].setParamHiStop(0, self.turnangle)
        self.joints[3].setParamLoStop(0, self.turnangle)                 
        return task.cont
    #синхронизаци видимых частей тележки с физическими
    def Sync(self):
        self.box.setPos(render, self.body.getPosition())
        self.camH.setTarget(self.box.getX(),self.box.getY(),self.box.getZ()+1)
        self.box.setQuat(render,Quat(self.body.getQuaternion()))
        for i in range(4):
            self.wheels[i].setPos(render, self.wheelsbody[i].getPosition())
            self.wheels[i].setQuat(render,Quat(self.wheelsbody[i].getQuaternion()))
World()

run()