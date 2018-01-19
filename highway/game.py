from __future__ import division, print_function
import pygame
from vehicle import Vehicle, ControlledVehicle, MDPVehicle
from road import Road, RoadSurface
from mdp import RoadMDP, SimplifiedMDP
import numpy as np
import os

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
FPS = 30
POLICY_FREQUENCY = 1
dt = 1/FPS

RECORD_VIDEO = False

def main():
    road = Road.create_random_road(4, 4.0, 50)
    vehicle = road.random_mdp_vehicle(25, ego=True)
    # road = Road.create_obstacles_road(4, 4.0)
    # vehicle = Vehicle([-20, road.get_lateral_position(0)], 0, 25, ego=True)
    # vehicle = ControlledVehicle.create_from(vehicle, road)
    road.vehicles.append(vehicle)

    t = 0
    done = False
    pause = False
    pygame.init()
    pygame.display.set_caption("Highway")
    clock = pygame.time.Clock()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    sim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT/2))
    sim_surface = RoadSurface(sim_surface. get_size(), 0, sim_surface)
    value_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT/2))

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause = not pause
            vehicle.handle_event(event)

        if not pause:
            if t % (FPS//POLICY_FREQUENCY) == 0:
                mdp = RoadMDP(road, vehicle)
                smdp = SimplifiedMDP(mdp.state)
                smdp.value_iteration()
                print(mdp.state)
                print(smdp.value)

                _, actions = smdp.plan()
                trajectory = vehicle.predict_trajectory(actions, mdp.TIME_QUANTIFICATION, 8*dt, dt)
                print(actions)

                action = smdp.pick_action()
                print(action)

                vehicle.perform_action(action)
                # pause = True
            road.step(dt)


        road.move_display_window(sim_surface)
        road.display_road(sim_surface)
        vehicle.display_trajectory(sim_surface, trajectory)
        road.display_traffic(sim_surface)
        smdp.display(value_surface)
        screen.blit(sim_surface, (0,0))
        screen.blit(value_surface, (0,SCREEN_HEIGHT/2))
        clock.tick(FPS)
        pygame.display.flip()
        t = t+1

        if RECORD_VIDEO:
            pygame.image.save(screen, "out/highway_{}.bmp".format(t))
            if vehicle.position[0] > np.max([o.position[0] for o in road.vehicles if o is not vehicle])+25:
                os.system("ffmpeg -road 60 -i out/highway_%d.bmp -vcodec libx264 -crf 25 out/highway.avi")
                os.system("rm out/*.bmp")
                done = True

    # Close everything down
    pygame.quit()

if __name__ == '__main__':
    main()