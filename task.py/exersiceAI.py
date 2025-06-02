import json
import os
import sys
from datetime import datetime, date
from typing import List, Dict, Optional
import argparse

class Task:
    def __init__(self, title, priority=None, due_date=None):
        self.id = None  # ID буде призначено пізніше
        self.title = title
        self.completed = False
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Виправлено datetime.datetime.now()
        self.priority = priority
        self.due_date = due_date
        self.tags = []  # Додано для підтримки тегів
    
    def __str__(self):
        status = "✓" if self.completed else "✗"
        priority = f" [{self.priority}]" if self.priority else ""
        due_date = f" (до {self.due_date})" if self.due_date else ""
        tags = f" #{','.join(self.tags)}" if self.tags else ""
        return f"{self.id}. {status} {self.title}{priority}{due_date}{tags}"
    
    def mark_completed(self):
        """Позначає завдання як виконане"""
        self.completed = True
    
    def add_tag(self, tag):
        """Додає тег до завдання"""
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self):
        """Конвертує завдання в словник для збереження"""
        task_dict = {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at,
            "tags": self.tags
        }
        
        if self.priority:
            task_dict["priority"] = self.priority
        
        if self.due_date:
            task_dict["due_date"] = self.due_date
        
        return task_dict
    
    @classmethod
    def from_dict(cls, data):
        """Створює завдання зі словника"""
        task = cls(title=data["title"], 
                  priority=data.get("priority"), 
                  due_date=data.get("due_date"))
        task.id = data["id"]
        task.completed = data["completed"]
        task.created_at = data["created_at"]
        task.tags = data.get("tags", [])
        return task

