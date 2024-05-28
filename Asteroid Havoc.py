import pygame
import random
from sys import exit

# todo:
# power ups
# I only use mask colisions for the asteroid interactions since it seemed unnecesary for the other interactions

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((800, 700))
pygame.display.set_caption('Asteroid Havoc')
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 50)

Color_line = (255, 0, 0)
p1w_color = (255,0,0)
p2w_color = (0,0,255)

space_surface = pygame.image.load('graphics/bg5.jpg')
text_surface = test_font.render('Asteroid Havoc', False, 'Yellow')

p1w_text_surface = test_font.render('Player 1 Wins! Press "r" to restart', False, 'White')
p2w_text_surface = test_font.render('Player 2 Wins! Press "r" to restart', False, 'White')


#sounds
laser_sound = pygame.mixer.Sound('graphics/laser1.wav')

impact_sound = pygame.mixer.Sound('graphics/impact_sound.mp3')

powerup_sound = pygame.mixer.Sound ('graphics/8_BIT_[50_SFX]_Powerup_Free_Sound_Effects_N1_BY_jalastram/SFX_Powerup_01.wav')

bg_music = pygame.mixer.Sound('graphics/Orbital Colossus.mp3')


# (this image originally faces right)
ufo_surface = pygame.image.load('graphics/Animated-UFO-by-MillionthVector/alien10008.png')

#using a ufo mask for more accurate collsions with asteroid
ufo_mask = pygame.mask.from_surface(ufo_surface)

ufo_surface_left = pygame.image.load('graphics/Animated-UFO-by-MillionthVector/alien10001.png')

ufo_surface_up = pygame.image.load('graphics/Animated-UFO-by-MillionthVector/alien10004.png')
ufo_surface_down = pygame.image.load('graphics/Animated-UFO-by-MillionthVector/alien10011.png')
ufo_rect = ufo_surface.get_rect(midbottom=(400, 200))




# (this image originally faces right)
spaceship_surface_raw = pygame.image.load('graphics/TurningShip1-by-MillionthVector/redfighter0009.png')
spaceship_surface = pygame.transform.scale(spaceship_surface_raw, (90, 90))

#using a spaceship mask for more accurate collsions with asteroid
spaceship_mask = pygame.mask.from_surface(spaceship_surface)

spaceship_surface_up_down_raw = pygame.image.load('graphics/TurningShip1-by-MillionthVector/redfighter0005.png')
spaceship_surface_up_down = pygame.transform.scale(spaceship_surface_up_down_raw, (90, 90))

spaceship_surface_left_raw = pygame.image.load('graphics/TurningShip1-by-MillionthVector/redfighter0001.png')
spaceship_surface_left = pygame.transform.scale(spaceship_surface_left_raw, (90, 90))

spaceship_rect = spaceship_surface_up_down.get_rect(midbottom=(400, 600))

spaceship_surface_to_blit = spaceship_surface_up_down
ufo_surface_to_blit = ufo_surface_down

#impact surface
impact_surface_raw = pygame.image.load('graphics/explosion1_package/package/png frames/64x48/explosion1_0016.png')
impact_surface = pygame.transform.scale(impact_surface_raw, (100, 100))

#asteroid surfaces
asteroid_list = []

temp_asteroid_surf = pygame.image.load("graphics/asteroids/Asteroid_1.png") #using this surface for the rect
asteroid_rect = temp_asteroid_surf.get_rect(midbottom = (0,350))

#only used for player colisions
asteroid_mask = pygame.mask.from_surface(temp_asteroid_surf)


#filling up list of surfaces to animate
for i in range(1, 5): 
    image = pygame.image.load(f"graphics/asteroids/Asteroid_{i}.png")
    image_rect = image.get_rect(center=(0, 350))
    asteroid_list.append(image)


#powerup star
powerup_list = []

temp_powerup_surf_raw = pygame.image.load(("graphics/star/1.png"))
temp_powerup_surf = pygame.transform.scale(temp_powerup_surf_raw, (90,90))
powerup_rect = temp_powerup_surf.get_rect(bottomright = (0,0)) #spawning the star outside of the screen

