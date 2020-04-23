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
class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        #loader.loadModel("models/environment")
        
        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)
        self.disableMouse()
        self.environment = loader.loadModel("environment/environment")
        self.environment.reparentTo(render)
        self.tempActor = Actor("models/act_p3d_chan", {"walk" : "models/a_p3d_chan_run"})
        self.tempActor2 = Actor("models/cube.bam")
        self.tempActor.reparentTo(render)
        self.tempActor2.reparentTo(render)
        self.tempActor.setPos(0, 3, 0)
        self.tempActor2.setPos(0, 3, 0)
        self.tempActor.getChild(0).setH(180)
        self.tempActor.loop("walk")
        #self.useDrive()
        self.useTrackball()
        # Move the camera to a position high above the screen
        # --that is, offset it along the z-axis.
        self.camera.setPos(0, 0, 32)
        # Tilt the camera down by setting its pitch.
        self.camera.setP(-90)
        self.camera.reparentTo(self.tempActor)
        
        self.makeCamera(self.win, displayRegion = (0, 0.5, 0, 1))
        self.makeCamera(self.win, displayRegion = (0.5, 1, 0, 1))
        self.camList[1].reparentTo(self.tempActor)
        self.camList[1].setPos(-0.5, 10, 20)

        self.camList[2].setPos(0.5, 0, 0)
        self.camList[2].reparentTo(render)

        #self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        


        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        colliderNode = CollisionNode("player")
        colliderNode.addSolid(CollisionSphere(0, 0, 0, 0.3))
        collider = self.tempActor.attachNewNode(colliderNode)
        collider.show()
        # The pusher wants a collider, and a NodePath that
        # should be moved by that collider's collisions.
        # In this case, we want our player-Actor to be moved.
        base.pusher.addCollider(collider, self.tempActor)
        # The traverser wants a collider, and a handler
        # that responds to that collider's collisions
        base.cTrav.addCollider(collider, self.pusher)
        self.pusher.setHorizontal(True)
        # Tubes are defined by their start-points, end-points, and radius.
        # In this first case, the tube goes from (-8, 0, 0) to (8, 0, 0),
        # and has a radius of 0.2.
        wallSolid = CollisionTube(-8.0, 0, 0, 8.0, 0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setY(8.0)

        wallSolid = CollisionTube(-8.0, 0, 0, 8.0, 0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setY(-8.0)

        wallSolid = CollisionTube(0, -8.0, 0, 0, 8.0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setX(8.0)

        wallSolid = CollisionTube(0, -8.0, 0, 0, 8.0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setX(-8.0)


        
        
        # buffer = self.win.make_texture_buffer("renderBuffer", 1000, 750, to_ram=True)
        # data = buffer.get_texture().getRamImage()
        # np_buffer = np.frombuffer(data, np.float32)
        # print(np_buffer)
        

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
            self.win.saveScreenshotDefault('www')
            imm=self.win.getScreenshot().getRamImageAs("RGB")
            #print(imm)
            np_buffer = np.array(imm, np.float32)
            
            #print(np_buffer.shape)
            print(np_buffer[:-300])
            #list of Nodespaths
            #self.tempActor.ls()
            #self.render.ls()
            #self.camera.ls()
            #print(self.camList)

            

        return task.cont  
    # def spinCameraTask(self, task):
    #     angleDegrees = task.time * 6.0
    #     angleRadians = angleDegrees * (pi / 180.0)
    #     self.camera.setPos(20 * sin(angleRadians), -20 * cos(angleRadians), 3)
    #     self.camera.setHpr(angleDegrees, 0, 0)
    #     return task.cont 
     
game = Game()
game.run()