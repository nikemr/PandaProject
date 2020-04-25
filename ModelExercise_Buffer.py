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
from panda3d.core import Filename
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
        
        
        

        self.disableMouse()
        self.environment = loader.loadModel("environment/environment")
        self.environment.reparentTo(render)
        """ In this block I create a textureBuffer and create camera 
        on that buffer that its display region is upper right corner of the window
        I use that region to create saveScreenShot xxxx or create a numpy array out of it
        (numpy_image_data) 
        second try is to make a screenshot directly from the buffer which is not so important
        Both works though """
        tex=Texture()
        mybuffer = self.win.makeTextureBuffer("My Buffer", 512, 512,tex,to_ram=True)
        mybuffer.setSort(-100)
        mycamera = self.makeCamera(mybuffer,displayRegion=(.5,1,.5,1))
        mycamera.reparentTo(render)

        self.graphicsEngine.renderFrame()

        print(mybuffer.getActiveDisplayRegions())

        save_it=mybuffer.getActiveDisplayRegion(0).saveScreenshotDefault('xxxx')
        my_output=mybuffer.getActiveDisplayRegion(0).getScreenshot()
        numpy_image_data=np.array(my_output.getRamImageAs("RGB"), np.float32)
        
        print(numpy_image_data)



        file_name=Filename.fromOsSpecific("save_gameDat_001.png")
        mybuffer.saveScreenshot(file_name)
        print('Cameras')
        print(self.camList)
        print('Number Of Display Regions')
        print(self.win.getNumDisplayRegions())
        print('Active Display Regions')
        print(self.win.getActiveDisplayRegions())

        print(self.win.getDisplayRegions())
        
        print('Number Of Display Regions')
        print(self.win.getNumDisplayRegions())

        
        
    
game = Game()
game.run()