class TaskManager:
    """Основний клас для керування завданнями"""
    
    def __init__(self):
        self.tasks = []
        self.filename = "tasks.json"
    
    def add_task(self, title, priority=None, due_date=None):
        """Додає нове завдання"""
        task = Task(title, priority, due_date)
        task.id = self._generate_id()
        self.tasks.append(task)
        return task
    
    def _generate_id(self):
        """Генерує унікальний ID для завдання"""
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1
    
    def get_all_tasks(self):
        """Повертає всі завдання"""
        return self.tasks
    
    def complete_task(self, task_id):
        """Позначає завдання як виконане"""
        for task in self.tasks:
            if task.id == task_id:
                task.mark_completed()
                return True
        return False
    
    def delete_task(self, task_id):
        """Видаляє завдання за ID"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                return True
        return False
    
    def load_tasks(self):
        """Завантажує завдання з файлу"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.tasks = [Task.from_dict(task_data) for task_data in data]
            return True
        except FileNotFoundError:
            return False
    
    def save_tasks(self):
        """Зберігає завдання у файл"""
        with open(self.filename, 'w', encoding='utf-8') as file:
            data = [task.to_dict() for task in self.tasks]
            json.dump(data, file, ensure_ascii=False, indent=2)
    
    def list_tasks(self, status=None, priority=None):
        """Показує список завдань з можливістю фільтрації
        
        Args:
            status (bool, optional): Фільтр за статусом (True - виконані, False - активні)
            priority (str, optional): Фільтр за пріоритетом
        """
        filtered_tasks = self.tasks
        
        if status is not None:
            filtered_tasks = [task for task in filtered_tasks if task.completed == status]
        
        if priority:
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority]
        
        return filtered_tasks
    
    def get_task_by_id(self, task_id):
        """Знаходить завдання за ID
        
        Args:
            task_id (int): ID завдання
            
        Returns:
            Task or None: Знайдене завдання або None, якщо не знайдено
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None  # Виправлено "return None,"
    
    def search_tasks(self, keyword):
        """Пошук завдань за ключовим словом в назві
        
        Args:
            keyword (str): Ключове слово для пошуку
            
        Returns:
            list: Список завдань, що містять ключове слово
        """
        if not keyword:
            return []
        
        keyword = keyword.lower()
        return [task for task in self.tasks if keyword in task.title.lower()]
    
    def filter_by_tag(self, tag):
        """Фільтрує завдання за тегом
        
        Args:
            tag (str): Тег для фільтрації
            
        Returns:
            list: Список завдань з вказаним тегом
        """
        return [task for task in self.tasks if tag in task.tags]
    
    def sort_tasks(self, tasks=None, by="id", reverse=False):
        """Сортує завдання за вказаним критерієм
        
        Args:
            tasks (list, optional): Список завдань для сортування
            by (str): Критерій сортування
            reverse (bool): Сортування у зворотному порядку
            
        Returns:
            list: Відсортований список завдань
        """
        if tasks is None:
            tasks = self.tasks
        
        if by == "id":
            return sorted(tasks, key=lambda t: t.id, reverse=reverse)
        elif by == "title":
            return sorted(tasks, key=lambda t: t.title.lower(), reverse=reverse)
        elif by == "priority":
            priority_order = {"високий": 3, "середній": 2, "низький": 1, None: 0}
            return sorted(tasks, key=lambda t: priority_order.get(t.priority, 0), reverse=reverse)
        elif by == "due_date":
            return sorted(tasks, key=lambda t: t.due_date if t.due_date else "9999-99-99", reverse=reverse)
        elif by == "created_at":
            return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)
        else:
            return tasks
    
    def get_upcoming_tasks(self, days=7):
        """Повертає список завдань з наближаючимся терміном виконання"""
        today = datetime.now().date()
        upcoming = []
        
        for task in self.tasks:
            if task.completed or not task.due_date:
                continue
            
            try:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                days_left = (due_date - today).days
                
                if 0 <= days_left <= days:
                    upcoming.append((task, days_left))
            except ValueError:
                continue
        
        return sorted(upcoming, key=lambda x: x[1])
    
    def export_tasks(self, filename, format="json"):
        """Експортує завдання у файл"""
        try:
            if format.lower() == "json":
                with open(filename, 'w', encoding='utf-8') as file:
                    data = [task.to_dict() for task in self.tasks]
                    json.dump(data, file, ensure_ascii=False, indent=2)
            elif format.lower() == "csv":
                import csv
                with open(filename, 'w', encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["ID", "Назва", "Статус", "Пріоритет", "Термін виконання", "Створено", "Теги"])
                    
                    for task in self.tasks:
                        status = "Виконано" if task.completed else "Активно"
                        writer.writerow([
                            task.id,
                            task.title,
                            status,
                            task.priority or "",
                            task.due_date or "",
                            task.created_at,
                            ",".join(task.tags)
                        ])
            else:
                print(f"Непідтримуваний формат: {format}")
                return False
                
            print(f"Завдання експортовано у файл {filename}")
            return True
        except Exception as e:
            print(f"Помилка при експорті завдань: {e}")
            return False
    
    def import_tasks(self, filename, format="json"):
        """Імпортує завдання з файлу"""
        try:
            if format.lower() == "json":
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    imported_tasks = [Task.from_dict(task_data) for task_data in data]
                    
                    next_id = self._generate_id()
                    for task in imported_tasks:
                        task.id = next_id
                        next_id += 1
                    
                    self.tasks.extend(imported_tasks)
                    
            elif format.lower() == "csv":
                import csv
                with open(filename, 'r', encoding='utf-8', newline='') as file:
                    reader = csv.reader(file)
                    headers = next(reader)
                    
                    for row in reader:
                        if len(row) >= 6:
                            title = row[1]
                            completed = row[2] == "Виконано"
                            priority = row[3] if row[3] else None
                            due_date = row[4] if row[4] else None
                            tags = row[6].split(",") if len(row) > 6 and row[6] else []
                            
                            task = self.add_task(title, priority, due_date)
                            if completed:
                                task.mark_completed()
                            for tag in tags:
                                task.add_tag(tag.strip())
                
            else:
                print(f"Непідтримуваний формат: {format}")
                return False
                
            print(f"Завдання імпортовано з файлу {filename}")
            return True
        except Exception as e:
            print(f"Помилка при імпорті завдань: {e}")
            return False
    
    def get_statistics(self):
        """Показує статистику завдань"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.completed)
        active = total - completed
        
        high_priority = sum(1 for task in self.tasks 
                          if not task.completed and task.priority == "високий")
        
        print(f"\n📊 Статистика завдань:")
        print("=" * 30)
        print(f"📝 Всього завдань: {total}")
        print(f"✅ Виконано: {completed}")
        print(f"⏳ Активних: {active}")
        print(f"🔴 Високий пріоритет (активні): {high_priority}")
        
        return {
            "total": total,
            "completed": completed,
            "active": active,
            "high_priority": high_priority
        }
    
    def run_cli(self):
        """Інтерактивний режим роботи"""
        print("\n🗒️  Розумний CLI Менеджер Завдань 🗒️")
        print("=" * 40)
        
        self.load_tasks()
        
        while True:
            print("\nОберіть дію:")
            print("1. Додати нове завдання")
            print("2. Показати всі завдання")
            print("3. Позначити завдання як виконане")
            print("4. Видалити завдання")
            print("5. Показати статистику")
            print("6. Фільтрувати завдання")
            print("7. Пошук завдань")
            print("8. Експорт завдань")
            print("9. Імпорт завдань")
            print("0. Вийти")
            
            choice = input("\nВаш вибір: ")
            
            if choice == "1":
                title = input("Введіть назву завдання: ")
                priority = input("Введіть пріоритет (низький/середній/високий або Enter для пропуску): ")
                due_date = input("Введіть термін виконання (YYYY-MM-DD або Enter для пропуску): ")
                tags_input = input("Введіть теги через кому (або Enter для пропуску): ")
                
                priority = priority if priority else None
                due_date = due_date if due_date else None
                
                task = self.add_task(title, priority, due_date)
                
                if tags_input:
                    tags = [tag.strip() for tag in tags_input.split(",")]
                    for tag in tags:
                        task.add_tag(tag)
                
                print(f"Завдання '{title}' додано!")
                
            elif choice == "2":
                tasks = self.get_all_tasks()
                if not tasks:
                    print("Список завдань порожній.")
                else:
                    print("\nСписок завдань:")
                    for task in tasks:
                        print(task)
                        
            elif choice == "3":
                task_id = input("Введіть ID завдання для позначення як виконане: ")
                if task_id.isdigit():
                    if self.complete_task(int(task_id)):
                        print(f"Завдання з ID {task_id} позначено як виконане!")
                    else:
                        print(f"Завдання з ID {task_id} не знайдено.")
                else:
                    print("Некоректний ID завдання.")
                    
            elif choice == "4":
                task_id = input("Введіть ID завдання для видалення: ")
                if task_id.isdigit():
                    if self.delete_task(int(task_id)):
                        print(f"Завдання з ID {task_id} видалено!")
                    else:
                        print(f"Завдання з ID {task_id} не знайдено.")
                else:
                    print("Некоректний ID завдання.")
                    
            elif choice == "5":
                self.get_statistics()
                
            elif choice == "6":
                status_input = input("Фільтрувати за статусом (1 - виконані, 0 - активні, Enter - всі): ")
                priority_input = input("Фільтрувати за пріоритетом (низький/середній/високий або Enter для всіх): ")
                
                status = None
                if status_input == "1":
                    status = True
                elif status_input == "0":
                    status = False
                    
                priority = priority_input if priority_input else None
                
                tasks = self.list_tasks(status, priority)
                if not tasks:
                    print("Немає завдань, що відповідають фільтрам.")
                else:
                    print("\nВідфільтровані завдання:")
                    for task in tasks:
                        print(task)
                        
            elif choice == "7":
                keyword = input("Введіть ключове слово для пошуку: ")
                tasks = self.search_tasks(keyword)
                if not tasks:
                    print("Завдання не знайдено.")
                else:
                    print("\nЗнайдені завдання:")
                    for task in tasks:
                        print(task)
                        
            elif choice == "8":
                filename = input("Введіть ім'я файлу для експорту: ")
                format_choice = input("Введіть формат (json/csv): ").lower()
                self.export_tasks(filename, format_choice)
                
            elif choice == "9":
                filename = input("Введіть ім'я файлу для імпорту: ")
                format_choice = input("Введіть формат (json/csv): ").lower()
                self.import_tasks(filename, format_choice)
                        
            elif choice == "0":
                self.save_tasks()
                print("Завдання збережено. До побачення!")
                break
                
            else:
                print("Некоректний вибір. Спробуйте ще раз.")

