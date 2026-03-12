from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.helpdesk.models import HelpdeskChat, HelpdeskMessage
from apps.helpdesk.services.bot_service import ask, TRANSFER

User = get_user_model()


def _is_agent(user) -> bool:
    return user.groups.filter(name='helpdesk_agent').exists()


class HelpdeskService:
    @staticmethod
    def get_active_chat(user) -> HelpdeskChat | None:
        return (
            HelpdeskChat.objects
            .filter(user=user)
            .exclude(status__in=[HelpdeskChat.RESOLVED, HelpdeskChat.LOCKED])
            .order_by('-created_at')
            .first()
        )

    @staticmethod
    def list_user_chats(user, limit: int = 3) -> list[HelpdeskChat]:
        return list(
            HelpdeskChat.objects
            .filter(user=user, status__in=[HelpdeskChat.RESOLVED, HelpdeskChat.LOCKED])
            .order_by('-updated_at')[:limit]
        )

    @staticmethod
    def create_chat(user) -> HelpdeskChat:
        existing = HelpdeskService.get_active_chat(user)
        if existing:
            existing.status = HelpdeskChat.RESOLVED
            existing.save(update_fields=['status'])
        return HelpdeskChat.objects.create(user=user)

    @staticmethod
    def post_user_message(chat: HelpdeskChat, text: str) -> list[HelpdeskMessage]:
        if chat.is_closed:
            raise ValidationError('This chat is closed.')

        user_msg = HelpdeskMessage.objects.create(
            chat=chat, role=HelpdeskMessage.USER, content=text
        )
        new_messages = [user_msg]

        if (chat.status == HelpdeskChat.AGENT_OPEN) or (chat.status == HelpdeskChat.WAITING):
            return new_messages

        result = ask(text)

        if result == TRANSFER:
            new_messages += HelpdeskService._do_transfer(chat)
        else:
            bot_msg = HelpdeskMessage.objects.create(
                chat=chat,
                role=HelpdeskMessage.BOT,
                content=result,
            )
            new_messages.append(bot_msg)

        return new_messages

    @staticmethod
    def resolve_by_user(chat: HelpdeskChat) -> HelpdeskChat:
        if chat.is_closed:
            raise ValidationError('Chat is already closed.')
        chat.status = HelpdeskChat.RESOLVED
        chat.save(update_fields=['status', 'updated_at'])
        HelpdeskMessage.objects.create(
            chat=chat, role=HelpdeskMessage.SYSTEM,
            content='Chat resolved by user.'
        )
        return chat

    @staticmethod
    def request_agent(chat: HelpdeskChat) -> list[HelpdeskMessage]:
        if chat.is_closed:
            raise ValidationError('Chat is closed.')
        if chat.status in (HelpdeskChat.WAITING, HelpdeskChat.AGENT_OPEN):
            raise ValidationError('Agent already requested or assigned.')
        return HelpdeskService._do_transfer(chat)

    @staticmethod
    def list_agent_chats() -> list[HelpdeskChat]:
        """All chats needing attention: waiting + agent_open."""
        return list(
            HelpdeskChat.objects
            .filter(status__in=[HelpdeskChat.WAITING, HelpdeskChat.AGENT_OPEN])
            .select_related('user', 'assigned_agent')
            .order_by('updated_at')
        )

    @staticmethod
    def mark_chat_read(user, chat: 'HelpdeskChat') -> None:
        from apps.helpdesk.models import ChatReadState
        latest = chat.messages.order_by('-id').values_list('id', flat=True).first()
        if latest is None:
            return
        ChatReadState.objects.update_or_create(
            user=user,
            chat=chat,
            defaults={'last_read_message_id': latest},
        )

    @staticmethod
    def _unread_count_for(user, chat: 'HelpdeskChat') -> int:
        from apps.helpdesk.models import ChatReadState
        try:
            state = ChatReadState.objects.get(user=user, chat=chat)
            last_read = state.last_read_message_id
        except ChatReadState.DoesNotExist:
            last_read = 0
        return (
            chat.messages
            .filter(id__gt=last_read)
            .exclude(role='system')
            .exclude(sender=user)
            .count()
        )

    @staticmethod
    def get_user_unread_counts(user) -> dict:
        from apps.helpdesk.models import ChatReadState
        active_chats = list(
            HelpdeskChat.objects
            .filter(user=user)
            .exclude(status__in=[HelpdeskChat.RESOLVED, HelpdeskChat.LOCKED])
            .prefetch_related('messages')
        )
        if not active_chats:
            return {}

        states = {
            rs.chat_id: rs.last_read_message_id
            for rs in ChatReadState.objects.filter(user=user, chat__in=active_chats)
        }

        result = {}
        for chat in active_chats:
            last_read = states.get(chat.id, 0)
            count = (
                chat.messages
                .filter(id__gt=last_read)
                .exclude(role='system')
                .exclude(sender=user)
                .count()
            )
            if count:
                result[chat.id] = count
        return result

    @staticmethod
    def get_agent_unread_counts(agent) -> dict:
        from apps.helpdesk.models import ChatReadState
        active_chats = list(
            HelpdeskChat.objects
            .exclude(status__in=[HelpdeskChat.RESOLVED, HelpdeskChat.LOCKED])
            .prefetch_related('messages')
        )
        if not active_chats:
            return {}

        states = {
            rs.chat_id: rs.last_read_message_id
            for rs in ChatReadState.objects.filter(user=agent, chat__in=active_chats)
        }

        result = {}
        for chat in active_chats:
            last_read = states.get(chat.id, 0)
            count = (
                chat.messages
                .filter(id__gt=last_read, role='user')
                .count()
            )
            if count:
                result[chat.id] = count
        return result

    @staticmethod
    def list_all_closed(search: str = '', page: int = 1, page_size: int = 20):
        from django.db.models import Q
        qs = (
            HelpdeskChat.objects
            .filter(status__in=[HelpdeskChat.RESOLVED, HelpdeskChat.LOCKED])
            .select_related('user', 'assigned_agent')
            .order_by('-updated_at')
        )
        if search:
            qs = qs.filter(
                Q(user__username__icontains=search) |
                Q(assigned_agent__username__icontains=search)
            )
        total  = qs.count()
        offset = (page - 1) * page_size
        return list(qs[offset:offset + page_size]), total

    @staticmethod
    def assign_agent(chat: HelpdeskChat, agent) -> HelpdeskChat:
        if not _is_agent(agent):
            raise ValidationError('User does not have the helpdesk_agent role.')
        if chat.status not in (HelpdeskChat.WAITING, HelpdeskChat.AGENT_OPEN):
            raise ValidationError('Chat is not awaiting an agent.')
        chat.assigned_agent = agent
        chat.status = HelpdeskChat.AGENT_OPEN
        chat.save(update_fields=['assigned_agent', 'status', 'updated_at'])
        HelpdeskMessage.objects.create(
            chat=chat, role=HelpdeskMessage.SYSTEM,
            content=f'{agent.username} has joined the chat.'
        )
        return chat

    @staticmethod
    def post_agent_message(chat: HelpdeskChat, agent, text: str) -> HelpdeskMessage:
        if not _is_agent(agent):
            raise ValidationError('User does not have the helpdesk_agent role.')
        if chat.status != HelpdeskChat.AGENT_OPEN:
            raise ValidationError('Chat is not in agent-open state.')
        return HelpdeskMessage.objects.create(
            chat=chat, role=HelpdeskMessage.AGENT, sender=agent, content=text
        )

    @staticmethod
    def resolve_by_agent(chat: HelpdeskChat, agent) -> HelpdeskChat:
        if not _is_agent(agent):
            raise ValidationError('User does not have the helpdesk_agent role.')
        if chat.is_closed:
            raise ValidationError('Chat is already closed.')
        chat.status = HelpdeskChat.RESOLVED
        chat.save(update_fields=['status', 'updated_at'])
        HelpdeskMessage.objects.create(
            chat=chat, role=HelpdeskMessage.SYSTEM,
            content=f'Chat resolved by agent {agent.username}.'
        )
        return chat

    @staticmethod
    def _do_transfer(chat: HelpdeskChat) -> list[HelpdeskMessage]:
        chat.status = HelpdeskChat.WAITING
        chat.save(update_fields=['status', 'updated_at'])
        bot_msg = HelpdeskMessage.objects.create(
            chat=chat, role=HelpdeskMessage.BOT,
            content=(
                "I've passed your chat to our support team. "
                "A helpdesk agent will join shortly. "
                "You can keep typing if you'd like to add more context."
            )
        )
        sys_msg = HelpdeskMessage.objects.create(
            chat=chat, role=HelpdeskMessage.SYSTEM,
            content='Waiting for a helpdesk agent.'
        )
        return [bot_msg, sys_msg]