init python in vector:
    import math
    import operator as op
    import itertools

    class Vector(list):
        POSITION_DIMENSIONS = {i: idx for idx, i in enumerate("xyzw")}
        _pos_getter = lambda self, key: self.POSITION_DIMENSIONS.get(key)

        COLOR_DIMENSIONS = {i: idx for idx, i in enumerate("rgba")}
        _color_getter = lambda self, key: self.COLOR_DIMENSIONS.get(key)

        def __init__(self, *vals, dims=4, _type=float):
            # Если значения не указаны, создаём нулевой вектор
            if not vals: 
                super().__init__(_type(0) for i in range(dims))

            elif len(vals) == 1: 
                super().__init__(map(_type, vals * dims))

            # Если кол-во значений соответствует кол-ву измерений вектора,
            # объявляем вектор как положено
            elif len(vals) == dims: 
                super().__init__(map(_type, vals))

            else:    
                cls = self.__class__.__name__
                x, y = dims, len(vals)
                raise TypeError(f"{cls} requires {x} arguments, but {y} given.")

        def __calc(self, o, f, rev=False, ip=False):
            # Операции над вектором и числом
            if isinstance(o, (int, float)) and not rev and not ip:
                return self.__class__(*map(f, self, itertools.repeat(self.val_type(o))))

            # Операции над числом и вектором
            elif isinstance(o, (int, float)) and rev:
                return self.__class__(*map(f, itertools.repeat(self.val_type(o)), self))

            # Операции над вектором и числом на месте
            elif isinstance(o, (int, float)) and ip:
                [self.__setitem__(idx, i) for idx, i in enumerate(
                        map(f, self, itertools.repeat(self.val_type(o))))]

                return self

            # Операции над вектором и списком
            elif (isinstance(o, (list, tuple)) and len(self) == len(o) and \
                    not rev and not ip):

                return self.__class__(*map(f, self, map(self.val_type, o)))

            # Операции над списком и вектором
            elif isinstance(o, (list, tuple)) and len(self) == len(o) and rev:
                return self.__class__(*map(f, map(self.val_type, o), self))

            # Операции над вектором и списком на месте
            elif isinstance(o, (list, tuple)) and len(self) == len(o) and ip:
                [self.__setitem__(idx, i) for idx, i in enumerate(
                        map(f, self, map(self.val_type, o)))]

                return self

            # Если у вектора и списка разные размеры:
            elif isinstance(o, (list, tuple)) and len(self) != len(0):
                raise TypeError(f"Invalid length of {o} for {self}. Required: {len(self)}")

            else:
                fname = f.__name__
                raise TypeError(f"{self} can't do '{fname}' operation with {o}")

        def __get_dim_map(self, dims):
            return {dim: idx for idx, dim, in enumerate(dims[:len(self)])}

        def dot(self, o):
            return sum(self * o)

        def cross(self, o):
            if len(self) != len(o):
                raise Exception(f"Can't do cross product betveen {self.__class__.__name__} and {o.__class__.__name__}")

            if len(self) == 2:
                return self[0] * o[1] - o[0] * self[1]

            elif len(self) == 3:
                return self.__class__(
                    self[1] * o[2] - o[1] * self[2],
                    self[2] * o[0] - o[2] * self[0],
                    self[0] * o[1] - o[0] * self[1])
            else:
                raise Exception(f"Can't do cross product for {len(self)}-dimensional vectors")

        @property
        def val_type(self):
            return type(self[0])

        @property
        def squared_length(self):
            return sum(i * i for i in self)

        @property
        def length(self):
            return math.sqrt(self.squared_length)

        @property
        def normalized(self):
            return self.__class__(*(self / self.length))

        def __repr__(self):
            name = self.__class__.__name__
            vals =", ".join(map(str, self))
            return f"{name}({vals})"

        def __getattr__(self, item):
            if len(item) == 1:
                idx = self._pos_getter(item)
                if idx is None: idx = self._color_getter(item)
                if idx is not None: return self[idx]

            if 1 < len(item) <= len(self):
                rv = []
                cur_getter = None
                for i in item:
                    if cur_getter is None and self._pos_getter(i) is not None:
                        cur_getter = self._pos_getter

                    elif cur_getter is None and self._color_getter(i) is not None:
                        cur_getter = self._color_getter

                    if cur_getter is None: break

                    cur_idx = cur_getter(i)
                    if cur_idx is None: break

                    rv.append(self[cur_idx])

                else:
                    return self.__list_to_vector(rv)

            # Для вызова стандартного исключения отсутствующего атрибута
            return object.__getattribute__(self, item)

        def __setattr__(self, item, value):
            # Нельзя менять больше компонентов, чем есть у вектора,
            if len(item) == 1:
                idx = self._pos_getter(item)
                if idx is None: idx = self._color_getter(item)
                if idx is not None: 
                    self[idx] = value
                    return

            elif 1 < len(item) <= len(self):
                if len(item) != len(set(item)):
                    raise AttributeError(f"'{self.__class__.__name__}' can't set one attribute at multiple times")
                cur_getter = None
                for val_idx, i in enumerate(item):
                    if cur_getter is None and self._pos_getter(i) is not None:
                        cur_getter = self._pos_getter

                    elif cur_getter is None and self._color_getter(i) is not None:
                        cur_getter = self._color_getter

                    if cur_getter is None: break

                    cur_idx = cur_getter(i)
                    if cur_idx is None: break
                    self[cur_idx] = value[val_idx]

                else:
                    return

            # Для вызова стандартного исключения отсутствующего атрибута
            return object.__getattribute__(self, item)

        def __list_to_vector(self, in_list):
            rv_types = {in_len: vec_type for in_len, vec_type in enumerate((vec2, vec3, vec4), start=2)}
            return rv_types[len(in_list)](*in_list, _type=self.val_type)

        # Операции с векторами
        # Сложение
        __add__ = lambda self, o: self.__calc(o, op.add)
        __radd__ = lambda self, o: self.__calc(o, op.add, rev=True)
        __iadd__ = lambda self, o: self.__calc(o, op.add, ip=True)

        # Вычитание
        __sub__ = lambda self, o: self.__calc(o, op.sub)
        __rsub__ = lambda self, o: self.__calc(o, op.sub, rev=True)
        __isub__ = lambda self, o: self.__calc(o, op.sub, ip=True)

        # Умножение
        __mul__ = lambda self, o: self.__calc(o, op.mul)
        __rmul__ = lambda self, o: self.__calc(o, op.mul, rev=True)
        __imul__ = lambda self, o: self.__calc(o, op.mul, ip=True)

        # Деление
        __truediv__ = lambda self, o: self.__calc(o, op.truediv)
        __rtruediv__ = lambda self, o: self.__calc(o, op.truediv, rev=True)
        __itruediv__ = lambda self, o: self.__calc(o, op.truediv, ip=True)

        # Деление целочисленное
        __floordiv__ = lambda self, o: self.__calc(o, op.floordiv)
        __rfloordiv__ = lambda self, o: self.__calc(o, op.floordiv, rev=True)
        __ifloordiv__ = lambda self, o: self.__calc(o, op.floordiv, ip=True)
            
        # Остаток от деления
        __mod__ = lambda self, o: self.__calc(o, op.mod)
        __rmod__ = lambda self, o: self.__calc(o, op.mod, rev=True)
        __imod__ = lambda self, o: self.__calc(o, op.mod, ip=True)

        # Возведение в степень:]
        __pow__ = lambda self, o: self.__calc(o, op.pow)
        __rpow__ = lambda self, o: self.__calc(o, op.pow, rev=True)
        __ipow__ = lambda self, o: self.__calc(o, op.pow, ip=True)

        # Можно даже вызывать divmod для векторов:]
        __divmod__ = lambda self, o: (self // o, self % o)
        __rdivmod__ = lambda self, o: (o // self, o % self)

        __round__ = lambda self, n: self.__class__(*map(round, self, itertools.repeat(n)))
        __abs__ = lambda self: self.__class__(*map(abs, self)) # abs(vec)
        __pos__ = lambda self: self.__class__(*self) # +vec
        __neg__ = lambda self: self * self._type(-1) # -vec

        __bool__ = lambda self: any(self) # vec is True

        copy = lambda self: self.__class__(*self)

        # Отключенные методы
        def __is_disabled(self):
            raise NotImplementedError

        append = lambda self, x: self.__is_disabled()
        clear = lambda self: self.__is_disabled()
        count = lambda self, x: self.__is_disabled()
        extend = lambda self, x: self.__is_disabled()
        insert = lambda self, x, y: self.__is_disabled()
        remove = lambda self, x: self.__is_disabled()
        reverse = lambda self: self.__is_disabled()
        def index(self, *args, **kwargs): self.__is_disabled()
        def pop(self, *args, **kwargs): self.__is_disabled()
        def sort(self, *args, **kwargs): self.__is_disabled()

    class vec2(Vector):
        def __init__(self, *vals, _type=float):
            super().__init__(*vals, _type=_type, dims=2)

    class vec3(Vector):
        def __init__(self, *vals, _type=float):
            super().__init__(*vals, _type=_type, dims=3)

    class vec4(Vector):
        pass

init python:
    vec2 = vector.vec2
    vec3 = vector.vec3
    vec4 = vector.vec4