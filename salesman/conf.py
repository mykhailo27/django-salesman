"""
Settings module.
"""

from __future__ import annotations

from typing import Callable

from salesman.orders.status import BaseOrderStatus


class DefaultSettings:
    @property
    def SALESMAN_PRODUCT_TYPES(self) -> dict:
        """
        A dictionary of product types and their respected serializers
        that are availible for purchase as product. Should be
        formated as ``'app_label.Model': 'path.to.Serializer'``.
        """
        product_types = self._setting('SALESMAN_PRODUCT_TYPES', {})
        ret = {}

        for key, value in product_types.items():
            model = self._model(key)
            ret[key] = self._callable(value)

            for attr in ['name', 'code']:
                if not hasattr(model, attr):
                    self._error(f"Product type `{key}` must define `{attr}` attribute.")

            if not hasattr(model, 'get_price'):
                self._error(f"Product type `{key}` must implement `get_price` method.")
        return ret

    @property
    def SALESMAN_BASKET_MODIFIERS(self) -> list:
        """
        A list of strings formated as ``path.to.CustomModifier``.
        Modifiers must extend ``salesman.basket.modifiers.BasketModifier`` class.
        and define a unique ``identifier`` attribute.
        """
        from salesman.basket.modifiers import BasketModifier

        basket_modifiers = self._setting('SALESMAN_BASKET_MODIFIERS', [])
        ret, identifiers = [], []

        for value in basket_modifiers:
            modifier = self._callable(value)
            identifier = getattr(modifier, 'identifier', None)

            if not issubclass(modifier, BasketModifier):
                self._error(f"Modifer `{modifier}` must subclass `{BasketModifier}`.")

            if not identifier:
                self._error(f"Modifier `{modifier}` must define a unique `idetifier`.")

            if identifier in identifiers:
                self._error(f"Modifier `{identifier}` appears more than once.")

            identifiers.append(identifier)
            ret.append(modifier)
        return ret

    @property
    def SALESMAN_BASKET_ITEM_VALIDATOR(self) -> Callable:
        """
        A dotted path to basket item validator function.
        """
        default = "salesman.basket.utils.validate_basket_item"
        value = self._setting('SALESMAN_BASKET_ITEM_VALIDATOR', default)
        return self._callable(value)

    @property
    def SALESMAN_BASKET_MODEL(self) -> str:
        """
        A dotted path to the Basket model. Must be set before migrations.
        """
        return self._setting('SALESMAN_BASKET_MODEL', 'salesmanbasket.Basket')

    @property
    def SALESMAN_BASKET_ITEM_MODEL(self) -> str:
        """
        A dotted path to the Basket Item model. Must be set before migrations.
        """
        return self._setting('SALESMAN_BASKET_ITEM_MODEL', 'salesmanbasket.BasketItem')

    @property
    def SALESMAN_PAYMENT_METHODS(self) -> list:
        """
        A list of strings formated as ``path.to.CustomPayment``.
        Payments must extend ``salesman.checkout.payment.PaymentMethod`` class
        and define a unique ``identifier`` attribute.
        """
        from salesman.checkout.payment import PaymentMethod

        payment_methods = self._setting('SALESMAN_PAYMENT_METHODS', [])
        ret, identifiers = [], []

        for value in payment_methods:
            payment = self._callable(value)
            identifier = getattr(payment, 'identifier', None)

            if not issubclass(payment, PaymentMethod):
                self._error(f"Payment `{payment}` must subclass `{PaymentMethod}`.")

            if not getattr(payment, 'label', None):
                self._error(f"Payment `{payment}` must define a `label`.")

            if not identifier:
                self._error(f"Payment `{payment}` must define a unique `identifier`.")

            if identifier in identifiers:
                self._error(f"Payment `{identifier}` appears more than once.")

            identifiers.append(identifier)
            ret.append(payment)
        return ret

    @property
    def SALESMAN_ORDER_STATUS(self) -> BaseOrderStatus:
        """
        A dotted path to enum class that contains available order statuses.
        Overriden class must extend ``salesman.orders.status.BaseOrderStatus`` class.
        Can optionally override a class method ``get_payable`` that returns a list of
        statuses an order is eligible to be paid from, ``get_transitions`` method that
        returns a dict of statuses with their transitions and ``validate_transition``
        method to validate status transitions.
        """
        default = 'salesman.orders.status.OrderStatus'
        value = self._setting('SALESMAN_ORDER_STATUS', default)
        status = self._callable(value)

        if not issubclass(status, BaseOrderStatus):
            self._error(f"Status `{status}` must subclass `{BaseOrderStatus}`.")

        required = ['NEW', 'CREATED', 'COMPLETED', 'REFUNDED']
        for item in required:
            if item not in status.names or status[item].value != item:
                self._error(
                    "Status must specify members with names/values "
                    "`NEW`, `CREATED`, `COMPLETED` and `REFUNDED`."
                )
        return status

    @property
    def SALESMAN_ORDER_REFERENCE_GENERATOR(self) -> Callable:
        """
        A dotted path to reference generator function for new orders.
        Function should accept a django request object as param: ``request``.
        """
        default = 'salesman.orders.utils.generate_ref'
        value = self._setting('SALESMAN_ORDER_REFERENCE_GENERATOR', default)
        return self._callable(value)

    @property
    def SALESMAN_ORDER_SERIALIZER(self) -> type:
        """
        A dotted path to a serializer class for Order.
        """
        default = 'salesman.orders.serializers.OrderSerializer'
        value = self._setting("SALESMAN_ORDER_SERIALIZER", default)
        return self._callable(value)

    @property
    def SALESMAN_ORDER_SUMMARY_SERIALIZER(self) -> type:
        """
        A dotted path to a summary serializer class for Order.
        """
        value = self._setting("SALESMAN_ORDER_SUMMARY_SERIALIZER", None)
        if not value:
            return self.SALESMAN_ORDER_SERIALIZER
        return self._callable(value)

    @property
    def SALESMAN_ORDER_MODEL(self) -> str:
        """
        A dotted path to the Order model. Must be set before migrations.
        """
        return self._setting('SALESMAN_ORDER_MODEL', 'salesmanorders.Order')

    @property
    def SALESMAN_ORDER_ITEM_MODEL(self) -> str:
        """
        A dotted path to the Order Item model. Must be set before migrations.
        """
        return self._setting('SALESMAN_ORDER_ITEM_MODEL', 'salesmanorders.OrderItem')

    @property
    def SALESMAN_ORDER_PAYMENT_MODEL(self) -> str:
        """
        A dotted path to the Order Payment model. Must be set before migrations.
        """
        return self._setting(
            'SALESMAN_ORDER_PAYMENT_MODEL', 'salesmanorders.OrderPayment'
        )

    @property
    def SALESMAN_ORDER_NOTE_MODEL(self) -> str:
        """
        A dotted path to the Order Note model. Must be set before migrations.
        """
        return self._setting('SALESMAN_ORDER_NOTE_MODEL', 'salesmanorders.OrderNote')

    @property
    def SALESMAN_PRICE_FORMATTER(self) -> Callable:
        """
        A dotted path to price formatter function. Function should accept a value
        of type: ``Decimal`` and return a price formatted string. Also recieves
        a ``context`` dictionary with additional render data like ``request``
        and either the ``basket`` or ``order`` object.
        """
        default = 'salesman.core.utils.format_price'
        value = self._setting('SALESMAN_PRICE_FORMATTER', default)
        return self._callable(value)

    @property
    def SALESMAN_ADDRESS_VALIDATOR(self) -> Callable:
        """
        A dotted path to address validator function. Function should accept a string
        value and return a validated version. Also recieves a ``context`` dictionary
        with additional validator context data like ``request``, a ``basket`` object
        and ``address`` type (set to either *shipping* or *billing*).
        """
        default = 'salesman.checkout.utils.validate_address'
        value = self._setting('SALESMAN_ADDRESS_VALIDATOR', default)
        return self._callable(value)

    @property
    def SALESMAN_EXTRA_VALIDATOR(self) -> Callable:
        """
        A dotted path to extra validator function. Function should accept a dict
        value and return a validated version. Also recieves a ``context`` dictionary
        with additional validator context data like ``request``, a ``basket`` object
        and ``basket_item`` in case validation is for bakset item.
        """
        default = 'salesman.basket.utils.validate_extra'
        value = self._setting('SALESMAN_EXTRA_VALIDATOR', default)
        return self._callable(value)

    @property
    def SALESMAN_ADMIN_REGISTER(self) -> bool:
        """
        Set to ``False`` to skip Salesman admin registration, in case
        you wish to build your own ``ModelAdmin`` for Django or Wagtail.
        """
        return self._setting('SALESMAN_ADMIN_REGISTER', True)

    @property
    def SALESMAN_ADMIN_CUSTOMER_FORMATTER(self) -> Callable:
        """
        A dotted path to Customer formatter function. Function should accept
        user as argument and return a string for customer display. Also recieves
        a ``context`` dictionary with additional render data.
        """
        default = 'salesman.admin.utils.format_customer'
        value = self._setting('SALESMAN_ADMIN_CUSTOMER_FORMATTER', default)
        return self._callable(value)

    @property
    def SALESMAN_ADMIN_JSON_FORMATTER(self) -> Callable:
        """
        A dotted path to JSON formatter function. Function should accept a dict
        value and return an HTML formatted string. Also recieves a ``context``
        dictionary with additional render data.
        """
        default = 'salesman.admin.utils.format_json'
        value = self._setting('SALESMAN_ADMIN_JSON_FORMATTER', default)
        return self._callable(value)

    def _setting(self, name, default=None):
        from django.conf import settings

        return getattr(settings, name, default)

    def _error(self, message):
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(message)

    def _model(self, label):
        from django.apps import apps

        try:
            app_label, model_name = label.split('.')
        except ValueError:
            self._error(f"Invalid model `{label}`, format as `app_label.Model`.")
        try:
            return apps.get_model(app_label, model_name)
        except LookupError as e:
            self._error(e)

    def _callable(self, path):
        from django.utils.module_loading import import_string

        try:
            value = import_string(path)
        except ImportError as e:
            self._error(e)
        if not callable(value):
            self._error(f"Specified `{value}` is not a callable.")
        return value


app_settings = DefaultSettings()
