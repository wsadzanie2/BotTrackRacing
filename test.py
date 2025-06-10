import main

run = True
car = main.Car()

def bot_moves():
    car.set_speed(100)
    for i in range(25):
        if car.will_hit_at(105, i):
            car.rotate_by(1)
            car.set_speed(10)
            return
        if car.will_hit_at(105, -i):
            car.rotate_by(-1)
            car.set_speed(10)
            return

while run:
    run = main.run()
    bot_moves()

