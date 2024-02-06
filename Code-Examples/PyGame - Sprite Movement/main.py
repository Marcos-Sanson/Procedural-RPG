import pygame
import asyncio


async def main():

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((1280, 720))
    image = pygame.image.load('image.png')
    delta = 5
    x = y = 0

    while True:

        # Needed to handle window-based quite events (non-pygbag runs)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Check if keys are _currently_ pressed down
        print("Keys:")
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            print("\tLeft!")
            x -= delta
        if keys[pygame.K_RIGHT]:
            print("\tRight!")
            x += delta
        if keys[pygame.K_UP]:
            print("\tUp!")
            y -= delta
        if keys[pygame.K_DOWN]:
            print("\tDown!")
            y += delta
        if keys[pygame.K_q]:
            print("\tQuit!")
            return

        screen.blit(image, (x, y))
        pygame.display.update()
        screen.fill("black")

        clock.tick(60)  # wait until next frame (at 60 FPS)
        await asyncio.sleep(0)  # Very important, and keep it 0

asyncio.run(main())
# Do not add anything from here
# asyncio.run is non-blocking on pygame-wasm