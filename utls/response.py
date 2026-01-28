class ResponseMessage:
    @staticmethod
    def ok(message):
        return {"detail": message}

    @staticmethod
    def error(message):
        return {"detail": message}