def create_parser():
    """Створює парсер аргументів командного рядка"""
    parser = argparse.ArgumentParser(description='Розумний CLI Менеджер Завдань')
    subparsers = parser.add_subparsers(dest='command', help='Команди')
    
    # Команда додавання завдання
    add_parser = subparsers.add_parser('add', help='Додати нове завдання')
    add_parser.add_argument('name', help='Назва завдання')
    add_parser.add_argument('-p', '--priority', choices=['низький', 'середній', 'високий'], 
                           help='Пріоритет завдання')
    add_parser.add_argument('-d', '--due', help='Термін виконання')
    
    # Команда перегляду списку завдань
    list_parser = subparsers.add_parser('list', help='Показати список завдань')
    list_parser.add_argument('-s', '--status', choices=['active', 'completed'], 
                            help='Фільтр за статусом')
    list_parser.add_argument('-p', '--priority', choices=['низький', 'середній', 'високий'], 
                           help='Фільтр за пріоритетом')
    
    # Команда позначення завдання як виконаного
    complete_parser = subparsers.add_parser('complete', help='Позначити завдання як виконане')
    complete_parser.add_argument('id', type=int, help='ID завдання')
    
    # Команда видалення завдання
    delete_parser = subparsers.add_parser('delete', help='Видалити завдання')
    delete_parser.add_argument('id', type=int, help='ID завдання')
    
    # Команда перегляду статистики
    subparsers.add_parser('stats', help='Показати статистику завдань')
    
    return parser

