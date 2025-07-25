from app.bussiness_logic.post_business_logic import Obj


def update_obj(param: int, obj: Obj):
    return {'param': param, 'Updated obj': obj}
