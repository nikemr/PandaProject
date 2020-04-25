from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.actor.Actor import Actor
from panda3d.core import AmbientLight
from panda3d.core import PointLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec4
from panda3d.core import DirectionalLight
from panda3d.core import Vec4, Vec3
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionNode
from panda3d.core import CollisionTube
from panda3d.core import Camera
from panda3d.core import NodePath
from panda3d.core import Material
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
        self.win.requestProperties(properties)
        self.disableMouse()
        self.useTrackball()
        self.environment = loader.loadModel("models/island.bam")
        self.environment.reparentTo(render)
        self.camera.getChild(0).setPos(100,100,15)
        # Tilt the camera down by setting its pitch.
        self.camera.getChild(0).setHpr(135,5,0)
        #self.camera.getChild(0).lookAt(self.environment)
        print(self.camera.getChild(0).getHpr())
        
        
        
        self.camera.reparentTo(render)
        
        
        
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor((.2, .2, .2, 1))
        
        self.ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(self.ambientLightNodePath)
        
        # plight = PointLight('plight')
        # plight.setColor((0.5, 0.5, 0.5, 1))
        # self.plnp = render.attachNewNode(plight)
        # self.plnp.setPos(0,0,3)
        # render.setLight(self.plnp)
        
        dlight = DirectionalLight('my dlight')
        self.dlnp = render.attachNewNode(dlight)
        self.dlnp.setHpr(45, -30, 0)
        
        self.dlnp.setColor((0.1, 0.1, 0.1, .1))
        render.setLight(self.dlnp)

        # mainLight = DirectionalLight("main light")
        # self.mainLightNodePath = render.attachNewNode(mainLight)
        # # Turn it around by 45 degrees, and tilt it down by 45 degrees
        # self.mainLightNodePath.setHpr(45, -45, 0)
        # render.setLight(self.mainLightNodePath)
        
        
        """ this block finds all materials from blender andclear Base Color
        which is white, otherwise while rendering everything is black or white
        (with directional light) other type of lights seems OK though """

        mats = self.environment .findAllMaterials()
        mats[0].clearBaseColor()
        mats[1].clearBaseColor()
        # mats[0].setDiffuse((0,1,0,1))
        # mats[0].setAmbient((0,1,0,1))
        #mats[0].setShininess(100)
        # mats[1].setDiffuse((0,0,1,.5))
        # mats[1].setAmbient((0,0,1,.5))
        mats[1].setShininess(10)
        render.setShaderAuto()
        print(mats[0])

        
        
        
       
       
        
        

        

    
game = Game()
game.run()