def interactive_mode():
    """Запускає інтерактивний режим роботи"""
    manager = TaskManager()
    manager.run_cli()

def main():
    """Головна функція програми"""
    parser = create_parser()
    
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    args = parser.parse_args()
    manager = TaskManager()
    manager.load_tasks()
    
    try:
        if args.command == 'add':
            manager.add_task(args.name, args.priority, args.due)
            manager.save_tasks()
            print(f"Завдання '{args.name}' додано!")
        
        elif args.command == 'list':
            status = True if args.status == 'completed' else False if args.status == 'active' else None
            tasks = manager.list_tasks(status, args.priority)
            if not tasks:
                print("Немає завдань, що відповідають фільтрам.")
            else:
                print("\nСписок завдань:")
                for task in tasks:
                    print(task)
        
        elif args.command == 'complete':
            if manager.complete_task(args.id):
                print(f"Завдання з ID {args.id} позначено як виконане!")
            else:
                print(f"Завдання з ID {args.id} не знайдено.")
            manager.save_tasks()
        
        elif args.command == 'delete':
            if manager.delete_task(args.id):
                print(f"Завдання з ID {args.id} видалено!")
            else:
                print(f"Завдання з ID {args.id} не знайдено.")
            manager.save_tasks()
        
        elif args.command == 'stats':
            manager.get_statistics()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n👋 Програма перервана користувачем.")
        manager.save_tasks()

if __name__ == "__main__":
    main()