from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Basket
from .serializers import (
    BasketExtraSerializer,
    BasketItemCreateSerializer,
    BasketItemSerializer,
    BasketSerializer,
)


class BasketViewSet(viewsets.ModelViewSet):
    """
    Basket API endpoint.
    """

    serializer_class = BasketItemSerializer
    lookup_field = 'ref'

    _basket = None

    def get_view_name(self):
        name = super().get_view_name()
        if name == "Basket List":
            return "Basket"
        if name == "Basket Instance":
            return "Basket Item"
        return name

    def get_basket(self):
        if not self._basket:
            self._basket, _ = Basket.objects.get_or_create_from_request(self.request)
        return self._basket

    def get_queryset(self):
        return self.get_basket().items.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return BasketItemCreateSerializer
        if self.action == 'list':
            return BasketSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['basket'] = self.get_basket()
        return context

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Show basket and items.
        """
        serializer = self.get_serializer(self.get_basket())
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """
        Delete the basket.
        """
        self.get_basket().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def count(self, request):
        """
        Show basket item count.
        """
        return Response({'count': self.get_basket().count})

    @action(detail=False, methods=['get'])
    def quantity(self, request):
        """
        Show basket total quantity.
        """
        return Response({'quantity': self.get_basket().quantity})

    @action(detail=False, methods=['post'], serializer_class=BasketSerializer)
    def clear(self, request):
        """
        Clear all items from basket.
        """
        self.get_basket().clear()
        return self.list(request)

    @action(detail=False, methods=['post'], serializer_class=BasketExtraSerializer)
    def extra(self, request):
        """
        Update basket extra data.
        """
        serializer = self.get_serializer(self.get_basket(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
