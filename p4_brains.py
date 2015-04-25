
import random

# EXAMPLE STATE MACHINE
class MantisBrain:

  def __init__(self, body):
    self.body = body
    self.state = 'idle'
    self.target = None

  def handle_event(self, message, details):

    if self.state is 'idle':

      if message == 'timer':
        # go to a random point, wake up sometime in the next 10 seconds
        world = self.body.world
        x, y = random.random()*world.width, random.random()*world.height
        self.body.go_to((x,y))
        self.body.set_alarm(random.random()*10)

      elif message == 'collide' and details['what'] == 'Slug':
        # a slug bumped into us; get curious
        self.state = 'curious'
        self.body.set_alarm(1) # think about this for a sec
        self.body.stop()
        self.target = details['who']

    elif self.state == 'curious':

      if message == 'timer':
        # chase down that slug who bumped into us
        if self.target:
          if random.random() < 0.5:
            self.body.stop()
            self.state = 'idle'
          else:
            self.body.follow(self.target)
          self.body.set_alarm(1)
      elif message == 'collide' and details['what'] == 'Slug':
        # we meet again!
        slug = details['who']
        slug.amount -= 0.01 # take a tiny little bite
    
class SlugBrain:

    def __init__(self, body):
        self.body = body
        self.state = 'idle'

    def follow_nearest_mantis(self):
        self.body.follow(self.body.find_nearest('Mantis'))


    def handle_event(self, message, details):
        if message == 'order':
            if isinstance(details, tuple):
                print("go over there!")
                self.state = 'move'
                self.body.go_to(details)
            elif isinstance(details, str):
                if details == 'i':
                    self.state = 'idle'
                    self.body.stop()
                    print("stopped!")
                if details == 'a':
                    print("attack!")
                    self.state = 'attack'
                    self.follow_nearest_mantis()
                    self.body.set_alarm(2)
        elif message == 'collide':
            print("collision!")
            if self.state == 'attack':
                if details['what'] == 'Mantis':
                    details['who'].amount -= 0.05
        elif message == 'timer':
            print("alarm going off!")
            if self.state == 'attack':
                self.follow_nearest_mantis()
                self.body.set_alarm(2)


world_specification = {
  'worldgen_seed': 13, # comment-out to randomize
  'nests': 2,
  'obstacles': 25,
  'resources': 5,
  'slugs': 5,
  'mantises': 5,
}

brain_classes = {
  'mantis': MantisBrain,
  'slug': SlugBrain,
}
