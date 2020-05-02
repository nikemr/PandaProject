# -*- coding: utf-8 -*-
"""
2.5D - how to collide a mixup of 2d and 3d objects

by fabius astelix @2010-02-16

Level: ADVANCED

More than just a snippet this is a whole game level were you'll see many of the features seen so far put together for a real-world game. This snippet singularity is indeed to be a mix of 2d and 3d objects but for us don't change very much cos we're gong to apply the same tecniques seen so far applied.
Note that the purpose of this snippet is not to have a perfect game but just for learning.

NOTE If you won't find here some line of code explained, probably you missed it in the previous steps - if you don't find there as well though, or still isn't clear for you, browse at http://www.panda3d.org/phpbb2/viewtopic.php?t=7918 and post your issue to the thread.
"""
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Vec3
from pandac.PandaModules import ActorNode, CollisionHandlerEvent, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay, NodePath
from direct.interval.IntervalGlobal import *

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", """sync-video 0
"""
)
import direct.directbase.DirectStart
#** snippet support routines - not concerning the tutorial part
import snipstuff

#=========================================================================
# Scenographic stuff
#=========================================================================

base.cam.setPos(40, -70, 35)

splash=snipstuff.splashCard()
snipstuff.info.append("2.5D collisions")
snipstuff.info.append("how to collide 2D and 3D objects")
snipstuff.info.append("Try to reach the top of the windmill\n\nwasd=move the avatar around\nSPACE=avatar jump")
snipstuff.info_show()

#=========================================================================
# Main
""" As suggested above, we're going to use what we learned so far to make collide 2d and 3d objects. By the way there is nothing special to do from 3d-3d collisions cos the colliders and handlers used are exactly the same as you'll see.
"""
#=========================================================================

#** Collision system ignition
base.cTrav=CollisionTraverser()

#** This is the known collision handler we use for floor collisions. We'll keep going with the usual settings here as well.
avatarFloorHandler = CollisionHandlerGravity()
avatarFloorHandler.setGravity(9.81+25)
avatarFloorHandler.setMaxVelocity(100)

#** the walls collider
wallHandler = CollisionHandlerPusher()

#** we'll use this to 'sense' the fallout impact velocity and also to 'read' various triggers we've put around the map for several purposes.
collisionEvent = CollisionHandlerEvent()

#** Collision masks - this time there is a new one: the TRIGGER_MASK is used to detect certain collision geometry to act as a trigger, therefore we need to distinguish'em from floor and walls.
FLOOR_MASK=BitMask32.bit(1)
WALL_MASK=BitMask32.bit(2)
TRIGGER_MASK=BitMask32.bit(3)

#** Our steering avatar
avatarNP=base.render.attachNewNode(ActorNode('yolkyNP'))
avatarNP.reparentTo(base.render)
# by the way: this time we wont use the same old smiley but a 2d guy for this snippet purposes only - it is just a plane with a texture glued on, a so 2d object then.
avatar = loader.loadModel('yolky')
avatar.reparentTo(avatarNP)
# why this? this is to have our flat puppet rendered always on top of all objects in the scene, either 2d and 3d.
avatar.setDepthWrite(True, 100)
# the rest of the stuff is as usual...
avatar.setPos(0,0,1)
avatar.setCollideMask(BitMask32.allOff())
avatarNP.setPos(0,0,15)
# The yolky collision sphere used to detect when yolky hits walls
avatarCollider = avatar.attachNewNode(CollisionNode('yolkycnode'))
avatarCollider.node().addSolid(CollisionSphere(0, 0, 0, 1))
avatarCollider.node().setFromCollideMask(WALL_MASK)
avatarCollider.node().setIntoCollideMask(BitMask32.allOff())

#** the avatar's fallout sensor - stuff already seen in former snippets, but this time we'll use it for more that to detect the fallout impact force, so we'll add another mask to look out
avatarSensor = avatarNP.attachNewNode(CollisionNode('yolkysensor'))
cs=CollisionSphere(0, 0, 0, 1.2)
avatarSensor.node().addSolid(cs)
# here the masking: note that this sensor will look for floor bashing but also for other geometries masked with TRIGGER_MASK.
avatarSensor.node().setFromCollideMask(FLOOR_MASK|TRIGGER_MASK)
avatarSensor.node().setIntoCollideMask(BitMask32.allOff())
cs.setTangible(0)

#** here's how to read the events fired by the 'sensor' while colliding with geometry we enable to collide with it.
collisionEvent.addInPattern('%fn-into')
collisionEvent.addOutPattern('%fn-out')

#** the floor ray collider for the avatar
avatarRay = avatarNP.attachNewNode(CollisionNode('avatarRay'))
avatarRay.node().addSolid(CollisionRay(0, 0, 2, 0, 0, -1))
avatarRay.node().setFromCollideMask(FLOOR_MASK)
avatarRay.node().setIntoCollideMask(BitMask32.allOff())

#** This is the scene map - we'll gather off here almost every element of the map: scenery, ground colliders, walls, and also triggers and spawn points. See the .blend source for details on the scene components.
scene = loader.loadModel("windmill")
scene.reparentTo(render)
scene.setCollideMask(BitMask32.allOff())
scene.setScale(10)
# Let's mask our main collision surfaces
floorcollider=scene.find("**/floor0/floor_collide*")
floorcollider.node().setIntoCollideMask(FLOOR_MASK)
wallcollider=scene.find("**/wall0/wall_collide*")
wallcollider.node().setIntoCollideMask(WALL_MASK)

#** And now, for something completely the same, we'll settle other walls and floor colliders but these are conveniently grouped, therefore we'll gather'em 1 by 1 and settle their masks using the following routine:
def loadblocks():
  for element in scene.findAllMatches("**/stairs*/block*"):
    # Let's mask our collision surfaces
    coll=element.find("**/floor_collide*")
    if not coll.isEmpty():
      coll.node().setIntoCollideMask(FLOOR_MASK)
    coll=element.find("**/wall_collide*")
    if not coll.isEmpty():
      coll.node().setIntoCollideMask(WALL_MASK)
loadblocks()

#** this routine is for the big windmill wheel: it got a sphere collider placed for each tooth acting as pushing walls - be careful passing by in the game!
bigwheel=scene.find("**/bigwheel")
def loadbigwheel():
  for element in bigwheel.findAllMatches("**/collide*"):
    if not element.isEmpty():
      element.node().setIntoCollideMask(WALL_MASK)
loadbigwheel()

#** This is for our lever objects - it is made by a 2d textured plane, a little floor and a sphere collider to act as its trigger: when yolky touch it, the lever will go down and something will made happen. By the way the TRIGGER_MASK is not settled here but near down cos it is a routine good for all the trigger objects in the scene. Go down to see how and when and also dig the blender source to see how is built up.
lever=scene.find("**/lever1")
# Let's mask our collision surfaces
coll=lever.find("**/floor_collide*")
coll.node().setIntoCollideMask(FLOOR_MASK)

#** Here the triggers setup: we'll search the whole scene for objects named triggers* and apply the proper mask to distinguish from wall and floor colliders.
for coll in scene.findAllMatches("**/trigger*"):
  coll.node().setIntoCollideMask(TRIGGER_MASK)
rope_stair=scene.find('**/block_ropest')
rope_stair.setSz(.1)

#** Now the spawn points - we'll use these to remember their positions as spawn points while yolky pass beyond'em
for coll in scene.findAllMatches("**/spawn*"):
  coll.node().setIntoCollideMask(TRIGGER_MASK)
# we initialize the first spawn point
last_spawn=scene.find("**/spawn.000")

#** Now assign the colliders for floor and wall detection
avatarFloorHandler.addCollider(avatarRay, avatarNP)
wallHandler.addCollider(avatarCollider, avatarNP)

#** Let's start the 3 collision handlers: the first 2 for wall and floor and the third to fire events (see above the setup) while the avatarSensor touch geometry he is allowed to react with via the masking (actually floor and triggers)
base.cTrav.addCollider(avatarRay, avatarFloorHandler)
base.cTrav.addCollider(avatarCollider, wallHandler)
base.cTrav.addCollider(avatarSensor, collisionEvent)

#** a real game gotta god mode, right?
godmode=False
def setgodmode(v):
  global godmode
  godmode=v
  if v: base.cTrav.removeCollider(avatarRay)
  else: base.cTrav.addCollider(avatarRay, avatarFloorHandler)
snipstuff.DO.accept('g', setgodmode, [True])
snipstuff.DO.accept('shift-g', setgodmode, [False])

#** something will call this function for sure - go and check it out
def respawn():
  global last_spawn
  avatarNP.setPos(scene, last_spawn.getPos())

#** that is something better not going to happen to yolky - see in the game why
def splat(on):
  if on:
    avatar.setHpr((0,-90,0))
    tex = loader.loadTexture('textures/smileyx_splat.png')
    avatar.setTexture(tex,1)
    avatarNP.setScale((4,4,.1))
  else:
    avatar.setHpr((0,0,0))
    tex = loader.loadTexture('textures/smileyx.png')
    avatar.setTexture(tex,1)
    avatarNP.setScale((1,1,1))

#** Called as soon as the yolky sensor will exit the collider geometry properly masked.
def yolkySensorOut(entry):
  np_into=entry.getIntoNodePath()
  # as you'll see playing it, the game gotta object that will balance the yolky weight - here the balancing will return to the default posiiton
  if np_into.getName().find('trigger_balance') >=0:
    model=np_into.getParent()
    LerpHprInterval(model, 3, (0,0,20), blendType='easeIn').start()
  # yolky leave the rope stair trigger so I guess it will fall it down
  elif np_into.getName().find('trigger_ropest') >=0:
    setgodmode(False)

#** Some celebration for having reached the level goal
def end_of_level():
  snipstuff.infotext['message'].setText("YOU MADE IT, BRAVO!")
  posout=(0,0,0)
  posin=(0,0,4)
  Sequence(
    LerpPosHprInterval(
      avatar, .6, posin, (0,0,180), (0,0,0), posout, blendType='easeOut'),
    LerpPosHprInterval(
      avatar, .6, posout, (0,0,360), posin, (0,0,180), blendType='easeIn'),
    Wait(1),
  ).loop()

#** Called while the avatar sensor enter a trigger - any of them. For each there we'll call the proper routine, see below for more.
def yolkySensorIn(entry):
  global last_spawn
  np_into=entry.getIntoNodePath()
  # the lever trigger
  if np_into.getName().find('trigger_lev1') >=0:
    if rope_stair.getSz() < 1.:
      np_into.getParent().setR(20)
      scale=rope_stair.getScale()
      LerpScaleInterval(
        rope_stair, 2, (scale[0],scale[1],.42), blendType='easeOut'
      ).start()
  # the balancing wooden surface
  elif np_into.getName().find('trigger_balance') >=0:
    model=np_into.getParent()
    LerpHprInterval(model, 3, (0,0,0), blendType='easeIn').start()
  # touching the rope stair
  elif np_into.getName().find('trigger_ropest') >=0:
    setgodmode(True)
  # reaching the end of the level
  elif np_into.getName().find('trigger_eol') >=0:
    end_of_level()
  # touching the next spawn point - will be shut off the former and stored the new one
  elif np_into.getName().find('spawn') >=0:
    if last_spawn != np_into:
      last_spawn.node().setIntoCollideMask(BitMask32.allOff())
      last_spawn=np_into
  # the sensor touch the floor, therefore we'll test if yolky is hitting it too hard
  else:
    def yolkyHitTheGround(task):
      if avatarFloorHandler.isOnGround():
        # Getting the impact speed - if that will be more than a certain value we'll consider yolky dead.
        iv=abs(avatarFloorHandler.getImpactVelocity())
        if iv > 35:
          t="Oh No, I guess is dead! Respawning..."
          Sequence(
            Func(snipstuff.infotext['message'].setText, t),
            Func(splat, 1), Wait(3), Func(splat, 0),
            Func(avatar.setHpr, (0,0,0)),
            Func(snipstuff.infotext['message'].setText, ""),
            Func(respawn),
          ).start()
        task.remove()
      else: return task.cont
    tsk=taskMgr.add(yolkyHitTheGround, "yolky_hit_g")

#** Here is where we tell the panda3D event manager to test when our sensor events occur.
snipstuff.DO.accept('yolkysensor-into', yolkySensorIn)
snipstuff.DO.accept('yolkysensor-out', yolkySensorOut)

#** Make the yolky roll on the the floor and jump
def avatarwalk(dt, vel):
  if vel[0]: avatar.setR(avatar.getR()+(40*vel[0]))
#
def avatarjump(dt):
  if avatarFloorHandler.isOnGround():
    avatarFloorHandler.addVelocity(20)

#** Now we're ready to activate the avatar steering and go
steering=snipstuff.avatar_steer(
  avatarNP, avatarwalk, avatarjump, lefthand=False, steer2d=True
)
def avatarup(move):
  global godmode
  if not godmode: move=0
  return Vec3(0,0,move)
def avatardown(move):
  global godmode
  if not godmode: move=0
  return Vec3(0,0,-move)
steering.up=avatarup
steering.down=avatardown
steering.start()
respawn()

#** let's rotate the big wheel
bwival=bigwheel.hprInterval(18, (0,0,-360), startHpr=(0,0,0))
bwival.loop()

splash.destroy()
run()
