class Classtime:

    def __init__(self,course,room):
        self.course = course
        self.room = room
        

    def __str__(self):
        return f"({self.course}-{self.room})"
        # return f"({self.room})"
        # return f"Course: {self.course}, Room: {self.room}"

    def copy(self):
        return Classtime(self.course,self.room) 
    
        