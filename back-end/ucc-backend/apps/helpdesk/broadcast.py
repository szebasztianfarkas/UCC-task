from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _room(chat_id: int) -> str:
    return f'helpdesk_{chat_id}'


def _serialize_message(msg) -> dict:
    return {
        'id':         msg.id,
        'role':       msg.role,
        'sender':     {'id': msg.sender.id, 'username': msg.sender.username} if msg.sender else None,
        'content':    msg.content,
        'created_at': msg.created_at.isoformat(),
    }


def broadcast_message(chat_id: int, message) -> None:
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        _room(chat_id),
        {
            'type':    'chat.message',
            'message': _serialize_message(message),
        },
    )


def broadcast_messages(chat_id: int, messages: list) -> None:
    for msg in messages:
        broadcast_message(chat_id, msg)


def broadcast_status(chat_id: int, status: str) -> None:
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        _room(chat_id),
        {
            'type':   'chat.status_change',
            'status': status,
            'chat_id': chat_id,
        },
    )