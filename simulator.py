import pygame
import os
import numpy as np
import sys
import time

# Motor power constants - use these with the motors() function
FORWARD = 1
BACKWARD = -1
STOP = 0

debug = False
mode = "obstacles"
frame = 0

def sin(degrees):
    return np.sin(np.radians(degrees))

def cos(degrees):
    return np.cos(np.radians(degrees))

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

def mm_to_px(mm):
    # Display zoom (pixels per mm)
    zoom = 0.5  # 0.5 pixels per mm means 1mm = 0.5 pixels
    return round(mm * zoom)

def add_border(surface, color=(0, 0, 0), thickness=3):
    """Add a border to a pygame surface"""
    width, height = surface.get_size()
    new_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    new_surface.blit(surface, (0, 0))
    pygame.draw.rect(new_surface, color, new_surface.get_rect(), thickness)
    return new_surface

class Robot:
    def __init__(self, use_simulator = True, n_obstacles = None, randomize_obstacles = None):
        if use_simulator:
            self.driver = SimulatorDriver(n_obstacles = n_obstacles, randomize_obstacles = randomize_obstacles)
        else:
            self.driver = RealRobotDriver()  # driver can be a simulator or real robot

    def motors(self, left, right, seconds):
        """Control the robot's wheels
        
        Parameters:
        * left: power for the LEFT wheel (use FORWARD, BACKWARD, or STOP)
        * right: power for the RIGHT wheel (use FORWARD, BACKWARD, or STOP)
        * seconds: how long to run the motors (can be a decimal like 0.5)
        
        Examples:
            # Go straight forward for 2 seconds
            robot.motors(left=FORWARD, right=FORWARD, seconds=2)
            
            # Go straight backward for 1 second
            robot.motors(left=BACKWARD, right=BACKWARD, seconds=1)
            
            # Spin left in place for 0.5 seconds
            robot.motors(left=BACKWARD, right=FORWARD, seconds=0.5)
            
            # Spin right in place for 0.5 seconds
            robot.motors(left=FORWARD, right=BACKWARD, seconds=0.5)
            
            # Stop both wheels
            robot.motors(left=STOP, right=STOP, seconds=0.1)
        """
        self.driver.motors(left, right, seconds)
    
    def left_sonar(self):
        """Read the distance from the left sonar sensor
        
        Returns: distance to the nearest object in centimeters (cm)
        
        Example:
            distance = robot.left_sonar()
            if distance < 10:
                print("Something is close on the left!")
        """
        return self.driver.left_sonar()
    
    def right_sonar(self):
        """Read the distance from the right sonar sensor
        
        Returns: distance to the nearest object in centimeters (cm)
        
        Example:
            distance = robot.right_sonar()
            if distance < 10:
                print("Something is close on the right!")
        """
        return self.driver.right_sonar()
    
    def exit(self):
        """Stop the simulator and close the window"""
        self.driver.exit()

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"(x={round(self.x)}, y={round(self.y)})"
    
    def to_vector(self):
        rho, phi = cart2pol(self.x, self.y)
        return Vector(rho, phi)
    
    def to_array(self):
        return np.array([self.x, self.y])
    
    def to_screen(self, screen):
        """Convert to screen coordinates for drawing"""
        screen_width, screen_height = screen.get_size()
        x_pixels = mm_to_px(self.x) + screen_width / 2
        y_pixels = mm_to_px(-self.y) + screen_height / 2
        return (int(x_pixels), int(y_pixels))
    
    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return np.sqrt(dx**2 + dy**2)
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

class Vector:
    def __init__(self, r, theta):
        self.r = r
        self.theta = theta
    
    def __repr__(self):
        return f"(r={round(self.r)}, theta={round(self.theta)})"
    
    def to_point(self):
        x = self.r * cos(self.theta)
        y = self.r * sin(self.theta)
        return Point(round(x), round(y))
    
    @classmethod
    def from_points(cls, p1, p2):
        """Create a vector from p1 to p2"""
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        rho, phi = cart2pol(dx, dy)
        return cls(rho, np.degrees(phi))
        

