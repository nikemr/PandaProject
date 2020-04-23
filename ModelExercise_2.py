from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.actor.Actor import Actor
from panda3d.core import AmbientLight
from panda3d.core import Vec4
from panda3d.core import DirectionalLight
from panda3d.core import Vec4, Vec3
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionNode
from panda3d.core import CollisionTube
from panda3d.core import Camera
from panda3d.core import NodePath

from panda3d.core import GraphicsOutput

import numpy as np
from direct.task import Task
from opensimplex import OpenSimplex
from panda3d.core import Texture
class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        
        
        properties = WindowProperties()
        properties.setSize(1000, 750)
        
        
        self.dr = self.camNode.getDisplayRegion(0) 
        self.dr.setActive(0) # disable
        print(self.dr.getSort())
        self.dr1 = self.win.makeDisplayRegion(0.0, 0.5, 0, .5) 
        self.dr1.setSort(self.dr.getSort())
        self.dr1.setCamera(self.camList[0])
        
        self.dr2 = self.win.makeDisplayRegion(0.5, 1, 0, 0.5) 
        
        
        self.makeCamera(self.win,sort=0,displayRegion=(0.5,1,0.5,1),camName="cam2")
        

        self.disableMouse()
        self.environment = loader.loadModel("environment/environment")
        self.environment.reparentTo(render)
        self.monkey = Actor("models/monkey")
        self.monkey.set_scale(.25)
        self.monkey.reparentTo(render)
        self.monkey.set_pos(0,0,2)   

        self.monkey2 = Actor("models/monkey")
        self.monkey2.set_scale(.25)
        self.monkey2.reparentTo(render)
        self.monkey2.set_pos(0,3,2)
        self.camList[0].reparentTo(self.monkey)
        self.camList[1].reparentTo(self.monkey2)
        self.taskMgr.add(self.example_Task, "updateTask")
        
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(self.ambientLightNodePath)
        # In the body of your code
        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = render.attachNewNode(mainLight)
        # Turn it around by 45 degrees, and tilt it down by 45 degrees
        self.mainLightNodePath.setHpr(45, -45, 0)
        render.setLight(self.mainLightNodePath)
        render.setShaderAuto()
        
        print('Cameras')
        print(self.camList)
        print('Number Of Display Regions')
        print(self.win.getNumDisplayRegions())
        print('Active Display Regions')
        print(self.win.getActiveDisplayRegions())
        
        self.win.removeDisplayRegion(self.win.getDisplayRegion(1))
        self.win.removeDisplayRegion(self.win.getDisplayRegion(1))
        self.win.removeDisplayRegion(self.win.getDisplayRegion(1))
        
        print(self.win.getDisplayRegions())
        
        print('Number Of Display Regions')
        print(self.win.getNumDisplayRegions())
        
        

        self.disableMouse()
        self.useTrackball()

        #self.win.getDisplayRegion(2).saveScreenshotDefault('www')

        #this works but I get black screen  because it gets the SC before the rendering
        texture = self.win.getDisplayRegion(1).getScreenshot()        
        numpy_image_data=np.array(texture.getRamImageAs("RGB"), np.float32)
        print(np.max(numpy_image_data[123456]))

       
        

        
    def example_Task(self,task):
        if task.time <5.0:
            self.monkey.setPos(self.monkey.getPos() + Vec3(0, 0.01, 0))            
            
            return Task.cont
        #this really works because it saves the SC during rendering
        self.win.getDisplayRegion(1).saveScreenshotDefault('www')
        print('matask Done')
        return Task.done   
        
        
        
       
       
        
        

        

    
game = Game()
game.run()
