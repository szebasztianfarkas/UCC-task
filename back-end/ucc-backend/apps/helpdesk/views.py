from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.helpdesk.models import HelpdeskChat
from apps.helpdesk.serializers import (
    HelpdeskChatSerializer,
    HelpdeskChatSummarySerializer,
    HelpdeskMessageSerializer,
    PostMessageSerializer,
)
from apps.helpdesk.services.helpdesk_service import HelpdeskService, _is_agent
from apps.helpdesk.broadcast import broadcast_messages, broadcast_message, broadcast_status


def _err(e):
    msg = e.message if hasattr(e, 'message') else str(e)
    return Response({'detail': msg}, status=status.HTTP_400_BAD_REQUEST)


class MyChatListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Helpdesk'], summary='List my closed chats (sidebar history)',
                   responses={200: HelpdeskChatSummarySerializer(many=True)})
    def get(self, request):
        chats = HelpdeskService.list_user_chats(request.user, limit=3)
        return Response(HelpdeskChatSummarySerializer(chats, many=True).data)

    @extend_schema(tags=['Helpdesk'], summary='Create a new helpdesk chat',
                   responses={201: HelpdeskChatSerializer})
    def post(self, request):
        chat = HelpdeskService.create_chat(request.user)
        return Response(HelpdeskChatSerializer(chat).data, status=status.HTTP_201_CREATED)


class MyActiveChatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Helpdesk'], summary='Get active chat (if any)',
                   responses={200: HelpdeskChatSerializer, 204: None})
    def get(self, request):
        chat = HelpdeskService.get_active_chat(request.user)
        if not chat:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(HelpdeskChatSerializer(chat).data)


class ChatDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_chat(self, request, pk):
        chat = get_object_or_404(HelpdeskChat, pk=pk)
        if not _is_agent(request.user) and chat.user != request.user:
            return None
        return chat

    @extend_schema(tags=['Helpdesk'], summary='Get a chat by ID',
                   responses={200: HelpdeskChatSerializer})
    def get(self, request, pk):
        chat = self._get_chat(request, pk)
        if not chat:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(HelpdeskChatSerializer(chat).data)

    @extend_schema(tags=['Helpdesk'], summary='Send a message to a chat',
                   request=PostMessageSerializer,
                   responses={201: HelpdeskMessageSerializer(many=True)})
    def post(self, request, pk):
        chat = self._get_chat(request, pk)
        if not chat:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = PostMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data['text']

        try:
            if _is_agent(request.user) and chat.status == HelpdeskChat.AGENT_OPEN:
                msgs = [HelpdeskService.post_agent_message(chat, request.user, text)]
            else:
                msgs = HelpdeskService.post_user_message(chat, text)
        except ValidationError as e:
            return _err(e)

        broadcast_messages(chat.id, msgs)
        chat.refresh_from_db()
        broadcast_status(chat.id, chat.status)

        return Response(HelpdeskMessageSerializer(msgs, many=True).data,
                        status=status.HTTP_201_CREATED)


class ResolveView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Helpdesk'], summary='Resolve chat (user says: yes, solved)',
                   responses={200: HelpdeskChatSerializer})
    def post(self, request, pk):
        chat = get_object_or_404(HelpdeskChat, pk=pk, user=request.user)
        try:
            chat = HelpdeskService.resolve_by_user(chat)
        except ValidationError as e:
            return _err(e)
        broadcast_status(chat.id, chat.status)
        return Response(HelpdeskChatSerializer(chat).data)


class RequestAgentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Helpdesk'], summary='Request a human agent',
                   responses={201: HelpdeskMessageSerializer(many=True)})
    def post(self, request, pk):
        chat = get_object_or_404(HelpdeskChat, pk=pk, user=request.user)
        try:
            msgs = HelpdeskService.request_agent(chat)
        except ValidationError as e:
            return _err(e)
        broadcast_messages(chat.id, msgs)
        broadcast_status(chat.id, HelpdeskChat.WAITING)
        return Response(HelpdeskMessageSerializer(msgs, many=True).data,
                        status=status.HTTP_201_CREATED)


class AgentQueueView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Helpdesk - Agent'], summary='List all chats needing attention',
                   responses={200: HelpdeskChatSummarySerializer(many=True)})
    def get(self, request):
        if not _is_agent(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        chats = HelpdeskService.list_agent_chats()
        return Response(HelpdeskChatSummarySerializer(chats, many=True).data)


class AgentAssignView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Helpdesk - Agent'], summary='Assign yourself to a waiting chat',
                   responses={200: HelpdeskChatSerializer})
    def post(self, request, pk):
        if not _is_agent(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        chat = get_object_or_404(HelpdeskChat, pk=pk)
        try:
            chat = HelpdeskService.assign_agent(chat, request.user)
        except ValidationError as e:
            return _err(e)
        sys_msg = chat.messages.filter(role='system').last()
        if sys_msg:
            broadcast_message(chat.id, sys_msg)
        broadcast_status(chat.id, chat.status)
        return Response(HelpdeskChatSerializer(chat).data)


class AgentResolveView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Helpdesk - Agent'], summary='Resolve a chat as agent',
                   responses={200: HelpdeskChatSerializer})
    def post(self, request, pk):
        if not _is_agent(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        chat = get_object_or_404(HelpdeskChat, pk=pk)
        try:
            chat = HelpdeskService.resolve_by_agent(chat, request.user)
        except ValidationError as e:
            return _err(e)
        sys_msg = chat.messages.filter(role='system').last()
        if sys_msg:
            broadcast_message(chat.id, sys_msg)
        broadcast_status(chat.id, chat.status)
        return Response(HelpdeskChatSerializer(chat).data)