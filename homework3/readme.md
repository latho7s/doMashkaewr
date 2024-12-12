# Установка
1. Установка программы и переход в директорию
   ```bash
   git clone <URL репозитория>
   cd <директория проекта>
   ```
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Для Linux/Mac
   venv\Scripts\activate     # Для Windows
   ```
3. Установите необходимые зависимости :
   ```bash
   Зависимости не требуются
   ```

# Запуск скрипта

Скрипт принимает текст конфигурационного файла через стандартный ввод и выводит yaml в стандартный вывод.

```bash
 Get-Content input.txt | py hw3.py
```

### Пример 
```
INPUT
{{!-- Это многострочный комментарий --}}
def myConst = 42
def myString = @"This is string"
myArray = [ 1; 2; 3; $(myConst); $(myString) ]
```

```
YAML
arrays:
  array_0:
  - '1'
  - '2'
  - '3'
  - '42'
  - '@"This is string"'
constants:
  myConst: '42'
  myString: '@"This is string"'
```

# Тесты

Шаги запуска тестов:
1. Установить библиотеку pytest (необходимо, если не сделано ранее):
   ```bash
   pip install pytest
   ```
   
2. Для запуска тестирования необходимо запустить следующий скрипт:
   ```shell
   py -m unittest unittests.py
   ```
