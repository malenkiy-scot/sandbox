class O(object):
  pass
  
class X(O):
  def b(self):
    print "X.b called"

  def c(self):
    print "X.c called"
    
  def d(self):
    print "X.d called"

class Y(O):
  def b(self):
    print "Y.b called"
  
  def c(self):
    print "Y.c called"

  def d(self):
    print "Y.d called"

class A(X,Y):
  def a(self):
    print "A.a called"
  
  def c(self):
    print "A.c called"
  
class B(Y,X):
  def a(self):
    print "B.a called"

  def b(self):
    print "B.b called"
    
#class C(A,B):
#  pass