class Box:
    """Represents a rectangular box (robot or arena) with a center, size, and heading"""
    
    def __init__(self, center_x, center_y, width, height, heading=0):
        self.center = Point(center_x, center_y)
        self.width = width
        self.height = height
        self.heading = heading  # 0 for arena (axis-aligned)
    
    def corners(self):
        """Get the four corners of the box
        
        Returns: dict with keys 'front_right', 'front_left', 'back_left', 'back_right'
        """
        half_diagonal = np.sqrt(self.width**2 + self.height**2) / 2
        base_angle = np.degrees(np.arctan2(self.height, self.width))
        
        return {
            'front_right': self.center + Vector(half_diagonal, self.heading + 360 - base_angle).to_point(),
            'front_left': self.center + Vector(half_diagonal, self.heading + base_angle).to_point(),
            'back_left': self.center + Vector(half_diagonal, self.heading + 180 - base_angle).to_point(),
            'back_right': self.center + Vector(half_diagonal, self.heading + 180 + base_angle).to_point()
        }
    
    def front_edge(self):
        """Get the two front corners"""
        corners = self.corners()
        return corners['front_right'], corners['front_left']

class Obstacle:
    """Represents a rectangular obstacle in the arena"""
    
    def __init__(self, center_x, center_y, width, height, heading=0):
        self.box = Box(center_x, center_y, width, height, heading=heading)
        self.center = Point(center_x, center_y)
        self.width = width
        self.height = height
        self.heading = heading
    
    def corners(self):
        """Get the four corners of the obstacle"""
        return self.box.corners()
    
    def contains_point(self, point):
        """Check if a point is inside this obstacle"""
        # This needs to be updated for rotated boxes, but skip for now
        half_width = self.width / 2
        half_height = self.height / 2
        
        return (abs(point.x - self.center.x) < half_width and 
                abs(point.y - self.center.y) < half_height)

