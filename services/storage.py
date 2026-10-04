from aiogram.fsm.storage.base import BaseStorage, StorageKey

class DictStorage(BaseStorage):
    def __init__(self):
        self.states = {}
        self.datas = {}

    async def set_state(self, key: StorageKey, state=None) -> None:
        if state is None:
            self.states.pop(key, None)
            return
        if hasattr(state, 'state'):
            self.states[key] = state.state
        else:
            self.states[key] = str(state)

    async def get_state(self, key: StorageKey):
        return self.states.get(key)

    async def set_data(self, key: StorageKey, data) -> None:
        self.datas[key] = dict(data)

    async def get_data(self, key: StorageKey):
        data = self.datas.get(key)
        if data is None:
            return {}
        return dict(data)

    async def close(self) -> None:
        self.states.clear()
        self.datas.clear()
