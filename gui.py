import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Pygame Test")
    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                print(event.key)
        pygame.display.flip()
        clock.tick(60)