#only used for player colisions:
powerup_mask = pygame.mask.from_surface(temp_powerup_surf)

for i in range(1,4):
    surface_raw = pygame.image.load(f"graphics/star/{i}.png")
    surface = pygame.transform.scale(surface_raw, (90,90))
    surface_rect = surface.get_rect(bottomright=(0,0))

    powerup_list.append(surface)



#ufo lasers
ufo_laser_surface=pygame.image.load('graphics/blue_laser.png')

#spaceship lasers
spaceship_laser_surface=pygame.image.load('graphics/red_laser.png')


#adjust speed here
ufo_speed = 4
spaceship_speed = 4

#keeping track of speed in x and y directions 
ufo_dx = 0
ufo_dy = 0
spaceship_dx = 0
spaceship_dy = 0

#store lasers
spaceship_lasers = []
ufo_lasers = []

#cooldown for shooting
spaceship_cooldown = 0
ufo_cooldown = 0



ufo_health = 5
spaceship_health= 5

#keeps track of how many frames have passed
frame_index = 0 #the frame we are on determines what image will be shown
asteroid_last_update = pygame.time.get_ticks() #time (in milliseconds) when the asteroid animation was last updated

powerup_frame_index = 0 #using same method for star animation

game_paused = False

spaceship_powerup_timer = 0
ufo_powerup_timer = 0
powerup_last_update = pygame.time.get_ticks() #used for animation 
powerup_last_spawn = pygame.time.get_ticks() #used for spawning at the right time

ufo_powered_up = None
spaceship_powered_up = None

pygame.mixer.Sound.play(bg_music)
def restart_game():
    global ufo_health, spaceship_health, game_paused
    ufo_health = 5
    spaceship_health = 5
    asteroid_rect.bottom = random.randint(0, 700)
    asteroid_rect.right = 0
    spaceship_rect.midbottom = (400, 600)
    ufo_rect.midbottom = (400, 200)
    spaceship_lasers.clear()
    ufo_lasers.clear()
    pygame.mixer.Sound.play(bg_music)
    
    game_paused = False



def ai_control():
    global ufo_dx, ufo_dy, ufo_surface_to_blit, ufo_cooldown

    #initial y position of the UFO, i want the ufo to prefer staying in the center. It looks better
    initial_y = 200
    ufo_x, ufo_y = ufo_rect.center #we want the center values of the ufo

    #avoiding asteroids automatically
    if asteroid_rect.colliderect(ufo_rect.inflate(100, 100)): #if the asteroid nears the ufo, move accordingly on the x and y axis
        if ufo_rect.centery < asteroid_rect.centery:
            ufo_dy = -ufo_speed
        else:
            ufo_dy = ufo_speed
        if ufo_rect.centerx < asteroid_rect.centerx:
            ufo_dx = -ufo_speed
        else:
            ufo_dx = ufo_speed
    else:
        #reset movement to avoid confusion
        ufo_dy = 0
        ufo_dx = 0

        #move towards the power-up star if it is on screen
        if powerup_rect.right > 0 and powerup_rect.left < 800:
            target_x, target_y = powerup_rect.center #designate target
        else:
            #make the spaceship the target if no stars or asteroids are nearby
            target_x = spaceship_rect.centerx

            #return to initial Y position
            target_y = initial_y

        #move towards the targets that are determined automatically
        if target_x > ufo_x + 55:  #adding a slight delay so it is easier to evade the ufo
            ufo_dx = ufo_speed
            ufo_surface_to_blit = ufo_surface
        elif target_x < ufo_x - 55:
            ufo_dx = -ufo_speed
            ufo_surface_to_blit = ufo_surface_left

        #move towards the targets that are determined automatically
        if target_y > ufo_y:
            ufo_dy = ufo_speed
            ufo_surface_to_blit = ufo_surface_down
        elif target_y < ufo_y:
            ufo_dy = -ufo_speed
            ufo_surface_to_blit = ufo_surface_up

    #The ufo shoots constantly, it would have been complicated otherwise
    if ufo_cooldown <= 0:
        pygame.mixer.Sound.play(laser_sound)
        new_ufo_laser = ufo_laser_surface.get_rect(midbottom=ufo_rect.midbottom)
        ufo_lasers.append(new_ufo_laser)
        ufo_cooldown = 60




