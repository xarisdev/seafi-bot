from .config import filter_configurations

class DataFilter:
    def __init__(
        self,
        input_data_key: str,
        output_data_key: str | None = None,
        params_to_record: list | None = None
    ) -> None:
        """
        Args:
            input_data_key (:obj:`str`, required): Имя фильтруемого словаря.            
            output_data_key (:obj:`str`, optional): Имя отфильтрованного словаря.
                Default: same as input_data_key
            params_to_record (:obj:`list`, optional): Список параметров для записи.
                Если список пустой - запишет список ключей фильтруемого словаря.
                Если `None` - запишет все значения для каждого ключа в фильтруемом словаре.
        """
        if output_data_key is None:
            output_data_key = input_data_key

        self.input_data_key = input_data_key
        self.output_data_key = output_data_key

        self.params_to_record = params_to_record

    def serizalize(self, data: dict) -> dict:
        output = {}

        if not data:
            output = {self.output_data_key: None}
            return output

        to_filter_data: dict = data.get(self.input_data_key)
        if to_filter_data is None:
            output = {self.output_data_key: None}
            return output

        if self.params_to_record is None:
            if hasattr(to_filter_data, "model_dump"):
                to_filter_data = to_filter_data.model_dump()

            output[self.output_data_key] = to_filter_data
            return output

        if not self.params_to_record:
            output[self.output_data_key] = []
            for _key in to_filter_data.keys():
                output[self.output_data_key].append(_key)
            return output

        output[self.output_data_key] = {}

        for key, value in to_filter_data.items():
            if hasattr(value, "model_dump"):
                value = value.model_dump()

            _key_dict = {}
            for _key, _value in value.items():
                if _key in self.params_to_record:
                    if isinstance(_key, int):
                        _key = str(_key)
                    _key_dict[_key] = _value 

            if _key_dict:
                output[self.output_data_key][key] = _key_dict

        return output

filters = [DataFilter(**config) for config in filter_configurations.values()]