import argparse
import asyncio


class Storage:
    """Класс для хранения метрик в памяти процесса,
    можно при желании в этом классе сохранять в базу
    """

    def __init__(self):
        # используем словарь для хранения метрик
        self._data = []

    def put(self, value):
        if value:
            self._data.append(value)

    def get(self):

        # Всегда возвращаем весь накопленный буфер
        result = self._data

        return result


class ParseError(ValueError):
    pass


class Parser:
    """Класс для реализации протокола"""

    def encode(self, responses):
        """Преобразование ответа сервера в строку для передачи в сокет"""
        result = str(responses)
        return result + "\n"

    def decode(self, data):
        """Разбор команды для дальнейшего выполнения. Возвращает список команд для выполнения"""
        parts = data.split("\n")
        commands = []
        for part in parts:
            if not part:
                continue
            try:
                params = part.strip().split(" ")
                for param in params:
                    if str.isnumeric(param):
                        commands.append(param)
            except ValueError:
                raise ValueError("try again")

        return commands


class ExecutorError(Exception):
    pass


class Executor:
    """Класс Executor реализует метод run, который знает как выполнять команды сервера"""

    def __init__(self, storage):
        self.storage = storage

    def run(self, response):
            self.storage.put(response)
            return self.storage.get()


class EchoServerClientProtocol(asyncio.Protocol):
    """Класс для реализции сервера при помощи asyncio"""

    # Обратите внимание на то, что storage является атрибутом класса
    # Объект self.storage для всех экземмпляров класса EchoServerClientProtocol
    # будет являться одним и тем же объектом для хранения метрик.
    storage = Storage()

    def __init__(self):
        super().__init__()

        self.parser = Parser()
        self.executor = Executor(self.storage)
        self._buffer = b''

    def process_data(self, data):
        """Обработка входной команды сервера"""

        # разбираем сообщения при помощи self.parser
        commands = self.parser.decode(data)
        # выполняем команды и запоминаем результаты выполнения
        response = self.executor.run(commands)


        # преобразовываем команды в строку
        # эту строку возвращаем клиенту
        return f"response {self.parser.encode(response)}"

    def connection_made(self, transport):
        self.transport = transport

        self.transport.write(b"WebVork connection ready\n")

    def data_received(self, data):
        """Метод data_received вызывается при получении данных в сокете"""
        self._buffer += data
        try:
            # Данные из сокета байтовые, нужно декодировать
            decoded_data = self._buffer.decode()
        except UnicodeDecodeError:
            return

        # ждем данных, если команда не завершена символом \n
        if not decoded_data.endswith('\n'):
            return

        self._buffer = b''

        try:
            # обрабатываем поступивший запрос
            resp = self.process_data(decoded_data)
        except (ParseError, ExecutorError) as err:
            # формируем ошибку, в случае ожидаемых исключений
            self.transport.write(f"error\n{err}\n\n".encode())
            return

        # формируем успешный ответ
        self.transport.write(resp.encode())


def run_server(host, port):
    """
    Запускаем асинхронный сервер

    Args:
        host: адрес хоста default=127.0.0.1
        port: адрес порта default=8080

    Returns:
        None
    """
    print(port, "\n")
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        EchoServerClientProtocol,
        host, port
        # host, port
    )
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":

    # запуск сервера для тестирования
    # в контейнере надо передавать пустую строку в адресе хоста
    print("ready port:80")
    run_server("", 80)
    #run_server("127.0.0.1", 8080)
