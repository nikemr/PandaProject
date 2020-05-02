# -*- coding: utf-8 -*-
"""
Smiley shooter - a real-life application with the panda3D simple physics engine

Level: ADVANCED

This is a minigame where you'll see how to settle a simple shooter where the player shoots bullets using physics ballistic against a target having different hitting points sensitivity.

NOTE If you won't find here some line of code explained, probably you missed it in the previous steps - if you don't find there as well though, or still isn't clear for you, browse at http://www.panda3d.org/phpbb2/viewtopic.php?t=7918 and post your issue to the thread.
"""
import math, random
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *

loadPrcFileData("", """sync-video 0
"""
)
import direct.directbase.DirectStart
#** snippet support routines - not concerning the tutorial part
import snipstuff
base.disableMouse()

#=========================================================================
# Scenographic stuff
#=========================================================================

base.cam.setPos(0,-30,10)
base.cam.lookAt((0,0,4))

splash=snipstuff.splashCard()
snipstuff.info.append("Smiley shootout")
snipstuff.info.append("advanced collision setup to work with the panda3D physics engine")
snipstuff.info.append("""You got 3 shots per session and each session you'll go back 4mt. Try to shoot the best you can!

arrows/wsad=aim direction
ENTER=shoot bullet""")
snipstuff.infotext["message"].setAlign(TextNode.ALeft)
snipstuff.infotext["message"].setPos(.5,-.85)
snipstuff.info_show()

#=========================================================================
# Main
""" This is the last step of this tutorial so I tried to do things big. The game is settled to play within a physics simulation - the player gotta shoot bullets toward a circular target, very close to the archery target. Each bullet will be shooted with a Y axis force impulse and gotta fight against the usual gravity force and also an horizontal (XY) wind force - both forces randomly changes during the game.
This snippet starts off the beginner/step8 and we just added a linear force for the wind. Beside that, this time we gotta face the problem to have rapidly moving objects like the bullets shooted with high velocities. Playing with such things often ends with the from object that penetrate completely the geometries collided, and with no collision detected, but panda3D solve this issue with the traverser setRespectPrevTransform() method, that keep track of the whole path followed by the object and so there is no way to loose a collision.
"""
#=========================================================================

#** Collision system ignition - even if we're going to interact with the physics routines, the usual traverser is always in charge to drive collisions
base.cTrav=CollisionTraverser()
#** As said above this is a very important setting, mandatory for what we're going to do, as is: detect collisions of fast moving objects.
base.cTrav.setRespectPrevTransform(True)
# as we know, the physics sistem is intimately related with the particle system so this is why this line is here.
base.enableParticles()
# here there is the handler to use this time to manage collisions: the first for all the physics simulations and the second for the lasersight_ray we'll see down.
collisionHandler = PhysicsCollisionHandler()
collisionHandler2 = CollisionHandlerEvent()

#** this mask will be used to determine when a FROM object - a bullet in the specific - will hit the straw target item
TARGET_MASK=BitMask32.bit(2)

#** Just a plane collider to act as a floor
cp = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
planeNP = render.attachNewNode(CollisionNode('planecnode'))
planeNP.node().addSolid(cp)
planeNP.show()

#** Defining the global forces applied to all the objects taking part to the physics simulation:
globalforcesFN=ForceNode('world-forces')
globalforcesFNP=render.attachNewNode(globalforcesFN)
# this is the gravity force...
globalforcesGravity=LinearVectorForce(0,0,-9.81)
globalforcesFN.addForce(globalforcesGravity)
base.physicsMgr.addLinearForce(globalforcesGravity)
# ... and this time we add another force: wind - at the startup is put to 0 but you'll see this is about to change to a horizontal linear force, pushing objects along XY axes.
globalforcesWind=LinearVectorForce(0,0,0)
globalforcesFN.addForce(globalforcesWind)
base.physicsMgr.addLinearForce(globalforcesWind)

#** settling the nozzle model - note we get the nozzle exit point (indeed the bullet starting point before to be shooted away) from inside the egg model file, defined in blender (see models.blend) as an empty.
nozzlemodel=loader.loadModel("nozzle")
nozzlemodel.setCollideMask(BitMask32.allOff())
nozzleexit=nozzlemodel.find("**/nozexhaust")

#** this is a ray shooting off the nozzlegun exit actin as a laser shight - I made just as an example to see how to use it to aim at a surface and get the collisoin point. See below the raygun_again function
lasersight_ray = nozzleexit.attachNewNode(CollisionNode('lasersight_ray'))
lasersight_ray.node().addSolid(CollisionRay(0, 0, 0, 0, 4, 0))
lasersight_ray.node().setFromCollideMask(TARGET_MASK)
lasersight_ray.node().setIntoCollideMask(BitMask32.allOff())
base.cTrav.addCollider(lasersight_ray, collisionHandler2)
lasersight_ray.show()

#** and this is the straw target. Note the collider is got off the egg file and this time is not an invisible collider as we saw so far but is used the same visible mesh. Dig the model.blend source to know more.
targetmodel=loader.loadModel("target")
targetcollider=targetmodel.find("**/targetcollide")
targetcollider.node().setIntoCollideMask(TARGET_MASK)
targetmodel.reparentTo(render)
targetmodel.setScale(4.0)
targetmodel.setPos(0,0,4)

