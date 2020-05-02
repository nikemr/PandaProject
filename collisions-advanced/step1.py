# -*- coding: utf-8 -*-
"""
inView 2: the revenge

by fabius astelix @2010-02-10

Level: ADVANCED

As seen in beginner/step7 we're going to use again the inView method - a cheap way to detect object in-sight of a camera. This time though we'll use it off a spotlight!

NOTE If you won't find here some line of code explained, probably you missed it in the previous steps - if you don't find there as well though, or still isn't clear for you, browse at http://www.panda3d.org/phpbb2/viewtopic.php?t=7918 and post your issue to the thread.
"""
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import ActorNode, CollisionHandlerQueue, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay
from pandac.PandaModules import PerspectiveLens, Spotlight
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

base.cam.setPos(40, -90, 40)

splash=snipstuff.splashCard()
snipstuff.info.append("isInView Over A Spotlight")
snipstuff.info.append("an advanced sample to show how to use creatively the isInView method")
snipstuff.info.append("Try to hide from the sentinel spot.\n\nwasd=steer the avatar\nSPACE=avatar jump\nf=toggle sentinel frustum")
snipstuff.info_show()
snipstuff.dlight.setColor((.1, .0, .2, 1))

#=========================================================================
# Main
"""
Do you ever heard about a game called The Sentinel? it was mid-80 game by the legendary dev Geoff Crammond where robot sentinels where lurking and keeping control over lanscapes, absorbing every form of life transforming it into cubes. Well, we're not going to do that, but rather a simple sentinel's intruder detection using frowney as the sentinel and our smiley avatar as the intruder guy that gotta run and hide to not be detected. The scene make good use of intermediate/step3 gravity floor and wall collider setup, the isInView feature seen in basic/step5, but applied this time to a spotlight instead the main camera, and the CollisionHandlerQueue to have a good and cheap sentinel's intruder detection simulation.
To recap the handlers:
  CollisionHandlerPusher for walls
  CollisionHandlerGravity for floor
  CollisionHandlerQueue for precise intruder detection
The colliders are:
  for smiley avatar (all INTO and masked colliders):
    CollisionRay for the floor (FLOOR_MASK)
    CollisionSphere for walls (WALL_MASK)
    CollisionSphere for sentinel accurate detection (SENTINEL_MASK)
  for sentinel:
    CollisionRay FROM collider with SENTINEL_MASK and WALL_MASK (we'll see why)
  the wall and floor geometry are as usual INTO colliders and masked accordingly
"""
#=========================================================================

#** Collision system ignition
base.cTrav=CollisionTraverser()

#** Collision masks
FLOOR_MASK=BitMask32.bit(1)
WALL_MASK=BitMask32.bit(2)
SENTINEL_MASK=BitMask32.bit(3)

#** The handlers used in this scene:
# floor
avatarFloorHandler = CollisionHandlerGravity()
avatarFloorHandler.setGravity(9.81+25)
avatarFloorHandler.setMaxVelocity(100)
# wall
wallHandler = CollisionHandlerPusher()
# and the sentinel
sentinelHandler = CollisionHandlerQueue()

#** our smiley avatar setup - see below that we added more stuff than usual
avatarNP=base.render.attachNewNode(ActorNode('smileyNP'))
avatarNP.reparentTo(base.render)
avatar = loader.loadModel('smiley')
avatar.reparentTo(avatarNP)
avatar.setCollideMask(BitMask32.allOff())
avatar.setPos(0,0,1)
avatarNP.setPos(0,0,15)
avatarCollider = avatar.attachNewNode(CollisionNode('smileycnode'))
avatarCollider.node().addSolid(CollisionSphere(0, 0, 0, 1))
avatarCollider.node().setFromCollideMask(WALL_MASK)
avatarCollider.node().setIntoCollideMask(BitMask32.allOff())
# here the additional stuff: it is a collider that will be used by the sentinel's ray to see if smiley is behind a wall - this is essential because the isInView method don't provide geometry culling but act as a body scanner reading everything found into its frustum's sight, including walls and other obstacles as well.
avatarBody = avatar.attachNewNode(CollisionNode('smileybody'))
avatarBody.node().addSolid(CollisionSphere(0, 0, 0, 1.2))
avatarBody.node().setFromCollideMask(BitMask32.allOff())
avatarBody.node().setIntoCollideMask(SENTINEL_MASK)
# as you should already know, to be recognized by, we must add the avatar's body collider to the sentinel's handler.
base.cTrav.addCollider(avatarBody, sentinelHandler)
# the avatar's ray collider for ground collision detection
raygeometry = CollisionRay(0, 0, 2, 0, 0, -1)
avatarRay = avatarNP.attachNewNode(CollisionNode('avatarRay'))
avatarRay.node().addSolid(raygeometry)
avatarRay.node().setFromCollideMask(FLOOR_MASK)
avatarRay.node().setIntoCollideMask(BitMask32.allOff())

#** The terrain map - the egg model loaded contains also the collider geometry for the terrain and for the walls as childs
terrain = loader.loadModel("scene1")
terrain.reparentTo(render)
terrain.setCollideMask(BitMask32.allOff())
terrain.setScale(10)
floorcollider=terrain.find("**/floor_collide")
floorcollider.node().setFromCollideMask(BitMask32.allOff())
floorcollider.node().setIntoCollideMask(FLOOR_MASK)
wallcollider=terrain.find("**/wall_collide")
wallcollider.node().setFromCollideMask(BitMask32.allOff())
wallcollider.node().setIntoCollideMask(WALL_MASK)

