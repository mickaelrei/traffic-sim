import pygame

# Abstract class representing a pygame app


class PygameApp:
    def __init__(
            self,
            width: int,
            height: int,
            fps: float = 60,
    ) -> None:
        assert width > 0 and height > 0, "Window dimensions must be positive"

        # Check if needs to initialize pygame
        if not pygame.get_init():
            pygame.init()

        # Window width
        self.width = width

        # Window height
        self.height = height

        # Window object
        self.window = pygame.display.set_mode((self.width, self.height))

        # Clock object, for rendering based on fps
        self.clock = pygame.time.Clock()

        # App rendering fps
        self.fps = fps

        # Whether app is currently running
        self.running = True

        # App last tick, used for calculating delta time (dt)
        self.__lastTick = pygame.time.get_ticks()

    def onEvent(self, event: pygame.event.Event) -> None:
        pass

    def onUpdate(self, dt: float) -> None:
        pass

    def run(self) -> None:
        # Reassign window if needed
        if self.window == None:
            self.window = pygame.display.set_mode((self.width, self.height))

        # Start running
        self.running = True
        while self.running:
            # Calculate dt
            t = pygame.time.get_ticks()
            dt = (t - self.__lastTick) / 1000.0
            self.__lastTick = t
            # Handle events
            for event in pygame.event.get():
                # If press close window, stop program
                if event.type == pygame.QUIT:
                    self.running = False
                self.onEvent(event)

            # Call update
            self.onUpdate(dt)

            # Update display
            pygame.display.update()
            self.clock.tick(self.fps)

        # Exit pygame
        pygame.display.quit()
        self.window = None
