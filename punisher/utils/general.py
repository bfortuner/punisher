import uuid

def make_id(length=32):
    return uuid.uuid4().hex[:length]
