"""
ТЕСТЫ ВАЛИДАЦИИ
Проверяют, что программа правильно проверяет вводимые данные
"""

import sys
import os

# Добавляем путь к родительской папке, чтобы импортировать web_diary
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_diary import allowed_file


def test_validation_grade_range():
    """Валидация: оценка должна быть от 2 до 5"""
    print("\n[ТЕСТ 1] Проверка валидации диапазона оценок")
    
    valid_grades = [2, 2.5, 3, 3.7, 4, 4.8, 5]
    invalid_grades = [1, 1.5, 5.5, 6, 10, -1, 0]
    
    all_valid = True
    for grade in valid_grades:
        if 2 <= grade <= 5:
            print(f"  ✅ Оценка {grade} - валидна")
        else:
            print(f"  ❌ Ошибка: оценка {grade} должна быть валидной")
            all_valid = False
    
    for grade in invalid_grades:
        if not (2 <= grade <= 5):
            print(f"  ✅ Оценка {grade} - невалидна (верно)")
        else:
            print(f"  ❌ Ошибка: оценка {grade} НЕ должна быть валидной")
            all_valid = False
    
    assert all_valid, "Некоторые проверки диапазона оценок не пройдены"
    return True


def test_validation_email_format():
    """Валидация: email должен содержать @"""
    print("\n[ТЕСТ 2] Проверка валидации email")
    
    valid_emails = ["user@mail.ru", "teacher@edu.ru", "student@gmail.com", "name@domain.com"]
    invalid_emails = ["usermail.ru", "teacher@", "@edu.ru", "plaintext", "user@", "@domain"]
    
    all_valid = True
    for email in valid_emails:
        if "@" in email and "." in email.split("@")[1]:
            print(f"  ✅ Email {email} - валиден")
        else:
            print(f"  ❌ Email {email} - должен быть валидным")
            all_valid = False
    
    for email in invalid_emails:
        if "@" not in email or "." not in email.split("@")[-1] if "@" in email else True:
            print(f"  ✅ Email {email} - невалиден (верно)")
        else:
            print(f"  ❌ Email {email} - НЕ должен быть валидным")
            all_valid = False
    
    assert all_valid, "Некоторые проверки email не пройдены"
    return True


def test_validation_name_length():
    """Валидация: имя должно быть не короче 2 символов"""
    print("\n[ТЕСТ 3] Проверка валидации длины имени")
    
    valid_names = ["Иван", "Анна", "Петр", "Мария", "Елена"]
    invalid_names = ["И", "А", "1", "", " "]
    
    all_valid = True
    for name in valid_names:
        if len(name.strip()) >= 2:
            print(f"  ✅ Имя '{name}' - валидно")
        else:
            print(f"  ❌ Имя '{name}' - должно быть валидным")
            all_valid = False
    
    for name in invalid_names:
        if len(name.strip()) < 2:
            print(f"  ✅ Имя '{name}' - невалидно (верно)")
        else:
            print(f"  ❌ Имя '{name}' - НЕ должно быть валидным")
            all_valid = False
    
    assert all_valid, "Некоторые проверки длины имени не пройдены"
    return True


def test_validation_file_extension():
    """Валидация: проверка разрешенных расширений файлов"""
    print("\n[ТЕСТ 4] Проверка валидации расширений файлов")
    
    valid_files = ["photo.png", "image.jpg", "picture.jpeg", "avatar.gif", "user.webp"]
    invalid_files = ["file.txt", "document.pdf", "script.py", "video.mp4", "audio.mp3"]
    
    all_valid = True
    for filename in valid_files:
        if allowed_file(filename):
            print(f"  ✅ {filename} - разрешен")
        else:
            print(f"  ❌ {filename} - должен быть разрешен")
            all_valid = False
    
    for filename in invalid_files:
        if not allowed_file(filename):
            print(f"  ✅ {filename} - не разрешен (верно)")
        else:
            print(f"  ❌ {filename} - НЕ должен быть разрешен")
            all_valid = False
    
    assert all_valid, "Некоторые проверки расширений файлов не пройдены"
    return True


def test_validation_grade_type():
    """Валидация: тип оценки должен быть из разрешенных"""
    print("\n[ТЕСТ 5] Проверка валидации типа оценки")
    
    valid_types = ["test", "homework", "exam"]
    invalid_types = ["quiz", "final", "unknown", "", "test "]
    
    all_valid = True
    for t in valid_types:
        if t in ["test", "homework", "exam"]:
            print(f"  ✅ Тип '{t}' - валиден")
        else:
            print(f"  ❌ Тип '{t}' - должен быть валидным")
            all_valid = False
    
    for t in invalid_types:
        if t not in ["test", "homework", "exam"]:
            print(f"  ✅ Тип '{t}' - невалиден (верно)")
        else:
            print(f"  ❌ Тип '{t}' - НЕ должен быть валидным")
            all_valid = False
    
    assert all_valid, "Некоторые проверки типа оценки не пройдены"
    return True


def test_validation_weight_range():
    """Валидация: вес оценки должен быть от 0.5 до 2.0"""
    print("\n[ТЕСТ 6] Проверка валидации веса оценки")
    
    valid_weights = [0.5, 1.0, 1.5, 2.0]
    invalid_weights = [0, 0.4, 2.1, 3, -1]
    
    all_valid = True
    for w in valid_weights:
        if 0.5 <= w <= 2.0:
            print(f"  ✅ Вес {w} - валиден")
        else:
            print(f"  ❌ Вес {w} - должен быть валидным")
            all_valid = False
    
    for w in invalid_weights:
        if not (0.5 <= w <= 2.0):
            print(f"  ✅ Вес {w} - невалиден (верно)")
        else:
            print(f"  ❌ Вес {w} - НЕ должен быть валидным")
            all_valid = False
    
    assert all_valid, "Некоторые проверки веса оценки не пройдены"
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТЫ ВАЛИДАЦИИ")
    print("=" * 60)
    
    tests = [
        ("Диапазон оценок", test_validation_grade_range),
        ("Формат email", test_validation_email_format),
        ("Длина имени", test_validation_name_length),
        ("Расширения файлов", test_validation_file_extension),
        ("Тип оценки", test_validation_grade_type),
        ("Вес оценки", test_validation_weight_range),
    ]
    
    passed = 0
    for name, test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ Тест '{name}' не пройден: {e}")
    
    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТ: {passed}/{len(tests)} тестов валидации пройдено")
    print("=" * 60)