#** Now we'll define the events we're interest to check in: when a FROM object hit something, that we'll use to check when a frowney hit either the target or anything else; and when a FROM is into a TO object, to poll the raygun against the target and report the collision point and the collision normal of the polygon hit.
collisionHandler.addInPattern('%fn-into-everything')
collisionHandler2.addAgainPattern('%fn-again-%in')

#** This function is a commodity I made to build up as many balls I need to interact and collide into a physics environment - the whole function body contain then the code to settle a single FROM object, returning the topmost node to drive it around the render scene.
def phyball_dispenser(modelname, scale=1., ballradius=1):
  ballNP=NodePath(PandaNode("phisicsball"))
  ballAN=ActorNode("ballactnode")
  ballANP=ballNP.attachNewNode(ballAN)
  ballmodel=loader.loadModel(modelname)
  ballmodel.reparentTo(ballANP)
  ballmodel.setScale(scale)

  ballCollider = ballANP.attachNewNode(CollisionNode('%scnode'%modelname))
  ballCollider.node().addSolid(CollisionSphere(0,0,0, ballradius*scale))
  base.physicsMgr.attachPhysicalNode(ballAN)
  # to let the physics engine the object we got to tell the physics collision handler who is the collider and who the node to be driven and here MUST be the ActorNode without exceptions.
  collisionHandler.addCollider(ballCollider, ballANP)
  # as usual it is time to add the collider and its handler to the main traverser schedule
  base.cTrav.addCollider(ballCollider, collisionHandler)
  # now the physics object is ready to exit off the dispenser - by default I stick to the main 3d render scene
  ballNP.reparentTo(render)
  return ballNP

#=========================================================================
# Game stuff
""" From now on begins the gameplay stuff - I'll try not to bloat the code with comments, but rather to say something when really needed.
"""
#=========================================================================

hitpoints=[0.180, 0.365, 0.55, 0.736, 0.917, 1000]
colori=['yellow','red','cyan','black','white','*straw*']
hitstats=[0 for n in range(len(colori))]
scorepoints=[16,8,4,2,1,0]
gundown=True
shootingdistance=0
score=0
lasthit=''
shotsmade=0
shootingpower=110.
windforce=Vec3(0,0,0)

#** returns 2d the distance from the origin to an x,y point
def calcdist(x,y): return math.sqrt(math.pow(x,2)+math.pow(y,2))

#** just an helper function - never mind
def acce(k,h,p):
  snipstuff.DO.accept(k, h, p)
  snipstuff.DO.accept(k+'-repeat', h, p)

#** return a human readable wind situation
def strwind(w):
  s="S" if w[1] < 1. else "N" if w[1] > 1. else ''
  s+="W" if w[0] < 1. else "E" if w[0] > 1. else ''
  return "%s @ %0.1f knots"%(s, abs(max(w)))

#** game info show
def refreshinfos():
  global lasthit, score, shootingdistance, shootingpower, windforce

  snipstuff.infotext["message"].setText(
    ("Dist: %0.1fmt Pow: %0.3f\nWind:%s\n"%(
      shootingdistance/10., shootingpower, strwind([windforce[0],windforce[1]])
    )+
    ("Last hit: %s Score: %d"%(lasthit, score))
  )
)

#** return the index of hitpoints to know which colorband the hitpoint cpos is in
def targethitindex(cpos):
  v=calcdist(cpos[0], cpos[2])
  for i in range(len(hitpoints)):
    if v < hitpoints[i]: return i
  return len(hitpoints)-1

#** Checking the target for frowneys hits - remember the frowney bullets are always FROM colliders
def shootHitCheck(entry):
  global gundown, lasthit, score, shotsmade

  def removebullet(bullet): bullet.removeNode()

  np_from=entry.getFromNodePath()
  np_into=entry.getIntoNodePath()

  # remove the bullet (FROM entry object) off the collision system to save fps
  base.physicsMgr.removePhysicalNode(np_from.getParent().node())
  np_from.getParent().setCollideMask(BitMask32.allOff())
  base.cTrav.removeCollider(np_from)

  if np_into.getName() == 'targetcollide':
    cpos=entry.getContactPos(np_into)
    hitindex=targethitindex(cpos)
    lasthit=colori[hitindex]
    score+=scorepoints[hitindex]
    hitstats[hitindex]+=1
    # ok, the player may shoot now
    gundown=False
  else:
    lasthit="*miss*"
    # we remove the bullet to save fps - Note: we may call getAncesto(1) cos we know that the bullet's ancestor is render and then come the topmost bullet node.
    taskMgr.doMethodLater(
      2, removebullet, "tsk_rmvb%d"%id(np_from),
      extraArgs=[np_from.getAncestor(1)]
    )
    # ok, the player may shoot now
    gundown=False
  # each 3 shots we pull back the player
  if (shotsmade % 3) == 0:
    # dude, put the gun down until I tell you otherwise
    gundown=True
    snipstuff.infotext["content"].setText("Changing position:\nstanby just a second...")
    taskMgr.doMethodLater(3, nextshootingpos, "tsk_nsp")
