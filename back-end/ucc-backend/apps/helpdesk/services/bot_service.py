import re

TRANSFER = '__TRANSFER__'

KNOWLEDGE_BASE = [
    {
        'triggers': ['agent', 'human', 'person', 'staff', 'representative', 'rep',
                     'real', 'speak', 'talk', 'connect', 'transfer', 'escalate',
                     'operator', 'live', 'someone'],
        'answer': TRANSFER,
    },
    {
        'triggers': ['event', 'events', 'browse', 'list', 'see', 'view', 'show'],
        'answer': (
            "You can browse all events on the Events dashboard. "
            "Use the search bar to filter by title or description, "
            "and the Upcoming and Attending filter pills to narrow results. "
            "Past events appear at reduced opacity and cannot be joined."
        ),
    },
    {
        'triggers': ['event', 'events', 'join', 'attend', 'rsvp', 'sign', 'going', 'register'],
        'answer': (
            "To join an event, click the Join button on its card. "
            "You cannot join an event you created yourself. "
            "Once joined the button switches to Leave, which removes you from the attendee list."
        ),
    },
    {
        'triggers': ['event', 'events', 'leave', 'unjoin', 'withdraw', 'quit', 'drop'],
        'answer': (
            "To leave an event you have joined, click the Leave button on the event card. "
            "Your spot is freed immediately and the attendee count updates straight away."
        ),
    },
    {
        'triggers': ['event', 'events', 'create', 'new', 'add', 'make', 'organise', 'organize', 'host', 'schedule'],
        'answer': (
            "Click New event at the top right of the Events page. "
            "Fill in a title and date/time — both are required. "
            "An optional description can help attendees understand what to expect. "
            "Click Create and the event appears in the list immediately, "
            "with you listed as the organiser."
        ),
    },
    {
        'triggers': ['event', 'events', 'edit', 'update', 'modify', 'rename', 'change event', 'correct'],
        'answer': (
            "Click the pencil icon on an event card to edit it. "
            "You can update the title, date/time, and description. "
            "Only the event creator can edit or delete their events."
        ),
    },
    {
        'triggers': ['event', 'events', 'delete', 'remove event', 'destroy', 'cancel event'],
        'answer': (
            "Click the trash icon on an event card you created, then confirm the prompt. "
            "Deletion is permanent — attendees will lose access immediately."
        ),
    },
    {
        'triggers': ['edit', 'account', 'profile', 'bio', 'settings', 'username', 'name'],
        'answer': (
            "Click your username in the bottom-left sidebar to open your Profile page. "
            "There you can update your bio. "
            "Username changes are not currently supported — "
            "contact an administrator if you need your username changed."
        ),
    },
    {
        'triggers': ['change', 'email', 'address', 'mail', 'inbox'],
        'answer': (
            "To change your email, open the Profile page and enter a new address in the Email section. "
            "A confirmation link will be sent to the new address — click it within one hour to apply the change. "
            "If you have MFA enabled you will confirm with your authenticator code instead."
        ),
    },
    {
        'triggers': ['password', 'passwd', 'credential', 'credentials', 'forgot', 'reset'],
        'answer': (
            "To change your password, go to your Profile page, enter your current password "
            "and the new one, then click Change password. "
            "If MFA is enabled you will also need your authenticator code. "
            "If you have forgotten your password, use the Forgot password link on the login page."
        ),
    },
    {
        'triggers': ['mfa', '2fa', 'two-factor', 'authenticator', 'totp', 'otp',
                     'verification', 'verify', 'secure', 'security'],
        'answer': (
            "MFA (multi-factor authentication) adds a second layer of security to your account. "
            "When enabled, signing in and making sensitive changes (like updating your password) "
            "requires a 6-digit code from your authenticator app in addition to your password. "
            "Contact an administrator to set up or reset MFA for your account."
        ),
    },
    {
        'triggers': ['helpdesk', 'support', 'ticket', 'issue', 'problem', 'question', 'help', 'ask'],
        'answer': (
            "This is the Evently helpdesk. Type your question and the bot will do its best to help. "
            "After each bot answer you can choose whether the answer solved your issue. "
            "If not, a helpdesk agent will be assigned to continue the conversation with you. "
            "Your previous chats are listed in the sidebar so you can refer back to them."
        ),
    },
    {
        'triggers': ['locked', 'lock', 'closed', 'readonly', 'read-only', 'archive'],
        'answer': (
            "A locked chat has been closed by an administrator. "
            "You can still read the full conversation but can no longer send messages. "
            "A resolved chat is one you or an agent closed after the issue was sorted. "
            "Start a new helpdesk chat from the sidebar if you have a new question."
        ),
    },
    {
        'triggers': ['logout', 'signout', 'sign out', 'log out', 'exit'],
        'answer': (
            "Click the red Sign out button at the bottom of the left sidebar. "
            "Your session ends immediately and you will be taken to the login page."
        ),
    },
    {
        'triggers': ['attendee', 'attendees', 'who', 'participants', 'people', 'members', 'going'],
        'answer': (
            "Each event card shows the initials of up to four attendees. "
            "If more people have joined, a +N badge indicates the remaining count. "
            "The total attendee number is shown next to the attendee bubbles."
        ),
    },
    {
        'triggers': ['search', 'filter', 'upcoming', 'past', 'attending', 'find event'],
        'answer': (
            "The Events page has a live search bar that matches event titles and descriptions. "
            "Use the Upcoming filter to show only future events, "
            "or Attending to show only events you have joined. "
            "These filters stack with the search query."
        ),
    },
    {
        'triggers': ['notification', 'notify', 'alert', 'remind', 'reminder', 'email notification'],
        'answer': (
            "Evently does not currently send event reminder notifications. "
            "Make a note of the event date yourself or add it to your personal calendar."
        ),
    },
    {
        'triggers': ['invite', 'share', 'link', 'send', 'friend'],
        'answer': (
            "You can share an event by copying the page URL and sending it to others. "
            "There is no built-in invite or share button at this time."
        ),
    },
    {
        'triggers': ['capacity', 'limit', 'max', 'full', 'spots', 'seats'],
        'answer': (
            "Events do not currently have a capacity limit — anyone can join until the event passes. "
            "If you need capped attendance, please ask an administrator."
        ),
    },
    {
        'triggers': ['time', 'timezone', 'zone', 'utc', 'local'],
        'answer': (
            "Event times are stored in UTC and displayed in your browser's local timezone automatically. "
            "If a time looks wrong, check that your device's timezone is set correctly."
        ),
    },
]

MIN_SCORE = 1


def _tokenise(text: str) -> set[str]:
    return set(re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)*', text.lower()))


def ask(question: str) -> str | None:
    tokens = _tokenise(question)
    best_score  = 0
    best_answer = None

    for entry in KNOWLEDGE_BASE:
        score = sum(1 for t in entry['triggers'] if t in tokens)
        if score > best_score:
            best_score  = score
            best_answer = entry['answer']

    return best_answer if best_score >= MIN_SCORE else None