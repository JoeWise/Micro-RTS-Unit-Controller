
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
        self.have_resource = False

    def follow_nearest_mantis(self):
        try:
            self.body.follow(self.body.find_nearest('Mantis'))
        except:
            print('no more Mantises')
            self.idle()

    def go_to_nearest_nest(self):
        try:
            self.body.go_to(self.body.find_nearest('Nest'))
        except:
            print('no more Nests')
            self.idle()

    def go_to_nearest_resource(self):
        try:
            self.body.go_to(self.body.find_nearest('Resource'))
        except:
            print('no more Resources')
            self.idle()

    def move(self, coordinates):
        self.state = 'move'
        self.body.go_to(coordinates)

    def idle(self):
        self.state = 'idle'
        self.body.stop()

    def attack(self):
        self.state = 'attack'
        self.follow_nearest_mantis()
        self.body.set_alarm(2)

    def build(self):
        self.state = 'build'
        self.go_to_nearest_nest()
        self.body.set_alarm(2)

    def harvest(self):
        self.state = 'harvest'
        if self.have_resource:
            self.go_to_nearest_nest()
        else:
            self.go_to_nearest_resource()
        self.body.set_alarm(2)

    def flee(self):
        self.state = 'flee'
        self.go_to_nearest_nest()
        self.body.set_alarm(2)

    def handle_event(self, message, details):
        if message == 'order':
            # if the message is order and details is a tuple, then it's a move order
            if isinstance(details, tuple):
                self.move(details)
            # if the message is order and details is a string, then it's a key order
            elif isinstance(details, str):
                if details == 'i':
                    self.idle()
                elif details == 'a':
                    print("attack!")
                    self.attack()
                elif details == 'b':
                    self.build()
                elif details == 'h':
                    self.harvest()

        elif message == 'collide':
            # if we're attacking and colliding with a mantis, do damage to the mantis
            if self.state == 'attack':
                if details['what'] == 'Mantis':
                    details['who'].amount -= 0.05
            elif self.state == 'build':
                if details['what'] == 'Nest':
                    details['who'].amount += 0.01
            elif self.state == 'harvest':
                if details['what'] == 'Resource' and not self.have_resource:
                    details['who'].amount -= 0.25
                    self.have_resource = True
                elif details['what'] == 'Nest':
                    self.have_resource = False
            elif self.state == 'flee':
                if details['what'] == 'Nest':
                    self.body.amount = 1


        elif message == 'timer':
            # if an alarm goes off and we're attacking, it's to update which mantis we're following
            if self.state == 'attack':
                self.attack()
            elif self.state == 'build':
                self.build()
            elif self.state == 'harvest':
                self.harvest()

            if self.body.amount < 0.5:
                print('flee!')
                self.flee()

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