snipstuff.DO.accept('frowneycnode-into-everything', shootHitCheck)

#** Let the next shootout session begins: the player is pulled back and the wind changes a bit...
def nextshootingpos(task=None):
  global colori, hitstats, gundown, shootingdistance, shotsmade, windforce

  shootingdistance+=40
  if shootingdistance <= 400:
    smiley.setY(-shootingdistance)
    base.cam.setY(smiley.getY()-20)
    # we set here the wind force specifying the vector of the globalforcesWind force object settled above of XY values to have an horizontal maximum wind force of 'Gentle Breeze', about 10 knots
    wf=10
    windforce=Vec3(random.uniform(-wf, wf), random.uniform(-wf, wf), 0)
    globalforcesWind.setVector(windforce)
    snipstuff.infotext["content"].setText("Ready.")
    gundown=False
  else:
    # ...unless the maximum distance is reached, therefore we end the shootout showing the result statistics.
    taskMgr.remove("tsk_setpow")
    snipstuff.infotext["content"].setText("Session ended.")
    snipstuff.infotext["message"].setText(
      ("* GAME RESULTS *\n")+
      ("Your score: %d\n"%(score))+
      ("'\n'".join(
          ["%s:%02d"%(colori[i], hitstats[i]) for i in range(len(colori))]
        )
      )+
      ("\nHits: %d Misses: %d"%(sum(hitstats), shotsmade-sum(hitstats)))
    )
    snipstuff.infotext["message"].setAlign(TextNode.ACenter)
    snipstuff.infotext["message"].setPos(0,.4)
  if task: return task.done

#** here we put a little spice to the game: will be randomly changed the power impulse force of the bullet - showing out to the gui nonetheless - to make the game a little less predictable.
def setpower(task):
  global shootingpower

  shootingpower=random.uniform(130., 160.)
  refreshinfos()
  return task.again
taskMgr.doMethodLater(.7, setpower, "tsk_setpow")

#** The shooting routine: a bullet ball with capabilities to interact with the physics setup will be made using our ball dispenser defined well above - then will be placed at the noozle exit extremity, and at last shooted applying it an impulse toward the Y axis.
def shoot():
  global gundown, shotsmade

  if gundown: return
  bullet=phyball_dispenser('frowney', .2)
  bullet.setPos(nozzleexit.getPos(base.render))
  bullet.setHpr(nozzleexit.getHpr(base.render))
  v=Vec3(0, shootingpower, 0)
  bullet.node().getChild(0).getPhysicsObject().addImpulse(v)
  #snipstuff.infotext["message"].setText("Bulletshoot :%r"%bullet.getHpr())
  shotsmade+=1
  # wait to shoot again - will be reset by other routines when it's time
  gundown=True
snipstuff.DO.accept('enter', shoot)

#** aiming smiley
def smileyaim(hpr):
  smiley.setHpr(smiley.getHpr()+hpr)
aimspd=.2
acce('arrow_up', smileyaim, [Point3(0,-aimspd,0)])
acce('arrow_down', smileyaim, [Point3(0,aimspd,0)])
acce('arrow_left', smileyaim, [Point3(aimspd,0,0)])
acce('arrow_right', smileyaim, [Point3(-aimspd,0,0)])
acce('w', smileyaim, [Point3(0,-aimspd,0)])
acce('s', smileyaim, [Point3(0,aimspd,0)])
acce('a', smileyaim, [Point3(aimspd,0,0)])
acce('d', smileyaim, [Point3(-aimspd,0,0)])

#** this is to show how an hipothetic raygun (we use the lasersight_ray defined above) should work and how to tap the hitting coordinates of the INTO objet. This function is called by our alternate collision handler coupled with the lasersight ray collider.
prexy=[0,0]
def raygun_again(entry):
  global prexy
  np_into=entry.getIntoNodePath()
  sup=entry.getSurfacePoint(np_into)
  curxy=[sup[0], sup[2]]
  if curxy <> prexy:
    prexy=curxy
    snipstuff.infotext["content"].setText(
      "Raygun @ %r\nNormal: %r"%(
        entry.getSurfacePoint(np_into), entry.getSurfaceNormal(np_into)
      )
    )

#** to toggle the lasersight_ray coordinate reporting
_raygun_again=False
def toggle_raygun_again():
  global _raygun_again
  _raygun_again=not _raygun_again
  if _raygun_again:
    snipstuff.DO.accept('lasersight_ray-again-targetcollide', raygun_again)
  else:
    snipstuff.DO.ignore('lasersight_ray-again-targetcollide')
    snipstuff.infotext["message"].setText('')
snipstuff.DO.accept('r', toggle_raygun_again)

#** let's create a smiley but without phisics involving
smiley=loader.loadModel('smiley')
smiley.reparentTo(base.render)
nozzlemodel.reparentTo(smiley)
nozzlemodel.setPos(-1, 1, 1)
smiley.setH(180)
nextshootingpos()

#** let's start the show
splash.destroy()

run()
