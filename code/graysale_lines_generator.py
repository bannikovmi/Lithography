import numpy as np
from PIL import Image


def create_gradient_image(width_pixels, height_pixels, micrometers_per_image, micrometers_per_stripe, brightness_a,
                          brightness_b, magnification):
    # Корректируем ширину изображения с учётом увеличения объектива
    effective_micrometers_per_image = micrometers_per_image * (100 / magnification)

    # Рассчитываем количество пикселей на микрометр
    pixels_per_micron = width_pixels / effective_micrometers_per_image

    # Рассчитываем ширину одной белой полосы в пикселях
    stripe_width_pixels = int(micrometers_per_stripe * pixels_per_micron)

    # Проверка на случай слишком большой ширины полосы
    if stripe_width_pixels == 0:
        raise ValueError("Ширина полосы слишком мала для заданного разрешения изображения.")

    # Рассчитываем количество полос
    total_stripes = width_pixels // (stripe_width_pixels * 2)  # Учитываем белые и чёрные полосы

    if total_stripes == 0:
        raise ValueError("Количество полос равно нулю. Проверьте параметры ширины полос и увеличения объектива.")

    # Создаем массив для изображения
    img_array = np.zeros((height_pixels, width_pixels, 3), dtype=np.uint8)

    # Определяем количество полос в одной половине изображения
    half_height = height_pixels // 2
    brightness_step = (brightness_b - brightness_a) / (total_stripes * 2)  # Делим на 2, чтобы учесть обе части

    # Заполняем первую (верхнюю) половину изображения градиентными полосами
    for stripe in range(total_stripes):
        brightness = brightness_a + stripe * brightness_step
        color_value = int(np.clip(brightness, 0, 255))  # Обрезаем значение до диапазона [0, 255]

        # Вычисляем координаты начала и конца полосы
        start_x = stripe * stripe_width_pixels * 2  # Учитываем белую и черную полосы
        end_x = start_x + stripe_width_pixels

        # Заполняем белую (серую) полосу
        img_array[:half_height, start_x:end_x] = [color_value] * 3  # Заполняем белую/серую полосу

    # Заполняем вторую (нижнюю) половину изображения с продолжением градиента
    for stripe in range(total_stripes):
        brightness = brightness_a + (total_stripes + stripe) * brightness_step  # Продолжаем градиент
        color_value = int(np.clip(brightness, 0, 255))  # Обрезаем значение до диапазона [0, 255]

        # Вычисляем координаты начала и конца полосы
        start_x = stripe * stripe_width_pixels * 2
        end_x = start_x + stripe_width_pixels

        # Заполняем белую (серую) полосу на нижней половине
        img_array[half_height:, start_x:end_x] = [color_value] * 3

    # Формируем название файла с указанием параметров, включая увеличение
    file_name = f'gradient_stripes_{micrometers_per_stripe}um_{brightness_a}to{brightness_b}_{magnification}x.png'

    # Конвертируем в изображение и сохраняем
    img = Image.fromarray(img_array)
    img.save('pics/'+file_name)


if __name__ == "__main__":
    # Параметры изображения
    micrometers_per_image = 61.0  # Общая длина изображения в микрометрах для объектива 100x
    micrometers_per_stripe = 20.0  # Ширина одной белой полосы в микрометрах
    brightness_a = 120.0  # Начальная яркость (0-255)
    brightness_b = 255.0  # Конечная яркость (0-255)
    magnification = 40  # Увеличение объектива (100x, 50x, 10x и т.д.)

    # Размер изображения в пикселях
    width_pixels = 1280
    height_pixels = 720

    # Генерация изображения
    create_gradient_image(width_pixels, height_pixels, micrometers_per_image, micrometers_per_stripe, brightness_a,
                          brightness_b, magnification)

    print(
        f"Изображение сгенерировано и сохранено с названием: 'gradient_stripes_{micrometers_per_stripe}um_{brightness_a}to{brightness_b}_{magnification}x.png'")
