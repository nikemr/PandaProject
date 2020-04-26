from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.actor.Actor import Actor
from panda3d.core import AmbientLight
from panda3d.core import Vec4
from panda3d.core import DirectionalLight
from panda3d.core import PointLight
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

import gltf

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        gltf.patch_loader(self.loader)
        
        properties = WindowProperties()
        properties.setSize(1000, 750)
        
        
        

        self.disableMouse()
        self.environment = loader.loadModel("environment/island.gltf")
        self.environment.reparentTo(render)
        self.environment.setPos(0,0,-3) 
        self.environment.setHpr(0,-90,0)


        """ I put this becase I think there is a default light that I cant reach and manupulate.
        thets why I setLightsOff first. Otherwise Ican't create or cast shadows etc. """
        self.environment.setLightOff()

        mats = self.environment .findAllMaterials()
        mats[0].clearBaseColor()
        mats[1].clearBaseColor()
       
        mats[0].setShininess(200)
        
        mats[1].setShininess(100)
        
        """ In this block I create a textureBuffer and create camera 
        on that buffer that its display region is upper right corner of the window
        I use that region to create saveScreenShot xxxx or create a numpy array out of it
        (numpy_image_data) 
        second try is to make a screenshot directly from the buffer which is not so important
        Both works though """
        
        self.useTrackball()
        # ambientLight = AmbientLight("ambient light")
        # ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        # self.ambientLightNodePath = render.attachNewNode(ambientLight)
        # render.setLight(self.ambientLightNodePath)
        # In the body of your code
        mainLight = DirectionalLight("main light")
        
        self.mainLightNodePath = render.attachNewNode(mainLight)
        # Turn it around by 45 degrees, and tilt it down by 45 degrees
        mainLight.setShadowCaster(True,1000,1000)
        self.mainLightNodePath.setHpr(45, -45, 0)
        render.setLight(self.mainLightNodePath)

        """ I put it here again"""
        self.environment.setLight(self.mainLightNodePath)

        pointLight = PointLight("point light")
        pointLight.setShadowCaster(True,1000,1000)
        self.pointLightNodePath = render.attachNewNode(pointLight)
        self.pointLightNodePath.setPos(0,0,10)
        render.setLight(self.pointLightNodePath)

        """ and again """
        self.environment.setLight(self.pointLightNodePath)

        render.setShaderAuto()

        self.tempActor2 = Actor("models/cube.bam")
        self.tempActor2.reparentTo(render)
        self.tempActor2.setPos(-2, 2, -1)
        self.tempActor2.setScale(.2)
        
        self.monkey = Actor("models/monkey")
        self.monkey.set_scale(.25)
        self.monkey.reparentTo(render)
        self.monkey.set_pos(-7,-7,2) 
        self.monkey.lookAt(self.tempActor2)  

        self.monkey2 = Actor("models/monkey")
        self.monkey2.set_scale(.25)
        self.monkey2.reparentTo(render)
        self.monkey2.set_pos(0,3,1)
        self.monkey2.lookAt(self.tempActor2)



        

        tex=Texture()
        self.mybuffer = self.win.makeTextureBuffer("My Buffer", 512, 512,tex,to_ram=True)
        self.mybuffer.setSort(-100)
        mycamera = self.makeCamera(self.mybuffer,displayRegion=(.5,1,.5,1))
        mycamera.reparentTo(self.monkey)



        tex2=Texture()
        mybuffer2 = self.win.makeTextureBuffer("My Buffer2", 512, 512,tex,to_ram=True)
        mybuffer2.setSort(-500)
        mycamera2 = self.makeCamera(mybuffer2,displayRegion=(0,.5,0,.5))
        mycamera2.reparentTo(self.monkey2)

        self.graphicsEngine.renderFrame()

        
        print(self.mybuffer.getActiveDisplayRegions())
        """shadows for cameras missing here in screenshot"""
        save_it=self.mybuffer.getActiveDisplayRegion(0).saveScreenshotDefault('1111')
        my_output=self.mybuffer.getActiveDisplayRegion(0).getScreenshot()
        numpy_image_data=np.array(my_output.getRamImageAs("RGB"), np.float32)
        """shadows for cameras missing here in screenshot"""
        save_it2=mybuffer2.getActiveDisplayRegion(0).saveScreenshotDefault('2222')
        my_output2=mybuffer2.getActiveDisplayRegion(0).getScreenshot()
        numpy_image_data2=np.array(my_output2.getRamImageAs("RGB"), np.float32)
        print(numpy_image_data)



        file_name=Filename.fromOsSpecific("save_gameDat_001.png")
        self.mybuffer.saveScreenshot(file_name)
        print('Cameras')
        print(self.camList)
        print('Number Of Display Regions')
        print(self.win.getNumDisplayRegions())
        print('Active Display Regions')
        print(self.win.getActiveDisplayRegions())

        print(self.win.getDisplayRegions())
        
        print('Number Of Display Regions')
        print(self.win.getNumDisplayRegions())


        self.keyMap = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "shoot" : False
        }
        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("mouse1", self.updateKeyMap, ["shoot", True])
        self.accept("mouse1-up", self.updateKeyMap, ["shoot", False])

        self.updateTask = taskMgr.add(self.update, "update")
    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
        print (controlName, "set to", controlState) 
   
    def update(self, task):
        # Get the amount of time since the last update
        dt = globalClock.getDt()

        # If any movement keys are pressed, use the above time
        # to calculate how far to move the character, and apply that.
        if self.keyMap["up"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, 5.0*dt, 0))
        if self.keyMap["down"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, -5.0*dt, 0))
        if self.keyMap["left"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(-5.0*dt, 0, 0))
        if self.keyMap["right"]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(5.0*dt, 0, 0))
        if self.keyMap["shoot"]:
            print ("Zap!")
            #imm=self.win.getScreenshot().getRamImage()
            """shadows for cameras visible in this screenshot"""
            self.mybuffer.getActiveDisplayRegion(0).saveScreenshotDefault('333')
            
            #print(np_buffer.shape)
            
            #list of Nodespaths
            #self.tempActor.ls()
            #self.render.ls()
            #self.camera.ls()
            #print(self.camList)

            

        return task.cont  

        

        
        
    
game = Game()
game.run()