#** Here the sentinel - the only collider we put in it is the ray detector (see below)
sentinel = loader.loadModel("frowney")
sentinel.setCollideMask(BitMask32.allOff())
sentinel.reparentTo(render)
sentinel.setPos((7.83, -25.31, 24))
avatar_in_sight=False
# we create a spotlight that will be the sentinel's eye and will be used to fire the inView method
slight = Spotlight('slight')
slight.setColor((1, 1, 1, 1))
lens = PerspectiveLens()
lens.setFar(80)
slight.setLens(lens)
slnp = sentinel.attachNewNode(slight)
render.setLight(slnp)
# this is important: as we said the inView method don't cull geometry but take everything is in sight frustum - therefore to simulate an hide and seek feature we gotta cheat a little: this ray is masked to collide with walls and so if the avatar is behind a wall the ray will be 'deflected' (we'll see how later in the sent_traverse function) - so we know who's behind a wall but we fake we can't see it.
sentraygeom = CollisionRay(0, 0, 0, 0, 1, 0)
sentinelRay = sentinel.attachNewNode(CollisionNode('sentinelray'))
sentinelRay.node().addSolid(sentraygeom)
# we set to the ray a cumulative masking using the or operator to detect either the avatar's body and the wall geometry
sentinelRay.node().setFromCollideMask(SENTINEL_MASK|WALL_MASK)
sentinelRay.node().setIntoCollideMask(BitMask32.allOff())
# we add the ray to the sentinel collider and now it is ready to go
base.cTrav.addCollider(sentinelRay, sentinelHandler)
# this interval will rotate the sentinel 360 deg indefinitely
a=-30
sentrotival = sentinel.hprInterval(8, (630,a,0), startHpr=(270,a,0))

#** the floor handler need to know what it got to handle: the avatar and its floor ray
avatarFloorHandler.addCollider(avatarRay, avatarNP)
# ...then add the avatar collide sphere and the wall handler
wallHandler.addCollider(avatarCollider, avatarNP)
# let's start'em up
base.cTrav.addCollider(avatarRay, avatarFloorHandler)
base.cTrav.addCollider(avatarCollider, wallHandler)

#** this is a siren, just for the show (and to annoy ppl)
siren=snipstuff.load3Dimage('textures/siren.png')
siren.hide()
siren.setScale(30,1,10)
siren.setPos(sentinel.getPos())
sirenrotival=siren.hprInterval(3, (360,0,0), startHpr=(0,0,0))
sirensound = loader.loadSfx("sounds/siren.mp3")
sirensound.setLoop(True)
def set_siren(v):
  if v:
    sirensound.play()
    siren.show()
    sirenrotival.loop()
  else:
    sirensound.stop()
    siren.hide()
    sirenrotival.pause()

#** to see or hide the sentinel's eye frustum
frustum=False
def frustum_toggle():
  global frustum, tsk
  frustum=not frustum
  if frustum: slight.showFrustum()
  else: slight.hideFrustum()
snipstuff.DO.accept("f", frustum_toggle)

#** Now check this out closely: this function will be called by some routine below to shoot the sentinel ray and see what is traversed by it - as you know from the basic/step1 and 2, after the traverse, the queue is full of what is found colliding with the handler - since we got a particular kind of FROM collider - a ray - that spear like a long pike everything on his path, if we sort the queue with sortEntries() we could know who's the first object the ray has pierced, and of course if it is not our avatar we don't care further to know who'll come then, simulating indeed a seek and hide feature.
def sent_traverse(o):
  # start the ray traverse
  base.cTrav.traverse(render)
  # align the colliders by order of piercing
  if (sentinelHandler.getNumEntries() > 0):
    sentinelHandler.sortEntries()
    entry = sentinelHandler.getEntry(0)
    colliderNode = entry.getIntoNode()
    # if the name of the 1st collider is our avatar then we say GOTCHA! the rest of the stuff is just for the show
    if colliderNode.getName() == 'smileybody':
      avatar_in_sight=True
      if sentrotival.isPlaying():
        sentrotival.pause()
        set_siren(1)
      return True
  if not sentrotival.isPlaying():
    sentrotival.loop()
    set_siren(0)
  avatar_in_sight=False
  return False

#** Here then we'll unleash the power of isInView method - this function is just a query if a 3D point is inside its frustum so it works for objects with lens, such as cameras or even, as in this case, a spotlight. But to make this happen, we got cheat a little, knowing in advance who we're going to seek, to query its position afterwards, and that's what the next line is about: to collect all the references for objects named 'smiley'
intruders=base.render.findAllMatches("**/smiley*")
def sent_detect(task):
  for o in intruders:
    # query the spotlight if something listed as 'intruders' is-In-View at its position and if this is the case we'll call the traverse function above to see if is open air or hidden from the sentinel's sight
    if slnp.node().isInView(o.getPos(slnp)):
      sentinel.lookAt(o)
      if sent_traverse(o): return task.cont
  if not sentrotival.isPlaying():
    sentrotival.loop()
    set_siren(0)
  return task.cont

#** settling up the scene for the imminent show
frustum_toggle()
sentrotival.loop()
tsk1 = taskMgr.add(sent_detect, "sentdetect", priority = 100)

#** Now we're ready to activate the avatar steering and go
def avatarwalk(dt, vel):
  if vel[0]: avatar.setR(avatar.getR()+(40*vel[0]))
  if vel[1]: avatar.setP(avatar.getP()+(-38*vel[1]))
#
def avatarjump(dt):
  if avatarFloorHandler.isOnGround(): avatarFloorHandler.addVelocity(20)
#
steering=snipstuff.avatar_steer(
  avatarNP, avatarwalk, avatarjump, fwspeed=8., lefthand=False
)
steering.start()

#** let's start the show
splash.destroy()
run()
