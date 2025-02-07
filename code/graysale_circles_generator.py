import numpy as np
from PIL import Image, ImageDraw


def create_circle_pattern(width_pixels, height_pixels, micrometers_per_image, circle_diameter_microns, spacing_microns,
                          brightness_a, brightness_b, magnification):
    # Переводим микрометры в пиксели в зависимости от увеличения объектива
    effective_micrometers_per_image = micrometers_per_image * (100 / magnification)
    pixels_per_micron = width_pixels / effective_micrometers_per_image  # Количество пикселей на 1 микрон

    # Перевод диаметра и расстояния между кружочками в пиксели
    circle_diameter_pixels = int(circle_diameter_microns * pixels_per_micron)
    spacing_pixels = int(spacing_microns * pixels_per_micron)

    # Создаем массив для изображения
    img_array = np.zeros((height_pixels, width_pixels, 3), dtype=np.uint8)

    # Вычисляем количество кружочков по горизонтали и вертикали
    circles_x = width_pixels // (circle_diameter_pixels + spacing_pixels)
    circles_y = height_pixels // (circle_diameter_pixels + spacing_pixels)

    # Рассчитываем отступы для центрирования изображения
    x_offset = (width_pixels - (circles_x * (circle_diameter_pixels + spacing_pixels) - spacing_pixels)) // 2
    y_offset = (height_pixels - (circles_y * (circle_diameter_pixels + spacing_pixels) - spacing_pixels)) // 2

    # Определяем шаг изменения яркости
    total_circles = circles_x * circles_y
    brightness_step = (brightness_b - brightness_a) / total_circles

    # Создаем изображение с кружочками
    img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img)

    for y in range(circles_y):
        for x in range(circles_x):
            # Рассчитываем текущую яркость для градиента
            brightness = brightness_a + (y * circles_x + x) * brightness_step
            color_value = int(np.clip(brightness, 0, 255))  # Обрезаем значение до диапазона [0, 255]
            fill_color = (color_value, color_value, color_value)

            # Координаты центра кружка с учётом отступов для центрирования
            center_x = x_offset + x * (circle_diameter_pixels + spacing_pixels) + circle_diameter_pixels // 2
            center_y = y_offset + y * (circle_diameter_pixels + spacing_pixels) + circle_diameter_pixels // 2

            # Координаты прямоугольника, в который вписан кружок
            bounding_box = [
                (center_x - circle_diameter_pixels // 2, center_y - circle_diameter_pixels // 2),
                (center_x + circle_diameter_pixels // 2, center_y + circle_diameter_pixels // 2)
            ]

            # Рисуем кружок
            draw.ellipse(bounding_box, fill=fill_color)

    # Формируем название файла с указанием параметров, включая увеличение и расстояние между кружочками
    file_name = f'circle_pattern_{circle_diameter_microns}um_{spacing_microns}um_spacing_{brightness_a}to{brightness_b}_{magnification}x.png'

    # Сохраняем изображение
    img.save('pics/'+file_name)


if __name__ == "__main__":
    # Параметры изображения
    micrometers_per_image = 61.0  # Общая длина изображения в микрометрах для объектива 100x
    circle_diameter_microns = 2.0  # Диаметр одного кружка в микрометрах
    spacing_microns = 10.0  # Расстояние между кружками в микрометрах
    brightness_a = 50.0  # Начальная яркость (0-255)
    brightness_b = 200.0  # Конечная яркость (0-255)
    magnification = 40  # Увеличение объектива (100x, 50x, 10x и т.д.)

    # Размер изображения в пикселях
    width_pixels = 1280
    height_pixels = 720

    # Генерация изображения
    create_circle_pattern(width_pixels, height_pixels, micrometers_per_image, circle_diameter_microns, spacing_microns,
                          brightness_a, brightness_b, magnification)

    print(
        f"Изображение сгенерировано и сохранено с названием: 'circle_pattern_{circle_diameter_microns}um_{spacing_microns}um_spacing_{brightness_a}to{brightness_b}_{magnification}x.png'")
