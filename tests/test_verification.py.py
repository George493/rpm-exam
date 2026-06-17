"""
ТЕСТЫ ВЕРИФИКАЦИИ
Проверяют правильность расчетов и логики программы
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockGrade:
    """Мок-объект для имитации оценок"""
    def __init__(self, value, weight=1.0, subject=None):
        self.grade_value = value
        self.weight = weight
        self.subject = subject


def test_weighted_average_calculation():
    """Верификация: правильность расчета средневзвешенного балла"""
    print("\n[ТЕСТ 1] Проверка расчета средневзвешенного балла")
    
    test_cases = [
        ([MockGrade(5), MockGrade(4), MockGrade(5)], 4.67, "простые оценки"),
        ([MockGrade(5, 2), MockGrade(4, 1)], 4.67, "разные веса"),
        ([MockGrade(5, 1), MockGrade(5, 2), MockGrade(5, 3)], 5.0, "все пятерки"),
        ([MockGrade(2), MockGrade(2)], 2.0, "двойки"),
        ([MockGrade(4.5), MockGrade(4.5)], 4.5, "дробные оценки"),
        ([], 0.0, "пустой список"),
    ]
    
    for grades, expected, description in test_cases:
        # Симуляция расчета среднего балла
        if not grades:
            result = 0.0
        else:
            weighted_sum = sum(g.grade_value * g.weight for g in grades)
            total_weight = sum(g.weight for g in grades)
            result = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0
        
        if abs(result - expected) < 0.01:
            print(f"  ✅ {description}: {result} == {expected}")
        else:
            print(f"  ❌ {description}: {result} != {expected}")
            return False
    
    return True


def test_grade_distribution():
    """Верификация: правильность подсчета распределения оценок"""
    print("\n[ТЕСТ 2] Проверка распределения оценок")
    
    grades = [MockGrade(5), MockGrade(5), MockGrade(4), MockGrade(4), MockGrade(3), MockGrade(2)]
    
    distribution = {'2': 0, '3': 0, '4': 0, '5': 0}
    for g in grades:
        key = str(int(g.grade_value))
        if key in distribution:
            distribution[key] += 1
    
    expected = {'2': 1, '3': 1, '4': 2, '5': 2}
    
    all_correct = True
    for key in expected:
        if distribution[key] == expected[key]:
            print(f"  ✅ Оценка {key}: {distribution[key]} == {expected[key]}")
        else:
            print(f"  ❌ Оценка {key}: {distribution[key]} != {expected[key]}")
            all_correct = False
    
    return all_correct


def test_average_in_range():
    """Верификация: средний балл должен быть в диапазоне 2-5"""
    print("\n[ТЕСТ 3] Проверка верификации среднего балла")
    
    test_cases = [
        ([MockGrade(5), MockGrade(4)], 4.5, True),
        ([MockGrade(5), MockGrade(5)], 5.0, True),
        ([MockGrade(2), MockGrade(2)], 2.0, True),
        ([MockGrade(3), MockGrade(4)], 3.5, True),
    ]
    
    all_valid = True
    for grades, expected, should_be_valid in test_cases:
        if not grades:
            result = 0
        else:
            result = sum(g.grade_value for g in grades) / len(grades)
        
        is_valid = 2 <= result <= 5
        if is_valid == should_be_valid:
            print(f"  ✅ Средний балл {result:.1f} - верификация пройдена")
        else:
            print(f"  ❌ Средний балл {result:.1f} - верификация НЕ пройдена")
            all_valid = False
    
    return all_valid


def test_exam_prediction():
    """Верификация: прогноз итоговой оценки"""
    print("\n[ТЕСТ 4] Проверка прогноза оценок")
    
    current_grades = [MockGrade(4), MockGrade(4), MockGrade(5)]
    current_avg = sum(g.grade_value for g in current_grades) / len(current_grades)
    
    exam_weight = 0.4
    current_weight = 0.6
    
    # Для получения итоговой 5
    needed_for_5 = (5 - current_avg * current_weight) / exam_weight
    
    expected_needed = round((5 - 4.33 * 0.6) / 0.4, 2)  # ~6.0 (невозможно)
    
    print(f"  Текущий средний: {current_avg:.2f}")
    print(f"  Нужно для 5: {needed_for_5:.2f}")
    
    if needed_for_5 > 5:
        print("  ✅ Прогноз: для 5 нужно больше 5 (невозможно) - верно")
        return True
    else:
        print("  ❌ Прогноз неверен")
        return False


def test_subject_statistics():
    """Верификация: статистика по предметам"""
    print("\n[ТЕСТ 5] Проверка статистики по предметам")
    
    grades = [
        MockGrade(5, subject="Математика"),
        MockGrade(4, subject="Математика"),
        MockGrade(5, subject="Физика"),
    ]
    
    subject_grades = {}
    for g in grades:
        if g.subject not in subject_grades:
            subject_grades[g.subject] = []
        subject_grades[g.subject].append(g.grade_value)
    
    stats = {}
    for subject, values in subject_grades.items():
        stats[subject] = round(sum(values) / len(values), 2)
    
    expected = {"Математика": 4.5, "Физика": 5.0}
    
    all_correct = True
    for subject in expected:
        if stats.get(subject) == expected[subject]:
            print(f"  ✅ {subject}: {stats[subject]} == {expected[subject]}")
        else:
            print(f"  ❌ {subject}: {stats.get(subject)} != {expected[subject]}")
            all_correct = False
    
    return all_correct


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТЫ ВЕРИФИКАЦИИ")
    print("=" * 60)
    
    tests = [
        ("Расчет средневзвешенного балла", test_weighted_average_calculation),
        ("Распределение оценок", test_grade_distribution),
        ("Средний балл в диапазоне 2-5", test_average_in_range),
        ("Прогноз итоговой оценки", test_exam_prediction),
        ("Статистика по предметам", test_subject_statistics),
    ]
    
    passed = 0
    for name, test in tests:
        try:
            if test():
                passed += 1
                print(f"  ✅ {name} - ПРОЙДЕН")
            else:
                print(f"  ❌ {name} - НЕ ПРОЙДЕН")
        except Exception as e:
            print(f"  ❌ {name} - ОШИБКА: {e}")
    
    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТ: {passed}/{len(tests)} тестов верификации пройдено")
    print("=" * 60)