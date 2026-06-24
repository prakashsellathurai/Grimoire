import turtle

# Create the screen and turtle objects
screen = turtle.Screen()
screen.bgcolor("lightblue")

pen = turtle.Turtle()
pen.color("blue")
pen.pensize(3)

# Draw a square by repeating a loop 4 times
for i in range(4):
    pen.forward(100)  # Move forward by 100 pixels
    pen.right(90)  # Turn 90 degrees to the right



# Keep the drawing window open
turtle.done()

