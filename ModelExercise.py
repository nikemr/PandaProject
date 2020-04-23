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
import numpy as np
from direct.task import Task
from opensimplex import OpenSimplex
from panda3d.core import Texture
class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        properties = WindowProperties()
        properties.setSize(1000,1000)
        self.win.requestProperties(properties)
        self.disableMouse()
        self.environment = loader.loadModel("environment/environment")
        self.environment.reparentTo(render)
        self.useTrackball()
        self.monkey = Actor("models/monkey")
        self.monkey.set_scale(.25)
        self.monkey.reparentTo(render)
        self.monkey.set_pos(0,0,2)   

        self.monkey2 = Actor("models/monkey")
        self.monkey2.set_scale(.25)
        self.monkey2.reparentTo(render)
        self.monkey2.set_pos(0,3,2)
        
        
        self.camera.reparentTo(self.monkey)
        
        
        props = WindowProperties.getDefault()
        props.setOrigin(0, 0)
        props.setSize(300, 300)
        props.setFixedSize(True)

        offwindow = self.openWindow(props, makeCamera=False, type="onscreen", requireWindow=True)
        display_region = offwindow.makeDisplayRegion(0, 1.0, 0, 1.0)

        self.graphicsEngine.renderFrame()
        texture = display_region.getScreenshot()
        numpy_image = memoryview(texture.getRamImage()) 
        numpy_image_data=np.array(texture.getRamImage())
        print(numpy_image_data[0:100])
        
       
       
        
        

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
        
        
    
    def example_Task(self,task):
            if task.time < 3.0:
                self.monkey.setPos(self.monkey.getPos() + Vec3(0, 0.01, 0))            
                
                return Task.cont

            print('matask Done')
            return Task.done

    
game = Game()
game.run()
print("bitti")