game_mode = None
menu_running = None
music_stopped = None

def main_menu():
    global game_mode, menu_running, game_paused, music_stopped
    menu_running = True
    music_stopped = False

    while menu_running:
        screen.fill((0, 0, 0))
        title_surface = test_font.render('Asteroid Havoc', False, 'Yellow')
        mode1_surface = test_font.render('1. 2 Player Mode', False, 'White')
        mode2_surface = test_font.render('2. VS AI Mode', False, 'White')
        mute_surface = test_font.render('M. Mute', False, 'White')
        quit_surface = test_font.render('Q. Quit Game', False, 'White')
        screen.blit(title_surface, (250, 100))
        screen.blit(mode1_surface, (250, 300))
        screen.blit(mode2_surface, (250, 400))
        screen.blit(mute_surface, (250, 500))
        screen.blit(quit_surface, (250, 600))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_mode = '2_player'
                    menu_running = False
                    game_paused = False
                if event.key == pygame.K_2:
                    game_mode = 'vs_ai'
                    menu_running = False
                    game_paused = False

                if event.key == pygame.K_m:
                    music_stopped = not music_stopped
                    if music_stopped:
                        pygame.mixer.pause()
                    else:
                        pygame.mixer.unpause()



                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                


main_menu()


while True:
    screen.blit(space_surface, (0, 0))
    screen.blit(text_surface, (300, 50))
    
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        #pausing with escape
        if event.type == pygame.KEYDOWN:
            
            
            if event.key == pygame.K_ESCAPE:
                game_paused = not game_paused
                main_menu()

            #movement and blitting images
            if game_paused == False:
                if event.key == pygame.K_w:
                    spaceship_surface_to_blit=spaceship_surface_up_down
                    spaceship_dy = -spaceship_speed
                elif event.key == pygame.K_s:
                    spaceship_surface_to_blit=spaceship_surface_up_down
                    spaceship_dy = spaceship_speed
                elif event.key == pygame.K_a:
                    spaceship_surface_to_blit=spaceship_surface_left
                    spaceship_dx = -spaceship_speed
                elif event.key == pygame.K_d:
                    spaceship_surface_to_blit = spaceship_surface
                    spaceship_dx = spaceship_speed
                
                elif event.key == pygame.K_SPACE:
                    #code for blitting spaceship laser
                    if spaceship_cooldown<=0:
                        pygame.mixer.Sound.play(laser_sound)
                        new_laser = spaceship_laser_surface.get_rect(midtop=spaceship_rect.midtop) #add a new laser to the list every time space is pressed
                        spaceship_lasers.append(new_laser)
                        spaceship_cooldown = 60

                elif event.key == pygame.K_UP:
                    ufo_surface_to_blit = ufo_surface_up
                    ufo_dy = -ufo_speed
                elif event.key == pygame.K_DOWN:
                    ufo_surface_to_blit = ufo_surface_down
                    ufo_dy = ufo_speed
                elif event.key == pygame.K_LEFT:
                    ufo_surface_to_blit = ufo_surface_left
                    ufo_dx = -ufo_speed
                elif event.key == pygame.K_RIGHT:
                    ufo_surface_to_blit = ufo_surface
                    ufo_dx = ufo_speed
                
                elif event.key==pygame.K_RETURN:
                    #code for blitting ufo laser
                    if ufo_cooldown<=0:
                        pygame.mixer.Sound.play(laser_sound)
                        new_ufo_laser = ufo_laser_surface.get_rect(midbottom = ufo_rect.midbottom)
                        ufo_lasers.append(new_ufo_laser)
                        ufo_cooldown = 60
            

        #Key releases and blitting default image when no key is held
        if event.type == pygame.KEYUP and game_paused == False:
            if event.key == pygame.K_w or event.key == pygame.K_s:
                spaceship_dy = 0
                if spaceship_dx == 0: #if spaceship is not moving on the x or y axis
                    spaceship_surface_to_blit = spaceship_surface_up_down
            elif event.key == pygame.K_a or event.key == pygame.K_d:
                spaceship_dx = 0
                if spaceship_dy == 0:
                    spaceship_surface_to_blit = spaceship_surface_up_down
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                ufo_dy = 0
                if ufo_dx == 0:
                    ufo_surface_to_blit = ufo_surface_down
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                ufo_dx = 0
                if ufo_dy == 0:
                    ufo_surface_to_blit = ufo_surface_down



    

    #Updating ufo and spaceship position
    ufo_rect.x += ufo_dx
    ufo_rect.y += ufo_dy
    spaceship_rect.x += spaceship_dx
    spaceship_rect.y += spaceship_dy

    #restrict movement
    if ufo_rect.top <=0:
        ufo_rect.top =0
    if ufo_rect.bottom >=350:
        ufo_rect.bottom = 350
    if ufo_rect.right >=800:
        ufo_rect.right = 800
    if ufo_rect.left <=0:
        ufo_rect.left = 0


    if spaceship_rect.right >=800:
        spaceship_rect.right = 800
    if spaceship_rect.left <=0:
        spaceship_rect.left = 0
    if spaceship_rect.top <=350:
        spaceship_rect.top = 350
    if spaceship_rect.bottom >= 700:
        spaceship_rect.bottom = 700



    #decreease laser cooldown
    spaceship_cooldown -= 2
    ufo_cooldown -= 2


    screen.blit(ufo_surface_to_blit, ufo_rect)
    screen.blit(spaceship_surface_to_blit, spaceship_rect)



    ufo_health_surface = test_font.render(str(ufo_health), False, 'Green')
    spaceship_health_surface = test_font.render(str(spaceship_health), False, 'Green')


    ufo_display_cooldown = ufo_cooldown
    spaceship_display_cooldown = spaceship_cooldown
    if ufo_cooldown < 0:
        ufo_display_cooldown = 0
    if spaceship_cooldown < 0:
        spaceship_display_cooldown = 0
    ufo_cooldown_surface = test_font.render(str(ufo_display_cooldown), False, 'Red')
    spaceship_cooldown_surface = test_font.render(str(spaceship_display_cooldown), False, 'Red')

    screen.blit(ufo_health_surface, ufo_rect.midtop)
    screen.blit(spaceship_health_surface, spaceship_rect.midtop)
    
    pygame.draw.line(screen, Color_line, (0, 350), (800, 350), 4)
