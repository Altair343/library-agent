class DbError(Exception):
    def __init__(self, detail: int):
        self.detail = detail
        super().__init__("Error DB")


class BookError(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code
        super().__init__("BookError")
