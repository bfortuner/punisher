import uuid

ORDER_ID_PREFIX = "OD"

def generate_order_id(length=10):
    return ORDER_ID_PREFIX + str(uuid.uuid4()).upper().replace('-','')[:length]