# Simulator Driver
class SimulatorDriver:
    def __init__(self, n_obstacles = 0, randomize_obstacles = False):
        print("simulator initializing...")
        if n_obstacles is None:
            n_obstacles = 0
        if randomize_obstacles is None:
            randomize_obstacles = False
        self.n_obstacles = n_obstacles
        self.randomize_obstacles = randomize_obstacles

        # Physics constants
        self.fps = 60
        self.degrees_per_frame = 0.98
        self.speed_per_power = 1

        # Robot dimensions (real world in mm)
        # actual robot pegboard is 20cm x 20cm with the wheels sticking out
        # another 1cm on each side
        self.robot_size = 200  # 20cm = 200mm
        self.robot_width = self.robot_size
        self.robot_height = self.robot_size
        self.sonar_inset = 30  # 3cm from corners
        
        # Arena dimensions (real world in mm)
        self.box_width = 2000   # 2m = 2000mm
        self.box_height = 1000  # 1m = 1000mm
        self.wall_thickness = 5
        self.padding = 10

        # Arena box (stationary)
        self.arena = Box(0, 0, self.box_width, self.box_height, heading=0)

        # Robot state
        self.origin = Point(0, 0)
        self.x = self.origin.x
        self.y = self.origin.y
        self.heading = 0  # degrees, 0 = pointing right

        self._calculate_box_boundaries()

        self.obstacle_specs = [
            {
                'width': 70,
                'height': 70, 
                'name': 'Square',
                'x': -300,
                'y': 180,
                'heading': 30
            },
            {
                'width': 100, 
                'height': 120, 
                'name': 'Short Rectangle',
                'x': 400,
                'y': 50,
                'heading': 0
            },
            {
                'width': 70,
                'height': 250,
                'name': 'Long Rectangle',
                'x': -100,
                'y': -170,
                'heading': 60
            },
        ]

        # Obstacles
        self.obstacles = []
        if self.n_obstacles > 0:
            self._generate_obstacles()

        # Graphics
        self.clock = pygame.time.Clock()
        self._load_images()
        self.start_simulation()

    def _get_robot_box(self):
        """Get the current robot as a Box"""
        return Box(self.x, self.y, self.robot_width, self.robot_height, self.heading)
    
    def _generate_obstacles(self):
        """Generate obstacles in the arena"""
        
        for i in range(min(self.n_obstacles, 5)):  # Max 5 obstacles
            spec = self.obstacle_specs[i]
            
            width = spec['width']
            height = spec['height']
            x, y = spec['x'], spec['y']
            heading = spec.get('heading', 0)  # Default to 0 if not specified
            
            obstacle = Obstacle(x, y, width, height, heading)
            self.obstacles.append(obstacle)
            print(f"Obstacle {i+1} ({spec['name']}): {width}x{height}mm at ({x}, {y}), rotated {heading}°")

    def _draw_obstacles(self):
        """Draw obstacles on the screen"""
        for i, obstacle in enumerate(self.obstacles):
            # Get obstacle corners
            corners = obstacle.corners()
            
            # Convert corners to screen coordinates
            corner_points = [
                corners['front_right'].to_screen(self.screen),
                corners['front_left'].to_screen(self.screen),
                corners['back_left'].to_screen(self.screen),
                corners['back_right'].to_screen(self.screen)
            ]
            
            # Draw filled rectangle
            pygame.draw.polygon(self.screen, (150, 75, 0), corner_points)  # Brown color
            
            # Draw border
            pygame.draw.polygon(self.screen, (0, 0, 0), corner_points, 2)  # Black border
            
            # Draw obstacle number (optional, for debugging)
            if debug:
                center_screen = obstacle.center.to_screen(self.screen)
                font = self.debug_font
                label = font.render(f"{i+1}", True, (255, 255, 255))
                self.screen.blit(label, (center_screen[0] - 5, center_screen[1] - 5))

    def _calculate_box_boundaries(self):
        self.max_x_box = self.box_width / 2 + self.origin.x
        self.min_x_box = self.origin.x - self.box_width / 2
        self.max_y_box = self.box_height / 2 + self.origin.y
        self.min_y_box = self.origin.y - self.box_height / 2

    def _draw_debug_info(self):
        """Draw coordinate labels for debugging"""
        if not debug:
            return
        
        font = self.debug_font
        
        # Robot center position
        center = Point(self.x, self.y)
        center_screen = center.to_screen(self.screen)
        
        center_text_world = font.render(f"mm: ({round(center.x)}, {round(center.y)})", True, (0, 255, 0))
        center_text_pixels = font.render(f"px: {center_screen}", True, (0, 255, 0))
        self.screen.blit(center_text_world, (center_screen[0] + 10, center_screen[1] + 10))
        self.screen.blit(center_text_pixels, (center_screen[0] + 10, center_screen[1] + 25))
        pygame.draw.circle(self.screen, (0, 255, 0), center_screen, 3)

        # Robot corners
        robot_box = self._get_robot_box()
        corners = robot_box.corners()
        
        for label, corner in corners.items():
            corner_screen = corner.to_screen(self.screen)
            pygame.draw.circle(self.screen, (0, 0, 255), corner_screen, 3)
            # Convert label from 'front_right' to 'FR'
            short_label = ''.join([word[0].upper() for word in label.split('_')])
            corner_text_world = font.render(f"{short_label} mm: ({round(corner.x)}, {round(corner.y)})", 
                                    True, (0, 0, 255))
            corner_text_pixels = font.render(f"px: {corner_screen}", 
                                    True, (0, 0, 255))
            self.screen.blit(corner_text_world, (corner_screen[0] + 5, corner_screen[1] - 30))
            self.screen.blit(corner_text_pixels, (corner_screen[0] + 5, corner_screen[1] - 15))
        
        # Origin point
        origin_screen = self.origin.to_screen(self.screen)
        pygame.draw.circle(self.screen, (255, 0, 0), origin_screen, 5)
        origin_text_world = font.render("Origin mm: (0, 0)", True, (255, 0, 0))
        origin_text_pixels = font.render(f"px: {origin_screen}", True, (255, 0, 0))
        self.screen.blit(origin_text_world, (origin_screen[0] + 10, origin_screen[1] + 10))
        self.screen.blit(origin_text_pixels, (origin_screen[0] + 10, origin_screen[1] + 25))
        
        # Arena corners
        arena_corners = self.arena.corners()
        
        for label, corner in arena_corners.items():
            corner_screen = corner.to_screen(self.screen)
            pygame.draw.circle(self.screen, (128, 0, 128), corner_screen, 5)
            # Convert label from 'front_right' to 'TR' (top right for arena)
            short_label = ''.join([word[0].upper() for word in label.split('_')])
            # For arena at heading=0, 'front' is 'top'
            short_label = short_label.replace('F', 'T').replace('B', 'B')
            
            arena_text_world = font.render(f"{short_label} mm: ({round(corner.x)}, ({round(corner.y)})", 
                                    True, (128, 0, 128))
            arena_text_pixels = font.render(f"px: {corner_screen}", 
                                    True, (128, 0, 128))
            offset_x = 10 if 'B' in short_label else -150
            offset_y = 10 if 'L' in short_label else -35
            self.screen.blit(arena_text_world, (corner_screen[0] + offset_x, corner_screen[1] + offset_y))
            self.screen.blit(arena_text_pixels, (corner_screen[0] + offset_x, corner_screen[1] + offset_y + 15))

    def _load_images(self):
        """Load and prepare robot images"""
        size = mm_to_px(self.robot_size)
        self.img_left = add_border(
            pygame.image.load(os.path.join('img', "left", f"{size}", 'robobunny.png')),
            color=(0, 0, 0),
            thickness=1
        )
        self.img_right = add_border(
            pygame.image.load(os.path.join('img', "right", f"{size}", 'robobunny.png')),
            color=(0, 0, 0),
            thickness=1
        )
        self.img = self.img_left

     
    def _detect_crash(self):
        """Check if robot has collided with arena boundaries"""
        robot_box = self._get_robot_box()
        corners = robot_box.corners()

        # Check if any robot corner is outside arena bounds
        for corner in corners.values():
            xcrash = corner.x > self.max_x_box or corner.x < self.min_x_box
            ycrash = corner.y > self.max_y_box or corner.y < self.min_y_box
            if xcrash or ycrash:
                return True
        return False

    def motors(self, left, right, seconds):
        """Apply power to motors for a duration"""
        num_frames = round(seconds * self.fps)
        
        for _ in range(num_frames):
            self._update_position(left, right)
            if self._detect_crash():
                if debug:
                    print("Crash!!!! Restarting!")
                    self.x = 0
                    self.y = 0
                    self.heading = 0
                else:
                    raise Exception(
                        "Ooops! Dr. Ebee doesn't know how to simulate what happens when you "
                        "hit the walls. Also, it's not good for the robot anyway. Try again!!"
                    )
            
            self.render()

    def _update_position(self, left, right):
        """Update robot position based on motor powers"""
        if left == right:
            if left != 0:
                # Move forward or backward
                speed = left * self.speed_per_power
                self.x += speed * cos(self.heading)
                self.y += speed * sin(self.heading)
        elif left == -right:
            if right == 1:
                # Rotate clockwise
                self.heading = (self.heading - self.degrees_per_frame) % 360
            else:
                # Rotate counter-clockwise
                self.heading = (self.heading + self.degrees_per_frame) % 360

        elif (left == 0 or right == 0) and (abs(left) == 1 or abs(right) == 1):
            # One wheel stopped, pivot around it
            # Pivoting is half the speed of spinning in place
            pivot_degrees_per_frame = self.degrees_per_frame / 2
            pivot_forward_per_frame = 0.208  # 75mm in 6 seconds = 12.5mm/sec = 0.208mm/frame
            
            if left == 0 and right != 0:
                # Pivot around left wheel
                direction = -1 if right == 1 else 1  # clockwise if right forward
                self.heading = (self.heading - direction * pivot_degrees_per_frame) % 360
                # Move forward in current heading direction
                self.x += right * pivot_forward_per_frame * cos(self.heading)
                self.y += right * pivot_forward_per_frame * sin(self.heading)
                
            elif right == 0 and left != 0:
                # Pivot around right wheel
                direction = 1 if left == 1 else -1  # counter-clockwise if left forward
                self.heading = (self.heading + direction * pivot_degrees_per_frame) % 360
                # Move forward in current heading direction
                self.x += left * pivot_forward_per_frame * cos(self.heading)
                self.y += left * pivot_forward_per_frame * sin(self.heading)
                
        else:
            raise Exception(
                "Ooops! Dr. Ebee didn't write code that let's you use those numbers as "
                "input to the `motors` function. If you *really* want those numbers, "
                "schedule some time on her calendar to help her implement that change!!"
            )
    
    def dist_to_box(self, sonar_position, h):
        """Calculate distance from sonar position to nearest wall in direction h"""
        # Distances to walls in cardinal directions
        N = self.box_height / 2 - sonar_position.y
        S = sonar_position.y + self.box_height / 2
        W = sonar_position.x + self.box_width / 2
        E = self.box_width / 2 - sonar_position.x
        
        # Handle cardinal directions directly
        if h == 0:
            return E
        elif h == 90:
            return N
        elif h == 180:
            return W
        elif h == 270:
            return S
        
        # Calculate distance to horizontal and vertical walls
        if sin(h) > 0:
            dist_to_horizontal = N / sin(h)
        else:
            dist_to_horizontal = S / -sin(h)
        
        if cos(h) > 0:
            dist_to_vertical = E / cos(h)
        else:
            dist_to_vertical = W / -cos(h)
        
        return min(dist_to_horizontal, dist_to_vertical)
    
    def left_sonar(self):
        left_sonar_position, right_sonar_position = self._get_sonar_positions()
        
        left_dist = self.dist_to_box(left_sonar_position, self.heading) / 10
        return left_dist

    def right_sonar(self):
        left_sonar_position, right_sonar_position = self._get_sonar_positions()
        right_dist = self.dist_to_box(right_sonar_position, self.heading) / 10
        
        return right_dist

    def sonars(self):
        """Get distances from left and right sonar sensors to nearest walls"""
        left_sonar_position, right_sonar_position = self._get_sonar_positions()
        
        left_dist = self.dist_to_box(left_sonar_position, self.heading) / 10
        right_dist = self.dist_to_box(right_sonar_position, self.heading) / 10
        
        return left_dist, right_dist
    
    def _get_sonar_positions(self):
        """Calculate the world positions of left and right sonars"""
        robot_box = self._get_robot_box()
        front_right_corner, front_left_corner = robot_box.front_edge()
        
        front_edge = Vector.from_points(front_left_corner, front_right_corner)
        
        left_sonar_offset = Vector(self.sonar_inset, front_edge.theta)
        left_sonar_position = front_left_corner + left_sonar_offset.to_point()
        
        right_sonar_offset = Vector(self.sonar_inset, front_edge.theta + 180)
        right_sonar_position = front_right_corner + right_sonar_offset.to_point()
        
        return left_sonar_position, right_sonar_position


    def _draw_sonar_debug(self):
        """Draw sonar positions and detection rays"""
        if not debug:
            return
        
        left_sonar_position, right_sonar_position = self._get_sonar_positions()
        left_dist, right_dist = self.sonars()
        
        # Draw sonar positions as orange circles
        left_screen = left_sonar_position.to_screen(self.screen)
        right_screen = right_sonar_position.to_screen(self.screen)
        pygame.draw.circle(self.screen, (255, 165, 0), left_screen, 4)
        pygame.draw.circle(self.screen, (255, 165, 0), right_screen, 4)
        
        # Draw sonar rays showing what they detect
        left_end = left_sonar_position + Vector(left_dist, self.heading).to_point()
        right_end = right_sonar_position + Vector(right_dist, self.heading).to_point()
        
        pygame.draw.line(self.screen, (255, 165, 0), left_screen, left_end.to_screen(self.screen), 2)
        pygame.draw.line(self.screen, (255, 165, 0), right_screen, right_end.to_screen(self.screen), 2)
        
        # Draw distance labels
        font = self.debug_font
        left_text = font.render(f"L: {round(left_dist)}mm", True, (255, 165, 0))
        right_text = font.render(f"R: {round(right_dist)}mm", True, (255, 165, 0))
        self.screen.blit(left_text, (left_screen[0] - 50, left_screen[1] - 20))
        self.screen.blit(right_text, (right_screen[0] + 10, right_screen[1] - 20))

    def render(self):
        """Draw the current frame"""
        self.screen.fill((255, 255, 255))
        
        self._draw_robot()
        self._draw_arena_border()
        self._draw_obstacles()
        self._draw_debug_info()
        self._draw_sonar_debug()
        for event in pygame.event.get():
            if(event == pygame.QUIT):
                quit()
            else:
                print(event)
        pygame.display.flip()
        self.clock.tick(self.fps)

    def _draw_robot(self):
        """Draw the robot at its current position and heading"""
        global frame
        frame += 1
        
        if debug and frame % 100 == 0:
            print(f"heading: {self.heading}, cosine: {cos(self.heading)}")
        
        # Choose image based on heading direction
        if cos(self.heading) >= 0:
            rotated_img = pygame.transform.rotate(self.img_right, self.heading + 90)
        else:
            rotated_img = pygame.transform.rotate(self.img_left, self.heading - 90)
        
        # Draw robot at current position
        rect = rotated_img.get_rect()
        position = Point(self.x, self.y)
        rect.center = position.to_screen(self.screen)
        self.screen.blit(rotated_img, rect)

    def _draw_arena_border(self):
        """Draw the arena boundary lines"""
        padding = self.padding
        border = self.wall_thickness
        
        # White outer border
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        self.screen.get_rect(), padding + border)
        
        # Black inner border
        inner_rect = self.screen.get_rect().inflate(-padding * 2, -padding * 2)
        pygame.draw.rect(self.screen, (0, 0, 0), inner_rect, border)

    def exit(self):
        print("Exiting simulation")
        self.running = False
        pygame.display.quit()
        pygame.quit()
        sys.exit()
        
    def start_simulation(self):
        # Initialize the Pygame window
        pygame.init()
        pygame.font.init()  # Add this line
        self.debug_font = pygame.font.Font(None, 18)
        self.screen = pygame.display.set_mode((mm_to_px(self.box_width) + self.wall_thickness*2 + self.padding*2, mm_to_px(self.box_height) + self.wall_thickness*2 + self.padding*2))
        pygame.display.set_caption("Robot Simulator")
        self.render()

