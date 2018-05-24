from enum import Enum, EnumMeta


class ChoiceEnumMeta(EnumMeta):
    def __iter__(self):
        return ((tag, tag.value) for tag in super().__iter__())


class ChoiceEnum(Enum, metaclass=ChoiceEnumMeta):
    '''
    Author: https://github.com/treyhunner
    Usage:

        class Gender(ChoiceEnum):
            male = 'male'
            female = 'female'
            no_answer = 'no-answer'

        models.CharField(max_length=10, choices=Gender)
    '''
    pass