########################################################################################################################################################################################################################################################################
    #pause the game if someone loses
    if spaceship_health <= 0 or ufo_health <= 0:
        laser_sound.stop() #fixes sound bug
        impact_sound.stop() #fixes sound bug
        bg_music.stop()
        game_paused = True

    #if the game is paused and r is pressed, restart
    keys = pygame.key.get_pressed()
    if game_paused and keys[pygame.K_r]:
        restart_game() 

    #displaying game over screen when someone loses
    if spaceship_health <= 0:
        spaceship_health = 0
        screen.fill((0,0,0))
        pygame.draw.line(screen, p2w_color, (100, 350), (700, 350), 600)
        screen.blit(p2w_text_surface, p2w_text_surface.get_rect(center = screen.get_rect().center)) #<3 stack overflow

    #displaying game over screen when someone loses
    if ufo_health <=0:
        ufo_health = 0
        screen.fill((0,0,0))
        pygame.draw.line(screen, p1w_color, (100, 350), (700, 350), 600)
        screen.blit(p1w_text_surface, p1w_text_surface.get_rect(center = screen.get_rect().center))


    if game_paused:
        pygame.display.flip() #update the screen so game over screen is shown
        continue #pause
########################################################################################################################################################################################################################################################################

    #slowed down animation
    current_time = pygame.time.get_ticks()
    if current_time - asteroid_last_update > 100: #if the difference is more than 100 ticks
        frame_index = (frame_index + 1) % len(asteroid_list) #start over at zero if we reach the end of the list
        asteroid_last_update = current_time #updating the time the asteroid was updated 


    #dealing with asteroid movement
    asteroid_rect.right += 8

    #Check if asteroid has moved off the screen
    if asteroid_rect.left >= 800:
        asteroid_rect.y = random.randint(0, 700)
        asteroid_rect.right = 0

    #only change the image of the surface, do not mess with the rectangle
    screen.blit(asteroid_list[frame_index], asteroid_rect)

    #asteroid colissions
    if asteroid_mask.overlap(ufo_mask, (ufo_rect.x - asteroid_rect.x, ufo_rect.y - asteroid_rect.y)):

        ufo_health = 0

    if asteroid_mask.overlap(ufo_mask, (spaceship_rect.x - asteroid_rect.x, spaceship_rect.y - asteroid_rect.y)):

        spaceship_health = 0
