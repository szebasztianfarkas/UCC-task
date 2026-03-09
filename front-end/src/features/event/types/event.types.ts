export interface EventAttendee {
  id: number
  username: string
  avatar: string
}

export interface Event {
  id: number
  title: string
  occurrence: string
  description: string
  created_by: EventAttendee
  attendees: EventAttendee[]
  attendee_count: number
  is_attending: boolean
  is_owner: boolean
  created_at: string
  updated_at: string
}

export interface CreateEventPayload {
  title: string
  occurrence: string
  description?: string
}

export interface UpdateEventPayload {
  title?: string
  occurrence?: string
  description?: string
}

export interface EventFilters {
  search?: string
  upcoming?: boolean
  attending?: boolean
}