if debug:
    if mode == "movement":
        robot = Robot(use_simulator=True)
    elif mode == "obstacles":
        robot = Robot(use_simulator=True, n_obstacles=3, randomize_obstacles=False)
    while True:
        command = input("What do you want the robot to do next?")
        if command == "q":
            robot.exit()
        if command == "f":
            robot.motors(1, 1, 0.1)
        if command == "l":
            robot.motors(1, -1, 0.1)
        if command == "r":
            robot.motors(-1, 1, 0.1)
        if command == "rr":
            robot.motors(-1, 1, 2)
        if command == "b":
            robot.motors(-1, -1, 0.1)
        if command == "bb":
            robot.motors(-1, -1, 2)
        if command == "ff":
            robot.motors(1, 1, 2)
        if command == "ll":
            robot.motors(1, -1, 2)
else:
    while True:
        mode = input("Do you want to run the real robot (r) or the simulator (s)?")
        if mode == "r":
            from robot import RealRobotDriver
            robot = Robot(use_simulator=False)
            break
        elif mode == "s":
            robot = Robot(use_simulator=True)
            break
        elif mode == "challenge":
            print("*** Simulator settings:")
            n = int(input("*** How many obstacles? (0-3): "))
            is_random = input("*** Randomize obstacle positions? (y/n): ").lower() == 'y'
            print(f"Starting simulation with {n} obstacles...")
            robot = Robot(use_simulator=True, n_obstacles=n, randomize_obstacles=is_random)
            break
        else:
            print("Please choose 'r' or 's'")