import os
import sys
import pygame

WINDOW_SIZE = WIDTH, HEIGHT = 440, 600

pygame.init()
all_sprites = pygame.sprite.Group()

# Гравитация и физические параметры
scale = 0.1
G = 9.81 / 60  # Ускорение свободного падения, м/с^2 (делим на FPS, чтобы уменьшить эффект за кадр)
thrust = 15 / 60  # Тяга ракеты (снижена для реальной симуляции)
fuel = (274 * 10**3) * scale  # Топливо
mass = 308000 * scale  # Масса ракеты в кг
rocket_speed = 0  # Начальная скорость
burn_rate = 0.9  # Скорость сжигания топлива

# Параметры орбиты и возвращения
orbit_reached = False  # Достигла ли ракета орбиты
orbit_time = 0  # Время пребывания на орбите
max_orbit_time = 100  # Условное время пребывания на орбите (в тиках)
max_speed = 5  # Максимальная скорость ракеты
landing_slowdown_start = 100  # Высота, с которой начнется замедление посадки

# Часы для управления кадрами
clock = pygame.time.Clock()


def load_image(name, colorkey=None):  # функция загрузки изображения
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    earth = pygame.sprite.Sprite(all_sprites)
    earth_image = pygame.transform.scale(load_image("earth.jpg", -1), (300, 290))
    earth.image = earth_image
    earth.rect = earth.image.get_rect()
    earth.rect.x = 70
    earth.rect.y = 300

    mks = pygame.sprite.Sprite(all_sprites)
    mks_image = pygame.transform.scale(load_image("mks.jpg", -1), (200, 190))
    mks.image = mks_image
    mks.rect = mks.image.get_rect()
    mks.rect.x = 100
    mks.rect.y = 30

    rocket = pygame.sprite.Sprite(all_sprites)
    rocket_image = pygame.transform.scale(load_image("rocket.jpg", -1), (100, 90))
    rocket.image = rocket_image
    rocket.rect = rocket.image.get_rect()
    rocket.rect.x = 200
    rocket.rect.y = 250

    pygame.display.set_caption('Запуск ракеты на МКС')
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)

        # Если ракета еще не достигла орбиты
        if not orbit_reached:
            if fuel > 0:
                # Рассчитываем ускорение как разницу между тягой и гравитацией
                acceleration = (thrust - G)  # Масса не влияет на ускорение напрямую в этой симуляции
                rocket_speed -= acceleration  # Движемся вверх (уменьшаем y)
                fuel -= burn_rate  # Уменьшаем топливо
            else:
                rocket_speed += G  # Если топливо кончилось, ракета замедляется под гравитацией

            # Ограничиваем максимальную скорость
            if rocket_speed > max_speed:
                rocket_speed = max_speed
            elif rocket_speed < -max_speed:
                rocket_speed = -max_speed

            # Изменение позиции ракеты
            rocket.rect.y += rocket_speed

            # Если ракета достигает орбиты (например, y <= 50)
            if rocket.rect.y <= 50:
                orbit_reached = True  # Ракета достигла орбиты
                rocket_speed = 0  # Останавливаем ракету

        # Если ракета на орбите, отсчитываем время пребывания
        if orbit_reached and orbit_time < max_orbit_time:
            orbit_time += 1  # Накапливаем время на орбите
        elif orbit_time >= max_orbit_time:
            # Если время пребывания на орбите закончилось, начинаем возвращение на Землю

            # Если ракета приближается к земле (высота < landing_slowdown_start), замедляем скорость
            if rocket.rect.y >= HEIGHT - landing_slowdown_start:
                rocket_speed += G / 2  # Замедляем падение в два раза ближе к земле
            else:
                rocket_speed += G  # Ускоряем падение под действием гравитации

            rocket.rect.y += rocket_speed

        # Если ракета вернулась на Землю (достигла нижней границы экрана)
        if rocket.rect.y >= HEIGHT - 340:
            rocket.rect.y = HEIGHT - 340  # Фиксируем положение ракеты на земле
            rocket_speed = 0  # Останавливаем ракету
            orbit_reached = False  # Для возможной новой симуляции
            orbit_time = 0  # Сбрасываем время на орбите
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