########################################################################################################################################################################################################################################################################
    #animation of star
    if current_time - powerup_last_update>200:
        powerup_frame_index = (powerup_frame_index + 1) % len(powerup_list) #start over at zero if we reach the end of the list
        powerup_last_update = current_time #updating the time the powerup was updated
    
    
    screen.blit(powerup_list[powerup_frame_index], powerup_rect)

    if powerup_mask.overlap(spaceship_mask, (spaceship_rect.x - powerup_rect.x, spaceship_rect.y - powerup_rect.y)):
        pygame.mixer.Sound.play(powerup_sound)
        #fire rate
        spaceship_cooldown = 30  #faster cooldown time
        spaceship_powerup_timer = 250 
        powerup_rect.left = 800 #hide star when picked up
       
        spaceship_powered_up = True

    if powerup_mask.overlap(ufo_mask, (ufo_rect.x - powerup_rect.x, ufo_rect.y - powerup_rect.y)):
        pygame.mixer.Sound.play(powerup_sound)
        ufo_cooldown = 30
        ufo_powerup_timer = 250
        powerup_rect.left = 800

        ufo_powered_up = True


    #making powerup appear every 10 seconds
    powerup_rect.right +=12
    if powerup_rect.left>=800 or ufo_powered_up or spaceship_powered_up:
        if current_time - powerup_last_spawn > 12000: #if 10 seconds have passed since it last appeared on screen
            powerup_rect.y = random.randint(0,700)
            powerup_rect.right = 0
            powerup_last_spawn = current_time

    #dealing with how long the powerup lasts for
    if spaceship_powerup_timer > 0:
        spaceship_cooldown -= 4
        spaceship_powerup_timer -= 1


    if ufo_powerup_timer > 0:
        ufo_cooldown -= 4
        ufo_powerup_timer -=1


    



    


########################################################################################################################################################################################################################################################################

    for laser in spaceship_lasers:
        laser.top -= 10 #move every laser that exists upwards
        screen.blit(spaceship_laser_surface, laser) #and blit all lasers #laser is a rect so this works

        if laser.top <= 0:
            spaceship_lasers.remove(laser)

        if laser.colliderect(ufo_rect): 
            pygame.mixer.Sound.play(impact_sound)
            spaceship_lasers.remove(laser)
            ufo_health-=1
            
            screen.blit(impact_surface, ufo_rect.topleft)
        
        if laser.colliderect(asteroid_rect):
            pygame.mixer.Sound.play(impact_sound)
            
            spaceship_lasers.remove(laser)
            screen.blit(impact_surface, asteroid_rect.topleft)
    
    for ufo_laser in ufo_lasers:
        ufo_laser.bottom +=10
        screen.blit(ufo_laser_surface, ufo_laser)

        if ufo_laser.bottom>=700:
            ufo_lasers.remove(ufo_laser)

        if ufo_laser.colliderect(spaceship_rect):
            pygame.mixer.Sound.play(impact_sound)
            ufo_lasers.remove(ufo_laser)
            spaceship_health-=1  

            screen.blit(impact_surface, spaceship_rect.topleft)

        if ufo_laser.colliderect(asteroid_rect):
            pygame.mixer.Sound.play(impact_sound)

            ufo_lasers.remove(ufo_laser)
            screen.blit(impact_surface, asteroid_rect.topleft)

    


    screen.blit(ufo_cooldown_surface, ufo_rect.midbottom)
    screen.blit(spaceship_cooldown_surface, spaceship_rect.midbottom)
    
    
    if menu_running == True:
        main_menu()

    if game_mode == 'vs_ai':
        ai_control()

    pygame.display.flip()
    clock.tick(60)